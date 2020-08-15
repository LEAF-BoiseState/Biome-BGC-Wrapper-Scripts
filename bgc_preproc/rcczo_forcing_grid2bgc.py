import yaml
import xarray as xr
import numpy as np
import pandas as pd
import WriteBGCForcing


def get_rcmet_dataarray(rcmetpath,rcmetbase,start_date,end_date,x_rcczo,y_rcczo):

	ds_get = xr.open_mfdataset(rcmetpath+rcmetbase+'*.nc',combine='by_coords')

	da_get_pt = ds_get.sel(x=x_rcczo, y=y_rcczo, method='nearest')
	da_get_pt = da_get_pt.sel(time = slice(start_date, end_date))
	da_get_pt = da_get_pt.sel(time =~ ((da_get_pt.time.dt.month==2)&(da_get_pt.time.dt.day==29)))

	ds_get.close()

	return da_get_pt;

def get_vpd(tmean, rh):
    # Calculate saturation vapor pressure based on mean daily temperature
    esat = (0.61078*1000.0) * np.exp((17.269*tmean)/(237.3 + tmean)) # In Pa

    # Calculate VPD based on esat and relative humidity
    VPD = esat*(1.0 - rh)

    return VPD;

def get_daylength(lat,lon,dates):
	# 1. Calculate the current Julian day
	n = (dates - np.datetime64('2000-01-01 12:00:00')) / np.timedelta64(1,'D')

	# 2. Calculate mean solar noon in Julian days
	Jstar = n - lon / 360.0

	# 3. Calculate the solar mean anomaly in degrees and radians
	Mdeg = (357.5291 + 0.98560028*Jstar) % 360.0
	Mrad = Mdeg*np.pi/180.0

	# 4. Calculate the equation of the center in degrees and radians
	Cdeg = (1.9148*np.sin(Mrad) + 0.0200*np.sin(2*Mrad) + 0.0003*np.sin(3*Mrad))
	Crad = Cdeg*np.pi/180.0

	# 5. Calculate the ecliptic longitude in degrees and radians
	lambdadeg = ((Mdeg + Cdeg + 180.0 + 102.9372) % 360.0)
	lambdarad = lambdadeg*np.pi/180.0

	# 6. Calculate the solar transit in Julian days
	Jtransit = 2451545.0 + Jstar + 0.0053*np.sin(Mrad) - 0.0069*np.sin(2*lambdarad)

	# 7. Calculate the declination of the Sun
	sindelta = np.sin(lambdarad) * np.sin(23.44*np.pi/180.0)

	# 8. Calculate the hour angle
	cosomega0 = (np.sin(-0.83*np.pi/180.0) - np.sin(lat*np.pi/180.0)*sindelta) \
	        / (np.cos(lat*np.pi/180.0)*np.cos(np.arcsin(sindelta)))

	# 9a. Calculate the sunrise time in Julian days
	Jrise = Jtransit - (np.arccos(cosomega0)*180.0/np.pi) / 360.0

	# 9b. Calculate the sunset time in Julian days
	Jset = Jtransit + (np.arccos(cosomega0)*180.0/np.pi) / 360.0

	# 10. Calculate the day length in days and convert to seconds
	daylen = (Jset - Jrise)*24.0*3600.0

	return daylen;

with open('config.yml','r') as file:
	myinp = yaml.full_load(file)

# Set the relative path to the Reynolds Creek meteorological data daily summary files
rc_metdata_path = myinp['rcczo_metdata']['rcmetpath']
print('\n\n\tReading met data from path... '+rc_metdata_path)

# Set the start and end dates for which to create the data. 
# NOTE: The Kormos et al. dataset is written in files containing a single water year.
# A water year extends from 01 October to 30 September of the following calendar year.
start_date = myinp['bgcsim_dates']['start_date']
end_date = myinp['bgcsim_dates']['end_date']
print('\n\n\tFor the period from '+start_date+' to '+end_date)

# Point to select: Using Reynolds Mountain East CORE site for example
x_rcczo_pt = myinp['bgcsim_points']['x_rcczo_pt']
y_rcczo_pt = myinp['bgcsim_points']['y_rcczo_pt']
print('\n\n\tAt point x = '+str(x_rcczo_pt)+', y = '+str(y_rcczo_pt))

# Set the path and name of the output meteorological file
bgc_out_path  = myinp['bgcsim_metdata']['bgcsim_metpath']
bgc_out_fname = myinp['bgcsim_metdata']['bgcsim_metname']
print('\n\n\tWriting met data to path and file '+bgc_out_path+bgc_out_fname)
print('\n\n')

tmax_fname_base = myinp['rcczo_metdata']['tmaxbase']
tmin_fname_base = myinp['rcczo_metdata']['tminbase']
tmean_fname_base = myinp['rcczo_metdata']['tmeanbase']
prcp_fname_base = myinp['rcczo_metdata']['prcpbase']
rh_fname_base = myinp['rcczo_metdata']['rhbase']
srad_fname_base = myinp['rcczo_metdata']['sradbase']

da_tmax_pt  = get_rcmet_dataarray(rc_metdata_path,tmax_fname_base,start_date,end_date,x_rcczo_pt,y_rcczo_pt)
da_tmin_pt  = get_rcmet_dataarray(rc_metdata_path,tmin_fname_base,start_date,end_date,x_rcczo_pt,y_rcczo_pt)
da_tmean_pt = get_rcmet_dataarray(rc_metdata_path,tmean_fname_base,start_date,end_date,x_rcczo_pt,y_rcczo_pt)
da_prcp_pt  = get_rcmet_dataarray(rc_metdata_path,prcp_fname_base,start_date,end_date,x_rcczo_pt,y_rcczo_pt)
da_rh_pt    = get_rcmet_dataarray(rc_metdata_path,rh_fname_base,start_date,end_date,x_rcczo_pt,y_rcczo_pt)
da_srad_pt  = get_rcmet_dataarray(rc_metdata_path,srad_fname_base,start_date,end_date,x_rcczo_pt,y_rcczo_pt)

tmax  = da_tmax_pt['TMAX'].values # Daily maximum temperature [°C]
tmin  = da_tmin_pt['TMIN'].values # Daily minimum temperature [°C]
tmean = da_tmean_pt['TMEAN'].values # Daily mean temperature [°C]
prcp  = da_prcp_pt['precipitation_amount'].values # Daily total precipitation [mm]
rh    = da_rh_pt['relative_humidity'].values # Daily mean relative humidity [0-1]
srad  = da_srad_pt['net_solar'].values # Daily mean solar radiation [W/m^2]

dates = da_tmax_pt.time.values # Get the dates in a datetime64 array

VPD = get_vpd(tmean,rh)

daylen = get_daylength(da_tmax_pt.lat.values[()],da_tmax_pt.lon.values[()],dates)

year  = pd.to_datetime(dates).year.values # Get the year associated with each record
yday  = pd.to_datetime(dates).dayofyear.values # Get the day of year associated with each record

mm_to_cm = 0.1 # Used to convert precipitation data from native mm to cm as required by Biome-BGC

OutArray = np.column_stack((year,yday,tmax,tmin,tmean,mm_to_cm*prcp,VPD,srad,daylen))

WriteBGCForcing.WriteBGCForcing(bgc_out_path,bgc_out_fname,OutArray)


