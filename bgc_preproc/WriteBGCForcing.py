import numpy as np

#==================================================================================#
#                                                                                  #
##
#                                                                                  #
#==================================================================================#
def WriteBGCForcing(WritePath,WriteFile,OutArray):

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

	np.savetxt(WritePath+WriteFile,OutArray,fmt=pntfmt,header=header1+header2,comments='',delimiter='')

	return;
#==================================================================================#
#                                                                                  #
##
#                                                                                  #
#==================================================================================#