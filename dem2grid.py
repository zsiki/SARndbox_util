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
parser.add_argument("-i", "--info", action='store_true', \
    help="info about input DEMfile")
parser.add_argument("ifilename", type=str, help="input DEM file")
parser.add_argument("ofilename", nargs="?", type=str, \
    help="output grid file, optional", default="")
parser.add_argument("-o", "--offset", type=float, help="z offset", default=0.0)
parser.add_argument("-s", "--scale", type=float, help="z scale", default=1.0)
args = parser.parse_args()
print args
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
n = rows * cols
# get and calculate coordinate limits
tr = idataset.GetGeoTransform()
xul = tr[0]
yul = tr[3]
xlr = xul + cols * tr[1]
ylr = yul + rows * tr[5]
#print "ul %.2f %.2f" % (tr[0], tr[3])
#print "lr %.2f %.2f" % (xlr, ylr)
#print "px %.2f %.2f" % (tr[1], tr[5])
#print "cr %d %d" % (cols, rows)
band = idataset.GetRasterBand(1)
d = band.ReadRaster(0, 0, cols, rows, cols, rows, band.DataType)
noData = band.GetNoDataValue()
# copy data to list
data = [ x for x in struct.unpack(gd_type[band.DataType] * n, d)]
# calculate avarege of not nodata elements
w = [i for i in data if i != noData]
avg = sum(w) / len(w)
if args.info:
    print "rows: {:d}".format(rows)
    print "cols: {:d}".format(cols)
    print "type: {:d}".format(band.DataType)
    print "nodata: {:.2f} {:d}".format(noData, n-len(w))
    print "extent: {:.2f}, {:.2f}, {:.2f}, {:.2f}".format(xul, yul, xlr, ylr)
    print "min z: {:.2f}".format(min(w))
    print "max z: {:.2f}".format(max(w))
    print "avg z: {:.2f}".format(avg)
    exit(0)
# transform z values
res = [0] * n
for i in range(n):
    x = 0 if data[i] == noData else data[i] - avg
    res[i] = x * args.scale + args.offset
# write data to binary output
of = open(args.ofilename, "wb")
of.write(struct.pack("2i", cols, rows))
of.write(struct.pack("4f", xul, ylr, xlr, yul))
of.write(struct.pack("f" * n, *res))
of.close()
