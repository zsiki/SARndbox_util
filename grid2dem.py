#!/usr/bin/env python
"""
    Convert SARnbox grid format to GDAL supported format
    (c) Zoltan Siki siki.zoltan@epito.bme.hu
    GPL 2

    Usage:
        python grid2dem.py input.grid [output.dem]
        or
        grid2dem.py input.grid [output.dem]

    Input file is a SARndbox binary grid file.
    Output file name is optional, default is the name of the input file.
    default output format is GTiff (if no output file given).
    
    Supported output data formats:
        Name                              Extension
        GTiff (GeoTiff single band)       tif
        USGSDEM (USGS DEM)                dem (integer values only)
        GRASSASCIIGrid (GRASS ASCII GRID) arx
        AAIGrid (ESRI ASCII GRID)         asc

    Notes:
    GDAL driver cannot direcly create USGSDEM file, only create copy available
    so a GTiff is created first, than a copy created
    DGAL USGSDEM driver supports int16 values only, so values are converted to int
    SRS for GTiff must be set for copycreate, we use UTM (false)  
"""

import sys
import os
import osgeo.gdal
import osgeo.osr
from gdalconst import GDT_Int16, GDT_Float32
import struct
import numpy as np

# GDAL extensions to driver name
gd_driver = {".tif": "GTiff",
             ".dem": "USGSDEM",
             ".arc": "AAIGrid",
             ".arx": "GRASSASCIIGrid"}
# check command line parameters
if len(sys.argv) <= 1:
    print("Usage: grid2dem.py input.grid [output.dem]")
    #sys.exit(1)
    ifilename = "../SARndbox-2.3/bin/test.grid"
else:
    ifilename = sys.argv[1]
if os.path.splitext(ifilename)[1] != ".grid":
    print("input file must be a .grid file")
    sys.exit(2)
# generate output file name if not given on the command line
if len(sys.argv) > 2:
    ofilename = sys.argv[2]
else:
    ofilename = os.path.splitext(ifilename)[0] + ".dem"
# check output file type (extension)
oext = os.path.splitext(ofilename)[1]
if not oext in gd_driver:
    print("Unsupported output format")
    sys.exit(2)
if oext == ".dem":
    tmpext = ".tif"
    tmpfilename = os.path.splitext(ifilename)[0] + tmpext
else:
    tmpext = oext
    tmpfilename = ofilename
# check if input file available
if not os.path.isfile(ifilename):
    print("input file not found")
    sys.exit(3)
ifile = open(ifilename, "rb")   # open binary input file
idataset = ifile.read()         # read all data
(cols, rows) = struct.unpack("2i", idataset[:8])
(xul, ylr, xlr, yul) = struct.unpack("4f", idataset[8:24])
psize = (xlr - xul) / cols  # pixel size
if oext == ".dem":
    # truncate data to int for gdal USGSDEM driver
    data = [int(d) for d in struct.unpack("f" * (rows * cols), idataset[24:])]
    gd_type = GDT_Int16
    np_type = np.int16
else:
    data = struct.unpack("f" * (rows * cols), idataset[24:])    # elevations
    gd_type = GDT_Float32
    np_type = np.float32
# create output (temperary geotiff in case of dem)
driver = osgeo.gdal.GetDriverByName(gd_driver[tmpext])
if driver is None:
    print("Cannot get GDAL driver")
    sys.exit(4)
odataset = driver.Create(tmpfilename, cols, rows, 1, gd_type)
if odataset is None:
    print("Cannot create output GDAL dataset")
    sys.exit(4)
odataset.SetGeoTransform((xul, psize, 0, yul, 0, -psize))
if oext == ".dem":
    # set spatial reference system to (false) UTM
    srs = osgeo.osr.SpatialReference()
    srs.SetUTM(11, 1)
    srs.SetWellKnownGeogCS('NAD27')
    odataset.SetProjection(srs.ExportToWkt())
odataset.GetRasterBand(1).WriteArray(np.array(data, \
    dtype=np_type).reshape((rows, cols)))
odataset.FlushCache()
odataset = None
if oext == ".dem":
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
