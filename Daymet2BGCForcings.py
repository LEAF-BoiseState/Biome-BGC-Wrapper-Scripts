import sys
import xarray as xr
import numpy as np
from osgeo import ogr
from osgeo import osr


def main(clargs):

	# Get command line arguments and verify
	DaymetInfo = GetCommandLineArgs(clargs)

	# Convert lat/long coord to LCC x,y
	xi, yi = TransformLatLongPoint(DaymetInfo['LonPoint'],DaymetInfo['LonPoint'])

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

def GetCommandLineArgs(clargs):

	if(len(clargs)!=11):
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
		'VPFile': VPFile, 'LatPoint': LatPoint, 'LonPoint': LonPoint};

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

def GetPointTimeseries(ReadPath,ReadFile,keyVarString,xi,yi):

	Daymet_file = ReadPath+ReadFile

	ds = xr.open_dataset(Daymet_file)
	dsloc = ds.interp(x=xi, y=yi)

	Vari = dsloc[keyVarString].values
	time = dsloc['time'].values

	return time, Vari;

if __name__ == '__main__':
    main(sys.argv)

