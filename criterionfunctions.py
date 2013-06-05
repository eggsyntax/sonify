'''
This module holds criterion functions which can be applied to DataObjects. Criterion functions 
define how DataObjects should be compared to determine which ones should be
kept. The criterion function should return a comparable value; the ones that return the
smallest values are the ones kept. Note that they can also be composed using create_combined_criterion()

Created on May 29, 2013
@author: egg
'''

def record_length(data_object):
    ''' Compare length of an arbitrary TimeSeries member of the DataObject 
    (they're assumed to all be the same length) '''
    key = data_object.keys()[0]
    return 1.0 / len(data_object[key]) # longer is better

def longer_than(n):
    def is_longer_than(data_object):
        key = data_object.keys()[0]
        return len(data_object[key]) > n
    return is_longer_than

def get_nearness_function(lat, lon):
    def nearness_function(data_object):
        start_lat = data_object['LAT'][0]
        start_lon = data_object['LON'][0]
        lat_diff = start_lat - lat
        lon_diff = start_lon - lon
        return lat_diff ** 2 + lon_diff ** 2 # pythagorean theorem. skip the sqrt for efficiency.
    return nearness_function

def get_num_missing_values_function(missing_value):
    def num_missing_values(data_object):
        ''' returns a value representing the combined number of missing values in the first and last
        members of the time series. '''
        total_missing = 0
        for ts in data_object.values():
            if ts[0] == missing_value:  total_missing += 1
            if ts[-1] == missing_value: total_missing += 1
        return total_missing
    return num_missing_values

def create_combined_criterion(list_of_functions):
    ''' Use a tuple of the results from multiple functions. Useful where the result of the first
    function is likely to be the same for all DataObjects (eg where we use record_length for all
    when we expect them to all be the same length) '''
    def combined_criterion(data_object):
        return (f(data_object) for f in list_of_functions)
    return combined_criterion

