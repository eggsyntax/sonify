sr = 44100	; audio sampling rate is 44.1 kHz
kr = 4400	; control rate is 4410 Hz
nchnls = 1	; number of channels of audio output

instr 1				
    kctrl	line	    0, p3, 10000	        ; amplitude envelope
    asig	oscil	    kctrl, cpspch(p5), 1	; audio oscillator
    out	    asig		                        ; send signal to channel 1
endin
