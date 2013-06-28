'''

Created on Jun 25, 2013
@author: egg
'''
import crnparsers
from renderers.visual_renderers import LineGraphRenderer
from renderers.midirenderers import MidiCCRenderer
from datamapper import DataMapper

def crnsong_01():
    parser = crnparsers.HourlyCrnParser()
    stations = parser.find_stations(('Asheville 13', 'Asheville 8'))
    fields = set(('T_CALC', 'SOIL_TEMP_10', 'SOIL_TEMP_50'))
    #fields = set(('T_CALC', 'SOLARAD', 'SOIL_TEMP_10', 'SOIL_TEMP_50'))
    years = [2012]
    doc = parser.parse(stations, years, fields)
    assert len(doc) == len(stations)


    # MIDI output
    mrenderer = MidiCCRenderer()
    mapper = DataMapper(doc, mrenderer)
    sine_to_midi_map = {'T_CALC': 74, 'SOIL_TEMP_10': 76, 'SOIL_TEMP_50' : 77} # sine to cc#
    #sine_to_midi_map = {'T_CALC': 74, 'SOLARAD': 75, 'SOIL_TEMP_10': 76, 'SOIL_TEMP_50' : 77} # sine to cc#
    transformed_doc = mapper.get_transformed_doc(sine_to_midi_map)

    # Create graph
    vrenderer = LineGraphRenderer()
    # No mapping because LineGraphRenderer doesn't need one.
    vrenderer.render(transformed_doc, showplot=True, outfile='/tmp/test.svg')

    # Output MIDI
    mrenderer.render(transformed_doc, output_file='/tmp/t.mid')

crnsong_01()
