'''
Created on May 8, 2013

@author: egg
'''
from renderers.datarenderer import DataRenderer
from midiutil.MidiFile import MIDIFile

class MidiRenderer01(DataRenderer):
    def __init__(self, tempo=120):
        super(MidiRenderer01, self).__init__()
        self.tempo = tempo

#     @property
#     def sample_rate(self):
#         return self._sample_rate
#     @sample_rate.setter
#     def sample_rate(self, val):
#         self._sample_rate = val
        
    def render(self, doc, output_file='output.mid'):
        ''' Produces actual output. Generally not called directly but rather by the DataMapper. 
        Assumptions: separate channel for each DataObject'''
        # Note to self - I deleted an apparent bug in MidiFile.py that was causing crashes (part of the midiutil lib)
        # Create the MIDIFile Object with 1 track
        MyMIDI = MIDIFile(1)
         
        # Tracks are numbered from zero. Times are measured in beats.
        track = 0   
        time = 0
         
        
        # Add track name and tempo.
        MyMIDI.addTrackName(track,time,"Sample Track")
        MyMIDI.addTempo(track,time,self.tempo)
         
        
        # Add a note. addNote expects the following information:
        track = 0
        time = 0
        
        for channel, do in enumerate(doc):
            for cc_number, time_series in do.items():
                for time, val in enumerate(time_series): 
                    #MyMIDI.addNote(track,channel,pitch,time,duration,volume)
                    #print 'adding: {} {} {} {} {}'.format(track, channel+1, time*8, cc_number, val)
                    MyMIDI.addControllerEvent(track, channel, time, cc_number, val)
         
        # And write it to disk.
        with open(output_file, 'wb') as binfile:
            MyMIDI.writeFile(binfile)
    
    def expose_parameters(self):
        return {74    : {'range' : (64, 127), 'sample_rate' : 14},
                75    : {'range' : (64, 80), 'sample_rate' : 14},
                76    : {'range' : (00, 127), 'sample_rate' : 14}}
