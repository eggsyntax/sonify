import abc
import pprint
from mimify import repl

pp = pprint.PrettyPrinter().pprint

# from renderers.datarenderer import DataRenderer

''' datamapper contains the three parts of the Data Mapper functionality:
    1) DataObjectCollection, DataObject, and TimeSeries represent the data to be used
        as the basis for the representation.
    2) DataRenderer is able to render a DataObjectCollection into a musical (or other)
        representation using a DataMapper
    3) DataMapper defines the mapping from DataObjectCollection to DataRenderer. It
        maps a key in the data ('temperature') to an attribute of the musical
        representation ('pitch'), with an understanding of the relative domains and
        ranges of each.
    #TODO - do we need one extra step of abstraction between DataMapper and DataRenderer?
    #   Something like OutputModel, which understands the available output attributes
    #   and their respective domains and ranges?

'''

class DataObjectCollection:
    ''' DataObjectCollection is a set-like class which contains DataObject objects
    (where a DataObject represents, say, a single buoy, ie a collection of TimeSeries).
    '''
    def __init__(self, starter_coll=None, sample_rate=None):
        self.data_objects = set()
        self.sample_rate = sample_rate
        if starter_coll:
            try:
                self.data_objects = set(starter_coll)
            except TypeError, e:
                error_msg = 'The starter collection for a DataObjectCollection must be something' \
                    ' that can reasonably be converted to a set;', type(starter_coll), 'does' \
                    ' not qualify. (',starter_coll,')' #TODO not print, but add to error
                raise e, error_msg

    def add(self,dob):
        assert(isinstance(dob,DataObject))
        self.data_objects.add(dob)
    def pop(self):
        data_object = self.data_objects.pop()
        if self.sample_rate and not data_object.sample_rate:
            data_object.sample_rate = self.sample_rate
        return data_object

    def __iter__(self):
        return self.data_objects.__iter__()

    def __len__(self):
        return self.data_objects.__len__()

    def __repr__(self):
        return self.data_objects.__repr__()

class DataObject: # make dictlike
    ''' DataObject is a dict-like collection of TimeSeries. It generally represents a single
    datasource (a buoy, a satellite, a ground station) which produces multiple measurements. '''
    def __init__(self, sample_rate=None):
         self.seriesdict = {}
         self.sample_rate = sample_rate
    def __setitem__(self, key, ts):
         assert(isinstance(ts, TimeSeries))
         self.seriesdict[key] = ts
    def __getitem__(self, key):
         series = self.seriesdict[key]
         if self.sample_rate and not series.sample_rate:
            series.sample_rate = self.sample_rate
         return series
    def items(self):
        # do this in a slightly complicated way to ensure sample rate is set (by calling __getitem__)
        its = []
        for key in self.keys():
            its.append((key, self.__getitem__(key)))
        return its
    def values(self):
        return self.seriesdict.values()
    def keys(self):
        return self.seriesdict.keys()
    def __repr__(self):
        return self.seriesdict.__repr__()
    def __len__(self):
        return self.seriesdict.__len__()

class TimeSeries:
    ''' TimeSeries is a list-like class which also contains metadata about the list, namely
    sample_rate (how many items represent one second) and rangex (the range of values or
    possible values contained in the list. This can be set to indicate the expected range
    (say, (-1,1)), but if TimeSeries is asked for its rangex and it hasn't been set, it's
    computed from the actual values).
    '''
    #TODO: missing_value value?
    def __init__(self, data, sample_rate=None, rangex=None):
        #domain?
        #if I want duration, it's float(len(data)) / self.sample_rate.
        # But test that.  #assert(data is listlike)? hard to test. can do
        # hasattr(data,'__iter__'), but a dict satisfies that too.
        self.data = data
        self.sample_rate = sample_rate
        self._rangex = rangex

    def copy(self):
        return TimeSeries(list(self.data), self.sample_rate, self.rangex)
    
    @property
    def rangex(self):
        if self._rangex: return self._rangex
        # We don't have a rangex. Compute from actual values
        sorted_vals = sorted(self.data)
        return (sorted_vals[0],sorted_vals[-1])
    @rangex.setter
    def rangex(self, r):
        self._rangex = r
    @rangex.deleter
    def rangex(self):
        self._rangex = None

    def __getitem__(self, index):
        return self.data[index]
    # add get_by_t(self, t) -- interpolated version. maybe.

    def __len__(self):
        return self.data.__len__()
    def __repr__(self):
        return self.data.__repr__()

