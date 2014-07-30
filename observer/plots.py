"""
plots.py

Created by Daniel Magee on 2008-01-29.
Copyright (c) 2008 UCO/Lick Observatory. All rights reserved.
"""

import matplotlib as M
import pylab as PL
import matplotlib.dates as MD
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from pytz import timezone
from datetime import datetime, timedelta
import ephem as E
import numpy as N

def limits(am, t, limit, direction):
    ai = N.argsort(N.abs(am - limit))[:2]
    amin = N.argmin(am)
    if t[ai[0]] > t[amin]:
        w_ai = ai[0]
        e_ai = ai[1]
    else:
        w_ai = ai[1]
        e_ai = ai[0]
    if direction == 'e':
        am[t>t[w_ai]] = 99.0
    else:
        am[t<t[e_ai]] = 99.0
    return am
        

def do_plot_airmass(observer, figure, **kw):
    obs = observer
    almanac = obs.almanac_data
    site = almanac.site_info
    airmass = obs.airmass_data
    M.rcParams['timezone'] = 'UTC'
    #local_tz = MD.timezone(site.timezone)
    local_tz = timezone(site.timezone)
    
    # set major ticks to hours in local time
    majorTick = MD.HourLocator(tz=local_tz)
    majorFmt = PL.DateFormatter('%Hh')
    # set minor ticks to 15 min intervals
    minorTick = MD.MinuteLocator(range(0,59,15), tz=local_tz)

    figure.clf()
    #ax1 = PL.subplot(111)
    ax1 = figure.add_subplot(111)
    
    #ax = PL.subplot(211)
    #ax.plot_date(dates, y, tz=local_tz)
    colors = ['r', 'b', 'g', 'c', 'm', 'y']
    lstyle = '-'
    lt_data = [t.datetime() for t in airmass[0].local]
    for i, am in enumerate(airmass):
        am_data = N.array(am.airmass)
        am_min = N.argmin(am_data)
        am_data_dots = am_data
        if 'telescope' in kw:
            if kw['telescope'] != None:
                tdots = N.array(airmass[0].local)
                if kw['telescope'] == 'keck1':
                    alimit = 1/N.sin(33.3*(N.pi/180.0)) # Keck 1 limits west
                    am_data_dots = limits(am_data, tdots, alimit, direction='w')
                if kw['telescope'] == 'keck2':
                    alimit = 1/N.sin(36.8*(N.pi/180.0)) # Keck 2 limits east
                    am_data_dots = limits(am_data, tdots, alimit, direction='e')
        color = colors[i % len(colors)]
        lc = color + lstyle
        # ax1.plot_date(lt_data, am_data, lc, linewidth=1.0, alpha=0.3, aa=True, tz=local_tz)
        # xs, ys = M.mlab.poly_between(lt_data, 2.02, am_data)
        # ax1.fill(xs, ys, facecolor=colors[i], alpha=0.2)
        lstyle = 'o'
        lc = color + lstyle
        ax1.plot_date(lt_data, am_data_dots, lc, aa=True, tz=local_tz)
        # plot object label
        targname = am.target.name
        ax1.text(MD.date2num(lt_data[am_data.argmin()]), am_data.min() + 0.08, targname.upper(), color=color, ha='center', va='center')
    ax1.set_ylim(2.02, 0.98)
    #PL.ylim(0.98, 2.02)
    #PL.xlim(lt_data[0], lt_data[-1])
    ax1.set_xlim(lt_data[0], lt_data[-1])
    ax1.xaxis.set_major_locator(majorTick)
    ax1.xaxis.set_minor_locator(minorTick)
    ax1.xaxis.set_major_formatter(majorFmt)
    labels = ax1.get_xticklabels()
    ax1.grid(True, color='#999999')
    title = 'Airmass for the night of %s' % str(almanac.localdate).split()[0]
    ax1.set_title(title)
    ax1.set_xlabel(site.tzname)
    ax1.set_ylabel('Airmass')
    #PL.setp(labels,'rotation', 45)
    #ax = PL.subplot(212)
    #PL.show()
    ax2 = ax1.twinx()
    moon_data = N.array(airmass[0].moon_altitude)*180/N.pi
    moon_illum = almanac.moon_phase()
    ax2.plot_date(lt_data, moon_data, '#666666', linewidth=2.0, alpha=0.5, aa=True, tz=local_tz)
    mxs, mys = M.mlab.poly_between(lt_data, 0, moon_data)
    # ax2.fill(mxs, mys, facecolor='#666666', alpha=moon_illum)
    ax2.set_ylabel('Moon Altitude (deg)', color='#666666')
    ax2.set_ylim(0, 90)
    ax2.set_xlim(lt_data[0], lt_data[-1])
    ax2.xaxis.set_major_locator(majorTick)
    ax2.xaxis.set_minor_locator(minorTick)
    ax2.xaxis.set_major_formatter(majorFmt)
    ax2.set_xlabel('')
    ax2.yaxis.tick_right()


def plot_airmass(observer, output, **kw):
    figure = M.figure.Figure()
    canvas = FigureCanvas(figure)
    do_plot_airmass(observer, figure, **kw)
    figure.savefig(output)
    
