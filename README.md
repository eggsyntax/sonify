sonify
======

Sonification middleware.

Sonify is a unified API for doing sonification (http://en.wikipedia.org/wiki/Sonification).
Sonify provides a consistent workflow and object structure, regardless of the type of data
you're using (at least for timeseries-based data and similar structures) and regardless of
your output method. Output methods will ultimately include CSound, pure-Python audio, MIDI
controller data, and Pylab visualizations. Creating new data parsers and/or new renderers
is straightforward. If you write a parser or renderer for Sonify, I'd love to know about
it.

The flow of data through classes is as follows:
1. Use a subclass of DataParser to generate a DataObjectCollection.
2. Use DataMapper to transform the DataObjectCollection into another DataObjectCollection.
3. Use a subclass of DataRenderer to render to audio.

test\_datamapper gives some examples of usage.


Installs:
link or copy requirements.txt to the virtualenv directory
mostly can just do pip install -r requirements.txt, but
- install numpy first (known bug)
- pip install http://midiutil.googlecode.com/files/MIDIUtil-0.87.tar.gz

