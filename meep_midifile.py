"""
Example of writing a basic MIDI file reader for Meep:
https://github.com/olemb/meep/

This doesn't supports only TrackName and EndOfTrack.

"""
from rawmidifile import read_rawmidifile, is_meta
from dataclasses import dataclass
import meep

@dataclass(frozen=True, eq=True)
class TrackName:
    type_byte=0x03
    name: str = ''


@dataclass(frozen=True, eq=True)
class EndOfTrack:
    type_byte=0x2f


@dataclass(frozen=True, eq=True)
class UnknownMeta: 
    type_byte: int = 0
    data: bytes = b''


def read_midifile(infile):
    mid = read_rawmidifile(infile)

    def decode_msg(msg):
        if is_meta(msg):
            type_byte = msg[1]
            data = msg[2:]
            if type_byte == 0x03:
                return TrackName(data.decode('latin1'))
            elif type_byte == 0x2f:
                return EndOfTrack()
            else:
                return UnknownMeta(type_byte, data)
        else:
            return meep.from_bytes(msg)

    def decode_track(track):
        return [(delta, decode_msg(msg)) for (delta, msg) in track]

    mid['tracks'] = [decode_track(track) for track in mid['tracks']]

    return mid


__all__ = ['read_midifile']
