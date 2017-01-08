#!/usr/bin/env python
"""
    Convert USGS ASCII DEM file to SARnbox grid format
    (c) Zoltan Siki siki.zoltan@epito.bme.hu
    GPL 2

    Usage:
        python grid2dem.py input.grid [output.dem]
        or
        grid2dem.py input.grid [output.dem]

    Input file is a SARndbox binary grid file, you can create it from SARndbox
    (Save Bathimetry) or several open source software can be used e.g. QGIS.
    Output file name is optional, default is the name of the input file.
    Output format is USGS ASCII DEM

    Notes:
    GDAL driver cannot direcly create USGSDEM file, only create copy available
    so a GTiff is created first, than a copy created
    DGAL USGSDEM driver supports int16 values only, so values are converted to int
    SRS for GTiff must be set for copycreate, we use UTM
"""

import sys
import os
import osgeo.gdal
import osgeo.osr
from gdalconst import *
import struct
import numpy as np

# check command line parameters
if len(sys.argv) <= 1:
    print("Usage: grid2dem.py input.grid [output.dem]")
    #sys.exit(1)
    ifilename = "../SARndbox-2.3/bin/LakeTahoe.grid"
else:
    ifilename = sys.argv[1]
# generate output file name if not given on the command line
if len(sys.argv) > 2:
    ofilename = sys.argv[2]
else:
    ofilename = os.path.splitext(ifilename)[0] + ".dem"
tmpfilename = os.path.splitext(ifilename)[0] + ".tif"
# check if input file available
if not os.path.isfile(ifilename):
    print("input file not found")
    sys.exit(2)
ifile = open(ifilename, "rb")
idataset = ifile.read()
(cols, rows) = struct.unpack("2i", idataset[:8])
(xul, ylr, xlr, yul) = struct.unpack("4f", idataset[8:24])
psize = (xlr - xul) / cols
# truncate data to int for gdal USGSDEM driver
data = [int(d) for d in struct.unpack("f" * (rows * cols), idataset[24:])]
# create temperary geotif
driver = osgeo.gdal.GetDriverByName("GTiff")
if driver is None:
    print("Cannot get GTiff driver")
    sys.exit(3)
odataset = driver.Create(tmpfilename, cols, rows, 1, GDT_Int16)
if odataset is None:
    print("Cannot create output GDAL dataset")
    sys.exit(4)
odataset.SetGeoTransform((xul, psize, 0, yul, 0, -psize))
# set spatial reference system to (false) UTM
srs = osgeo.osr.SpatialReference()
srs.SetUTM( 11, 1 )
srs.SetWellKnownGeogCS( 'NAD27' )
odataset.SetProjection( srs.ExportToWkt() )
odataset.GetRasterBand(1).WriteArray(np.array(data, dtype=np.int16).reshape((rows, cols)))
odataset.FlushCache()
odataset = None
# make a copy of tif to dem
src_ds = osgeo.gdal.Open(tmpfilename)
driver = osgeo.gdal.GetDriverByName("USGSDEM")
if driver is None:
    print("Cannot get USGSDEM driver")
    sys.exit(4)
dst_ds = driver.CreateCopy(ofilename, src_ds, 0 )
src_ds = None
dst_ds = None
# remove temperary geotif file
os.remove(tmpfilename)
