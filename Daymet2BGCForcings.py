import sys
import xarray as xr
import numpy as np
from osgeo import ogr
from osgeo import osr


def main(clargs):

	# Get command line arguments and verify
	GetCommandLineArgs(clargs)

	# Convert lat/long coord to LCC x,y
	xi, yi = TransformLatLongPoint()

	# Get precip
	GetPointTimeseries(ReadPath,ReadFile,'prcp',xi,yi)

	# Get tmin

	# Get tmax

	# Get srad

	# Get vp

	# Get dayl

	# Concatenate and write to ouput



def GetCommandLineArgs(clargs):

	if(len(sys.argv)!=11):
		print("Usage: "+sys.argv[0]+" <Daymet Path> <>")

	ReadPath  = sys.argv[1]
	PrcpFile  = sys.argv[2]
	TmaxFile  = sys.argv[3]
	TminFile  = sys.argv[4]
	SradFile  = sys.argv[5]
	VPFile    = sys.argv[6]

	WritePath = sys.argv[7]
	WriteFile = sys.argv[8]

	LatPoint  = float(sys.argv[9])
	LonPoint  = float(sys.argv[10])

	return;

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


if __name__ == '__main__':
    main(sys.argv)

