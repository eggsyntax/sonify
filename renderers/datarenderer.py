'''

Created on Apr 28, 2013
@author: egg
'''
import abc

#TODO TODO TODO - workflow simulations with other coders
class DataRenderer(object):
    ''' DataRenderer is responsible for producing actual output from the data
    provided by DataMapper. Abstract base class. '''
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def sample_rate(self):
        return 'Should never get here'
    #setter here as well?

    @abc.abstractmethod
    def render(self, doc):
        ''' Produces actual output. Generally not called directly but rather by the DataMapper. '''
        pass
    
    @abc.abstractmethod
    def expose_parameters(self):
        ''' expose_parameters provides a dict from parameter names to their expected
        range and sample rate. Or, arguably, provides an immutable DataObjectCollection.'''
        pass

