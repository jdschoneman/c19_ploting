# -*- coding: utf-8 -*-
"""

Utility import functions for reading the various available data formats:
    
    IHME model extrapolations
        https://covid19.healthdata.org/united-states-of-america
    COVID-19 Github repository (International data)
        https://github.com/CSSEGISandData/COVID-19
    Covid-Tracking data (US state data)
        https://covidtracking.com/
        
Note that I've made minor alterations to the header of some IHME CSV files
to unify header titles for the read scripts below.

"""

import numpy as np

def intfun(s):
    try:
        return int(s)
    except ValueError:
        return 0

def foo(astr):
    # replace , outside quotes with ;
    # and strip out the quotes themsevlves
    # a bit crude and specialized
    start_ind = 0
    items = list(astr)
    while True:
        try:
            start_ind = items.index('"', start_ind)
            stop_ind = items.index('"', start_ind + 1)
            for ind in range(start_ind, stop_ind):
                items[ind] = items[ind].replace(',', ';')
            start_ind = stop_ind + 1
        except ValueError:
            break
    
    return ''.join(items)

    
def get_data_ctrack(state, fname):
    """
    Returns dictionary of all data for the Covid Tracking dataset. This function
    applicable for data dated 4/2 and onwards. 
    """
    
    # Get the headers
    headers = np.loadtxt(fname, delimiter = ',', max_rows = 1, dtype = str, 
                         unpack = True)
    out = dict()
    
    for ind, header in enumerate(headers):
        if header == 'date':
            out[header] = np.loadtxt(fname, dtype = str, delimiter = ',', 
               skiprows = 1, usecols = (ind, ), unpack = True)
            continue
        
        try:
            out[header] = np.loadtxt(fname, dtype = int, delimiter = ',', 
                                     skiprows = 1, usecols = ind, unpack = True)
        except ValueError:
            out[header] = np.loadtxt(fname, dtype = str, delimiter = ',', 
                                     skiprows = 1, usecols = (ind, ),
                                     unpack = True)
            
    # Filter to state
    state_inds = out['state'] == state
    for key, val in out.items():
        out[key] = np.flip(val[state_inds])
    
    # List of items to convert to int
    convert_items = ['death', 'hospitalizedCurrently', 'hospitalized', 'positive', 'negative',
                     'inIcuCurrently', 'onVentilatorCurrently']
    for item in convert_items:
        out[item] = np.array([intfun(s) for s in out[item]])
    
    return out


def get_data_c19(country, filename):
    """
    Reads (day, value) pairs from CSV file from the COVID-19 Github page
    """
    
    with open(filename, 'rt') as fid:
        txtgen = [foo(astr) for astr in fid.readlines()]
    
    all_countries = np.loadtxt(txtgen,
                               delimiter = ',', skiprows = 1,
                               usecols = (1), dtype = str)
        
    
    all_data = np.loadtxt(txtgen,
                               delimiter = ',', skiprows = 1,
                               dtype = str)[:, 4:].astype(int)
    
    dates_out = np.loadtxt(txtgen,
                               delimiter = ',', max_rows = 1,
                               dtype = str)[4:]
    
    data_out = all_data[np.where(all_countries == country)[0], :]
    keep_ind = np.argmax(data_out[:, -1])  # Full country will have highest count
    
    return data_out[keep_ind, :], dates_out


def get_data_ihme(fname):
    """
    Load the IHME data projections; returns a dictionary of dictionaries
    containing the header data for each stored location.
    """
    
    with open(fname, 'rt') as fid:
        txtgen = [foo(astr) for astr in fid.readlines()]
        
    # Get the headers
    headers = np.loadtxt(txtgen, delimiter = ',', max_rows = 1, dtype = str, 
                         unpack = True)
    headers = [s.replace('"', '') for s in headers]
    data = dict()
    
    
    
    for ind, header in enumerate(headers):
        print(header)
        if (header == 'location') or header == ('date') or header == ('location_name'):
            
            data[header] = np.loadtxt(txtgen, dtype = str, delimiter = ',', 
               skiprows = 1, usecols = (ind, ), unpack = True)
            data[header] = np.array([s.replace('"', '') for s in data[header]])
        else:
            data[header] = np.loadtxt(txtgen, dtype = float, delimiter = ',', 
                                     skiprows = 1, usecols = (ind,),  unpack = True)
        
            
    # Set up dictionary of all data by state/country
    try:
        loc_keys = np.unique(data['location'])
        keyname = 'location'
    except KeyError:
        loc_keys = np.unique(data['location_name'])
        keyname = 'location_name'
    
    out = dict()
    for loc_key in loc_keys:
        out[loc_key] = dict()
        for data_key, val in data.items():
            state_inds = data[keyname] == loc_key
            out[loc_key][data_key] = val[state_inds]
    
    return out

def format_date_ihme(date_in):
    """
    Formats "m/d/yyy" to "yyyymmdd"
    """
    
    try:
        month, day, year = date_in.split('/')
        return '%s%02i%02i' % (year, int(month), int(day))
    except:
        return date_in.replace('-', '')
    

def format_date_c19(date_in):
    """
    Formats "m/d/y" to "yyyymmdd"
    """
    
    month, day, year = date_in.split('/')
    return '20%s%02i%02i' % (year, int(month), int(day))