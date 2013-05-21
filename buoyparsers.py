'''

Created on May 13, 2013
@author: egg
'''
from datamapper import DataParser, DataObjectCollection, DataObject, TimeSeries
from heapq import *
from functools import total_ordering

import pprint
from datetime import datetime

pp = pprint.PrettyPrinter().pprint

import parsedatetime.parsedatetime as PDT #@UnresolvedImport (Eclipse)

'''
Criterion functions define how DataObjects should be compared to determine which ones should be
kept. A custom criterion_function must follow the __cmp__ conventions. 
See http://stackoverflow.com/questions/12908933/overriding-cmp-python-function
#TODO the above has changed
The criterion function should return a comparable value; the Observations that return the
smallest values are the ones kept.
'''

def record_length(data_object):
    ''' Compare length of an arbitrary TimeSeries member of the DataObject 
    (they're assumed to all be the same length) '''
    key = data_object.keys()[0]
    return len(data_object[key])

''' End criterion functions '''
    

class GlobalDrifterParser(DataParser):
    cal = PDT.Calendar()
    
    
    def parse(self, input_filename, num_buoys=4, criterion_function=record_length, start=None, end=None):
        ''' Parse a file from the Global Drifter buoy program. Keeps the num_buoys buoys that most
        closely match the criterion function (eg longest record, closest to some latitude, closest
        to some lat/long pair). Each buoy becomes a DataObject.
         '''
        
        ''' Metadata for global drifter program:
        VE and VN are eastward and northward velocity. SPD is speed. Last 3 are variance. Do I care about any of them?
             ID     MM  DD   YY       LAT      LON       TEMP      VE        VN        SPD     VAR. LAT   VAR. LON  VAR. TEMP
                                                 Deg C    CM/S      CM/S       CM/S
        Note: file is very large (2+ GB) 
        Files can be obtained from ftp://ftp.aoml.noaa.gov/phod/pub/buoydata/
            and must be gunzipped despite the odd .dat-gz suffix. '''
        column_names = 'ID     MM  DD   YY       LAT      LON       TEMP      VE        VN        SPD     VAR_LAT   VAR_LON  VAR_TEMP'.split()
        
        def _getDataObject():
            ''' Convenience method to return a DataObject initialized to fit the buoy data. '''
            do = DataObject(metadata = {'buoy_id': id})
            for key in ['LAT', 'LON', 'TEMP']:
                do[key] = TimeSeries([])
            return do
        
        with open(input_filename) as input_file:
            data = [] # treat as heapq
            buoy_id = None
            curdata = _getDataObject()

            for i, line in enumerate(input_file):
                if i > 40000: break # TODO for testing, at least

                splitline = line.split()
                
                new_id = splitline[0] # buoy_id for this line
                if new_id != buoy_id: # Have we moved on to a new buoy?
                    if curdata:
                        curdata.metadata['buoy_id'] = buoy_id
                        if len(data) >= num_buoys:
#                             import pdb;pdb.set_trace()
                            heapindex = criterion_function(curdata)
                            heappushpop(data, (heapindex,curdata))
                        else: # Still building our heap to the size we want
                            heappush(data, curdata)
                    buoy_id = new_id
                    curdata = _getDataObject()
                    
                # Start by stuffing all the data for this observation into a dict:
                temp_data_dict = {}
                for i, val in enumerate(splitline):
                    column_name = column_names[i]
                    temp_data_dict[column_name] = val
                    
                # But we don't want to save all of it (there's a bunch of stuff we don't care
                # about). So we pick through it for the stuff we want, parsing and transforming
                # as necessary. Right now they're all strings.
                
                # Date/time first
                # Day of month plus time of day is represented like: 3.75 (3rd day, 3/4 of the way through)
                day_time = float(temp_data_dict['DD'])
                day = int(day_time)
                percent_of_day = day_time - day
                hour = int(24 * percent_of_day) # leaves us with 0, 6, 12, or 18
                year = int(temp_data_dict['YY'])
                month = int(temp_data_dict['MM'])
                date_time = datetime(year, month, day, hour)
                
                if start and date_time < start: continue
                if end   and date_time >   end: continue
                
                #TODO how do we add the date_time? as metadata, maybe? Or maybe not; maybe it's sufficient
                # to add the start and end times
                
                curdata['LAT'].append(float(temp_data_dict['LAT']))
                curdata['LON'].append(float(temp_data_dict['LON']))
                curdata['TEMP'].append(float(temp_data_dict['TEMP']))
                
                #TODO What I *actually* want to put on the heap is a DataObject. Right?
                # No. I think not. Because right now I need to focus on the heapification, but I
                # don't want to go overriding the comparison methods for DataObject (although I could,
                # and then put the old ones back later). At the cost of some efficiency, I probably
                # should instead do them as these _Datalist objects and then once I've got the ones
                # I want on the heap, I can convert to DataObject.
                # But on the other hand, it may be that the criterion function wants to do things
                # that are naturally expressed about DataObjects, and that way the client doesn't
                # need to think about a different representation.
#             for _, do in data:
#                 key = do.keys()[0]
#                 print len(do[key]), do.metadata['buoy_id']
                
#             _restoreComparisonMethods(data)

            doc = DataObjectCollection(sample_rate=1.0/360) # 1 sample per six hours
            for _, do in data: # _ is the heap index
                doc.add(do)
            return doc
        
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
