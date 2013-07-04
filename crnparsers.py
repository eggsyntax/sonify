'''
Contains parsers for Climate Reference Network data (extremely reliable and sensitive climate
monitoring data from US locations). CRN produces data sets at various resolutions (monthly, daily,
hourly, subhourly), so these are different parsers (only implementing hourly at first). 

Created on Jun 20, 2013
@author: egg
'''
from dataparser import DataParser
import requests, re
import os
from datamapper import DataObjectCollection, DataObject, TimeSeries
from interpolation import interpolate_forward_backward

missing_values = (-9999.0, -99999)

class HourlyCrnParser(DataParser):
    ''' Convert the input data into a DataObjectCollection and return it. '''

    def __init__(self, storage_dir='/tmp/'):
        ''' files will be cached in the storage dir so they don't have to be re-downloaded
        every time you rerun. '''

        # CRN FTP directory can also be accessed with a web interface:
        self.webdir = 'http://www1.ncdc.noaa.gov/pub/data/uscrn/products/hourly02/'
        self.storage_dir = storage_dir
        self._known_stations = set()
        self.fields = fields = 'WBANNO UTC_DATE UTC_TIME LST_DATE LST_TIME CRX_VN LONGITUDE LATITUDE T_CALC T_HR_AVG T_MAX T_MIN P_CALC SOLARAD SOLARAD_FLAG SOLARAD_MAX SOLARAD_MAX_FLAG SOLARAD_MIN SOLARAD_MIN_FLAG SUR_TEMP_TYPE SUR_TEMP SUR_TEMP_FLAG SUR_TEMP_MAX SUR_TEMP_MAX_FLAG SUR_TEMP_MIN SUR_TEMP_MIN_FLAG RH_HR_AVG RH_HR_AVG_FLAG SOIL_MOISTURE_5 SOIL_MOISTURE_10 SOIL_MOISTURE_20 SOIL_MOISTURE_50 SOIL_MOISTURE_100 SOIL_TEMP_5 SOIL_TEMP_10 SOIL_TEMP_20 SOIL_TEMP_50 SOIL_TEMP_100'.split()

    @property
    def known_stations(self):
        if not self._known_stations:
            self._fetch_stations()
        return self._known_stations

    def _fetch_stations(self, year=2012):
        ''' Fetch the list of stations which are available for download in a given year. Defaults
        to 2012, when most stations were available. No return; just sets self.known_stations. '''
        url = 'http://www1.ncdc.noaa.gov/pub/data/uscrn/products/hourly02/%d/' % (year)
        r = requests.get(url)
        file_pattern = re.compile('CRNH0203-\d+-([\w-]+).txt')

        stations = []
        for line in r:
            match = file_pattern.search(line)
            if match:
                stations.append(match.group(1))
        self._known_stations.update(set(stations))

    def _filename(self, station, year):
        return 'CRNH0203-%d-%s.txt' % (year, station)

    def _download(self, stations, years):
        ''' Download any needed station-year files which are not in the cache directory.
        "The Hourly02 ftp directory contains USCRN hourly temperature, precipitation, 
        global solar radiation, and surface infrared temperature data in easy to read text 
        formats...For those seeking USCRN hourly station data in bulk, each 
        of the year subdirectories (such as 2009 or 2010) contains a station-year file for each 
        station, allowing for rapid access to all station hourly data for a year." '''
        existing_files = os.listdir(self.storage_dir)

        for station in stations:
            for year in years:
                filename = self._filename(station, year)
                if filename not in existing_files:
                    url = self.webdir + str(year) + '/' + filename
                    r = requests.get(url)
                    local_file = open(self.storage_dir + filename, 'w')
                    local_file.writelines(r)

    def find_stations(self, criteria, match=False):
        ''' Find stations which match a criterion string or a list of criterion
        strings. Note that this will return a list, even if only one station
        matches. If match is true, only looks for a match at the beginning of
        the station string. '''
        matches = []
        if type(criteria) == str:
            criteria_list = [criteria]
        else:
            criteria_list = list(criteria)
        for criterion in criteria_list:
            matches.extend(self._find_stations_from_criterion(criterion, match=match))
        return matches

    def _find_stations_from_criterion(self, criterion, match=False):
        matches = []
        pat = re.compile(criterion.lower().replace(' ', '_'))
        search = pat.match if match else pat.search
        for station in self.known_stations:
            if search(station.lower()):
                matches.append(station)
        return matches

    def find_stations_by_state(self, state):
        prefix = state + '_'
        return self.find_stations(prefix, match=True)

    def parse(self, stations, years, fields):
        ''' Pass in some stations and years. For convenience (and to match CRN's data output)
        we'll only deal with data in complete years. '''
        # First make sure we've got the data locally:
        self._download(stations, years)

        doc = DataObjectCollection()
        for station in stations:
            do = DataObject()
            for field in self.fields:
                # Skip some fields we know we don't care about
                useless_fields = ['WBANNO', 'UTC_DATE', 'UTC_TIME', 'LST_DATE', 'LST_TIME', 'CRX_VN', 'SUR_TEMP_TYPE']
                if (fields and field not in fields) or (not fields and field in useless_fields):
                    continue
                do[field] = TimeSeries([])

            for year in years:
                f = open(self.storage_dir + self._filename(station, year))
                for line in f:
                    values = line.split()
                    do.append(values, self.fields)
            for ts in do.values():
                ts.replace_data(interpolate_forward_backward(ts, missing_values))
            doc.append(do)
        return doc
