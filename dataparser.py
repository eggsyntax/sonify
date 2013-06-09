'''
Abstract base class for parsers. Create a new subclass of this to handle some new flavor of data.

Created on May 3, 2013
@author: egg
'''
#TODO Consider declarative descriptions of data. Could have an interactive builder for those
# as well.

import abc
class DataParser(object):
    ''' DataParser (ABC) is responsible for parsing input data and converting
    it to a DataObjectCollection. '''

    @abc.abstractmethod
    def parse(self, *args):
        ''' After doing whatever setup is necessary, this method should
        convert the input data into a DataObjectCollection and return it. '''
        pass
