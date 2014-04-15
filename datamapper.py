import pprint
import logging

pp = pprint.PrettyPrinter().pprint
logging.basicConfig(filename="/tmp/log.txt", level=logging.INFO)

# from renderers.datarenderer import DataRenderer

''' datamapper contains the three parts of the Data Mapper functionality:
    1) DataObjectCollection, DataObject, and TimeSeries represent the data to be used
        as the basis for the representation.
    2) DataRenderer is able to render a DataObjectCollection into a musical (or other)
        representation
    3) A map defines the mapping from DataObjectCollection to DataRenderer. It
        maps a key in the data ('temperature') to an attribute of the musical
        representation ('pitch'), with an understanding of the relative domains and
        ranges of each.
'''
#TODO Think about realtime capabilities

class DataObjectCollection(list):
    ''' DataObjectCollection is a list-like class which contains DataObject objects
    (where a DataObject represents, say, a single buoy, ie a collection of TimeSeries).
    '''
    '''
    Conceptually DataObjectCollection is unordered, ie it's set-like, but there are some pain 
    points around that, notably the fact that we often want to grab an arbitrary member and look
    at it, so we're treating it as a list.
    '''
    #TODO add facilities for pickling and unpickling?
    #TODO: unify __repr__ and __init__ for this and DataObject and TimeSeries?
    def __init__(self, starter_coll=None, sample_rate=None, metadata={}):
        self._sample_rate = sample_rate
        self.metadata = metadata # A place to store extra info about the DOC
        if starter_coll:
            try:
                data_objects = list(starter_coll)
            except TypeError, e:
                error_msg = 'The starter collection for a DataObjectCollection must be something' \
                    ' that can reasonably be converted to a list;', type(starter_coll), 'does' \
                    ' not qualify. (', starter_coll, ')'
                raise e, error_msg
            for do in data_objects:
                # or should we try to make a DataObject out of it? Probably...
                assert type(do) == DataObject, 'Gotta populate a DataObjectCollection with DataObjects.'
            list.__init__(self, data_objects)
        else:
            list.__init__(self)

    def transform(self, mapping, data_renderer, intify=False):
        ''' Pass in a mapping (a dict) from keys in the source data to keys in the 
        rendered data, eg {'altitude': 'pitch', 'temperature': 'amplitude'}. The method
        will use this mapping to create a new DataObjectCollection containing the
        data in the format the renderer desires, with sample rate and range transformed
        as necessary. 
        If intify is true, values in the transformed doc will be ints (necessary for 
        some rendering methods) '''
        target_parameters = data_renderer.expose_parameters()

        transformed_doc = DataObjectCollection()
        for do in self:
            transformed_do = DataObject()
            for key in do.keys():
                target_key = mapping[key]
                series = do[key]

                target_params = target_parameters[target_key]
                target_ts_range = target_params['range'] if 'range' in target_params else None
                target_sample_rate = target_params['sample_rate'] if 'sample_rate' in target_params else None

                # TODO remap sample rate
                # Current thoughts: separate this into two parts. Basic sample rate remapping results in the
                # exact same list of values, just with a different sample rate. There's a separate
                # function, resample(), which actually interpolates values so that a list of values
                # with 10 values at 120 BPM becomes a list of 40 values at 30 BPM.

                series = series.remap_range(target_ts_range)
                series.sample_rate = target_sample_rate
                series.ts_range = target_ts_range # Necessary?

                transformed_do[target_key] = series
            transformed_doc.append(transformed_do)
        # pp(transformed_doc)
        return transformed_doc

    @property
    def sample_rate(self):
        if self._sample_rate is not None: return self._sample_rate
        # We don't have a sample_rate. Get it from a DO
        for do in self:
            do_rate = do.sample_rate
            if do_rate:
                self._sample_rate = do_rate
                return self._sample_rate
        # Damn, no one has one.
        return None
    @sample_rate.setter
    def sample_rate(self, r):
        self._sample_rate = r

	def resample(self, factor):
		for dob in self:
			print 'DOB:', dob
			dob.resample(factor)

    def append(self, dob):
        assert isinstance(dob, DataObject), "You've got a " + str(type(dob)) + ", not a DataObject"
        list.append(self, dob)

    def trim(self):
        ''' Shorten all DataObjects in the collection to the length of the shortest one '''
        min_length = min((do.ts_length() for do in self))
        for do in self:
            do.trim_to(min_length)

    def combine_range(self, key):
        ''' Often a DataObjectCollection contains multiple DataObjects with the same key
        (eg temperature) and we would like their range to be based not on the range within each
        but on the combined range across all of them. '''
        combined_range = self._get_combined_range(key)
        self._set_ranges(key, combined_range)

    def combine_all_ranges(self):
        ''' Combine ranges across DataObjects for each key (NOT across all keys, of course) '''
        for key in self[0].keys():
            self.combine_range(key)

    @property
    def global_min(self):
        global_min, _ = self._get_global_min_max()
        return global_min

    @property
    def global_max(self):
        _, global_max = self._get_global_min_max()
        return global_max

    def intify(self):
        ''' In some situations we need int-only TimeSeries. '''
        for do in self:
            for ts in do.values():
                ts.replace_data([int(v) for v in ts])

    def __getitem__(self, i):
        data_object = list.__getitem__(self, i)
        if self.sample_rate and not data_object.sample_rate:
            data_object.sample_rate = self.sample_rate
        return data_object

    def _get_combined_range(self, key):
        ''' If all TimeSeries for a particular key were to be combined, what would be the overall
        min and max of that combined TimeSeries? '''
        ranges = self._get_ranges(key)
        minval = None
        maxval = None
        for ts_range in ranges:
            if not minval:
                minval = ts_range[0]
            else:
                minval = min(minval, ts_range[0])

            if not maxval:
                maxval = ts_range[1]
            else:
                maxval = max(maxval, ts_range[1])
        #print 'combining to', minval, maxval
        return (minval, maxval)

    def _get_ranges(self, key):
        ranges = set()
        for do in self:
            ts = do[key]
            ranges.add(ts.ts_range)
        return ranges

    def _set_ranges(self, key, arange):
        for do in self:
            ts = do[key]
            ts.ts_range = arange

    def _get_keys(self):
        ''' On the assumption that all DataObjects have the same keys, return those keys. '''
        do = self[0]
        return list(do.keys())

    def _get_global_min_max(self):
        ''' What if all TimeSeries for a particular key were compared? What would be the range
        of all those series combined? '''
        ranges = []
        keys = self._get_keys()
        for key in keys:
            ranges.append(self._get_combined_range(key))
