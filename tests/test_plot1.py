import observer
obs = observer.Observer('subaru')
hudf = obs.target('HUDF', '3 32 39.0', '-27 47 29.1')
ms1054 = obs.target('MS1054', '10 56 59.99', '-03 37 36.0')
cl1256 = obs.target('CL1256', '12 55 33.76', '01 04 3.72')
obs.almanac('2010/01/12')
obs.airmass(hudf, ms1054, cl1256)
observer.plots.plot_airmass(obs, None)

