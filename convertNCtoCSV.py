from netCDF4 import Dataset
import numpy as np

nc_file = 'DAYMET_v4-Daily_Average_Snow_Water_Equivalent_of_Snowpack-Continental_North_America-2021.nc'
fh = Dataset(nc_file, mode='r')

print(fh.__dict__)

for dim in fh.dimensions.values():
    print(dim)

for var in fh.variables.values():
    print(var)