#        ranges = [ts.ts_range for ts in do.values()]
        min_range, max_range = zip(*ranges)
        global_min = min(min_range)
        global_max = max(max_range)
        return global_min, global_max

    def interactive_map(self, renderer):
        print 'Let\'s build an interactive map!'
        print 'Available keys:'
        mapping = {}
        target_params = renderer.expose_parameters()
        pp(target_params)
        unused_targets = set(target_params.keys())
        sample_data_object = self[0]
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



class DataObject(dict):
    ''' DataObject is a dict-like collection of TimeSeries. It generally represents a single
    datasource (a buoy, a satellite, a ground station) which produces multiple measurements. '''
    def __init__(self, sample_rate=None, metadata={}):
         self.sample_rate = sample_rate
         self.metadata = metadata # A place to store information about the entire DataObject
         dict.__init__(self)

    def items(self):
        # override to ensure sample rate is set (by calling __getitem__)
        its = []
        for key in self.keys():
            its.append((key, self.__getitem__(key)))
        return its

    def append(self, values, fields):
        ''' Convenience method -- rather than appending a value to each TimeSeries individually,
        use this to do them all at once. Must pass in a list of fields, the same length and order
        as the values. '''
        for i, key in enumerate(fields):
            # Skip fields we don't contain (generally fields we don't care about)
            if key not in self:
                continue
            value = float(values[i])
            self[key].append(value)


    def __hash__(self):
        return hash(repr(self))

    def ts_length(self):
        ''' Note! assumes all TimeSeries are the same length. You should worry if they're not. '''
        return len(self.values()[0])

    def trim_to(self, length):
        for ts in self.values():
            ts.replace_data(ts[:length])

	def resample(self, factor):
		for ts in self.values():
			ts.resample(factor)

    def __setitem__(self, key, ts):
         assert(isinstance(ts, TimeSeries))
         dict.__setitem__(self, key, ts)

    def __getitem__(self, key):
         series = dict.__getitem__(self, key)
         if self.sample_rate and not series.sample_rate:
            series.sample_rate = self.sample_rate
         return series