class DataMapper:
    ''' DataMapper transforms a DataObjectCollection into another
    DataObjectCollection. It will remap time and/or range as desired. '''
    def __init__(self, data_object_collection, data_renderer, mapping=None):
        self.data_object_collection = data_object_collection
        self.data_renderer = data_renderer
        self.render = data_renderer.render
        self.mapping = mapping

    def remap_time_index(self, out_index, out_sr, in_sr):
        ''' Given a desired index in the output, find the
        (non-integer) index in the input which refers to the
        same moment, given the output's sample rate and
        the input's sample rate. Note: the output's
        sample rate is just a representation of time relative to
        the original, not anything about a final representation
        of time (eg a 44100 sample rate for audio). Typically
        we iterate over the indices of the list we're creating
        and get a list of indices to pull from the original. We
        then have to actually pull the values, possibly using
        interpolation and/or averaging. '''
        #TODO handle as TimeSeries? Using TimeSeries.copy()? See remap_range
        return (in_sr / out_sr) * out_index

    def _diff(self, duple):
        return duple[1] - duple[0]

    def remap_range(self, time_series, original_range, desired_range):
        remapped_series = time_series.copy()
        scaling_factor = float(self._diff(desired_range)) \
                / self._diff(original_range)
        remapped_data = []
        original_floor = original_range[0]
        desired_floor = desired_range[0]
        for v in remapped_series.data:
            newv = ((v - original_floor) * scaling_factor) + desired_floor
            remapped_data.append(newv)
        remapped_series.data = remapped_data
        return remapped_series

    def interactive_map(self, doc, renderer):
        print 'Let\'s build an interactive map!'
        print 'Available keys:'
        mapping = {}
        target_params = renderer.expose_parameters()
        pp(target_params)
        unused_targets = set(target_params.keys())
        sample_data_object = doc.data_objects.copy().pop()
        for source_key in sample_data_object.keys():
            print
            print 'Available targets: {}'.format(list(unused_targets))
            question = 'What do you want to map {} to? '.format((source_key))
            answer = raw_input(question).strip()
            if answer not in unused_targets:
                raise KeyError('{} is not an available parameter'.format(answer))
            unused_targets.remove(answer)
            mapping[source_key] = answer
        pp(mapping)
        return mapping
        
    def get_transformed_doc(self, mapping):
        ''' Pass in a mapping (a dict) from keys in the source data to keys in the 
        rendered data, eg {'altitude': 'pitch', 'temperature': 'amplitude'}. The method
        will use this mapping to create a new DataObjectCollection containing the
        data in the format the renderer desires, with sample rate and range transformed
        as necessary. ''' 
        target_parameters = self.data_renderer.expose_parameters()
    
        transformed_doc = DataObjectCollection()
        for do in self.data_object_collection:
            transformed_do = DataObject()
            for key in do.keys():
                target_key = mapping[key]
                series = do[key]
                
                target_params = target_parameters[target_key]
                target_rangex = target_params['range'] if 'range' in target_params else None
                target_sample_rate = target_params['sample_rate'] if 'sample_rate' in target_params else None
                
                #TODO use the target_range & target_sample_rate to transform the time series
                series = self.remap_range(series, series.rangex, target_rangex)
                series.sample_rate = target_sample_rate
                series.rangex = target_rangex
#                 import pdb;pdb.set_trace()
                transformed_do[target_key] = series
            transformed_doc.add(transformed_do)
        #pp(transformed_doc)
        return transformed_doc
    
class DataParser(object):
    ''' DataParser (ABC) is responsible for parsing input data and converting
    it to a DataObjectCollection. '''

    @abc.abstractmethod
    def parse(self, *args):
        ''' After doing whatever setup is necessary, this argument should
        convert the input data into a DataObjectCollection and return it. '''
        pass


