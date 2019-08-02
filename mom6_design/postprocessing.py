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


# Padding missing values
def pad_ice_model(ds):
    """pad the stupid masked out values in the restart files"""
    def fill_missing(data, fillval):
        return data.where(data<1e36).fillna(fillval)
    
    ds = ds.copy()
    # Special treatmeant for the first class of `part_size`. There the fill value should be 1
    part_size_1 = fill_missing(ds.part_size.isel(zaxis_1=0),1)
    
    ds_padded = fill_missing(ds, 0)
    
    temp = xr.concat([part_size_1, ds_padded.part_size.isel(zaxis_1=slice(1,None))], dim='zaxis_1')
    ds_padded['part_size'] = temp
    return ds_padded

def transpose_like_ref(ds, ref):
    """MOM6 needs the varaible data to have the exact same axes as befoer"""
    ds = ds.copy()
    ref = ref.copy()
    ds_trans = ds.copy()
    for dvar in ds.data_vars:
        ds_trans[dvar] = ds_trans[dvar].transpose(*ref[dvar].dims)
    return ds_trans