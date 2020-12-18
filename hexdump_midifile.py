#!/
"""
Print a hex dump of a MIDI file.

This is useful for debugging.

"""
import sys
from rawmidifile import read_rawmidifile


def hex_encode(msg):
    return ' '.join(f'{byte:02x}' for byte in msg)


mid = read_rawmidifile(sys.argv[1])
print(f'# type={mid["format"]}')
print(f'# ticks_per_beat={mid["resolution"]}')
for trackno, track in enumerate(mid['tracks']):
    print(f'# track {trackno}:')
    for (ticks, msg) in track:
        print(f'{ticks:>6}  {hex_encode(msg)}')
