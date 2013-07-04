'''
Climate Reference Network is a network of climate monitoring stations across the US. Download data
from their FTP site and parse it into MIDI output.

Created on Jun 25, 2013
@author: egg
'''
import crnparsers
from renderers.visual_renderers import LineGraphRenderer
from renderers.midirenderers import MidiCCRenderer

def crnsong_01():
    parser = crnparsers.HourlyCrnParser()
    
    # Get six stations that pretty much cover CONUS
    stations = parser.find_stations(('Darrington', 'Barbara', 'Northgate', 'Port Aransas', 'Old Town', 'Brunswick'))
    print stations

    fields = set(('T_CALC', 'SOIL_TEMP_10', 'SOIL_TEMP_50', 'SOLARAD', 'P_CALC'))
    #fields = set(('T_CALC', 'SOLARAD', 'SOIL_TEMP_10', 'SOIL_TEMP_50'))
    years = [2012]
    doc = parser.parse(stations, years, fields)
    assert len(doc) == len(stations)
    doc.combine_all_ranges()

    # MIDI output
    mrenderer = MidiCCRenderer(sample_rate=24) #24 is the natural fit.
    sine_to_midi_map = {'T_CALC': 74, 'SOIL_TEMP_10': 75, 'SOIL_TEMP_50' : 76, 'SOLARAD' : 77, 'P_CALC' : 78} # sine to cc# # 1 is mod wheel, for bowing using the Serenade reaktor patch
    #sine_to_midi_map = {'T_CALC': 74, 'SOLARAD': 75, 'SOIL_TEMP_10': 76, 'SOIL_TEMP_50' : 77}
    transformed_doc = doc.transform(sine_to_midi_map, mrenderer)

    # Create graph
    vrenderer = LineGraphRenderer()
    # No mapping because LineGraphRenderer doesn't need one.
    vrenderer.render(transformed_doc, showplot=True, outfile='/tmp/test.svg')
    
    # Output MIDI
    mrenderer.render(transformed_doc, output_file='t.mid')

crnsong_01()
