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

Licensing: full licensing to follow later. In short: free in every way for noncommercial
use. If you're using my code in the context of a commercial enterprise, you need to 
talk to me about a license. This applies only if your business model is a technical one,
for example if you sell software.
If you're a musician and are using using my tools or your own modification of them to
make music, and then selling the music, that doesn't qualify as commercial use. You're
free to do whatever you want with it (although I'd love to hear about it if you're
using these tools to make music!). 
This license may open up more later so that it's free and unencumbered for all use, 
noncommercial and commercial, but I haven't totally decided yet. I'll worry about 
that when there are people using it. If you're considering using it but are 
concerned about licensing, just talk to me and we'll work it out.  

For my dev environment, anyway, nosetest runs better if I actively add
the sonify directory to virtualenv's pythonpath. So edit
./lib/python2.7/site-packages/sonify.pth
and put in the line
/Users/egg/Documents/Programming/sonify-env/sonify
