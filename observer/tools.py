"""
tools.py

Created by Daniel Magee on 2008-01-29.
Copyright (c) 2008 UCO/Lick Observatory. All rights reserved.
"""

import ephem as E
import numpy as N
from datetime import datetime
from time import strftime
from pytz import timezone


class Target:
    """Class for astronomical targets"""
    def __init__(self, name, ra, dec, epoch=2000.0):
        self.name = name
        self.ra = ra
        self.dec = dec
        self.epoch = epoch
        # Create an instance of a PyEphem body for the target
        self.targetdb = '%s,f|A,%s,%s,0.0,%s' % (name, ra, dec, epoch)
        self.target = E.readdb(self.targetdb)

class Almanac:
    def __init__(self, site_info, date):
        """Computes an astronomical almanac for a given site and date"""
        self.site_info = site_info
        self.site = site_info.observer()
        self.localdate = date
        self.ltz = timezone(self.site_info.timezone)
        self.utc = timezone('UTC')
        self.date = self.local2utc(date)
        self.site.date = self.date
        self.horizon = self.site.horizon
        self.horizon12 = -1.0*E.degrees('12:00:00.0')
        self.horizon18 = -1.0*E.degrees('18:00:00.0')
        self.sun = E.Sun()
        self.moon = E.Moon()
        self.sun.compute(self.site)
        self.moon.compute(self.site)

    def sunset(self):
        """Sunset in UTC"""
        self.site.horizon = self.horizon
        self.site.date = self.date
        return self.site.next_setting(self.sun)

    def sunrise(self):
        """Sunrise in UTC"""
        self.site.horizon = self.horizon
        self.site.date = self.date
        return self.site.next_rising(self.sun)
        
    def evening_twilight_12(self):
        """Evening 12 degree (nautical) twilight in UTC"""
        self.site.horizon = self.horizon12
        self.site.date = self.date
        return self.site.next_setting(self.sun)

    def evening_twilight_18(self):
        """Evening 18 degree (civil) twilight"""
        self.site.horizon = self.horizon18
        self.site.date = self.date
        return self.site.next_setting(self.sun)

    def morning_twilight_12(self):
        """Morning 12 degree (nautical) twilight in UTC"""
        self.site.horizon = self.horizon12
        self.site.date = self.date
        return self.site.next_rising(self.sun)

    def morning_twilight_18(self):
        """Morning 18 degree (civil) twilight in UTC"""
        self.site.horizon = self.horizon18
        self.site.date = self.date
        return self.site.next_rising(self.sun)

    def sun_set_rise_times(self, local=False):
        """Sunset, sunrise and twilight times. Returns a tuple with (sunset, 12d, 18d, 18d, 12d, sunrise).
        Default times in UTC. If local=True returns times in local timezone"""
        if local:
            rstimes =  (self.utc2local(self.sunset()),
                        self.utc2local(self.evening_twilight_12()),
                        self.utc2local(self.evening_twilight_18()), 
                        self.utc2local(self.morning_twilight_18()),
                        self.utc2local(self.morning_twilight_12()),
                        self.utc2local(self.sunrise()))
        else:
            rstimes =  (self.sunset(),
                        self.evening_twilight_12(),
                        self.evening_twilight_18(), 
                        self.morning_twilight_18(),
                        self.morning_twilight_12(),
                        self.sunrise())
        return rstimes

    def moon_rise(self):
        """Moon rise time in UTC"""
        self.site.date = self.date
        moonrise = self.site.next_rising(self.moon)
        if moonrise < self.sunset():
            None
        return moonrise

    def moon_set(self):
        """Moon set time in UTC"""
        self.site.date = self.date
        moonset = self.site.next_setting(self.moon)
        if moonset > self.sunrise():
            moonset = None
        return moonset
    
    def moon_phase(self):
        """Moon percentage of illumination"""
        self.site.date = self.date
        return self.moon.moon_phase

    def night_center(self):
        """Compute night center"""
        return (self.sunset() + self.sunrise())/2.0
            
    def local2utc(self, date):
        """Convert local time to UTC"""
        y, m, d = date.split('/')
        tlocal = datetime(int(y), int(m), int(d), 12, 0, 0, tzinfo=self.ltz)
        return E.Date(tlocal.astimezone(self.utc))
        
    def utc2local(self, date_time):
        """Convert UTC to local time"""
        if date_time != None:
            dt = date_time.datetime()
            utc_dt = datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond, tzinfo=self.utc)
            return E.Date(utc_dt.astimezone(self.ltz))
        else:
            return None
    
    def __repr__(self):
        text = ''
        text += 'Almanac for the night of %s\n' % str(self.date).split()[0]
        text += '\nEvening\n'
        text += '_'*30 + '\n'
        rst = self.sun_set_rise_times(local=True)
        rst = [t.datetime().strftime('%H:%M') for t in rst]
        text += 'Sunset: %s\n12d: %s\n18d: %s\n' % (rst[0], rst[1], rst[2])
        text += '\nMorning\n'
        text += '_'*30 + '\n'
        text += '18d: %s\n12d: %s\nSunrise: %s\n' % (rst[3], rst[4], rst[5])
        return text

