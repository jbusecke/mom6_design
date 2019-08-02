import xarray as xr
import matplotlib.pyplot as plt

# Viz
def plot_all(ds, **kwargs):
    for pvar in ds.data_vars:
        plt.figure()
        ds[pvar].plot(**kwargs)
        plt.show()
        
def plot_cut(ds):
    return ds.squeeze().isel(zaxis_1=0, zaxis_2=0, aaxis_2=0).drop('H_to_kg_m2')

# Merging restart files
def combine_mom6_restarts(file_name):
    datasets = []
    for nrange in [range(0,4), range(4,8), range(8,12), range(12,16)]:
        flist = ['%s.%04i' %(file_name, n) for n in nrange]
        ds_sub = xr.merge([xr.open_mfdataset(file) for file in flist])
        datasets.append(ds_sub)
    out = xr.merge(datasets) # not sure why I have to do these seperately to work...
    out.attrs['jb_notes'] = 'Combined using xarray by Julius Busecke. See https://github.com/jbusecke/mom6_design for details'
    return out

# Padding missing values
def transpose_like_ref(ds, ref):
    ds_trans = ds.copy()
    for dvar in ds.data_vars:
        ds_trans[dvar] = ds_trans[dvar].transpose(*ref[dvar].dims)
    return ds_trans

def fill_missing(data, fillval):
        return data.where(data<1e36).fillna(fillval)


def pad_ice_model(ds):
    """pad the stupid masked out values in the restart files"""
    
    ds = ds.copy()
    
    ds_padded = fill_missing(ds, 0)
        
    # Special treatmeant for the first class of `part_size`. There the fill value should be 1
    part_size_1 = fill_missing(ds.part_size.isel(zaxis_1=0),1)
    temp = xr.concat([part_size_1, ds_padded.part_size.isel(zaxis_1=slice(1,None))], dim='zaxis_1')
    ds_padded['part_size'] = temp
    ds_padded = transpose_like_ref(ds_padded, ds)
    return ds_padded