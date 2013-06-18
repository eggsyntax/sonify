import pprint
import pdb # @UnusedImport
from datamapper import TimeSeries, DataObject, DataObjectCollection, DataMapper
from renderers.datarenderer import DataRenderer
from renderers.csound01_simple import CsoundSinesSimpleRenderer, CsoundBowedSimpleRenderer, \
    CsoundRenderer
from renderers.midirenderers import MidiCCRenderer
import buoyparsers
from datetime import datetime
from nose.plugins.skip import SkipTest
from buoyparsers import interpolate_forward_backward, missing_value
from renderers.visual_renderers import CSVRenderer, LineGraphRenderer
from criterionfunctions import get_num_missing_values_function, get_nearness_function, \
    create_combined_criterion, record_length
from dataparser import DataParser

pp = pprint.PrettyPrinter().pprint

from nose.tools import assert_raises # @UnresolvedImport (Eclipse)
from math import sin

def test_datamapper_1():
    # create a TimeSeries and stick something in it
    ts1 = TimeSeries(['datapoint'], sample_rate=60)

    # create a DO and put the TS in it
    do1 = DataObject()
    do1['somedata'] = ts1
    assert do1.keys() == ['somedata']

    # create a DOC and put the DO in it
    doc = DataObjectCollection()
    doc.append(do1)

    # dig down through the levels and get the datapoint we originally inserted
    timeseries = doc[0]['somedata']
    datapoint = timeseries[0]
    assert(datapoint == 'datapoint')

def test_do_imposes_sample_rate():
    # create a TimeSeries
    ts1 = TimeSeries(['datapoint'])

    # create a DO and put the TS in it
    do1 = DataObject(sample_rate=60)
    do1['somed'] = ts1

    # test the sample_rate of the TimeSeries (which it should derive from the DO)
    assert(do1['somed'].sample_rate == 60)

    # while we're at it, make sure that it percolates up to the DOC
    doc = DataObjectCollection([do1])
    assert doc.sample_rate == 60, str(doc.sample_rate) + ' is not 60.'

def test_doc_imposes_sample_rate():
    # create a DO
    do1 = DataObject()

    # create a DOC and put the DO in it
    doc = DataObjectCollection(sample_rate=60)
    doc.append(do1)

    retrieved_do = doc[0]
    assert(retrieved_do.sample_rate == 60)

def test_ts_range():
    ts = TimeSeries([2, 3, 1, 5, 4], ts_range=(0, 5))
    assert(ts.ts_range == (0, 5))

    ts = TimeSeries([2, 3, 1, 5, 4])
    assert(ts.ts_range == (1, 5))

def test_DOC_rejects_bad_starter_coll():
    assert_raises(TypeError, DataObjectCollection, 1) # 1 is totally not a collection

def test_resample():
    ts = TimeSeries([0, 1, 2, 3, 4, 5, 6])
    ts.resample(.4)
    assert str(ts) == 'TimeSeries([0.0, 0.4, 0.8, 1.2000000000000002, 1.6, 2.0, 2.4000000000000004, 2.8000000000000003, 3.2, 3.6, 4.0, 4.4, 4.800000000000001, 5.2, 5.6000000000000005], sample_rate=None, ts_range=(0.0, 5.6000000000000005))'
    ts.resample(1 / .4) # Reversible? Should be except that we lose some off the end (we have to)
    assert str(ts) == 'TimeSeries([0.0, 1.0, 2.0, 3.0, 4.0, 5.0], sample_rate=None, ts_range=(0.0, 5.0))'

def test_remap_range():
    dm = DataMapper(None, ToyDataRenderer())
    inlist = TimeSeries([0, .5, 1])
    original_range = (0, 1)
    desired_range = (0, 10)
    outlist = dm.remap_range(inlist, original_range, desired_range)
    assert outlist == TimeSeries([0.0, 5.0, 10.0]), 'outlist is ' + str(outlist) + ': ' + str(type(outlist))

    inlist = TimeSeries([1.0, 1.5, 2])
    original_range = (1, 2)
    desired_range = (100, 110)
    outlist = dm.remap_range(inlist, original_range, desired_range)
    assert outlist == TimeSeries([100.0, 105.0, 110.0]), 'outlist is ' + str(outlist)

    # same thing without explicitly setting the original range
    inlist = TimeSeries([1.0, 1.5, 2])
    desired_range = (100, 110)
    outlist = dm.remap_range(inlist, original_range, desired_range)
    assert outlist == TimeSeries([100.0, 105.0, 110.0]), 'outlist is ' + str(outlist)

def test_interpolate_forward_backward():
    l = [999.999, 999.999, 3, 4, 5, 999.999, 7, 999.999, 999.999]
    new_l = interpolate_forward_backward(l)
    assert new_l == [3, 3, 3, 4, 5, 5, 7, 7, 7], new_l

