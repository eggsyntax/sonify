;===========
; Simple bowed string
; Input: 
;===========

sr = 44100
ksmps = 128
nchnls = 2
0dbfs = 1

        ; Instrument #1.
        instr 1
          kamp = 31129.60
          kfreq = 440
          kpres = 3.0
          krat = 0.127236
          kvibf = 6.12723
          ifn = 1
          
          ; Table #1, a sine wave.
          ; Note ftgen format for function table inside orchestra
          gisine ftgen 1, 0, 1024, 10, 1 
          
          ; Create an amplitude envelope for the vibrato.
          kv linseg 0, 0.5, 0, 1, 1, p3-0.5, 1
          kvamp = kv * 0.01
          ; kamp, kfreq, kpres, krat, kvibf, kvamp, ifn
          a1 wgbow p4, p5, p6, p7, kvibf, kvamp, ifn
          ; a1 wgbow p4, p5, p6, p7, kvibf, kvamp, ifn
          out a1, a1
        endin



