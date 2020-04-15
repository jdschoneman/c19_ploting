# -*- coding: utf-8 -*-
"""

Plot comparisons of IHME comparisons to reported data for US and European
countries. 

IHME data per IHME:
    https://covid19.healthdata.org/united-states-of-america
    
    IHME data stored here in the "..\data\ihme" directory for each release
    that was obtained.
    
Country data per COVID-19 Github:
    https://github.com/CSSEGISandData/COVID-19
    
    Data for the COVID-19 repo is contained here in the "..\data\COVID-19"
    directory.

"""

import os
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
from datetime import date


from read_data import get_data_c19, format_date_c19, get_data_ihme, format_date_ihme



# Select states and set data dates for display    
country = 'Sweden'

country = 'United Kingdom'
#country = 'Germany'
#country = 'Norway'
#country = 'Italy'
#country = 'Spain'
#country = 'US'


# Set files which we're loading from and set data dates for display
datapath = r'..\data\COVID-19\csse_covid_19_data\csse_covid_19_time_series'
dataname = 'time_series_covid19_deaths_global.csv'
data_filename = os.path.join(datapath, dataname)
data_date = '14 April'

# model_fname = r'..\data\ihme-covid19_20200401\2020_03_31.1\Hospitalization_all_locs.csv'
#model_fname = r'..\data\ihme-covid19_20200405\2020_04_05.05.us\Hospitalization_all_locs.csv'
#project_date = '5 April'
#model_fname = r'..\data\ihme-covid19_20200408\2020_04_07.06.all\Hospitalization_all_locs.csv'
#project_date = '8 April'
#
#model_fname = r'..\data\ihme-covid19_20200410\2020_04_09.04\Hospitalization_all_locs.csv'
#project_date = '10 April'
model_fname = r'..\data\ihme\2020_04_12.02\Hospitalization_all_locs.csv'
project_date = '13 April'

# project_date = '31 March'

start_date = '20200315'
stop_date = '20200601'

# Savenames for images
today = date.today()
impath = '../images/ihme_compare'
imname = '%s_data%s_project%s_%s.png' % (country, data_date, project_date, str(today))


# Load data and format
death, dates = get_data_c19(country, data_filename)
dates = [format_date_c19(s) for s in dates]
date_inds = range(len(dates))        
ddeath = np.diff(death, prepend = 0)

xticks = date_inds[::4]
xticklabels = ['%s/%s' % (s[-3], s[-2:]) for s in dates[::4]]

# Load ihme data
if country == 'US':
    data_ihme = get_data_ihme(model_fname)['United States of America']
else:
    data_ihme = get_data_ihme(model_fname)[country]

dates_ihme = [format_date_ihme(s) for s in data_ihme['date']]
start_c19 = dates.index(start_date)
dates = dates[start_c19:]
death = death[start_c19:]
ddeath = ddeath[start_c19:]

start_ihme = dates_ihme.index(start_date)
stop_ihme = dates_ihme.index(stop_date)

dates_ihme = dates_ihme[start_ihme:stop_ihme]
date_inds_ihme = range(len(dates_ihme))

death_ihme_m, death_ihme_l, death_ihme_u = (data_ihme['totdea_mean'][start_ihme:stop_ihme], 
                                                    data_ihme['totdea_lower'][start_ihme:stop_ihme], 
                                                    data_ihme['totdea_upper'][start_ihme:stop_ihme])

ddeath_ihme_m, ddeath_ihme_l, ddeath_ihme_u = (data_ihme['deaths_mean'][start_ihme:stop_ihme], 
                                                    data_ihme['deaths_lower'][start_ihme:stop_ihme], 
                                                    data_ihme['deaths_upper'][start_ihme:stop_ihme])

xticks = date_inds_ihme[::4]
xticklabels = ['%s/%s' % (s[-3], s[-2:]) for s in dates_ihme[::4]]


#%% Show info on hospitalizations

lightblue = [0.3, 0.3, 0.8]
darkblue = [0.2, 0.2, 0.6]
fig, ax = plt.subplots(2, 1, figsize = (12, 6))
ax = ax.flatten()

ax = [None, ax[0], None, ax[1]]

ax[1].plot(dates, death, 'o', label = 'Reported',
            color = darkblue, markerfacecolor = lightblue)
ax[1].plot(dates_ihme, death_ihme_m, 'k-', label = 'IHME Projected [Mean]')
ax[1].plot(dates_ihme, death_ihme_l, 'r--', label = 'IHME Projected [Lower CI]')
ax[1].plot(dates_ihme, death_ihme_u, 'r--', label = 'IHME Projected [Upper CI]')
ax[1].set_xlim(0, date_inds_ihme[-1])
ax[1].set_xticks(xticks)
ax[1].set_xticklabels(xticklabels)
ax[1].legend()
ax[1].set_ylabel('Total Deaths', fontsize = 12, fontweight = 'bold')
#ax[1].set_title('Deaths', fontsize = 12, fontweight = 'bold')


ax[3].plot(dates, ddeath, 'o',
           color = darkblue, markerfacecolor = lightblue)
ax[3].plot(dates_ihme, ddeath_ihme_m, 'k-')
ax[3].plot(dates_ihme, ddeath_ihme_l, 'r--')
ax[3].plot(dates_ihme, ddeath_ihme_u, 'r--')
ax[3].set_xlim(0, date_inds_ihme[-1])
ax[3].set_xticks(xticks)
ax[3].set_xticklabels(xticklabels)
ax[3].set_ylabel('New Deaths', fontsize = 12, fontweight = 'bold')
ax[3].set_xlabel('Date', fontsize = 12, fontweight = 'bold')

# plt.tight_layout()
fig.suptitle('%s: Reported Data [%s] vs IHME Projections [%s]' % 
             (country, data_date, project_date), fontsize = 14, fontweight = 'bold')

plt.savefig(os.path.join(impath, imname), bbox_inches = 'tight')




