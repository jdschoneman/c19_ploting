# -*- coding: utf-8 -*-
"""

Compare Sweden to NY state and Denmark by growth rate of deaths starting from
first 10 deaths.

IHME data per IHME:
    https://covid19.healthdata.org/united-states-of-america
    
    IHME data stored here in the "..\data\ihme" directory for each release
    that was obtained.
    
Country data per COVID-19 Github:
    https://github.com/CSSEGISandData/COVID-19
    
    Data for the COVID-19 repo is contained here in the "..\data\COVID-19"
    directory.
    
State-level data per Covid tracking project:
    https://covidtracking.com/
    
    Data for the COVID-19 repo is contained here in the 
    "..\data\covid19_tracker" directory for each day that the state
    historical values were obtained. 

"""

import os
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
from datetime import date


from read_data import get_data_c19, format_date_c19, get_data_ihme, format_date_ihme, get_data_ctrack

# Populations (millions)
ny_pop = 19.45
sweden_pop = 10.23
denmark_pop = 5.6

# Read IHME projections
model_fname = r'..\data\ihme\2020_04_12.02\Hospitalization_all_locs.csv'
project_date = '13 April'
all_ihme = get_data_ihme(model_fname)
dates_ihme = [format_date_ihme(s) for s in all_ihme['Sweden']['date']]

sweden_ihme_death = all_ihme['Sweden']['totdea_mean']
denmark_ihme_death = all_ihme['Denmark']['totdea_mean']
ny_ihme_death = all_ihme['New York']['totdea_mean']

# Load data for Sweden and denmark
datapath = r'..\data\COVID-19\csse_covid_19_data\csse_covid_19_time_series'
dataname = 'time_series_covid19_deaths_global.csv'
data_filename = os.path.join(datapath, dataname)
country_data_date = '14 April'
sweden_c19, dates_c19 = get_data_c19('Sweden', data_filename)
denmark_c19, dates_c19 = get_data_c19('Denmark', data_filename)
dates_c19 = [format_date_c19(s) for s in dates_c19]

# Load data for NY state
data_filename = r'..\data\covid19_tracker\states-daily_20200414.csv'
state_data_date = '14 April'
data_ctrack = get_data_ctrack('NY', data_filename)
ny_ctrack = data_ctrack['death']
dates_ctrack = data_ctrack['date']


#%% Determine starting date for each country/state using first to 10 deaths
# from data

n_death = 10

start_ind_sweden = np.where(sweden_c19 >= n_death)[0][0]
start_ind_denmark = np.where(denmark_c19 >= n_death)[0][0]
start_ind_ny = np.where(ny_ctrack >= n_death)[0][0]

start_date_sweden = dates_c19[start_ind_sweden]
start_date_denmark = dates_c19[start_ind_denmark]
start_date_ny = dates_ctrack[start_ind_ny]

n_days_sweden = len(dates_c19[start_ind_sweden:])
n_days_denmark = len(dates_c19[start_ind_denmark:])
n_days_ny = len(dates_ctrack[start_ind_ny:])

start_ihme_sweden = list(dates_ihme).index(start_date_sweden)
start_ihme_denmark = list(dates_ihme).index(start_date_denmark)
start_ihme_ny = list(dates_ihme).index(start_date_ny)


#%% Plot deaths for Sweden vs NY and Sweden vs Denmark

impath = r'..\images\sweden_ny_denmark.png'


fig, ax = plt.subplots(2, 2, figsize = (12, 6))
ax = ax.flatten()

gray = 0.3*np.array([1, 1, 1])
lightblue = [0.3, 0.3, 0.8]
darkblue = [0.2, 0.2, 0.6]
darkred = [0.6, 0.2, 0.2]
lightred = [0.8, 0.4, 0.4]

### New York vs Sweden; All ####
ax[0].plot(np.arange(n_days_sweden), sweden_c19[start_ind_sweden:]/sweden_pop,
          'o', label = 'Sweden; Reported',
            color = 'k', markerfacecolor = gray)
ax[0].plot(np.arange(n_days_ny), ny_ctrack[start_ind_ny:]/ny_pop,
          'o', label = 'New York State; Reported',
            color = darkred, markerfacecolor = lightred)


