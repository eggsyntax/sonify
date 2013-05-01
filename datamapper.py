import abc
import pprint

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
        return (in_sr / out_sr) * out_index

    def _diff(self, duple):
        return duple[1] - duple[0]

    def remap_range(self, inlist, original_range, desired_range):
        scaling_factor = float(self._diff(desired_range)) \
                / self._diff(original_range)
        outlist = []
        original_floor = original_range[0]
        desired_floor = desired_range[0]
        for v in inlist:
            newv = ((v - original_floor) * scaling_factor) + desired_floor
            outlist.append(newv)
        return outlist

    def set_mapping(self, mapping):
        #TODO provide a set of tuples mapping DOs in the input DOC
        # to DOs in the output DOC.
#         import pdb;pdb.set_trace()
        target_param_dict = self.data_renderer.expose_parameters()
    
        renderer_params = []
        for do in self.data_object_collection:
            for key in do.keys():
                target_key = mapping[key]
                target_params = target_param_dict[target_key]
                target_range = target_params['range'] if 'range' in target_params else None
                target_sample_rate = target_params['sample_rate'] if 'sample_rate' in target_params else None
                current_map = {'source_key': key,
                               'target_key': target_key,
                               'target_range': target_range,
                               'target_sample_rate': target_sample_rate
                               }
                renderer_params.append(current_map)
#         import code; code.interact(local=locals())
        self.mapping = renderer_params # I think renderer_params is badly in need of a rename #TODO
        #return renderer_params
    
    def get_transformed_doc(self):
        if not self.mapping:
            raise Exception('Mapping must be set to execute this function.')
        return self.data_object_collection # TODO transform #YOUAREHERE

# class Mapping:
#     ''' Mapping contains a list of dicts. Each dict contains, at minimum, a
#     source key ('temperature') and a target key ('frequency'). It can additionally
#     contain a target range or a target sample rate. '''
#     def __init__(self, dicts):
#         self._validate(dicts)
#         
#     def _validate(self, dicts):
#         for d in dicts:
#             for expected_key in ['source_key', 'target_key']:
#                 assert d.has_key(expected_key)
#         # other validation?
    
class DataParser(object):
    ''' DataParser (ABC) is responsible for parsing input data and converting
    it to a DataObjectCollection. '''

    @abc.abstractmethod
    def parse(self, *args):
        ''' After doing whatever setup is necessary, this argument should
        convert the input data into a DataObjectCollection and return it. '''
        pass


