#!/usr/bin/env python
"""
    Convert GDAL supported single band DEM file to SARnbox grid format
    (c) Zoltan Siki siki.zoltan@epito.bme.hu
    GPL 2

    Usage:
        python dem2grid.py input.dem [output.grid]
        or
        dem2grid.py input.dem [output.grid]

    Input file is a GDAL suported DEM file, you can create it from SARndbox
    (Save Bathimetry) or several open source software can be used e.g. QGIS.
    Output file name is optional, default is the name of the input file.
    Some supported input data formats:
        Name                              Extension
        GTiff (GeoTiff single band)       tif
        USGSDEM (USGS DEM)                dem
        GRASSASCIIGrid (GRASS ASCII GRID) arx
        AAIGrid (ESRI ASCII GRID)         asc
        ...
"""
import sys
import os
import osgeo.gdal as gd
from gdalconst import GA_ReadOnly, GDT_Byte, GDT_UInt16, GDT_Int16, \
     GDT_UInt32, GDT_Int32, GDT_Float32, GDT_Float64
import struct

# GDAL data types to packt data_types
gd_type = {GDT_Byte:    "b",
           GDT_UInt16:  "H",
           GDT_Int16:   "h",
           GDT_UInt32:  "I",
           GDT_Int32:   "i",
           GDT_Float32: "f",
           GDT_Float64: "d"}
# check command line parameters
if len(sys.argv) <= 1:
    print("Usage: dem2grid.py input.dem [output.grid]")
    #sys.exit(1)
    ifilename = "../SARndbox-2.3/bin/test.asc"
else:
    ifilename = sys.argv[1]
# generate output file name if not given on the command line
if len(sys.argv) > 2:
    ofilename = sys.argv[2]
else:
    ofilename = os.path.splitext(ifilename)[0] + ".grid"
# use gdal to read DEM file
idataset = gd.Open(ifilename, GA_ReadOnly)
if idataset is None:
    print("Cannot read input file {}".format(ifilename));
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
d = band.ReadRaster(0, 0, cols, rows, cols, rows, band.DataType)
data = struct.unpack(gd_type[band.DataType] * (rows * cols), d)
print(band.DataType)
print(len(data))
print(type(data))
print(data)
of.write(struct.pack("f" * (cols * rows), *data))
of.close()
