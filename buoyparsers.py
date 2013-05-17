'''

Created on May 13, 2013
@author: egg
'''
from datamapper import DataParser, DataObjectCollection, DataObject, TimeSeries
import parsedatetime.parsedatetime as pdt #@UnresolvedImport (Eclipse)
from heapq import *
from functools import total_ordering

class GlobalDrifterParser(DataParser):
    cal = pdt.Calendar()
    
    '''
    Criterion functions define how records should be compared to determine which ones should be
    kept. self and other come in as lists of lists. A custom criterion_function must follow 
    the __cmp__ conventions. See http://stackoverflow.com/questions/12908933/overriding-cmp-python-function
    '''
    
    def record_length(self, other):
        if len(self) < len(other): return -1
        if len(self) > len(other): return 1
        return 0

    def parse(self, input_filename, num_buoys=4, criterion_function=record_length, start=None, end=None):
        ''' Parse a file from the Global Drifter buoy program. Keeps the num_buoys buoys that most
        closely match the criterion function (eg longest record, closest to some latitude, closest
        to some lat/long pair.
         '''
        
        ''' Metadata for global drifter program:
             ID     MM  DD   YY       LAT      LON       TEMP      VE        VN        SPD     VAR. LAT   VAR. LON  VAR. TEMP
                                                 Deg C    CM/S      CM/S       CM/S
        Note: file is very large (2+ GB) 
        Files can be obtained from ftp://ftp.aoml.noaa.gov/phod/pub/buoydata/
            and must be gunzipped despite the odd .dat-gz suffix. '''
        column_names = 'ID     MM  DD   YY       LAT      LON       TEMP      VE        VN        SPD     VAR_LAT   VAR_LON  VAR_TEMP'.split()
        
        # We need a custom class for our lists so that we can override comparison methods
        @total_ordering
        class _Datalist(list):
            
            def __cmp__(self, other):
                return criterion_function(self, other)
            
            def __eq__(self, other):
                return (criterion_function(self, other) == 0)
            
            def __lt__(self, other):
                cls = self.__class__
                return (self.__cmp__(other) == -1)
            
        with open(input_filename) as input_file:
            data = [] # treat as heapq
            buoy_id = None
            curdata = _Datalist()

            for i, line in enumerate(input_file):
                if i > 10000: break # TODO for testing, at least

                splitline = line.split()
                
                # Have we moved on to a new buoy?
                new_id = splitline[0] # buoy_id for this line
#                 print buoy_id, new_id
                if new_id != buoy_id:
                    if curdata:
                        if len(data) >= num_buoys:
                            heappushpop(data, curdata)
                        else: # Still building our heap to the size we want
                            heappush(data, curdata)
                    buoy_id = new_id
                    curdata = _Datalist()
                else: #another line for the same buoy
                    #TODO YOUAREHERE
                    # I'm just adding the line (as a list) to the list of data for this buoy.
                    # Instead I need to use column_names to create a dict containing the
                    # variables I'll want to use, including transformation and parsing of
                    # the datetime elements
                    curdata.append(splitline)
            
            for item in data:
                print len(item), item[0][0]
                
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
