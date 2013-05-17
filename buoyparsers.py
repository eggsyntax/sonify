'''

Created on May 13, 2013
@author: egg
'''
from datamapper import DataParser, DataObjectCollection, DataObject, TimeSeries
import parsedatetime.parsedatetime as pdt
from heapq import *

class GlobalDrifterParser(DataParser):
    cal = pdt.Calendar()
    
    # Criterion functions: Functions should accept all data for a single buoy (as a list) and 
    # return a value; smallest values are the ones kept.
    
    @staticmethod
    def record_length(list_of_records):
        return 1.0 / len(list_of_records) # invert to match heapq's bias toward a minheap
    
    def parse(self, input_filename, num_buoys=4, criterion=record_length, start=None, end=None):
        ''' Parse a file from the Global Drifter buoy program. Keeps the num_buoys buoys that most
        closely match the criterion function (eg longest record, closest to some latitude, closest
        to some lat/long pair '''
        ''' Metadata for global drifter program:
             ID     MM  DD   YY       LAT      LON       TEMP      VE        VN        SPD     VAR. LAT   VAR. LON  VAR. TEMP
                                                 Deg C    CM/S      CM/S       CM/S
        Note: file is very large (2+ GB) 
        Files can be obtained from ftp://ftp.aoml.noaa.gov/phod/pub/buoydata/
            and must be gunzipped despite the odd .dat-gz suffix. '''
        column_names = 'ID     MM  DD   YY       LAT      LON       TEMP      VE        VN        SPD     VAR_LAT   VAR_LON  VAR_TEMP'.split()
        
        with open(input_filename) as input_file:
            data = [] # treat as heapq
            for line in input_file:
                splitline = line.split()
                heappush(data, splitline)
                if len(data) > 1: break
                print splitline[0]
        
#TODO just here for visual reference
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
            doc.add(do)
        return doc
