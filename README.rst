rawmidifile
===========

rawmdifile allows you to read and write MIDI files and get at the raw
MIDI bytes.

Note: The API is experimental and may change.


* ``read_rawmidifile()`` takes a filename or a file object and returns
  a dictionary with ``format`` (1 or 2), ``resolution`` (ticks per
  beat) and ``tracks`` (a list of tracks where each track is a list of
  ``(delta, msg)`` tuples.)

* ``write_rawmidifile()`` takes a filename or file object and optional
  ``format``, ``resolution`` and ``tracks``.

* ``is_meta()`` checks if a messages is a meta message. (The first
  byte is 0xff and there is more than one byte.)

Included examples::

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
