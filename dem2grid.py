#!/usr/bin/env python
"""
    Convert GDAL supported single band DEM file to SARnbox grid format
    (c) Zoltan Siki siki.zoltan@epito.bme.hu
    GPL 2

    Usage:
        python dem2grid.py [-o DZ] [-s SZ] input.dem [output.grid]
        or
        dem2grid.py [-o DZ] [-s SZ] input.dem [output.grid]

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
import struct
import argparse
import osgeo.gdal as gd
from gdalconst import GA_ReadOnly, GDT_Byte, GDT_UInt16, GDT_Int16, \
     GDT_UInt32, GDT_Int32, GDT_Float32, GDT_Float64

# GDAL data types to packt data_types
gd_type = {GDT_Byte:    "b",
           GDT_UInt16:  "H",
           GDT_Int16:   "h",
           GDT_UInt32:  "I",
           GDT_Int32:   "i",
           GDT_Float32: "f",
           GDT_Float64: "d"}
# check command line parameters
parser = argparse.ArgumentParser()
parser.add_argument("ifilename", type=str, help="input DEM file")
parser.add_argument("ofilename", nargs="?", type=str, \
    help="output grid file, optional", default="")
parser.add_argument("-o", "--offset", type=float, help="z offset", default=0.0)
parser.add_argument("-s", "--scale", type=float, help="z scale", default=1.0)
args = parser.parse_args()

# generate output file name if not given on the command line
if len(args.ofilename) == 0:
    args.ofilename = os.path.splitext(args.ifilename)[0] + ".grid"
# use gdal to read DEM file
idataset = gd.Open(args.ifilename, GA_ReadOnly)
if idataset is None:
    print("Cannot read input file {}".format(args.ifilename))
    sys.exit(2)
# get size of dem
cols = idataset.RasterXSize
rows = idataset.RasterYSize
# get and calculate coordinate limits
tr = idataset.GetGeoTransform()
xul = tr[0]
yul = tr[3]
xlr = xul + cols * tr[1]
ylr = yul + rows * tr[5]
print "ul %.2f %.2f" % (tr[0], tr[3])
print "lr %.2f %.2f" % (xlr, ylr)
print "px %.2f %.2f" % (tr[1], tr[5])
print "cr %d %d" % (cols, rows)
# write data to binary output
of = open(args.ofilename, "wb")
of.write(struct.pack("2i", cols, rows))
of.write(struct.pack("4f", xul, ylr, xlr, yul))
band = idataset.GetRasterBand(1)
d = band.ReadRaster(0, 0, cols, rows, cols, rows, band.DataType)
data = [(x + args.offset) * args.scale \
    for x in struct.unpack(gd_type[band.DataType] * (rows * cols), d)]
#print(band.DataType)
#print(len(data))
#print(type(data))
#print(data)
of.write(struct.pack("f" * (cols * rows), *data))
of.close()
