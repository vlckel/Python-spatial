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

# encoding=utf8


import arcpy, os, sys
from arcpy import mapping as map
reload(sys)
sys.setdefaultencoding('utf8')


arcpy.env.workspace = r"C:/gc_work/evl/Data/Belgium/Outputs.gdb"
mxd =  map.MapDocument(r"C:/gc_work/evl/MXDs/RMSHD_atlas_bel2.mxd")
arcpy.env.overwriteOutput = True

####VARIABLES####
floodmodel = "RMS HD and National Belgium Official " #user input flood model
cityTitle = "Belgium"
returnperiod = "100 years"
coordinatesystem = "Belge 1972 / Belgian Lambert 72 (EPSG: 31370)"
cellsize = "100 x 100 m"
cityfield = "CRESTA_DES"


try:

    if arcpy.Exists (arcpy.env.workspace):
            arcpy.AddMessage("GDb exists")
            df = map.ListDataFrames(mxd, "Layers")[0]

            FCs = arcpy.ListFeatureClasses()
            BuildingFCs = arcpy.ListFeatureClasses("official_MBBuilding*")
            OfficialFishnetFCs =  arcpy.ListFeatureClasses("official_MBFishnet*")
            RMSHDFishnetFCs = arcpy.ListFeatureClasses("rmshd_MBFishnet*")
            CityFCs =  arcpy.ListFeatureClasses("rmshd_MBCity*")

##            for Bfc, Officialfc, RMSHDfc, Cfc in FCs:
##                pass


            for Bfc in BuildingFCs:
                BfcID = str(Bfc.split("_")[2])
                for Officialfc in OfficialFishnetFCs:
                    OfficialfcID = str(Officialfc.split("_")[2])
                    for RMSHDfc in RMSHDFishnetFCs:
                        RMSHDfcID = str(RMSHDfc.split("_")[2])
                        for Cfc in CityFCs:
                            CfcID = str(Cfc.split("_")[2])


                            if BfcID == OfficialfcID and BfcID == RMSHDfcID and BfcID == CfcID:

##                                arcpy.AddMessage("City Code" + BfcID + OfficialFfcID + RMSHDFfcID)

                                InputBuildingLayer_temp = map.Layer(Bfc)
                                InputOfficialFishnetLayer_temp = map.Layer(Officialfc)
                                InputRMSHDFishnetLayer_temp = map.Layer(RMSHDfc)
                                InputCityLayer_temp = map.Layer(Cfc)


                                map.AddLayer(df, InputCityLayer_temp, "TOP")
                                map.AddLayer(df, InputOfficialFishnetLayer_temp, "TOP")
                                map.AddLayer(df, InputBuildingLayer_temp, "TOP")
                                map.AddLayer(df, InputRMSHDFishnetLayer_temp, "TOP")





                                RMSHDFishnetLayer = map.ListLayers(mxd, "", df)[0]
                                BuildingLayer = map.ListLayers(mxd, "", df)[1]
                                OfficialFishnetLayer = map.ListLayers(mxd, "", df)[2]
                                CityLayer = map.ListLayers(mxd, "", df)[3]


                                arcpy.ApplySymbologyFromLayer_management(BuildingLayer, "C:/gc_work/evl/LYRs/belgium/buildings.lyr")
                                arcpy.ApplySymbologyFromLayer_management(RMSHDFishnetLayer, "C:/gc_work/evl/LYRs/belgium/rmshd_fishnet.lyr")
                                arcpy.ApplySymbologyFromLayer_management(OfficialFishnetLayer, "C:/gc_work/evl/LYRs/belgium/official_fishnet.lyr")
                                arcpy.ApplySymbologyFromLayer_management(CityLayer, "C:/gc_work/evl/LYRs/city.lyr")


                                df.extent = BuildingLayer.getExtent()

                                BuildingLayer.name = "Open Street Map buildings"
                                RMSHDFishnetLayer.name = "RMSHD"
                                OfficialFishnetLayer.name = "Official"


                                ##search cityname - search cursor#
                                SC = arcpy.SearchCursor(CityLayer, fields="CRESTA_DES")
                                for row in SC:
                                    name = row.getValue("CRESTA_DES")
                                del row, SC




                                ########change the layout elements ########
                                #title
                                for elm in (map.ListLayoutElements(mxd)):
                                    if elm.name == "Title":
                                        elm.text = str("FLOODED BUILDINGS IN ") + name + (" IN ") + cityTitle
                                        elm.elementPositionX = 0.1
                                        elm.elementPositionY = 7.7656
                                    if elm.name == "Subtitle":
                                        elm.text = str("Model provided by " +  floodmodel)
                                        elm.elementPositionX = 0.22
                                        elm.elementPositionY = 7.3252
                                    if elm.name == "returnperiod":
                                        elm.text = str("Return period: " +  returnperiod)
                                        elm.elementPositionX = 0.22
                                        elm.elementPositionY = 7.0664
                                    if elm.name == "coordinatesystem":
                                        elm.text = str("Coordinate system: " +  coordinatesystem)
                                        elm.elementPositionX = 0.22
                                        elm.elementPositionY = 0.3454
                                    if elm.name == "cellsize":
                                        elm.text = str("Fishnet cell size: " +  cellsize)
                                        elm.elementPositionX = 0.22
                                        elm.elementPositionY = 0.0797

                                legend = arcpy.mapping.ListLayoutElements(mxd, "LEGEND_ELEMENT")[0]
                                styleItem = arcpy.mapping.ListStyleItems("USER_STYLE", "Legend Items","EVLStyle")[0]
                                legend.elementPositionX = 9.4683
                                legend.elementPositionY = 4.9
                                for item in legend.listLegendItemLayers():
                                    legend.updateItem(item, styleItem, show_feature_count=True)
##                                    if item.name == str(Cfc):
##                                       legend.removeItem(item)
##                                    if item.name == str(Officialfc) or item.name == str(RMSHDfc):
##                                        legend.updateItem(item, show_feature_count = True)

                                #Refresh TOC and ActiveView
                                arcpy.RefreshActiveView()
                                arcpy.RefreshTOC()

                                map.ExportToPDF(mxd, r"C:/gc_work/evl/Outputs/" + floodmodel + "_" + name + ".pdf")

                                map.RemoveLayer(df, InputBuildingLayer_temp)
                                map.RemoveLayer(df, InputRMSHDFishnetLayer_temp)
                                map.RemoveLayer(df, InputOfficialFishnetLayer_temp)
                                map.RemoveLayer(df, InputCityLayer_temp)
                                map.RemoveLayer(df, BuildingLayer)
                                map.RemoveLayer(df, RMSHDFishnetLayer)
                                map.RemoveLayer(df, OfficialFishnetLayer)
                                map.RemoveLayer(df, CityLayer)

##                    mxd.save()

                                del InputBuildingLayer_temp, InputRMSHDFishnetLayer_temp,InputOfficialFishnetLayer_temp, InputCityLayer_temp
                                del BuildingLayer, RMSHDFishnetLayer, OfficialFishnetLayer, CityLayer
                        del Cfc
                    del RMSHDfc
                del Officialfc
            del Bfc

##                    del mxd
    else:
        print("GDB Does not exists")
        arcpy.AddMessage("GDB Does not exists")

except arcpy.ExecuteError:
    arcpy.AddError(arcpy.GetMessages(2))
