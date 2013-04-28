import pprint
import pdb  # @UnusedImport
from datamapper import TimeSeries, DataObject, DataObjectCollection, DataMapper, DataParser, Mapping
from renderers.datarenderer import DataRenderer
from renderers.csound01_simple import CsoundSinesSimpleRenderer
pp = pprint.PrettyPrinter().pprint

import pylab

from nose.tools import assert_raises  # @UnresolvedImport (Eclipse)
from math import sin

def test_datamapper_1():
    # create a TimeSeries
    ts1 = TimeSeries(['datapoint'], sample_rate=60)

    # create a DO and put the TS in it
    do1 = DataObject()
    do1['somedata'] =ts1
    assert do1.keys() == ['somedata']

    # create a DOC and put the DO in it
    doc = DataObjectCollection()
    doc.add(do1)

    # dig down through the levels and get the datapoint we originally inserted
    timeseries = doc.pop()['somedata']
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

def test_doc_imposes_sample_rate():
    # create a DO
    do1 = DataObject()

    # create a DOC and put the DO in it
    doc = DataObjectCollection(sample_rate=60)
    doc.add(do1)

    retrieved_do = doc.pop()
    assert(retrieved_do.sample_rate == 60)

def test_rangex():
    ts = TimeSeries([2,3,1,5,4], rangex=(0,5))
    assert(ts.rangex == (0,5))

    ts = TimeSeries([2,3,1,5,4])
    assert(ts.rangex == (1,5))

def test_DOC_rejects_bad_starter_coll():
    assert_raises(TypeError, DataObjectCollection,1) # 1 is totally not a collection

def test_mapping_validation():
    dicts = [{'sourcekey':'blah'}]
    assert_raises(AssertionError, Mapping, dicts) # must have targetkey as well
    dicts = [{'sourcekey':'blah', 'targetkey':1}]
    assert_raises(AssertionError, Mapping, dicts) # key must refer to string
    
def test_remap_time_index():
    ''' given a starting sample rate of 1.0/60 and a desired sample rate of 1.0/5,
    produce a set of (non-integer) indices to pull from to create our representation.
    '''
    dm = DataMapper(None,ToyDataRenderer()) # Just testing static methods
    remap = dm.remap_time_index
    out_sr = 1/5.0
    in_sr = 1/20.0
    converted = [remap(i,out_sr,in_sr) for i in range(10)]
    assert(converted==[0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25])

def test_remap_range():
    dm = DataMapper(None, ToyDataRenderer())
    inlist = [0, .5, 1]
    original_range = (0,1)
    desired_range = (0,10)
    outlist = dm.remap_range(inlist, original_range, desired_range)
    assert(outlist == [0, 5, 10])

    inlist = [1.0, 1.5, 2]
    original_range = (1,2)
    desired_range = (100,110)
    outlist = dm.remap_range(inlist, original_range, desired_range)
    assert(outlist == [100, 105, 110])

class ToyDataParser(DataParser):
    def parse(self, listofdicts):
        doc = DataObjectCollection()
        for curdict in listofdicts:
            do = DataObject()
            for key, val in curdict.items():
                do[key] = val
            doc.add(do)
        return doc

class ToyDataRenderer(DataRenderer):
    @property
    def sample_rate(self):
        return self._sample_rate
    @sample_rate.setter
    def sample_rate(self,rate):
        self._sample_rate = rate

    def expose_parameters(self):
        return None
    
    def render(self, doc):
        return "rendered"
        #TODO how exactly and in what form is data fed from Mapper to Renderer?

#TODO YOUAREHERE implement actual end-to-end with ToyDataParser, ToyDataRenderer
def test_end_to_end_toy():
    parser = ToyDataParser()
    data = [{'a':TimeSeries([1,2,3]), 'b':TimeSeries([2,3,4])},
            {'c':TimeSeries([3,4,5]), 'd':TimeSeries([4,5,6])}]
    doc = parser.parse(data)
    doc.sample_rate = 3

    renderer = ToyDataRenderer()
    renderer.sample_rate = 3
    #renderer.range?

    mapper = DataMapper(doc, renderer)
    mapper.set_mapping('fakemapping')
    transformed_doc = mapper.get_transformed_doc()
    results = mapper.render(transformed_doc)
    assert(results == "rendered")

class SineDictParser(DataParser):
    ''' Expects a single dict from numbers 0..n to sine timeseries(-1..1) '''
    def parse(self, sines):
        doc = DataObjectCollection()
        do = DataObject()
        for key, sine in sines.items():
           ts = TimeSeries(sine)
           do[key] = ts
        doc.add(do)
        return doc

class SineDictRenderer(DataRenderer):
    @property
    def sample_rate(self):
        return self._sample_rate
    @sample_rate.setter
    def sample_rate(self,rate):
        self._sample_rate = rate

    def render(self, doc, showplot=False):
        for i in range(len(doc)):
            do = doc.pop()
            for key, ts in do.items():
                x = range(len(ts))
                plot = pylab.plot(x,ts.data)
        if showplot: pylab.show()
        return plot

    def expose_parameters(self):
        return None
    
def generate_sines(num, length):
    out = {}
    for i in range(num):
        out[i] = []
        factor = (i+1)*3
        for j in range(length):
            out[i].append(sin(j*factor))
    return out

def test_end_to_end_sines():
    parser = SineDictParser()
    sines = generate_sines(3, 4)
    doc = parser.parse(sines)
    renderer = SineDictRenderer()
    plot = renderer.render(doc, showplot=False)
    assert('matplotlib.lines.Line2D' in str(plot))

def test_csound_with_mapping():
    parser = SineDictParser()
    sines = generate_sines(3, 20)
    doc = parser.parse(sines)
    
    mapper = DataMapper(doc, SineDictRenderer())
    mapper.set_mapping('fakemapping')
    transformed_doc = mapper.get_transformed_doc()
    renderer = CsoundSinesSimpleRenderer()
    renderer.render(transformed_doc, filename='t.csd')
    #TODO assert

