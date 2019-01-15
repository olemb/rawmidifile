import struct


DEFAULT_RESOLUTION = 240


def read_chunk_header(infile):
    header = infile.read(8)
    if len(header) < 8:
        raise EOFError

    # TODO: check for b'RIFF' and switch endian?

    return struct.unpack('>4sL', header)


def read_file_header(infile):
    name, size = read_chunk_header(infile)

    if name != b'MThd':
        raise IOError('MThd not found. Probably not a MIDI file')
    else:
        data = infile.read(size)

        if len(data) < 6:
            raise EOFError

    return struct.unpack('>hhh', data[:6])
         

def read_byte(infile):
    return ord(infile.read(1))


def read_variable_int(infile):
    delta = 0

    while True:
        byte = read_byte(infile)
        delta = (delta << 7) | (byte & 0x7f)
        if byte < 0x80:
            return delta


def encode_variable_int(value):
    """Encode variable length integer.

    Returns the integer as a list of bytes,
    where the last byte is < 128.

    This is used for delta times and meta message payload
    length.
    """
    bytes = []
    while value:
        bytes.append(value & 0x7f)
        value >>= 7

    if bytes:
        bytes.reverse()

        # Set high bit in every byte but the last.
        for i in range(len(bytes) - 1):
            bytes[i] |= 0x80
        return bytes
    else:
        return [0]


def get_msg_len(status):
    # Channel messages:
    if 0x80 <= status <= 0xbf or 0xe0 <= status <= 0xef:
         return 3
    elif 0xc0 <= status <= 0xdf:
         return 2
    else:
         return {0xf1: 2,
                 0xf2: 3,
                 0xf3: 2,
                 0xf6: 1,
                 0xf8: 1,
                 0xfa: 1,
                 0xfb: 1,
                 0xfc: 1,
                 0xfe: 1,
                 0xff: 1,}[status]


def read_message(infile, status_byte, peek_data):
    msg_len = get_msg_len(status_byte)

    # Subtract 1 for status byte.
    size = msg_len - 1 - len(peek_data)
    data_bytes = peek_data + infile.read(size)

    return bytes([status_byte]) + data_bytes


def read_sysex(infile):
    length = read_variable_int(infile)
    data = infile.read(length)

    # Strip start and end bytes.
    # TODO: is this necessary?
    data = data.lstrip(b'\xf0').rstrip(b'\xf7')

    return b'\xf0' + data + b'\xf7'


def read_meta_message(infile):
    meta_type = infile.read(1)
    length = read_variable_int(infile)
    data = infile.read(length)
    return b'\xff' + meta_type + data


def read_track(infile):
    track = []

    name, size = read_chunk_header(infile)

    if name != b'MTrk':
        raise IOError('no MTrk header at start of track')

    start = infile.tell()
    last_status = None

    while True:
        # End of track reached.
        if infile.tell() - start == size:
            break

        delta = read_variable_int(infile)

        status_byte = read_byte(infile)

        if status_byte < 0x80:
            if last_status is None:
                raise IOError('running status without last_status')
            peek_data = bytes([status_byte])
            status_byte = last_status
        else:
            if status_byte != 0xff:
                # Meta messages don't set running status.
                last_status = status_byte
            peek_data = bytes()

        if status_byte == 0xff:
            msg = read_meta_message(infile)

        elif status_byte in [0xf0, 0xf7]:
            # TODO: I'm not quite clear on the difference between
            # f0 and f7 events.
            msg = read_sysex(infile)
        else:
            msg = read_message(infile, status_byte, peek_data)

        track.append((delta, msg))

    return track


def print_event(event):
    delta = event[0]
    msg = ' '.join(['{:02x}'.format(byte) for byte in event[1]])
    print(f'{delta:5}  {msg}  {event[1]}')


def write_chunk(outfile, name, data):
    """Write an IFF chunk to the file.

    `name` must be a bytestring."""
    outfile.write(name)
    outfile.write(struct.pack('>L', len(data)))
    outfile.write(data)


def write_track(outfile, track):
    data = bytearray()

    running_status_byte = None
    for (delta, msg) in track:
        data.extend(encode_variable_int(delta))

        if is_meta(msg):
            data.extend(msg[:2])  # 0xff and meta type
            data.extend(encode_variable_int(len(msg[2:])))
            data.extend(msg[2:])
            running_status_byte = None
        elif msg[0] == 0xf0:
            data.append(0xf0)
            # length (+ 1 for end byte (0xf7))
            data.extend(encode_variable_int(len(msg.data) + 1))
            data.extend(msg[1:])
            running_status_byte = None
        else:
            status_byte = msg[0]

            if status_byte == running_status_byte:
                data.extend(msg[1:])
            else:
                data.extend(msg)

            if status_byte < 0xf0:
                running_status_byte = status_byte
            else:
                running_status_byte = None

    write_chunk(outfile, b'MTrk', data)


def write_rawmidifile(outfile, tracks=(),
                       format=1, resolution=DEFAULT_RESOLUTION):
    if isinstance(outfile, str):
        with open(outfile, 'wb') as fp:
            return write_rawmidifile(fp, format=format,
                                     resolution=resolution, tracks=tracks)
        
    header = struct.pack('>hhh', format,
                         len(tracks),
                         resolution)
    write_chunk(outfile, b'MThd', header)

    for track in tracks:
        write_track(outfile, track)


def read_rawmidifile(infile):
    if isinstance(infile, str):
        with open(infile, 'rb') as fp:
            return read_rawmidifile(fp)


    (format,
     num_tracks,
     resolution) = read_file_header(infile)
    tracks = [read_track(infile) for _ in range(num_tracks)]

    return {'format': format, 'resolution': resolution, 'tracks': tracks}


def is_meta(msg):
    return msg.startswith(b'\xff') and len(msg) > 1


__all__ = ['read_rawmidifile', 'write_rawmidifile', 'is_meta']
