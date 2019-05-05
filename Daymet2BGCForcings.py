import sys
import xarray as xr
import numpy as np
from osgeo import ogr
from osgeo import osr


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