class ToyDataParser(DataParser):
    def parse(self, listofdicts):
        doc = DataObjectCollection()
        for curdict in listofdicts:
            do = DataObject()
            for key, val in curdict.items():
                do[key] = val
            doc.append(do)
        return doc

class ToyDataRenderer(DataRenderer):
    @property
    def sample_rate(self):
        return self._sample_rate
    @sample_rate.setter
    def sample_rate(self, rate):
        self._sample_rate = rate

    def expose_parameters(self):
        return None

    def render(self, doc):
        return "rendered"


class SineDictParser(DataParser):
    ''' Expects a single dict from numbers 0..n to sine timeseries(-1..1) '''
    def parse(self, sines):
        doc = DataObjectCollection()
        do = DataObject()
        for key, sine in sines.items():
           ts = TimeSeries(sine)
           ts.sample_rate = 1
#            ts.ts_range = (-1,1)
           do[key] = ts
        doc.append(do)
        return doc

class MultiSineDictParser(DataParser):
    ''' Expects a list of dicts from numbers 0..n to sine timeseries(-1..1) '''
    def parse(self, sineslist):
        doc = DataObjectCollection()
        for sines in sineslist:
            do = DataObject()
            for key, sine in sines.items():
               ts = TimeSeries(sine)
               ts.sample_rate = 1
               do[key] = ts
            doc.append(do)
        return doc

def generate_sines(num, length, factor=None):
    ''' Returns a dict from key to list of values (which can become a TimeSeries) '''
    out = {}
    for i in range(num):
        out[i] = []
        if factor:
            factor = ((factor + 1) * 3 + i)
        else:
            factor = (i + 1) * 3
        for j in range(length):
            out[i].append(sin((j + factor) / 10.3))
    return out


def test_end_to_end_sines():
    parser = SineDictParser()
    sines = generate_sines(3, 40)
    doc = parser.parse(sines)
    renderer = LineGraphRenderer()
    plot = renderer.render(doc, showplot=False)
    assert plot.__sizeof__() == 16 # not many assert options on these objects

def test_csound_with_mapping():
    parser = SineDictParser()
    sines = generate_sines(3, 40)
    doc = parser.parse(sines)
    doc.sample_rate = 5
    renderer = CsoundSinesSimpleRenderer()
    mapper = DataMapper(doc, renderer)
    sine_to_csound_map = {0: '0', 1: '1', 2: '2'} # Degenerate case for testing
    transformed_doc = mapper.get_transformed_doc(sine_to_csound_map)
    result = renderer.render(transformed_doc, filename='/tmp/t.csd', play=False)
    known_result = 'i    1    7.8    0.2    0.989624574626    770'
    assert known_result in result

def test_combine_range():
    ''' Make some sines, modify them to have different ranges, and combine the ranges. '''
    parser = MultiSineDictParser()
    sinelist = []
    for i in range(3):
        sines = generate_sines(3, 3)
        sinelist.append(sines)
    doc = parser.parse(sinelist)
    for i, do in enumerate(doc):
        do[0] = TimeSeries([(i + 1) * v for v in do[0]])
    old_ranges = [do[0].ts_range for do in doc]
    assert old_ranges[0] == (0.2871614310423001, 0.4665948234153722), old_ranges[0]
    assert len(set(old_ranges)) == 3 # All identical
    doc.combine_range(0)
    new_ranges = [do[0].ts_range for do in doc]
    assert new_ranges[0] == (0.2871614310423001, 1.3997844702461166), new_ranges[0]
    assert len(set(new_ranges)) == 1 # All identical

@SkipTest
#Skip this test since the interactivity is a pain during testing
def test_csound_with_interactive_mapping():
    parser = SineDictParser()
    sines = generate_sines(3, 8)
    doc = parser.parse(sines)
#    pp(doc)
    doc.sample_rate = 5
    renderer = CsoundSinesSimpleRenderer()
    mapper = DataMapper(doc, renderer)
    interactive_map = mapper.interactive_map(doc, renderer)
    transformed_doc = mapper.get_transformed_doc(interactive_map)
#    pp(transformed_doc)
    renderer.render(transformed_doc, filename='/tmp/t.csd', play=False)

