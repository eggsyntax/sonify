'''

Created on Apr 27, 2013
@author: egg
'''
from csutils import *
# from csoundSession import CsoundSession # NOTE: can't use csound directly from python
# because it depends on the Apple version of python :( lame lame lame
# http://csound.1045644.n5.nabble.com/CSound-crashing-python-td5714074.html

from datarenderer import DataRenderer

class CsoundSinesSimpleRenderer(DataRenderer):
    def render(self, doc, filename=None):
        content = []
        
        content.append('i 1     0     2')
        #content.append('i 1     0     2     0.8     440')
        
        instruments = instruments_header + '''
        instr 1
            aSin    oscils .25, 440, 0
            out aSin
        endin
        '''
        outstring = csound_header + cs_instruments(instruments) + cs_score(content) + csound_footer
        if filename:
            with open(filename, 'w') as f:
                f.write(outstring)
        print outstring
    
    @property
    def sample_rate(self):
        return self._sample_rate
    @sample_rate.setter
    def sample_rate(self, val):
        self._sample_rate = val
        
    def expose_parameters(self):
        pass #TD