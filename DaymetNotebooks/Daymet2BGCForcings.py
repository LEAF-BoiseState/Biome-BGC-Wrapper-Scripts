import sys
import xarray as xr
import numpy as np
import pandas as pd
from osgeo import ogr
from osgeo import osr

#==================================================================================#
#                                                                                  #
##
#                                                                                  #
#==================================================================================#
def main(clargs):

	# Get command line arguments and verify
	DaymetInfo = GetCommandLineArgs(clargs)

	# Convert lat/long coord to LCC x,y
	xi, yi = TransformLatLongPoint(DaymetInfo['LonPoint'],DaymetInfo['LatPoint'])

	# This part could be parallelized:

	# Get precip
	time_prcp, prcp = GetPointTimeseries(DaymetInfo['ReadPath'],DaymetInfo['PrcpFile'],'prcp',xi,yi)

	# Get tmax
	time_tmax, tmax = GetPointTimeseries(DaymetInfo['ReadPath'],DaymetInfo['TmaxFile'],'tmax',xi,yi)

	# Get tmin
	time_tmin, tmin = GetPointTimeseries(DaymetInfo['ReadPath'],DaymetInfo['TminFile'],'tmin',xi,yi)

	# Get srad
	time_srad, srad = GetPointTimeseries(DaymetInfo['ReadPath'],DaymetInfo['SradFile'],'srad',xi,yi)

	# Get dayl
	time_dayl, dayl = GetPointTimeseries(DaymetInfo['ReadPath'],DaymetInfo['DaylFile'],'dayl',xi,yi)

	# Get vp
	time_vp, vp     = GetPointTimeseries(DaymetInfo['ReadPath'],DaymetInfo['VPFile'],'vp',xi,yi)

	# Concatenate and write to ouput
	DaymetDataPoint = {'prcp': prcp, 'tmax': tmax, 'tmin': tmin, 'srad': srad, 'dayl': dayl, 'vp': vp }
	DaymetTimePoint = {'time_prcp': time_prcp, 'time_tmax': time_tmax, 'time_tmin': time_tmin, \
		'time_srad': time_srad, 'time_dayl': time_dayl, 'time_vp': time_vp }
	
	WriteBGCForcing(DaymetInfo['WritePath'],DaymetInfo['WriteFile'],DaymetTimePoint,DaymetDataPoint)

	return;

#==================================================================================#
#                                                                                  #
##
#                                                                                  #
#==================================================================================#
def GetCommandLineArgs(clargs):

	if(len(clargs)!=12):
		print("\nUSAGE: "+clargs[0]+" <Daymet Path> <prcp file name>")
		print("\t<tmax file name> <tmin file name> <srad file name>")
		print("\t<dayl file name> <vp file name> <write path> <write file>")
		print("\t<point lat> <point lon>\n")
		print("<prcp file name> = Daymet precipitation netCDF file name")
		print("<tmax file name> = Daymet maximum temperature netCDF file name")
		print("<tmin file name> = Daymet minimum temperature netCDF file name")
		print("<srad file name> = Daymet solar radiation netCDF file name")
		print("<dayl file name> = Daymet day length netCDF file name")
		print("<vp file name>   = Daymet vapor pressure netCDF file name")
		print("<write path>     = Output file write path")
		print("<write file>     = Output file write name")
		print("<point lat>      = Latitude of point to interpolate to")
		print("<point lon>      = Longitude of point to interpolate to\n")
		print("Exiting...\n")
		exit(1)


	ReadPath  = clargs[1]
	PrcpFile  = clargs[2]
	TmaxFile  = clargs[3]
	TminFile  = clargs[4]
	SradFile  = clargs[5]
	DaylFile  = clargs[6]
	VPFile    = clargs[7]
	WritePath = clargs[8]
	WriteFile = clargs[9]

	LatPoint  = float(clargs[10])
	LonPoint  = float(clargs[11])

	return {'ReadPath': ReadPath, 'PrcpFile': PrcpFile, 'TmaxFile': TmaxFile, \
		'TminFile': TminFile, 'SradFile': SradFile, 'DaylFile': DaylFile, \
		'VPFile': VPFile, 'WritePath': WritePath, 'WriteFile': WriteFile, \
		'LatPoint': LatPoint, 'LonPoint': LonPoint};

