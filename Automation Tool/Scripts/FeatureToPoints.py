#-------------------------------------------------------------------------------
# Name:       Feature to point script
# Purpose:
#
# Author:      u1117236
#
# Created:     12/02/2019
# Copyright:   (c) Eliška Vlčková 2019 /// GC Prague Analytics team
# Licence:     <your licence>
#-------------------------------------------------------------------------------


input_fc = arcpy.GetParameterAsText(0)
output_fc = arcpy.GetParameterAsText(1)

arcpy.AddField_management(input_fc, "X", "DOUBLE")
arcpy.AddField_management(input_fc, "Y", "DOUBLE")

arcpy.CalculateField_management(input_fc, "X", "!SHAPE.CENTROID.X!", "PYTHON_9.3")
arcpy.CalculateField_management(input_fc, "Y", "!SHAPE.CENTROID.Y!", "PYTHON_9.3")


