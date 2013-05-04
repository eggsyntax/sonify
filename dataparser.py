'''

Created on May 3, 2013
@author: egg
'''
import abc
class DataParser(object):
    ''' DataParser (ABC) is responsible for parsing input data and converting
    it to a DataObjectCollection. '''

    @abc.abstractmethod
    def parse(self, *args):
        ''' After doing whatever setup is necessary, this argument should
        convert the input data into a DataObjectCollection and return it. '''
        pass
