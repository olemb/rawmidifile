rawmidifile
===========

rawmdifile allows you to read and write MIDI files and get at the raw
MIDI bytes.

Note: The API is experimental and may change.

.. code-block:: python

    >>> import pprint
    >>> from rawmidifile import read_rawmidifile
    >>> pprint.pprint(read_rawmidifile('example.mid'))
    {'format': 1,
     'resolution': 480,
     'tracks': [[(0, b'\xff\x03Melody'),
                 (0, b'\xc0\x0c'),
                 (16, b'\x90@d'),
                 (16, b'\x80@d'),
                 (16, b'\x90Gd'),
                 (16, b'\x80Gd'),
                 (16, b'\x90@d'),
                 (16, b'\x80@d'),
                 (16, b'\x90@d'),
                 (16, b'\x80@d'),
                 (0, b'\xff/')]]}

* ``read_rawmidifile()`` takes a filename or a file object and returns
  a dictionary with ``format`` (1 or 2), ``resolution`` (ticks per
  beat) and ``tracks`` (a list of tracks where each track is a list of
  ``(delta, msg)`` tuples.)

* ``write_rawmidifile()`` takes a filename or file object and optional
  ``format``, ``resolution`` and ``tracks``.

* ``is_meta()`` checks if a messages is a meta message. (The first
  byte is 0xff and there is more than one byte.)

Included examples:

* ``mido_midifile.py`` - an alternative MIDI file reader/writer for
   Mido built on top of ``rawmidifile``. https://github.com/mido/mido/

* ``meep_midifile.py`` - the beginnings of a MIDI file reader/writer
  for Meep. https://github.com/olemb/meep/


Acknowledgements
----------------

The code is based on the MIDI file module in Mido.


Author
------

Ole Martin Bjørndalen
