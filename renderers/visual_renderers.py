'''

Created on May 26, 2013
@author: egg
'''
from renderers.datarenderer import DataRenderer

class CSVRenderer(DataRenderer):
    def render(self, doc, print_to_screen=False, filename=None):
        keys = sorted(doc[0].keys())
        min_length = 1000000 # ONE. MILLION.
        for do in doc:
#            print 'length:', do.ts_length()
            min_length = min(min_length, do.ts_length())
#        print 'min_length:', min_length
        if filename: file = open(filename, 'w')

        output = []
        for i in range(min_length):
            curvals = []
            for do in doc:
                for key in keys:
                    curval = do[key][i]
                    curvals.append(str(curval))
            outstring = ','.join(curvals)
            output.append(outstring)
        if print_to_screen:
            print '\n'.join(output)
        if filename:
            file.write('\n'.join(output))
            file.close()
        return output

    def expose_parameters(self):
        return None

    
