"""
Script:    SplitLayerByAttributes.py
Path:      F:\A0_Main\
Author:    Dan.Patterson@carleton.ca
Created:   2005-06-23
Modified:  2015-06-05  (last change date)
Purpose:
  Converts each shape in a feature class to a separate shapefile
Requires:
Notes:
References:
Script:
Toolbox Properties (right-click on the tool and specify the following)
General
  Name   SplitLayerByAttributes
  Label  Split Layer By Attributes
  Desc   Splits a layer according to attributes within the selected field producing
         a separate shapefile for common attributes.
Source script SplitLayerByAttributes.py
Parameter list          Parameter Properties
          Display Name         Data type        Type      Direction  MultiValue
  argv[1]  Input feature class  Feature Layer    Required  Input      No
  argv[2]  Field to query       Field            Required  Input      No
  argv[3]  File basename        String           Optional  Input      No
  argv[4]  Output folder        Folder           Required  Input      No
"""
#--------------------------------------------------------------------
#Import the standard modules and the geoprocessor
#
import os
import sys
import arcpy

#Get the input feature class, optional fields and the output filename
input_FC = sys.argv[1]
inField = sys.argv[2]
theFName = sys.argv[3]
outFolder = sys.argv[4]

script = sys.argv[0]
msg = "\nRunning: ... {}".format(script)
arcpy.AddMessage(msg)
  
arcpy.env.overwriteOutput = True
desc = arcpy.Describe

shp_type = desc(input_FC).ShapeType
FullName = desc(input_FC).CatalogPath
thePath = (os.path.split(FullName)[0]).replace("\\","/")
if theFName != "#":
  theFName = theFName.replace(" ","_")
else:
  theFName = (os.path.split(FullName)[1]).replace(".shp","")

outFolder = outFolder.replace("\\","/")

#Determine if the field is integer, decimal (0 scale) or string field

arcpy.AddMessage("\n  Checking for appropriate field type" \
              + "(  string, decimal (0 scale) or integer)")

theFields = arcpy.ListFields(input_FC)
inType = ""
OIDField = desc(input_FC).OIDFieldName
OKFields = [OIDField]

field_list = [OIDField]
try:
  aField = theFields.next()
  while aField:
    field_list.append(aField)
    aField = theFields.next()
except:
  field_list = theFields

#arcpy.AddMessage("%-10s %-10s %-6s %-6s " % ("Field","Type","Scale","Useable"))

for aField in field_list:
  fType = aField.type
  fScale = aField.scale
  fName = aField.name
  if fName == inField:
    inType = fType   #used to determine field type later on
    inScale = fScale
    inName = fName
  isOK = "Y"
  if (fType == "String"):
    OKFields.append(fName)
  elif ((fScale == 0) and (fType not in ["Geometry", "Date"])):
    OKFields.append(fName)
  else:
    isOK = "N"
    
  arcpy.AddMessage("%-10s %-10s %-6s %-6s " % (fName, fType, fScale,isOK))

if inField not in OKFields:
  arcpy.AddMessage("The field " + inField + " is not an appropriate" + \
                " field type.  Terminating operation.  " + \
                "Convert date fiels to strings, and ensure integers " \
                "are positive" + "\n")  
  del arcpy
  sys.exit()
#  
#Determine unique values in the selected field

arcpy.AddMessage(inField + " is being queried for unique values.")
valueList = []
rows = arcpy.SearchCursor(input_FC)
row = rows.next()
aString = ""
aLen = 0; aFac = 1

while row:
  aVal = row.getValue(inField)
  if aVal not in valueList:
    valueList.append(aVal)
    aLen = len(aString)
    if aLen > 50 * aFac:
      aString = aString + "\n"
      aFac = aFac + 1
    aString = aString + " " + str(aVal)
  row = rows.next()
arcpy.AddMessage("Unique values: " + "\n" + aString)
#
arcpy.AddMessage("\n  Processing: " + FullName )
#
#Do the actual work of producing the unique shapefiles
aMax = 1
for aVal in valueList:
  aMax = max(aMax, len(str(aVal)))
for aVal in valueList:
  if (str(aVal).isdigit()) and (not inType == "String"):
    fs = '"' + "%" + str(aMax) + "." + str(aMax) + 'i"'
    aSuffix = fs % aVal
    aVal = str(aVal)
  elif inType == "Double" and inScale == 0:
    aSuffix = str(aVal).replace(".0","")  ###### 
    aVal = str(aVal).replace(".0","")
  else:
    aSuffix = str(aVal) 
    aVal = str(aVal)
  try:
    aSuffix = aSuffix.replace(" ","_")  #replace garbage in output files
    aSuffix = aSuffix.replace('"',"")
    aSuffix = aSuffix.replace("/","")
    aSuffix = aSuffix.replace("-","")
    outName = theFName + aSuffix + ".shp"
    outShapeFile = outFolder + "/" + outName
    outShapeFile = outShapeFile.replace("\\","/")
    # 
    #Create a query and produce the file
    if (not aVal.isdigit()) or (inType == "String"):
      aVal = "'" + aVal + "'"
    whereClause = "%s = %s" % (inField, aVal)
    arcpy.MakeFeatureLayer_management(input_FC, "TempLayer", whereClause)
    arcpy.CopyFeatures_management("TempLayer",outShapeFile)
    arcpy.AddMessage("Output and query: " + outShapeFile + "  " + whereClause)
  except:
    whereClause = "%s = %s" % (inField, aVal)
    arcpy.AddMessage("Output and query: " + outShapeFile + "  " + whereClause + " did not work ")
#
arcpy.AddMessage("\n  Processing complete" + "\n")
del arcpy
