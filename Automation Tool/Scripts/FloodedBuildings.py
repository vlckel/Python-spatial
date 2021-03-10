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


arcpy.env.workspace = r"C:/gc_work/evl/Data/Belgium/RMS_HD.gdb"
mxd =  map.MapDocument(r"C:/gc_work/evl/MXDs/RMSHD_atlas.mxd")
arcpy.env.overwriteOutput = True

####VARIABLES####
floodmodel = "RMS HD Flood Hazard 2" #user input flood model
cityTitle = "Belgium"
returnperiod = "100 years"
coordinatesystem = "Belge 1972 / Belgian Lambert 72 (EPSG: 31370)"
cellsize = "100 x 100 m"
cityfield = "CRESTA_DES"


try:

    if arcpy.Exists (arcpy.env.workspace):
            arcpy.AddMessage("GDb exists")
            df = map.ListDataFrames(mxd, "Layers")[0]

            #### input symbology layers ####
            BuildingSymbology = "C:/gc_work/evl/LYRs/buildings_belgium.lyr"
            FishnetSymbology = "C:/gc_work/evl/LYRs/fishnet_belgium.lyr"
            CitySymbology = "C:/gc_work/evl/LYRs/city.lyr"


            BuildingFCs = arcpy.ListFeatureClasses("MBBuilding*")
            FishnetFCs =  arcpy.ListFeatureClasses("MBFishnet*")
            CityFCs =  arcpy.ListFeatureClasses("MBCity*")


            for Bfc in BuildingFCs:
                BfcID = str(Bfc.split("_")[1])
##                BfcOfficial = str(Bfc.split("_")[2])
                for Ffc in FishnetFCs:
                    FfcID = str(Ffc.split("_")[1])
                    for Cfc in CityFCs:
                        CfcID = str(Cfc.split("_")[1])
                        if BfcID == FfcID and BfcID == CfcID:
                            InputBuildingLayer_temp = map.Layer(Ffc)
                            InputFishnetLayer_temp = map.Layer(Bfc)
                            InputCityLayer_temp = map.Layer(Cfc)


                            map.AddLayer(df, InputCityLayer_temp, "TOP")
                            map.AddLayer(df, InputBuildingLayer_temp, "TOP")
                            map.AddLayer(df, InputFishnetLayer_temp, "TOP")


                            BuildingLayer = map.ListLayers(mxd, "", df)[0]
                            FishnetLayer = map.ListLayers(mxd, "", df)[1]
                            CityLayer = map.ListLayers(mxd, "", df)[2]


                            arcpy.ApplySymbologyFromLayer_management(BuildingLayer, "C:/gc_work/evl/LYRs/buildings_belgium.lyr")
                            arcpy.ApplySymbologyFromLayer_management(FishnetLayer, "C:/gc_work/evl/LYRs/fishnet_belgium.lyr")
                            arcpy.ApplySymbologyFromLayer_management(CityLayer, "C:/gc_work/evl/LYRs/city.lyr")

                            df.extent = BuildingLayer.getExtent()



                            ##search cityname - search cursor#
                            SC = arcpy.SearchCursor(CityLayer, fields=cityfield)
                            for row in SC:
                                name = row.getValue(cityfield)
                            del row, SC




                            ########change the layout elements ########
                            #title
                            for elm in (map.ListLayoutElements(mxd)):
                                if elm.name == "Title":
                                    elm.text = str("FLOODED BUILDINGS IN " + name + " (" + cityTitle + ")")
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


                            styleItem = arcpy.mapping.ListStyleItems("USER_STYLE", "Legend Items", "EVLStyle")[0]
                            legend = arcpy.mapping.ListLayoutElements(mxd, "LEGEND_ELEMENT")[0]
                            legend.elementPositionX = 9.4683
                            legend.elementPositionY = 4.9
                            for item in legend.listLegendItemLayers():
##                                legend.updateItem(item, styleItem)
                                legend.updateItem(item, styleItem, show_feature_count=True)
                                if item.name == str(Cfc):
                                    print("FOUNF IT")
                                    legend.removeItem(item)
                                if item.name == str(Bfc):
                                    print("BLABLA")
                                    legend.updateItem(item,styleItem, show_feature_count = True)

                            BuildingLayer.name = "Open Street map building"
                            FishnetLayer.name = "Number of flooded buildings"
                            InputBuildingLayer_temp.name = "Open Street map building"
                            InputFishnetLayer_temp.name = "Number of flooded buildings"

                            #Refresh TOC and ActiveView
                            arcpy.RefreshActiveView()
                            arcpy.RefreshTOC()

                            map.ExportToPDF(mxd, r"C:/gc_work/evl/Outputs/" + floodmodel + "_" + name + ".pdf")

                            map.RemoveLayer(df, InputBuildingLayer_temp)
                            map.RemoveLayer(df, InputFishnetLayer_temp)
                            map.RemoveLayer(df, InputCityLayer_temp)
                            map.RemoveLayer(df, BuildingLayer)
                            map.RemoveLayer(df, FishnetLayer)
                            map.RemoveLayer(df, CityLayer)

                            #mxd.save()
                            del InputBuildingLayer_temp, InputFishnetLayer_temp, BuildingLayer, FishnetLayer, CityLayer, InputCityLayer_temp
                        del Cfc
                    del Ffc
                del Bfc
            del mxd
    else:
        print("GDB Does not exists")
        arcpy.AddMessage("GDB Does not exists")

except arcpy.ExecuteError:
    arcpy.AddError(arcpy.GetMessages(2))
