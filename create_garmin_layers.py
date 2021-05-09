import arcpy, os

# Set environment settings
arcpy.env.workspace = r"C:\Users\elisk\Desktop\_git\garmin\test.gdb"
arcpy.env.overwriteOutput=True

# Set the local variables
in_folder = r"C:\Users\elisk\Desktop\_git\garmin\CSV"

x_coords = "longitude"
y_coords = "latitude"
z_coords = ""


#grab all the text files and put them in  a list
text_file_list = [ ]

for file in os.listdir(in_folder):
    if ".csv" in file:
        text_file_list.append(file)


for text_file in text_file_list:
    in_table = os.path.join(in_folder,text_file)
    name = text_file.strip(".tcx.csv")
    print(name)
    layer = arcpy.management.XYTableToPoint(in_table, name, x_coords, y_coords, z_coords, arcpy.SpatialReference(4326))
    arcpy.PointsToLine_management(layer,"line"+name,"", "")
    arcpy.Delete_management(layer)
    
#arcpy.Merge(path_list,merged_fc)

#arcpy.Delete_management("in_memory")
