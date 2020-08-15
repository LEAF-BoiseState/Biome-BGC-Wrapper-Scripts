#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 28 19:37:04 2019

@author: lejoflores
"""

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from osgeo import ogr
from osgeo import osr
import scipy.interpolate

Daymet_path = '/Users/lejoflores/data/daymet/'
Daymet_name = 'tmax_1980-2018.nc'
Daymet_file = Daymet_path + Daymet_name

# Coordinates of Wyoming Big Sage site
lati = 43.167545
loni = -116.713205

InSR = osr.SpatialReference()
InSR.ImportFromEPSG(4326)       # WGS84/Geographic
OutSR = osr.SpatialReference()
OutSR.ImportFromEPSG(102009)     # WGS84 UTM Zone 56 South

OutSR.SetProjParm("Central_Meridian", -100.0)
OutSR.SetProjParm("Latitude_Of_Origin", 42.5)
OutSR.SetProjParm("Standard_Parallel_1", 25.0)
OutSR.SetProjParm("Standard_Parallel_2", 60.0)

Point = ogr.Geometry(ogr.wkbPoint)
Point.AddPoint(loni,lati)             # use your coordinates here
Point.AssignSpatialReference(InSR)    # tell the point what coordinates it's in
Point.TransformTo(OutSR)              # project it to the out spatial reference

yi = Point.GetY()
xi = Point.GetX()

ds = xr.open_dataset(Daymet_file)

dsloc = ds.sel(x=xi, y=yi, method='nearest')



Tmax = dsloc['tmax'].values
time = dsloc['time'].values

plt.figure(figsize=(16,10))
plt.plot(time, Tmax)
plt.title('Daily Maximum Air Temperature at Wyoming Big Sage Site from Daymet')
plt.xlabel('Time')
plt.ylabel('$T_{max} {}^{\circ}C$')
plt.show()

