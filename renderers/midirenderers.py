'''

Renderers to create a MIDI file with CC messages (and maybe notes) which represent the data. It's
a bit tricky to work with MIDI data as a composer -- most audio environments don't expect you
to load automation information from a file. A couple of good options:
- Use MIDIPipe (https://www.macupdate.com/app/mac/10541/midipipe) (Mac-only; I'm sure there are
similar programs for other OSes) and feed the data to your DAW in real time (and record it).
- Reaper (http://reaper.fm/) is an inexpensive and featureful DAW. Using it in conjunction with
the free MIDItoReaControlPath plugin (http://forum.cockos.com/showthread.php?t=43741) gives you
a lot of options for connecting MIDI files to parameters. You may also want to use the CC Injector
script, which you can find at http://forum.cockos.com/showthread.php?t=114866.
 
Created on May 8, 2013

@author: egg
'''
from renderers.datarenderer import DataRenderer
from midiutil.MidiFile import MIDIFile
import logging

#TODO: think about creating parameter map from params passed during creation.

class MidiCCRenderer(DataRenderer):
    def __init__(self, sample_rate=7):
        super(MidiCCRenderer, self).__init__()
        self.tempo = 60 # 1 beat per second
        self.sample_rate = sample_rate

#     @property
#     def sample_rate(self):
#         return self._sample_rate
#     @sample_rate.setter
#     def sample_rate(self, val):
#         self._sample_rate = val

    def render(self, doc, output_file='output.mid'):
        ''' Produces actual output.
        Assumptions: separate channel for each DataObject'''
        # Note - I fixed a bug in MidiFile.py that was causing crashes (part of the midiutil lib).
        # Author confirms this is a bug, and will eventually fix and patch, but for now there's a
        # modified version of midiutil bundled with the project.

        # Create the MIDIFile Object with 1 track
        MyMIDI = MIDIFile(1)

        # Tracks are numbered from zero. Times are measured in beats.
        track = 0
        time = 0

        # Add track name and tempo.
        MyMIDI.addTrackName(track, time, "Sample Track")
        MyMIDI.addTempo(track, time, self.tempo)

        for channel, do in enumerate(doc):
            for cc_number, time_series in do.items():
                for i, val in enumerate(time_series):
                    time = float(i) / time_series.sample_rate
                    logging.debug(str(time) + ' ' + str(val))
                    MyMIDI.addControllerEvent(track, channel, time, cc_number, int(val))

        # And write it to disk.
        with open(output_file, 'wb') as binfile:
            MyMIDI.writeFile(binfile)
        return MyMIDI

    def expose_parameters(self):
        return {74    : {'range' : (0, 127), 'sample_rate' : self.sample_rate}, #TODO temporary
                75    : {'range' : (0, 127), 'sample_rate' : self.sample_rate},
                76    : {'range' : (0, 127), 'sample_rate' : self.sample_rate},
                77    : {'range' : (0, 127), 'sample_rate' : self.sample_rate},
                78    : {'range' : (0, 127), 'sample_rate' : self.sample_rate}}