def test_csound_with_bowed_string():
    parser = MultiSineDictParser()

    # Generate some raw data
    sinelist = []
    for i in range(3):
        sines = generate_sines(3, 128, factor=i)
        sinelist.append(sines)

    doc = parser.parse(sinelist)
    doc.sample_rate = 5
    renderer = CsoundBowedSimpleRenderer()
    mapper = DataMapper(doc, renderer)
    sine_to_csound_map = {0: 'amplitude', 1: 'pressure', 2: 'bow_position'}
    transformed_doc = mapper.get_transformed_doc(sine_to_csound_map)
    # pp(transformed_doc)
    result = renderer.render(transformed_doc, filename='/tmp/t.csd', play=False)
    known_result = 'i    1    27.2142857143    0.336428571429    0.199397199181    385    3.71966793095    0.12'
    assert known_result in result

def test_csound_from_orchestra_file():
    parser = MultiSineDictParser()

    # Generate some raw data
    sinelist = []
    for i in range(3):
        sines = generate_sines(3, 128, factor=i)
        sinelist.append(sines)

    doc = parser.parse(sinelist)
    doc.sample_rate = 5

    orchestra_file = '/Users/egg/Documents/Programming/sonify-env/sonify/csound_files/bowed_string.orc'
    renderer = CsoundRenderer(orchestra_file)
    mapper = DataMapper(doc, renderer)
    sine_to_csound_map = {0: 'amplitude', 1: 'pressure', 2: 'bow_position'}
    transformed_doc = mapper.get_transformed_doc(sine_to_csound_map)
    # pp(transformed_doc)
    result = renderer.render(transformed_doc, filename='/tmp/t.csd', play=False)
    known_result = 'p5 - frequency (Hz)\n            \n            */\n            \n            ; function table moved to orchestra\n            \n            \ni    1    0.0    0.193571428571    0.160885686814    146.7    4.90556786078    0.102379805523\ni    1    0.214285714286'
    assert known_result in result

def test_midi_renderer_01():
    parser = MultiSineDictParser()

    # Generate some raw data
    sinelist = []
    for i in range(3):
        sines = generate_sines(3, 120, factor=i)
        sinelist.append(sines)

    doc = parser.parse(sinelist)
    doc.sample_rate = 5

    renderer = MidiCCRenderer()
    mapper = DataMapper(doc, renderer)
    sine_to_midi_map = {0: 74, 1: 75, 2: 76} # sine to cc#
    transformed_doc = mapper.get_transformed_doc(sine_to_midi_map)
    renderer.render(transformed_doc, output_file='/tmp/t.mid')
    # No reasonable asserts for these MIDI outputs

def test_buoy_parser_01():
    parser = buoyparsers.GlobalDrifterParser()
    doc = parser.parse('test_resources/buoydata.dat')
    doc.intify()
#     doc = parser.parse('/Users/egg/Temp/oceancurrents/globaldrifter/buoydata_5001_sep12.dat')
    renderer = LineGraphRenderer()
    # No mapping because LineGraphRenderer doesn't need one.
    plot = renderer.render(doc, showplot=False, outfile='/tmp/test.svg')
    assert plot.__sizeof__() == 16

def test_buoy_parser_02():
    parser = buoyparsers.GlobalDrifterParser()
    doc = parser.parse('test_resources/buoydata.dat')
#     doc = parser.parse('/Users/egg/Temp/oceancurrents/globaldrifter/buoydata_5001_sep12.dat')
    doc.combine_range('TEMP')
    orchestra_file = '/Users/egg/Documents/Programming/sonify-env/sonify/csound_files/bowed_string.orc'
    renderer = CsoundRenderer(orchestra_file)
    mapper = DataMapper(doc, renderer)
    sine_to_csound_map = {'LAT': 'amplitude', 'LON': 'pressure', 'TEMP': 'bow_position'}
    transformed_doc = mapper.get_transformed_doc(sine_to_csound_map)
    result = renderer.render(transformed_doc, filename='/tmp/t.csd', play=True)
    known_result = '\ni    1    8.35714285714    0.336428571429    0.0    220.1    1.08011444921    0.14756946158\n</CsScore>\n\n</CsoundSynthesizer>\n'
    #assert known_result in result #TODO


def test_buoy_parser_04():
#    datafile = '/Users/egg/Temp/oceancurrents/globaldrifter/buoydata_5001_sep12.dat'
    datafile = 'test_resources/buoydata.dat'
    parser = buoyparsers.GlobalDrifterParser()
    my_nearness_function = get_nearness_function(-33, 25) #big cluster between cuba and africa
    combined_criterion_function = create_combined_criterion((record_length, my_nearness_function))
    doc = parser.parse(datafile,
                       num_buoys=4,
                       criterion_function=combined_criterion_function,
                       start=datetime(2012, 06, 01), end=datetime(2012, 10, 01), maxlines=None)
    renderer = CSVRenderer()
    result = renderer.render(doc, print_to_screen=False, filename='/tmp/out.txt')
    known_result = '26.592,324.555,27.123,41.963,5.79,7.73,26.158,324.069,27.386'
    assert known_result in result

