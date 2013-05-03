'''

Created on Apr 28, 2013
@author: egg
'''
import abc

class DataRenderer(object):
    ''' DataRenderer is responsible for producing actual output from the data
    provided by DataMapper. Abstract base class. '''
    __metaclass__ = abc.ABCMeta

    @property
    def sample_rate(self):
        return self._sample_rate
    @sample_rate.setter
    def sample_rate(self, val):
        self._sample_rate = val
        
    @abc.abstractmethod
    def render(self, doc):
        ''' Produces actual output. Generally not called directly but rather by the DataMapper. '''
        pass
    
    @abc.abstractmethod
    def expose_parameters(self):
        ''' expose_parameters provides a dict from parameter names to their expected
        range and sample rate. Or, arguably, provides an immutable DataObjectCollection.'''
        pass

