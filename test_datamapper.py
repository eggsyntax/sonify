from datamapper import *
from nose.tools import assert_raises

class ToyDataRenderer(DataRenderer):
    @property
    def sample_rate(self):
        return None

    def render(self):
        pass

def test_datamapper_1():
    # create a TimeSeries
    ts1 = TimeSeries(['datapoint'], sample_rate=60)

    # create a DO and put the TS in it
    do1 = DataObject()
    do1['somed'] =ts1
    assert do1.keys() == ['somed']

    # create a DOC and put the DO in it
    doc = DataObjectCollection()
    doc.add(do1)

    # dig down through the levels and get the datapoint we originally inserted
    timeseries = doc.pop()['somed']
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

def test_remap_time_index():
    ''' given a starting sample rate of 1.0/60 and a desired sample rate of 1.0/5,
    produce a set of (non-integer) indices to pull from to create our representation.
    '''
    dm = DataMapper(None,ToyDataRenderer()) # Just testing static methods
    remap = dm.remap_time_index
    out_sr = 1/5.0
    in_sr = 1/20.0
    converted = [remap(i,out_sr,in_sr) for i in range(10)]
    print converted
    assert(converted==[0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25])

def test_remap_range():
    dm = DataMapper(None, ToyDataRenderer())
    inlist = [0, .5, 1]
    original_range = (0,1)
    desired_range = (0,10)
    outlist = dm.remap_range(inlist, original_range, desired_range)
    print 'outlist',outlist
    assert(outlist == [0, 5, 10])
            
    inlist = [1.0, 1.5, 2]
    original_range = (1,2)
    desired_range = (100,110)
    outlist = dm.remap_range(inlist, original_range, desired_range)
    print 'outlist',outlist
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

#TODO YOUAREHERE implement actual end-to-end with ToyDataParser, ToyDataRenderer
