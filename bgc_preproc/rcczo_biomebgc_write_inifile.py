import yaml
import xarray as xr
import numpy as np
import pandas as pd
import re


template_path = '../biomebgc_run/ini/'
template_name = 'template.ini'

output_path = template_path
output_name = 'test_mod.ini'

soil_depth = 1.0

with open(template_path+template_name,'r') as infile:
	text = infile.read()
	text = re.sub('SOILDEPTH','{:<9.2f}'.format(soil_depth),text)

	with open(output_path+output_name,'w') as outfile:
		outfile.seek(0)
		outfile.write(text)
		outfile.truncate()
		outfile.close()

	infile.close()


