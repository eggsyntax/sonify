'''

Created on Apr 27, 2013
@author: egg
'''
from csutils import *
import os, stat

CSOUND_BIN = '/usr/local/bin/csound'

# NOTE: can't use csound directly from python
# because it depends on the Apple version of python :( lame lame lame
# http://csound.1045644.n5.nabble.com/CSound-crashing-python-td5714074.html
# Unless -- can make a virtualenv pointing to /usr/bin/python
# Complaint about OS version mismatch during virtualenv creation? https://gimmebar.com/view/4e7255892f0aaa5a61000005
# This kinda sorta almost works but not quite. Takeaway: csound + python + mac is a nightmare
# and just is not bloody worth it.

from datarenderer import DataRenderer

class CsoundSinesSimpleRenderer(DataRenderer):
    def render(self, doc, filename=None, play=False):
        content = ['''
/*
        
p1 - instrument number
p2 - start time
p3 - duration
---
p4 - amplitude (0-1)
p5 - frequency (Hz)

*/
''']
        if len(doc) > 1:
            raise ValueError('This renderer can only handle a DataObjectCollection' +
                             ' with a single DataObject.')
        do = doc.pop()
        for key, time_series in do.items():
            print 'time series sample rate:',time_series.sample_rate
            duration = 1.0 / time_series.sample_rate
            # Ignore key for the moment #TODO
            # Temporarily make key represent pitch
            pitch = int(key) * 220 + 330
            for t, n in enumerate(time_series):
                start = float(t) / time_series.sample_rate
                content.append('i    1    {}    {}    {}    {}'.format(start, duration, n, pitch))
                
        content.append('i 1     0     2')
        #content.append('i 1     0     2     0.8     440')
        
        instruments = instruments_header + '''
        instr 1
            aSin    oscils p4, p5, 0
            out aSin
        endin
        '''
        outstring = csound_header + cs_instruments(instruments) + cs_score(content) + csound_footer
        if filename:
            with open(filename, 'w') as f:
                f.write(outstring)
                #maybe not necessary:
                #permission = os.stat(filename).st_mode | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
                #os.chmod(filename, permission)
            if play:
                ''' Don't expect this to work for everyone as is '''
                #os.system('`which csound` '+filename) # weird permissions issue
                os.system(CSOUND_BIN+' '+filename) # hardly universal
            
        #print outstring
    
    def expose_parameters(self):
        # ]
        # Could return an immutable DOC?
        return {'0' : {'range' : (0,1), 'sample_rate' : 9},
                '1' : {'range' : (0,1), 'sample_rate' : 7},
                '2' : {'range' : (0,1), 'sample_rate' : 5}}
        
class CsoundBowedSimpleRenderer(DataRenderer):
    orchestra_data = '''
                ; Table #1, a sine wave.
                f 1 0 128 10 1
                ''    def render(self, doc, filename=None, play=False):
                '''
    
    def render(self, doc, filename=None, play=False):
        print 'Rendering.'
        content = ['''
/*
        
p1 - instrument number
p2 - start time
p3 - duration
---
p4 - amplitude (0-1)
p5 - frequency (Hz)

*/

; Table #1, a sine wave.
f 1 0 128 10 1

''']
        pitch = 220
        for i, do in enumerate(doc):
            pitch += 55
            amplitude = do['amplitude']
            pressure = do['pressure']
            bow_position = do['bow_position']
            # for this renderer, all three of the above are assumed to have the same length and
            # sample rate; we'll arbitrarily use amplitude in the following lines.
            for t in range(len(amplitude)):
                # YOUAREHERE swap loops (do.items vs time). for each t, grab vals for amplitude, pressure, bow_position
                duration = (i + 2.71) / amplitude.sample_rate
                # Ignore key for the moment #TODO
                
                start = float(t*3) / amplitude.sample_rate
#                 import pdb;pdb.set_trace()
                content.append('i    1    {}    {}    {}    {}    {}    {}'.format(start, duration, amplitude[t], 
                                                                           pitch, pressure[t], bow_position[t]))

        instruments = instruments_header + '''
        ; Instrument #1.
        instr 1
          kamp = 31129.60
          kfreq = 440
          kpres = 3.0
          krat = 0.127236
          kvibf = 6.12723
          ifn = 1
        
          ; Create an amplitude envelope for the vibrato.
          kv linseg 0, 0.5, 0, 1, 1, p3-0.5, 1
          kvamp = kv * 0.01
          ; kamp, kfreq, kpres, krat, kvibf, kvamp, ifn
          a1 wgbow p4, p5, p6, p7, kvibf, kvamp, ifn
          ; a1 wgbow p4, p5, p6, p7, kvibf, kvamp, ifn
          out a1, a1
        endin
        '''
        outstring = csound_header + cs_instruments(instruments) + cs_score(content) + csound_footer
        if filename:
            with open(filename, 'w') as f:
                f.write(outstring)
                #maybe not necessary:
                #permission = os.stat(filename).st_mode | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
                #os.chmod(filename, permission)
            if play:
                ''' Don't expect this to work for everyone as is '''
                #os.system('`which csound` '+filename) # weird permissions issue
                os.system(CSOUND_BIN+' '+filename) # hardly universal
            
        print 'Here\'s the csound file:'
        print outstring
    
    def expose_parameters(self):
        # TODO: think about how to make this better and DRYer
        # Could return an immutable DOC?
        # ranges taken from http://www.csounds.com/manualOLPC/wgbow.html
        return {'amplitude'    : {'range' : (0,1), 'sample_rate' : 14},
                'pressure'     : {'range' : (1,5), 'sample_rate' : 14},
                'bow_position' : {'range' : (.12, .12), 'sample_rate' : 14}}
        
