'''

Created on Jun 2, 2013
@author: egg
'''
import buoyparsers
from criterionfunctions import get_nearness_function, get_num_missing_values_function, \
    create_combined_criterion, record_length, longer_than, reject_prime_meridian_crossers
from buoyparsers import missing_value
from renderers.visual_renderers import LineGraphRenderer, CSVRenderer
from datetime import datetime
from renderers.midirenderers import MidiCCRenderer
from datamapper import DataMapper

def get_quick_buoys():
    datafile = '/Users/egg/Temp/oceancurrents/globaldrifter/buoydata_5001_sep12.dat'
#    datafile = 'test_resources/buoydata.dat'
    parser = buoyparsers.GlobalDrifterParser()
    my_nearness_function = get_nearness_function(-33, 25) #big cluster between cuba and africa
    my_missing_vals_function = get_num_missing_values_function(missing_value)
    combined_criterion_function = create_combined_criterion((my_missing_vals_function,
                                                             reject_prime_meridian_crossers,
                                                             longer_than(2500),
                                                             my_nearness_function))

    # Fast-running sample data
#    doc = parser.parse(datafile,
#                       num_buoys=3,
#                       criterion_function=combined_criterion_function,
#                       maxlines=100000)
    # Real data
    doc = parser.parse(datafile,
                       num_buoys=6,
                       criterion_function=combined_criterion_function,
                       start=datetime(2011, 01, 01), end=datetime(2013, 01, 01))
    doc.combine_all_ranges()
    doc.trim()
    return doc

def graph(doc, keys=None):
    renderer = LineGraphRenderer()
    plot = renderer.render(doc, showplot=True, outfile='/tmp/plot.svg', keys=keys, render_separate=True)

def csound(doc):
    pass
def csv(doc):
    csvrenderer = CSVRenderer()
    result = csvrenderer.render(doc, print_to_screen=False, filename='/tmp/out.txt')

def midi(doc):
    renderer = MidiCCRenderer()
    mapper = DataMapper(doc, renderer)
    sine_to_midi_map = {'LAT': 74, 'LON': 75, 'TEMP': 76} # sine to cc#
    transformed_doc = mapper.get_transformed_doc(sine_to_midi_map)

    renderer.render(transformed_doc, output_file='output.mid')

doc = get_quick_buoys()
graph(doc)
midi(doc)