#==================================================================================#
#                                                                                  #
##
#                                                                                  #
#==================================================================================#
def TransformLatLongPoint(LonPoint,LatPoint):
	InSR = osr.SpatialReference()
	InSR.ImportFromEPSG(4326) # WGS84/Geographic
	OutSR = osr.SpatialReference()
	OutSR.ImportFromEPSG(102009) # Lambert Conformal Conic North America 

	# Note: these parameters have to be set because they are different from the default values
	OutSR.SetProjParm("Central_Meridian", -100.0)
	OutSR.SetProjParm("Latitude_Of_Origin", 42.5)
	OutSR.SetProjParm("Standard_Parallel_1", 25.0)
	OutSR.SetProjParm("Standard_Parallel_2", 60.0)

	Point = ogr.Geometry(ogr.wkbPoint)
	Point.AddPoint(LonPoint,LatPoint) 
	Point.AssignSpatialReference(InSR) # Specify the spatial reference of the input Lat/long coords
	Point.TransformTo(OutSR) # Now transform it to projected coordinates 

	# Get the projected x and y coordinates 
	yi = Point.GetY()
	xi = Point.GetX()

	return xi, yi;
#==================================================================================#
#                                                                                  #
##
#                                                                                  #
#==================================================================================#
def GetPointTimeseries(ReadPath,ReadFile,keyVarString,xi,yi):

	Daymet_file = ReadPath+ReadFile

	ds = xr.open_dataset(Daymet_file)
	dsloc = ds.interp(x=xi, y=yi)

	Vari = dsloc[keyVarString].values
	time = dsloc['time'].values

	return time, Vari;

	# print("ReadPath     = " + ReadPath)
	# print("ReadFile     = " + ReadFile)
	# print("keyVarString = " + keyVarString)
	# print("LonPoint     = " + str(xi))
	# print("LatPoint     = " + str(yi))
#==================================================================================#
#                                                                                  #
##
#                                                                                  #
#==================================================================================#
def WriteBGCForcing(WritePath,WriteFile,DaymetTimePoint,DaymetDataPoint):

	header1 = '{:>6}'.format('year') + \
			  '{:>6}'.format('yday') + \
              '{:>8}'.format('Tmax') + \
              '{:>8}'.format('Tmin') + \
              '{:>8}'.format('Tday') + \
              '{:>8}'.format('prcp') + \
              '{:>9}'.format('VPD') + \
              '{:>9}'.format('srad') + \
              '{:>8}'.format('daylen') + '\n'

	header2 = '{:>6}'.format('') + \
			  '{:>6}'.format('') + \
              '{:>8}'.format('(deg C)') + \
              '{:>8}'.format('(deg C)') + \
              '{:>8}'.format('(deg C)') + \
              '{:>8}'.format('(cm)') + \
              '{:>9}'.format('(Pa)') + \
              '{:>9}'.format('(W m-2)') + \
              '{:>8}'.format('(s)')
              
	pntfmt = ['%6d','%6d','%8.2f','%8.2f','%8.2f','%8.2f','%9.2f','%9.2f','%8d']

    # Extract year and day of year
	time2 = pd.to_datetime(DaymetTimePoint['time_prcp'])
	year  = time2.year
	yday  = time2.dayofyear

	print(DaymetDataPoint['tmax'].shape)

	OutArray = np.column_stack((year,yday,DaymetDataPoint['tmax'],DaymetDataPoint['tmin'],\
    	((DaymetDataPoint['tmax']+DaymetDataPoint['tmin'])/2),DaymetDataPoint['prcp'],\
    	DaymetDataPoint['vp'],DaymetDataPoint['srad'],DaymetDataPoint['dayl']))

	np.savetxt(WritePath+WriteFile,OutArray,fmt=pntfmt,header=header1+header2,comments='',delimiter='')

	return;
#==================================================================================#
#                                                                                  #
##
#                                                                                  #
#==================================================================================#
if __name__ == '__main__':

    main(sys.argv)
    print("Writing of BGC forcing file complete...\n")

