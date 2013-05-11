'''
Created on May 8, 2013

@author: egg
'''
from renderers.datarenderer import DataRenderer
from midiutil.MidiFile import MIDIFile

class MidiRenderer01(DataRenderer):
    def __init__(self):
        super(MidiRenderer01, self).__init__()
        # my init stuff

    @property
    def sample_rate(self):
        return self._sample_rate
    @sample_rate.setter
    def sample_rate(self, val):
        self._sample_rate = val
        
    def render(self, doc, output_file='output.mid'):
        ''' Produces actual output. Generally not called directly but rather by the DataMapper. '''
        # Create the MIDIFile Object with 1 track
        MyMIDI = MIDIFile(1)
         
        # Tracks are numbered from zero. Times are measured in beats.
        track = 0   
        time = 0
         
        
        # Add track name and tempo.
        MyMIDI.addTrackName(track,time,"Sample Track")
        MyMIDI.addTempo(track,time,120)
         
        
        # Add a note. addNote expects the following information:
        track = 0
        channel = 0
        pitch = 60
        time = 0
        duration = 1
        volume = 100
         
        
        # Now add the note.
        for time in range(10):
            #MyMIDI.addNote(track,channel,pitch,time,duration,volume)
            MyMIDI.addControllerEvent(track, channel, time, 0x09, 10*time) # cc 74
         
        
        # And write it to disk.
        binfile = open(output_file, 'wb')
        MyMIDI.writeFile(binfile)
        binfile.close()
    
    def expose_parameters(self):
        # TODO: think about how to make this better and DRYer
        # Could return an immutable DOC?
        # TODO: temp
        return {'amplitude'    : {'range' : (0, 0.25), 'sample_rate' : 14},
                'pressure'     : {'range' : (1, 5), 'sample_rate' : 14},
                'bow_position' : {'range' : (.12, .12), 'sample_rate' : 14}}
