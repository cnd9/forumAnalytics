# -*- coding: utf-8 -*-
"""
Created on Sun Jun 30 18:26:02 2019

@author: Christine
"""

def number_from_string(input_string):
    output_str = (''.join(filter(str.isdigit, input_string)))
    if len(output_str) == 0:
        output_int = 0
    else:
        output_int = int(output_str)    
    return output_int