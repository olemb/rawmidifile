"""
MIDI file reader and writer for Mido built on top of rawmidifile.

There is no official API in Mido for encoding and decoding meta
messages so I've had to use some internal functions.
"""
from rawmidifile import read_rawmidifile, write_rawmidifile


import mido
from mido.midifiles.meta import (build_meta_message,
                                 _META_SPEC_BY_TYPE, UnknownMetaMessage)


def decode_msg(msg, delta=0):
    if msg[0] == 0xff and len(msg) > 1:
        # Meta message.
        return build_meta_message(msg[1], msg[2:], delta)
    else:
        return mido.Message.from_bytes(msg, delta)


def decode_track(track):
    return [decode_msg(msg, delta) for (delta, msg) in track]


def encode_msg(msg):
    if msg.is_meta:
        spec = _META_SPEC_BY_TYPE[msg.type]
        data = spec.encode(msg)
        msg_bytes = bytes([0xff, spec.type_byte]) + bytes(data)
    elif isinstance(msg, UnknownMetaMessage):
        msg_bytes = bytes([0xff, msg.type_byte]) + bytes(data)
    else:
        msg_bytes = bytes(msg.bytes())

    return (msg.time, msg_bytes)


def encode_track(track):
    return [encode_msg(msg).to_dict() for msg in track]


def read_midifile(infile):
    mid = read_rawmidifile(infile)
    mid = mid.copy()
    mid['tracks'] = [decode_track(track) for track in mid['tracks']]

    return mid


def write_midifile(infile, tracks=(), format=1, resolution=240):
    mid = {
        'format': format,
        'resolution': resolution,
        'tracks': [encode_track(track) for track in tracks],
    }
    write_rawmidifile(infile, **mid)
