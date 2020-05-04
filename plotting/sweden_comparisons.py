# -*- coding: utf-8 -*-
"""

Compare Sweden to various US states

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
import matplotlib.colors as colors
from datetime import date


from read_data import get_data_c19, format_date_c19, get_data_ctrack



# Class-based method for reading/tracking/formatting data associated with a country
class country_data:
    
    def __init__(self, name, population, datafile):
        """
        Create country and load data per COVID-19 Tracker. Enter
        population in millions.
        """
        
        self.name = name
        self.population = population
        self.datafile = datafile
        self.death, dates = get_data_c19(name, datafile)
        self.dates = [format_date_c19(s) for s in dates]
        
        self.n_death = None
        self.trim_death = None
        self.trim_dates = None
        self.trim_days = None
        
    def trim_to_first(self, n_death):
        """
        Trims dataset to start from day with first N deaths. Saves results
        to trim_death, trim_dates, and trim_days properties.
        """
        
        self.n_death = n_death
        try:
            start_ind = np.where(self.death >= n_death)[0][0]
        except IndexError:
            start_ind = -1
        self.trim_death = self.death[start_ind:]
        self.trim_dates = self.dates[start_ind:]
        self.trim_days = np.arange(len(self.trim_death))
        
    def plot_trim(self, ax = None, dark_lines = False, label = False, **kwargs):
        """
        Plots trimmed and normalized (per million) on an optionally supplied
        axis.
        """
        
        if ax is None:
            fig, ax = plt.subplots(1, 1)
            
        if label is False:
#            display_date = '%s-%s' % (self.trim_dates[0][5], self.trim_dates[0][6:])
            label = '%s [Pop %.1fM]' % (self.name, self.population)
        g = ax.plot(self.trim_days, self.trim_death/self.population, 
                label = label, **kwargs)
        
        if dark_lines:
            color = colors.to_rgb(g[0].get_color())
            print(color)
            g[0].set_color([0.5*c for c in color])
            g[0].set_markerfacecolor(color)
            
    def plot_dtrim(self, ax = None, dark_lines = False, label = False, **kwargs):
        """
        Plots trimmed and normalized new deaths per day (per million) on an 
        optionally supplied axis.
        """
        
        if ax is None:
            fig, ax = plt.subplots(1, 1)
            
        if label is False:
            label = '%s [%s]' % (self.name, self.trim_dates[0])
        g = ax.plot(self.trim_days, np.diff(self.trim_death, prepend = 0)/self.population, 
                label = label, **kwargs)
        
        if dark_lines:
            color = colors.to_rgb(g[0].get_color())
            print(color)
            g[0].set_color([0.5*c for c in color])
            g[0].set_markerfacecolor(color)
        
class state_data(country_data):

    def __init__(self, name, population, datafile):
        """
        Create country and load data per COVID-19 Tracker. Enter
        population in millions.
        """
        
        self.name = name
        self.population = population
        self.datafile = datafile
        data = get_data_ctrack(name, datafile)
        self.death = data['death']
        self.dates = data['date']
        
        self.n_death = None
        self.trim_death = None
        self.trim_dates = None
        self.trim_days = None
    
    
        
        
country_pops = {'Denmark': 5.6,
                'Norway': 5.4,
                'Netherlands': 17.3,
                'United Kingdom': 66.7,
                'France': 67.,
                'Italy': 60.4,
                'Spain': 47.,
                'Sweden': 10.2,
                'Germany': 83.02,
                'Finland': 5.52,
                'US': 328.2,
                'Belgium': 11.46,
                'Canada': 37.59}

state_pops = {'CA': 39.51,
              'TX': 28.99,
              'FL': 21.48,
              'NY': 20.2,
              'PA': 12.8,
              'IL': 12.67,
              'OH': 11.69,
              'GA': 10.62,
              'NC': 10.49,
              'MI': 9.9,
              'NJ': 8.88,
              'VA': 8.54,
              'WA': 7.61,
              'AZ': 7.28,
              'MA': 6.95,
              'TN': 6.83,
              'IN': 6.72,
              'MO': 6.14,
              'MD': 6.05,
              'WI': 5.82,
              'CO': 5.76,
              'MN': 5.64,
              'SC': 5.45,
              'AL': 4.90,
              'LA': 4.65,
              'KY': 4.47,
              'OR': 4.22,
              'OK': 3.96,
              'CT': 3.57,
              'UT': 3.2,
              'IA': 3.16,
              'NV': 3.08,
              'AR': 3.02,
              'MS': 2.98,
              'KS': 2.91,
              'NM': 2.10,
              'NE': 1.93,
              'WV': 1.76,
              'ID': 1.79,
              'HI': 1.42,
              'NH': 1.36,
              'ME': 1.34,
              'MT': 1.01,
              'RI': 1.06,
              'DE': 0.97,
              'SD': 0.88,
              'ND': 0.76,
              'AK': 0.73,
              'DC': 0.71,
              'VT': 0.62,
              'WY': 0.78}


# Load data for Sweden
datapath = r'..\data\COVID-19\csse_covid_19_data\csse_covid_19_time_series'
dataname = 'time_series_covid19_deaths_global.csv'
country_filename = os.path.join(datapath, dataname)
state_filename = r'..\data\covid19_tracker\states-daily_20200429.csv'
state_data_date = '29 April'
country_data_date = '1 May'
n_death = 10


sweden = country_data('Sweden', country_pops['Sweden'], country_filename)
sweden.trim_to_first(n_death)




# Make lists of countries, populations, and plot styles
countries = ['Denmark', 'United Kingdom', 'Spain', 'Italy', 'Germany', 'Sweden']
highlight_countries = {'Canada': {'color': 'r', 'linestyle': '-'},
                    'United Kingdom': {'color': 'b', 'linestyle': '-'},
                    'US': {'color': 'k', 'linestyle': '-.'},
                    'Italy': {'color': 'r', 'linestyle': '--'},
                    'Netherlands': {'color': 'b', 'linestyle': '--'},
                    'Sweden': {'color': 'k', 'linestyle': '--'}}

# States to plot and their styles
highlight_states = {'NY': {'color': 'r', 'linestyle': '-'},
                    'WA': {'color': 'b', 'linestyle': '-'},
                    'CA': {'color': 'k', 'linestyle': '-'},
                    'WI': {'color': 'r', 'linestyle': '--'},
                    'GA': {'color': 'b', 'linestyle': '--'},
                    'FL': {'color': 'k', 'linestyle': '--'}}


state_objs = list()
for state in highlight_states.keys():
    cdata = state_data(state, state_pops[state], state_filename)
    cdata.trim_to_first(n_death)
    state_objs.append(cdata)
state_obj_dict = {s.name: s for s in state_objs}


country_objs = list()
for country in highlight_countries.keys():
    cdata = country_data(country, country_pops[country], country_filename)
    cdata.trim_to_first(n_death)
    country_objs.append(cdata)
country_obj_dict = {s.name: s for s in country_objs}

#%%

xl = [0, 70]
yl = [0, 1000]


fig, ax = plt.subplots(1, 2, figsize = (12, 6))
for cdata in state_objs:
    cdata.plot_trim(ax[0], linewidth = 2, **highlight_states[cdata.name])
ax[0].legend()


for cdata in country_objs:
    cdata.plot_trim(ax[1], **highlight_countries[cdata.name])
ax[1].legend()


ax[0].set_xlim(xl)
ax[1].set_xlim(xl)
ax[0].set_ylim(yl)
ax[1].set_ylim(yl)
ax[0].grid()
ax[1].grid()

ax[0].set_ylabel('Covid-19 Attributed Deaths Per Million', fontsize = 12, fontweight = 'bold')
ax[0].set_xlabel('Days Since 10 Deaths', fontsize = 12, fontweight = 'bold')
ax[1].set_xlabel('Days Since 10 Deaths', fontsize = 12, fontweight = 'bold')
plt.suptitle('Population-Adjusted Covid-19 Deaths vs. Days Since 10 Deaths\n' + 
             'US Data per Covid Tracking Project [%s]; European Data per COVID-19 Github [%s]' % (state_data_date, country_data_date),
             fontsize = 12, fontweight = 'bold')

figname = '../images/pop_comparisons_us%s_europe%s.png' % (state_data_date, country_data_date)
plt.savefig(figname, bbox_inches = 'tight')
#ax.set_title('Sweden vs. US States; Population-Adjusted Fatalities [State Data %s; Swedish Data %s]\n%i of 50 States Have Exceed %i Deaths' 
#             % (state_data_date, country_data_date, states_over_n, n_death),
#             fontsize = 13,
#             fontweight = 'bold')
#
#plt.tight_layout()