### New York vs Sweden; NEW ####
ax[2].plot(np.arange(n_days_sweden), np.diff(sweden_c19[start_ind_sweden:], prepend = 0)/sweden_pop,
          'o', label = 'Sweden; Reported',
            color = 'k', markerfacecolor = gray)
ax[2].plot(np.arange(n_days_ny), np.diff(ny_ctrack[start_ind_ny:], prepend = 0)/ny_pop,
          'o', label = 'New York State; Reported',
            color = darkred, markerfacecolor = lightred)

### Denmak vs Sweden; All ####
ax[1].plot(np.arange(n_days_sweden), sweden_c19[start_ind_sweden:]/sweden_pop,
          'o', label = 'Sweden; Reported',
            color = 'k', markerfacecolor = gray)
ax[1].plot(np.arange(n_days_denmark), denmark_c19[start_ind_denmark:]/denmark_pop,
          'o', label = 'Denmark; Reported',
            color = darkblue, markerfacecolor = lightblue)


### New York vs Sweden; NEW ####
ax[3].plot(np.arange(n_days_sweden), np.diff(sweden_c19[start_ind_sweden:], prepend = 0)/sweden_pop,
          'o', label = 'Sweden; Reported',
            color = 'k', markerfacecolor = gray)
ax[3].plot(np.arange(n_days_denmark), np.diff(denmark_c19[start_ind_denmark:], prepend = 0)/denmark_pop,
          'o', label = 'Denmark; Reported',
            color = darkblue, markerfacecolor = lightblue)


# Grab axis limits
#xl = ax[0].get_xlim()
#yl = ax[0].get_ylim()
#ax[0].plot(np.arange(len(dates_ihme[start_ihme_sweden:])), 
#           sweden_ihme_death[start_ihme_sweden:]/sweden_pop,
#          '-', label = 'Sweden; Projected',
#            color = 'k')
##
#
#
#ax[0].set_xlim(xl)
#ax[0].set_ylim(yl)

#ax[0].plot(np.arange(n_days_ny), ny_ctrack[start_ind_ny:]/ny_pop,
#          'o', label = 'New York State; Reported',
#            color = darkred, markerfacecolor = lightred)



#ax[0].plot(dates_ihme, death_ihme_m, 'k-', label = 'Sweden; Projected')


ax[0].legend()
ax[1].legend()
ax[0].set_ylabel('Total Deaths Per Million', fontsize = 12, fontweight = 'bold')
ax[2].set_ylabel('New Deaths Per Million', fontsize = 12, fontweight = 'bold')
ax[2].set_xlabel('Days Since 10 Deaths (Absolute)', fontsize = 12, fontweight = 'bold')
ax[3].set_xlabel('Days Since 10 Deaths (Absolute)', fontsize = 12, fontweight = 'bold')

title1 = ('NY [Reached 10 Deaths %s]\nvs\nSweden [Reached 10 Deaths %s]' 
          % (start_date_ny, start_date_sweden))
ax[0].set_title(title1, fontsize = 12, fontweight = 'bold')

title2 = ('Denmark [Reached 10 Deaths %s]\nvs\nSweden [Reached 10 Deaths %s]' 
          % (start_date_denmark, start_date_sweden))
ax[1].set_title(title2, fontsize = 12, fontweight = 'bold')
plt.tight_layout()
plt.savefig(impath, bbox_inches = 'tight')
#ax[1].set_title('Deaths', fontsize = 12, fontweight = 'bold')

#
#ax[3].plot(dates, ddeath, 'o',
#           color = darkblue, markerfacecolor = lightblue)
#ax[3].plot(dates_ihme, ddeath_ihme_m, 'k-')
#ax[3].plot(dates_ihme, ddeath_ihme_l, 'r--')
#ax[3].plot(dates_ihme, ddeath_ihme_u, 'r--')
#ax[3].set_xlim(0, date_inds_ihme[-1])
#ax[3].set_xticks(xticks)
#ax[3].set_xticklabels(xticklabels)
#ax[3].set_ylabel('New Deaths', fontsize = 12, fontweight = 'bold')
#ax[3].set_xlabel('Date', fontsize = 12, fontweight = 'bold')
#
## plt.tight_layout()
#fig.suptitle('%s: Reported Data [%s] vs IHME Projections [%s]' % 
#             (country, data_date, project_date), fontsize = 14, fontweight = 'bold')
#
#plt.savefig(os.path.join(impath, imname), bbox_inches = 'tight')
#
#
#