class TimeSeries(list):
    ''' TimeSeries is a list-like class which also contains metadata about the list, namely
    sample_rate (how many items represent one second) and ts_range (the range of values or
    possible values contained in the list. This can be set to indicate the expected range
    (say, (-1,1)), but if TimeSeries is asked for its ts_range and it hasn't been set, it's
    computed from the actual values).
    '''
    @property
    def ts_range(self):
        if self._ts_range: return self._ts_range
        # We don't have a ts_range. Compute from actual values
        sorted_vals = sorted(self)
        return (sorted_vals[0], sorted_vals[-1])
    @ts_range.setter
    def ts_range(self, r):
        self._ts_range = r
    @ts_range.deleter
    def ts_range(self):
        self._ts_range = None

    def __init__(self, data, sample_rate=None, ts_range=None, missing_value_indicator=None):
        # domain?
        # if I want duration, it's float(len(data)) / self.sample_rate.
        # But test that.  #assert(data is listlike)? hard to test. can do
        # hasattr(data,'__iter__'), but a dict satisfies that too.
        self.sample_rate = sample_rate
        self._ts_range = ts_range
        self.missing_value_indicator = missing_value_indicator
        list.__init__(self, data)

    def copy(self, new_data=None):
        if not new_data: new_data = self # Copy own data if other data is not supplied
        return TimeSeries(list(new_data), sample_rate=self.sample_rate, ts_range=self.ts_range,
                          missing_value_indicator=self.missing_value_indicator)

    def replace_data(self, new_data=None):
        del(self[:]) # clear all data
        self.extend(new_data)

    def resample(self, factor):
        ''' Increase or decrease the length of a TimeSeries by resampling. Factor of two means the 
        resulting TimeSeries is half as long; factor of .5
        means it's twice as long (minus one). This resampling method is fairly crude, and
        the user is advised to take a look at http://en.wikipedia.org/wiki/Sample_rate_conversion
        if they prefer something more sophisticated. Note that the sample rate remains unchanged. '''
        newlen = int(len(self) / factor)
        new_vals = []
        for i in range(newlen):
            old_i_float = float(i) * factor
            old_i_int = int(old_i_float)
            if old_i_int > len(self) - 2: break # We've gone as far as we can go
            fraction = old_i_float - old_i_int

            left_val = self[old_i_int]
            right_val = self[old_i_int + 1]
            new_val = left_val * (1.0 - fraction) + right_val * fraction
            new_vals.append(new_val)
        self.replace_data(new_vals)

    def remap_range(self, desired_range):
        original_floor = self.ts_range[0]
        desired_floor = desired_range[0]
        original_diff = self._diff(self.ts_range)

        if original_diff:
            scaling_factor = float(self._diff(desired_range)) / original_diff
            remapped_data = []
            for v in self:
                newv = ((v - original_floor) * scaling_factor) + desired_floor
                remapped_data.append(newv)
        else: # original data is all the same value. All we can do is remap to the desired floor
            remapped_data = [desired_floor] * len(self)
        remapped_series = TimeSeries(remapped_data, sample_rate=self.sample_rate,
                                     ts_range=self.ts_range)
        return remapped_series

    def _diff(self, duple):
        return duple[1] - duple[0]

    def __eq__(self, other):
        if not isinstance(other, TimeSeries): return False
        if len(self) != len(other): return False
        for i in range(len(self)):
            if self[i] != other[i]: return False
        return True

    def __repr__(self):
        return 'TimeSeries(%r, sample_rate=%r, ts_range=%r)' % (list(self), self.sample_rate, self.ts_range)
