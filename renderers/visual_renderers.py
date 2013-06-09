'''

Created on May 26, 2013
@author: egg
'''
from renderers.datarenderer import DataRenderer
import pygal
from math import floor

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

class LineGraphRenderer(DataRenderer):
    ''' Responsible for rendering the doc from SineDictParser '''
    def __init__(self):
        super(LineGraphRenderer, self).__init__()

    @property
    def sample_rate(self):
        return self._sample_rate

    @sample_rate.setter
    def sample_rate(self, rate):
        self._sample_rate = rate

    def _get_xlabels(self, num_labels, xmax):
        tick_size = xmax / 10
        if not tick_size: return []
        labels = [str(v) if v % tick_size == 0 else '' for v in range(xmax)]
        return labels

    def _render(self, doc, keys, showplot, outfile, show_dots):
        print 'keys:', keys #TODO
        line_chart = pygal.Line(show_dots=show_dots) #@UndefinedVariable #Eclipse is confused about the import
        line_chart.title = ''
        maxlen = 0
        for i, do in enumerate(doc):
            for key in keys:
                ts = do[key]
                maxlen = max(maxlen, len(ts))
                title = str(i) + '-' + str(key)
                line_chart.add(title, list(ts))

        line_chart.x_labels = self._get_xlabels(10, maxlen)

        if outfile: line_chart.render_to_file(outfile)
        return line_chart

    def render(self, doc, showplot=False, outfile='/tmp/buoyline.svg', render_separate=True,
                        show_dots=False, keys=None, num_xlabels=10):
        ''' In case you'd rather have a separate plot for each key '''
        if not keys: keys = sorted(doc[0].keys())

        # We want to either iterate over each key or pass all keys at once
        if render_separate:
            for key in keys:
                filename = outfile.replace('.svg', '_' + key + '.svg')
                self._render(doc, (key,), showplot, filename, show_dots)
        else:
            self._render(doc, keys, showplot, outfile, show_dots)

    def expose_parameters(self):
        return None
