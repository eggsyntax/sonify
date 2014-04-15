''' This is a parser for a particular project (the geothermophone). The data
is already in optimized form (a list of dicts from varname to a list of values).
'''
from datamapper import DataObjectCollection, DataObject, TimeSeries
from dataparser import DataParser
from renderers.midirenderers import MidiCCRenderer
from renderers.visual_renderers import LineGraphRenderer


class GriddedDataParser(DataParser):
    ''' Convert the input data into a DataObjectCollection and return it. '''

    def __init__(self):

        self.file = open(
            '/Users/egg/Documents/Work In Progress/geothermophone/final_values/final_values.txt')

    def parse(self):
        d = eval(self.file.readline().strip())
        doc = DataObjectCollection(sample_rate=1 / 3.0)
        for i, octant in enumerate(d):
            do = DataObject()
            for varname, values in octant.items():
                ts = TimeSeries(values)
                do[varname] = ts
            doc.append(do)
        return doc


def build_data():
    parser = GriddedDataParser()
    doc = parser.parse()
    doc.resample(.1403) # Trial and error to get 30 min of data

    # renderer = LineGraphRenderer()
    # plot = renderer.render(doc, showplot=True, render_separate=True)

    # Produce MIDI data
    renderer = MidiCCRenderer()
    # divide 20 by 1.782
    renderer.tempo = 20
    var_to_midi_map = {'air': 74,
                       'prate': 75,
                       'rhum': 76,
                       'wspd': 77}
    transformed_doc = doc.transform(var_to_midi_map, renderer)
    renderer.render(transformed_doc,
                    output_file='/Users/egg/Documents/Work In Progress/geothermophone/midi/geothermophone.mid')

build_data()

