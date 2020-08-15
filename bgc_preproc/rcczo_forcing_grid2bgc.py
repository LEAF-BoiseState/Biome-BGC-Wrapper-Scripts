import yaml
import xarray as xr
import numpy as np
import pandas as pd
import WriteBGCForcing

with open('config.yml','r') as f:
	doc = yaml.load(f)


rc_metdata_path = doc['rcczo_metdata']['rcczo_metdata']
print(rc_metdata_path)