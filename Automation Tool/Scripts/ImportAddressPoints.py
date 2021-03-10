#!/usr/local/bin/python

# -*- coding: windows-1250 -*-

import arcpy
from arcpy import env
import os, csv, sys



arcpy.env.overwriteOutput = True
arcpy.env.workspace =r"C:\\gc_work\\evl\DATA\\address_points"
workspace= r"C:\\gc_work\\evl\DATA\\address_points"

arcpy.env.overwriteOutput = True

spatialref = arcpy.SpatialReference(5514) 

#arcpy.env.workspace = arcpy.GetParameterAsText(0)


try:
    for csv_file in arcpy.ListFiles("*.csv"):
        path = workspace + "\\" + csv_file
        outfc = csv_file.split(".")[0] + ".shp"
        print outfc
        
        arcpy.CreateFeatureclass_management(workspace, outfc, "POINT", None, None, None, spatialref)
        cursor = arcpy.InsertCursor(outfc,["SHAPE@XY"]) # Create InsertCursor.
        
        with open(path, 'r') as f:
            reader = csv.reader(f, delimiter=';')
            headers = reader.next() # Read the first line as the header names.
            print len(headers)
            for line in reader:
                if len(line[16]) > 2:
                    feature = cursor.newRow()                
                    point = arcpy.CreateObject("Point")
                    xcoord = ((float(line[16]))*(-1))
                    ycoord = ((float(line[17]))*(-1))
                    point.X = xcoord
                    point.Y = ycoord
                        
                    feature.shape = point
                    cursor.insertRow(feature)
                else:
                    pass

    shplist = arcpy.ListFeatureClasses("*.shp")   
    arcpy.Merge_management(shplist, r"C:\\gc_work\\evl\DATA\\address_points\\mergedXYFIN.shp")
    
except ValueError, e:
    print "error", e, "on line", line, "in csv", csv_file,

 

    