class Airmass:
    def __init__(self, almanac, target, time_interval=5):
        """Compute the airmass of a target given an almanac and a target object."""
        self.almanac = almanac
        self.target = target.target
        self.time_interval = time_interval*E.minute
        self.utc = []
        self.local = []
        self.lmst = []
        self.hour_angle = []
        self.airmass = []
        self.parallactic_angle = []
        self.moon_altitude = []
        self.compute()

    def GMST(self, date):
        """Compute Greenwich Mean Sidereal Time"""
        jd = E.julian_date(date)
        T = (jd - 2451545.0)/36525.0
        gmstdeg = 280.46061837+(360.98564736629*(jd-2451545.0))+(0.000387933*T*T)-(T*T*T/38710000.0)
        gmst = E.degrees(gmstdeg*N.pi/180.0)
        return gmst
    
    def LMST(self, date, longitude):
        """Compute Local Mean Sidereal Time"""
        gmst = self.GMST(date)
        lmst = E.degrees(gmst + longitude)
        return lmst.norm
    
    def HA(self, lmst, ra):
        """Compute Hour Angle"""
        return lmst - ra 
    
    def parallactic(self, dec, ha, lat, az):
        """Compute parallactic angle"""
        if N.cos(dec) != 0.0:
            sinp = -1.0*N.sin(az)*N.cos(lat)/N.cos(dec)
            cosp = -1.0*N.cos(az)*N.cos(ha)-N.sin(az)*N.sin(ha)*N.sin(lat)
            parang = E.degrees(N.arctan2(sinp, cosp))
        else:
            if lat > 0.0:
                parang = N.pi
            else:
                parang = 0.0
        return parang

    def secz(self, alt):
        """Compute airmass"""
        if alt < E.degrees('03:00:00'):
            alt = E.degrees('03:00:00')
        sz = 1.0/N.sin(alt) - 1.0
        xp = 1.0 + sz*(0.9981833 - sz*(0.002875 + 0.0008083*sz))
        return xp
    
    def moon_alt(self, site):
        """Compute Moon altitude"""
        moon = E.Moon()
        moon.compute(site)
        return moon.alt
        
    def compute(self):
        """Compute the Local Mean Sideral Time, Hour Angle, Parallactic Angle and Airmass for a target from sunrise to sunset"""
        t_range = self._set_data_range(self.almanac.sunset(), self.almanac.sunrise(), self.time_interval)
        for t in t_range:
            self.almanac.site.date = t
            self.target.compute(self.almanac.site)
            lst = self.LMST(t, self.almanac.site.long)
            self.lmst.append(lst)
            ha = self.HA(lst, self.target.ra)
            self.hour_angle.append(ha)
            pang = self.parallactic(float(self.target.dec), float(ha), float(self.almanac.site.lat), float(self.target.az))
            self.parallactic_angle.append(pang)
            am = self.secz(float(self.target.alt))
            self.airmass.append(am)
            lt = self.almanac.utc2local(self.almanac.site.date)
            m_alt = self.moon_alt(self.almanac.site)
            self.moon_altitude.append(m_alt)
            self.local.append(lt)
            self.utc.append(self.almanac.site.date)

    def __repr__(self):
        """Prints a table of hourly airmass data"""
        text = ''
        format = '%-16s  %-5s  %-5s  %-5s  %-5s  %-5s %-5s\n'
        header = ('Date       Local', 'UTC', 'LMST', 'HA', 'PA', 'AM', 'Moon')
        hstr = format % header
        text += hstr
        text += '_'*len(hstr) + '\n'
        for i, lt in enumerate(self.local):
            s_lt = lt.datetime().strftime('%d%b%Y  %H:%M')
            s_utc = self.utc[i].datetime().strftime('%H:%M')
            s_ha = ':'.join(str(E.hours(self.hour_angle[i])).split(':')[:2])
            s_lst = ':'.join(str(E.hours(self.lmst[i])).split(':')[:2])
            s_pa = round(self.parallactic_angle[i]*180.0/N.pi, 1)
            s_am = round(self.airmass[i], 2)
            s_ma = round(self.moon_altitude[i]*180.0/N.pi, 1)
            if s_ma < 0:
                s_ma = ''
            s_data = format % (s_lt, s_utc, s_lst, s_ha, s_pa, s_am, s_ma)
            text += s_data
        return text

    def _set_data_range(self, sunset, sunrise, tint):
        """Returns numpy array of dates 15 minutes before sunset and after sunrise."""
        ss = self._set_time(E.Date(sunset - 15*E.minute))
        sr = self._set_time(E.Date(sunrise + 15*E.minute))
        return N.arange(ss, sr, tint)
    
    def _set_time(self, dtime):
        """Sets time to nice rounded value"""
        y, m ,d, hh, mm, ss = dtime.tuple()
        mm = mm - (mm % 5)
        return E.Date(datetime(y, m , d, hh, mm, 5, 0))