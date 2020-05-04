# -*- coding: utf-8 -*-
"""

Plot comparisons of IHME projections to actual data for US states. 

IHME data per IHME:
    https://covid19.healthdata.org/united-states-of-america
    
    IHME data stored here in the "..\data\ihme" directory for each release
    that was obtained.
    
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
from scipy.signal import medfilt

from read_data import get_data_ctrack, get_data_ihme, format_date_ihme



def intfun(s):
    try:
        return int(s)
    except ValueError:
        return 0

# Select states and set data dates for display    
#state = 'NY'
#state_long = 'New York'
#state = 'GA'
#state_long = 'Georgia'
#state = 'KY'
#state_long = 'Kentucky'
#state = 'CA'
#state_long = 'California'
#state = 'WI'
#state_long = 'Wisconsin'
#ylpct = [0., 15.]
#state = 'IA'
#state_long = 'Iowa'
state = 'AL'
state_long = 'Alabama'
#state = 'OR'
#state_long = 'Oregon'
#state = 'FL'
#state_long = 'Florida'
#ylpct = [0.,25.]
#state = 'MI'
#state_long = 'Michigan'
#state = 'WA'
#state_long = 'Washington'
#state = 'DC'
#state_long = 'District of Columbia'
#state = 'NJ'
#state_long = 'New Jersey'
#state = 'OK'
#state_long = 'Oklahoma'
#state = 'SD'
#state_long = 'South Dakota'
# TODO: Have to add all state data together for the covid tracker data
#state = 'US'
#state_long = 'US'
#state = 'TX'
#state_long = 'Texas'
#state = 'GA'
#state_long = 'Georgia'
#state = 'MN'
#state_long = 'Minnesota'
#state = 'CO'
#state_long = 'Colorado'
ylpct = [0., 30.]

# Set files which we're loading from and set data dates for display
data_filename = r'..\data\covid19_tracker\states-daily_20200504.csv'
data_date = '04 May'

#model_fname = r'..\data\ihme\2020_03_31.1\Hospitalization_all_locs.csv'
#project_date = '31 March'

#model_fname = r'..\data\ihme\2020_04_12.02\Hospitalization_all_locs.csv'
#project_date = '13 April'

model_fname = r'..\data\ihme\2020_04_16.05\Hospitalization_all_locs.csv'
project_date = '17 April'

# When to stop the plotting
start_date = '20200401'
stop_date = '20200510'

# Which plots to make
plot_testing = True
plot_hosp_death = True
today = date.today()

# Load data and format
data = get_data_ctrack(state, data_filename)

dates = data['date']
start_date_ind = list(dates).index(start_date)
dates = dates[start_date_ind:]
pos = data['positive']
neg = data['negative']
hosp = data['hospitalizedCurrently']
icu = data['inIcuCurrently']
vent = data['onVentilatorCurrently']
death = data['death']
date_inds = range(len(dates))        
  
dpos = np.diff(pos, prepend = 0)
dneg = np.diff(neg, prepend = 0)
dhosp = np.diff(hosp, prepend = 0.)
ddhosp = np.diff(dhosp, prepend = 0)
ddeath = np.diff(death, prepend = 0)

pos = pos[start_date_ind:]
neg = neg[start_date_ind:]
hosp = hosp[start_date_ind:]
death = death[start_date_ind:]

dpos = dpos[start_date_ind:]
dneg = dneg[start_date_ind:]
dhosp = dhosp[start_date_ind:]
ddeath = ddeath[start_date_ind:]


xticks = date_inds[::4]
xticklabels = ['%s/%s' % (s[-3], s[-2:]) for s in dates[::4]]

# Load ihme data
data_ihme = get_data_ihme(model_fname)[state_long]
dates_ihme = [format_date_ihme(s) for s in data_ihme['date']]

# Trim to desired range
start_ihme = dates_ihme.index(start_date)
stop_ihme = dates_ihme.index(stop_date)
dates_ihme = dates_ihme[start_ihme:stop_ihme]
date_inds_ihme = range(len(dates_ihme))

dhosp_ihme_m, dhosp_ihme_l, dhosp_ihme_u = (data_ihme['admis_mean'][start_ihme:stop_ihme], 
                                                    data_ihme['admis_lower'][start_ihme:stop_ihme], 
                                                    data_ihme['admis_upper'][start_ihme:stop_ihme])

hosp_ihme_m, hosp_ihme_l, hosp_ihme_u = (data_ihme['allbed_mean'][start_ihme:stop_ihme], 
                                                    data_ihme['allbed_lower'][start_ihme:stop_ihme], 
                                                    data_ihme['allbed_upper'][start_ihme:stop_ihme])

death_ihme_m, death_ihme_l, death_ihme_u = (data_ihme['totdea_mean'][start_ihme:stop_ihme], 
                                                    data_ihme['totdea_lower'][start_ihme:stop_ihme], 
                                                    data_ihme['totdea_upper'][start_ihme:stop_ihme])

ddeath_ihme_m, ddeath_ihme_l, ddeath_ihme_u = (data_ihme['deaths_mean'][start_ihme:stop_ihme], 
                                                    data_ihme['deaths_lower'][start_ihme:stop_ihme], 
                                                    data_ihme['deaths_upper'][start_ihme:stop_ihme])

xticks = date_inds_ihme[::4]
xticklabels = ['%s/%s' % (s[-3], s[-2:]) for s in dates_ihme[::4]]

#%% Data on tests


if plot_testing:
    fig, ax = plt.subplots(1, 3, figsize = (17, 5))
    gray = 0.3*np.array([1, 1, 1])
    lightblue = [0.3, 0.3, 0.8]
    darkblue = [0.2, 0.2, 0.6]
    red = [0.6, 0.2, 0.2]
    lightred = [0.8, 0.4, 0.4]
    
    
    dtotal = dpos + dneg
    avg_7 = medfilt(dtotal, 7)
    ax[0].plot(dates, dtotal, 'o', label = 'Total Tests', 
              color = darkblue, markerfacecolor = lightblue)
    ax[0].plot(dates, avg_7, 'k--', label = '7 Day Moving Average')

    ax[0].set_xticks(xticks)
    ax[0].set_xticklabels(xticklabels)
    ax[0].set_ylabel('Number of Tests', fontsize = 12, fontweight = 'bold')
    ax[0].set_xlabel('Date', fontsize = 12, fontweight = 'bold')
    
    ax[1].plot(dates, dpos, 'o', label = 'Positive Tests',
                color = red, markerfacecolor = lightred)
    
    avg_3 = medfilt(dpos, 3)
    avg_7 = medfilt(dpos, 7)
#    ax[1].plot(dates, avg_3, 'b--', label = '3 Day Moving Average')
    ax[1].plot(dates, avg_7, 'k--', label = '7 Day Moving Average')
    
    ax[1].set_xticks(xticks)
    ax[1].set_xticklabels(xticklabels)
    ax[1].set_ylabel('Number of Positives', fontsize = 12, fontweight = 'bold')
    ax[1].set_xlabel('Date', fontsize = 12, fontweight = 'bold')

    avg_7 = medfilt(100*dpos/dtotal, 7)
    ax[2].plot(dates, avg_7, 'k--', label = '7 Day Moving Average')
    ax[2].plot(dates, 100*dpos/dtotal, 'o', color = 'k',
              markerfacecolor = gray)
    ax[2].set_xticks(xticks)
    ax[2].set_xticklabels(xticklabels)
    ax[2].set_xlabel('Date', fontweight = 'bold', fontsize = 12)
    ax[2].set_ylabel('Percentage of Positive Tests', 
                     fontweight = 'bold', fontsize = 12)
    
    ax[0].set_title('All Tests', fontsize = 12, fontweight = 'bold')
    ax[1].set_title('Positive Tests', fontsize = 12, fontweight = 'bold')
    ax[2].set_title('Percentage of Tests Positive', fontsize = 12, fontweight = 'bold')
    
    yl0 = ax[0].get_ylim()
    yl1 = ax[1].get_ylim()
    yl2 = ax[2].get_ylim()
    
    ax[0].set_ylim([-5, yl0[1]])
    ax[0].set_xlim([0, len(dates)])
    
    ax[1].set_ylim([-5, yl1[1]])
    ax[1].set_xlim([0, len(dates)])
    
    ax[1].legend()
    if ylpct is None:
        ax[2].set_ylim([-5, yl2[1]])
    else:
       ax[2].set_ylim(ylpct) 
    ax[2].set_xlim([0, len(dates)])
    
    
    
    fig.suptitle('%s: All Tests, Positive Tests, and Positive Test Percentages' % 
             state_long, fontsize = 14, fontweight = 'bold')
    
    
    impath = '../images/test_data'
    imname = '%s_data%s_%s.png' % (state_long, data_date, str(today))
    plt.savefig(os.path.join(impath, imname), bbox_inches = 'tight')


#%% Show info on hospitalizations and deaths

if plot_hosp_death:
    
    impath = '../images/ihme_compare'
    imname = '%s_data%s_project%s_%s.png' % (state_long, data_date, project_date, str(today))
    
    lightblue = [0.3, 0.3, 0.8]
    darkblue = [0.2, 0.2, 0.6]
    fig, ax = plt.subplots(2, 2, figsize = (12, 6))
    ax = ax.flatten()
    
    
    ax[0].plot(dates, hosp, 'o', label = 'Reported', 
               color = darkblue, markerfacecolor = lightblue)
    ax[0].plot(dates_ihme, hosp_ihme_m, 'k-', label = 'IHME Projected [Mean]')
    ax[0].plot(dates_ihme, hosp_ihme_l, 'r--', label = 'IHME Projected [Lower CI]')
    ax[0].plot(dates_ihme, hosp_ihme_u, 'r--', label = 'IHME Projected [Upper CI]')
    
    ax[0].set_xlim(0, date_inds_ihme[-1])
    ax[0].set_xticks(xticks)
    ax[0].set_xticklabels(xticklabels)
    ax[0].legend()
    ax[0].set_ylabel('Total Hospitalized', fontsize = 12, fontweight = 'bold')
    ax[0].set_title('Hospitalizations', fontsize = 12, fontweight = 'bold')
    
    ax[2].plot(dates, dhosp, 'o',
               color = darkblue, markerfacecolor = lightblue)
    ax[2].plot(dates_ihme, dhosp_ihme_m, 'k-')
    ax[2].plot(dates_ihme, dhosp_ihme_l, 'r--')
    ax[2].plot(dates_ihme, dhosp_ihme_u, 'r--')
    ax[2].set_xlim(0, date_inds_ihme[-1])
    ax[2].set_xticks(xticks)
    ax[2].set_xticklabels(xticklabels)
    ax[2].set_ylabel('New Hospitalized', fontsize = 12, fontweight = 'bold')
    ax[2].set_xlabel('Date', fontsize = 12, fontweight = 'bold')
    
    
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
    ax[1].set_title('Deaths', fontsize = 12, fontweight = 'bold')
    
    
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
                 (state_long, data_date, project_date), fontsize = 14, fontweight = 'bold')
    
    plt.savefig(os.path.join(impath, imname), bbox_inches = 'tight')
