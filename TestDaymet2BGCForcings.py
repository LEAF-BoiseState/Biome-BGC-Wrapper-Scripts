import os

DateRange  = '_1980-2018'
FileExt    = '.nc'

cmdName    = 'Daymet2BGCForcings.py'

ReadPath   = '/Users/lejoflores/data/daymet/'
PrcpFile   = 'prcp' + DateRange + FileExt
TmaxFile   = 'tmax' + DateRange + FileExt
TminFile   = 'tmin' + DateRange + FileExt
SradFile   = 'srad' + DateRange + FileExt
DaylFile   = 'dayl' + DateRange + FileExt
VPFile     = 'vp' + DateRange + FileExt
WritePath  = './'
WriteFile  = 'tmp.met'
LatPoint   = 43.167545
LonPoint   = -116.713205

cmdOpts    = ReadPath + ' '  + PrcpFile + ' ' + TmaxFile + ' ' + TminFile + ' ' + SradFile + \
	' ' + DaylFile + ' ' + VPFile + ' ' + WritePath + ' ' + WriteFile + ' ' + str(LatPoint) + \
	' ' + str(LonPoint)

print(cmdName + ' ' + cmdOpts)
os.system('python ' + cmdName + ' ' + cmdOpts)

