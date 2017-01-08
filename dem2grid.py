#!/usr/bin/env python
"""
    Convert USGS ASCII DEM file to SARnbox grid format
    (c) Zoltan Siki siki.zoltan@epito.bme.hu
    GPL 2

    Usage:
        python dem2grid.py input.dem [output.grid]
        or
        dem2grid.py input.dem [output.grid]

    Input file is a USGS ASCII DEM file, you can create it from SARndbox
    (Save Bathimetry) or several open source software can be used e.g. QGIS.
    Output file name is optional, default is the name of the input file.
"""

import sys
import os
import osgeo.gdal
from gdalconst import *
import struct

# check command line parameters
if len(sys.argv) <= 1:
    print("Usage: dem2grid.py input.dem [output.grid]")
    sys.exit(1)
ifilename = sys.argv[1]
# generate output file name if not given on the command line
if len(sys.argv) > 2:
    ofilename = sys.argv[2]
else:
    ofilename = os.path.splitext(ifilename)[0] + ".grid"
# use gdal to read USGS DEM file
idataset = osgeo.gdal.Open(ifilename, GA_ReadOnly)
if idataset is None:
    print("Cant read input file");
    sys.exit(2)
# get size of dem
cols = idataset.RasterXSize
rows = idataset.RasterYSize
# get and calculate coordinate limits
tr = idataset.GetGeoTransform()
xul = tr[0]
yul = tr[3]
xlr = xul + (cols - 1) * tr[1] 
ylr = yul + (rows - 1) * tr[5]
# write data to binary output
of = open(ofilename, "wb")
of.write(struct.pack("2i", cols, rows))
of.write(struct.pack("4f", xul, ylr, xlr, yul))
band = idataset.GetRasterBand(1)
of.write(band.ReadRaster(0, 0, cols, rows, cols, rows, band.DataType))
of.close()
