# SARndbox_util
Simple utilities to Augmented Reality Sandbox

##dem2grid.py
Convert .dem/.tif/.arc digital elevation modell file to SARndbox
compatible .grid file. The DEM size should be not larger then 640x480.
Optional offset parameter can be used to vertically shift dem to fit SARndbox.

```
usage: dem2grid.py [-h] [-o OFFSET] ifilename [ofilename]

positional arguments:
  ifilename                   input DEM file
  ofilename                   output grid file, optional

optional arguments:
  -h, --help                  show this help message and exit
  -o OFFSET, --offset OFFSET  z offset
```

##grid2dem.py
Convert SARndbox .grid file to GDAL compatible DEM format (.tif/.asc/.dem).

```
usage: grid2dem.py [-h] ifilename [ofilename]

positional arguments:
  ifilename   input grid file
  ofilename   output DEM file, optional

optional arguments:
  -h, --help  show this help message and exit
```
