#-------------------------------------------------------------------------------
# Name:        step 2 - map creation
# Purpose:     RMS HD comparison
#
# Author:      Eliška Vlčková // Prague Analytics Team

########### eliska.vlckova@guycarp.com
#
# Created:     11/02/2019
# Copyright:   (c) Eliška Vlčková 2019
#-------------------------------------------------------------------------------


import arcpy
from arcpy import mapping


file = open("report2.txt", "w")
mxd = mapping.MapDocument(r"C:\gc_work\evl\Automation Tool\MXDs\RMSHD_atlas.mxd")

mxd_name = mxd.filePath.split("\\")[-1]
file.write(mxd_name+"\n\n")
list_df = mapping.ListDataFrames(mxd)

for df in list_df:
    num_lyr = len(mapping.ListLayers(mxd, "", df))
    file.write(df.name+ ": " + str(num_lyr) + " layers\nn")
    for lyr in mapping.ListLayers(mxd, "", df):
       file.write(df.name + " + " + lyr.name + "\n")
       ext = lyr.getExtent()

       if lyr.isFeatureLayer:
        file.write(lyr.name + " VECTOR\n ")
        file.write((str(((str(ext)).split(" ")[0:4]))) + " \n")
        file.write(lyr.dataSource + " \n\n")
       else:
        file.write(lyr.name + " RASTR\n ")
        file.write(" does not have extent  \n ")
        file.write(lyr.dataSource + " \n\n")
file.close()
##for feature in arcpy.ListFeatureClasses():
##    if feature.startswith('MBCity'):
##        CityID_City = feature.split('_')[1]
##        print(CityID_City)
##    if feature.startswith('MBBuilding'):
##        CityID_Building = feature.split('_')[1]
##        print(CityID_Building)
##    if feature.startswith('MBFlooded'):
##        CityID_Flooded = feature.split('_')[1]
##        print(CityID_Flooded)
##    if str(CityID_City) == str(CityID_Building) and str(CityID_City) == str(CityID_Flooded):
##        print(str(feature))

