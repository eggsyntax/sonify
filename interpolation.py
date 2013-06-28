'''
Interpolation functions handle missing values in the data. They take a list and substitute
something for the occurrences of the missing values.

Created on Jun 25, 2013
@author: egg
'''

def interpolate_forward(l, missing_values):
    ''' Go through a list from front to back. Carry non-missing values forward to replace missing. '''
    new_l = []
    interpolation_value = l[0]
    for v in l:
        if v in missing_values:
            new_l.append(interpolation_value)
        else:
            interpolation_value = v
            new_l.append(v)
    return new_l

def interpolate_backward(l, missing_values):
    new_l = list(l)
    new_l.reverse()
    new_l = interpolate_forward(new_l, missing_values)
    new_l.reverse()
    return new_l

def interpolate_forward_backward(l, missing_values):
    ''' This is the standard interpolation function -- carries values forward to replace
    missing values, and then does it backward to take care of any missing values at the beginning. '''
    new_l = interpolate_forward(l, missing_values)
    new_l = interpolate_backward(new_l, missing_values)
    return new_l
