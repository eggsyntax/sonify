'''

Created on Apr 28, 2013
@author: egg
'''

csound_header = '''
<CsoundSynthesizer>
<CsOptions>
  -d -o /tmp/t.wav -W -m0 ; for csoundSession
</CsOptions> 
'''

csound_footer = '''
</CsoundSynthesizer>
'''

instruments_header = '''
sr = 44100
ksmps = 128
nchnls = 2
0dbfs = 1

'''

instruments_header2 = '''
sr = 44100
ksmps = 10
nchnls = 1
0dbfs = 1

'''

def cs_score(content):
    ''' Trivial function to wrap the score with tags '''
    if type(content) == list: content = '\n'.join(content)
    return '<CsScore>\n%s\n</CsScore>\n' % (content,)

def cs_instruments(content):
    ''' Trivial function to wrap the instruments with tags '''
    if type(content) == list: content = '\n'.join(content)
    return '<CsInstruments>\n%s\n</CsInstruments>\n' % (content,)
