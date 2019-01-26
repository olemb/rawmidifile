"""
Example of writing a basic MIDI file reader for midict:
https://github.com/olemb/midict/

This doesn't supports only 'track_name', 'marker' and 'end_of_track'.
All other messages are returned as 'unknown_meta'.

"""
from rawmidifile import read_rawmidifile, is_meta
from midict import from_bytes

# This is just a quickly put together example. It could use some more
# though.
meta_specs = {
    0x03: {
        'prototype': {'type': 'track_name', 'name': ''},
        'has_text': True,
        'encode': lambda msg, encoding: msg['name'].encode(encoding),
        'decode': lambda data, encoding: {'name': data.decode(encoding)},
    },
    0x06: {
        'prototype': {'type': 'marker', 'text': ''},
        'has_text': True,
        'encode': lambda msg, encoding: msg['text'].encode(encoding),
        'decode': lambda data, encoding: {'text': data.decode(encoding)},
    },
    0x2f: {
        'prototype': {'type': 'end_of_track'},
        'encode': lambda msg: b'',
        'decode': lambda data: {},
    },
}


def decode_msg(midi_bytes, encoding):
    if is_meta(midi_bytes):
        _, type_byte, *data = midi_bytes

        if type_byte in meta_specs:
            spec = meta_specs[type_byte]
            decode = spec['decode']

            msg = spec['prototype'].copy()

            if spec.get('has_text'):
                msg.update(decode(bytes(data), encoding))
            else:
                msg.update(decode(bytes(data)))

            return msg
        else:
            return {'type': 'unknown_meta',
                    'type_byte': type_byte, 'data': bytes(data)}
    else:
        return from_bytes(midi_bytes)



def read_midifile(infile):
    mid = read_rawmidifile(infile)

    encoding = 'latin1'

    def decode_track(track):
        return [(delta, decode_msg(msg, encoding)) for (delta, msg) in track]

    mid['tracks'] = [decode_track(track) for track in mid['tracks']]

    return mid


__all__ = ['read_midifile']
