"""
Observer package computes nightly almanacs and airmass data for
astronomical targets.

Usage:
    >>> import observer
    >>> obs = observer.Observer('keck')
    >>> hudf = obs.target('HUDF', '3 32 39.0', '-27 47 29.1')
    >>> ms1054 = obs.target('MS1054', '10 56 59.99', '-03 37 36.0')
    >>> cl1256 = obs.target('CL1256', '12 55 33.76', '01 04 3.72')
    >>> obs.almanac('2008/01/12')
    >>> obs.airmass(hudf, ms1054, cl1256)
    >>> observer.plots.plot_airmass(obs, '12Jan08_keck.png')

Created by Daniel Magee
----------------------------------------------------------------------------
"THE BEER-WARE LICENSE" (Revision 42):
<magee@ucolick.org> wrote this file. As long as you retain this notice you
can do whatever you want with this stuff. If we meet some day, and you think
this stuff is worth it, you can buy me a beer in return. Daniel K. Magee
----------------------------------------------------------------------------
"""

__all__ = ['sites', 'tools', 'plots']

import sites, tools, plots

def site_list():
    """Prints a list of site ids and names"""
    sobj = sites.Site(None)
    format = '%-12s  %-60s'
    hdr = format % ('SiteID', 'Site Name')
    print hdr
    print '_'*len(hdr)
    for s, n in sobj.sites():
        print  format % (s, n)

class Observer:
    def __init__(self, site):
        """
        A simplified interface for computing nightly almanacs and airmass data
        for targets.
        Input parameters:
            site: site_id of an astronomical observatory
        """
        self.site_info = sites.Site(site)
        self.almanac_data = None
        self.airmass_data = []
    
    def target(self, name, ra, dec, epoch=2000.0):
        """
        Returns a Target object instance.
        Input paramters:
            name:  Target Name
            ra:    Target Right Ascension coordinate
            dec:   Target Declination coordinate
            epoch: Epoch of coordinates
        """
        return tools.Target(name, ra, dec, epoch)
    
    def almanac(self, date):
        """
        Computes an nightly almanac (Sun set and rise times) for a specific date.
        Inputs paramters:
            date: Date to compute almanac in YYYY/MM/DD format.
        """
        self.almanac_data = tools.Almanac(self.site_info, date)
    
    def airmass(self, *targets):
        """
        Computes LMST, Hour Angle, Parallactic Angle, and Airmass data
        for a target/s on the date the almanac was computed.
        Input parameters:
            targets: A list of Target object instances
        """
        if self.almanac_data == None:
            raise ValueError('No almanac data exists!')
        for targ in targets:
            self.airmass_data.append(tools.Airmass(self.almanac_data, targ))