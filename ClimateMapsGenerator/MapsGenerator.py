
#################
### LIBRARIES ###
#################
import sys
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import arcpy
import arcpy.mapping as map
import sys, csv, os
from arcpy import env

#################
### FUNCTIONS ###
#################
''' Enables or disables layer according to the parameters introduced by user '''
def check_enable_layer (layer, btn_layer, check):
    if btn_layer.isChecked()==True:
        #Remember to review the names are the same in ArcGIS Template and
        #Interface
        if layer.name == btn_layer.text(): 
            layer.visible = check
            arcpy.RefreshActiveView()
            arcpy.RefreshTOC()
        
'''Draws graphic element'''
#Without position
def draw_graphic(graphic, graphic_name_map, graphic_btn):
    if graphic.name == graphic_name_map:
        if graphic_btn.isChecked()==False:
            #Graphic element out of layout
            graphic.elementPositionX = 33.3523
            graphic.elementPositionY = 0.4023
            #print graphic_name_map, ": Disabled"

###With position
##def draw_graphic(graphic, graphic_name_map, graphic_btn, PositionX, PositionY):
##    if graphic.name == graphic_name_map:                
##        if graphic_btn.isChecked()==True:
##            #Graphic element in of layout
##            graphic.elementPositionX = PositionX
##            graphic.elementPositionY = PositionY
##            print graphic_name_map, ": Enabled"
##        if graphic_btn.isChecked()==False:
##            #Graphic element out of layout
##            graphic.elementPositionX = 33.3523
##            graphic.elementPositionY = 0.4023
##            print graphic_name_map, ": Disabled"

'''Draws graphic elements according to the parameters introduced by user'''
def draw_graphic_maps(mxd, graphic_list):
    check_logo, check_date, check_legend, check_scale = graphic_list 
    graphic_list_map = map.ListLayoutElements(mxd)
    for graphic in graphic_list_map:
        #Draw logo
        draw_graphic(graphic, 'logo_map', check_logo) #function created before 
        #Draw Date
        draw_graphic(graphic, 'date_map', check_date)
        draw_graphic(graphic, 'hour_map', check_date)
        #Draw Legend
        draw_graphic(graphic, 'legend_map', check_legend)

        
##            #Draw Scale
##            draw_graphic(graphic, 'scale_map', check_scale)
            
''' Zooms the map according to the parameters introduced by user'''
def zoom_to_value(dataframe, btn_zoom_to_layer_list, layers, \
                  btn_zoom_to_layer_attribute_list):   
    j = 0 #Contador
    for btn_zoom_to_layer in btn_zoom_to_layer_list:
        if btn_zoom_to_layer.isChecked()==True:
            for admin_layer in layers:
                if admin_layer.name == btn_zoom_to_layer.text():
                    if admin_layer.name == btn_zoom_to_layer_list[2].text():
                        SQL = "[COMARCA_] = '" + \
                              unicode(btn_zoom_to_layer_attribute_list[j].currentText()) + "'"
                    else:
                        SQL = "[ROTULO] = '" + \
                              unicode(btn_zoom_to_layer_attribute_list[j].currentText()) + "'"
                    
                    arcpy.SelectLayerByAttribute_management(admin_layer, "NEW_SELECTION", SQL)
                    dataframe.zoomToSelectedFeatures()
                    arcpy.SelectLayerByAttribute_management(admin_layer, "CLEAR_SELECTION")
                    arcpy.RefreshActiveView()
            break
        j += 1

'''Export maps according to the parameters introduced by user '''
def export_maps(mxd, btn_layer, btn_export_pdf, btn_export_png):
    map_name = str(btn_layer.objectName())[6:]
    if btn_export_png.isChecked() == True:
        #print btn_layer.text(), ' Print PNG'
        map.ExportToPNG(mxd, map_name+".png", resolution=300, \
                        transparent_color='255, 255, 255')
    if btn_export_pdf.isChecked() == True:
        #print btn_layer.text(), ' Print PDF'
        map.ExportToPDF(mxd, map_name+".pdf" )

'''Creates thematic maps according to the parameters introduced by user '''
'''This function uses other functions: draw_graphic(),
check_enable_layer(), export_maps()'''
def create_thematic_map(progressBar, mxd, input_files_path, i, btn_layer, btn_export_pdf,\
                        btn_export_png, administrative_layer_list, other_layer_list, \
                        graphic_list, btn_zoom_to_layer_list, btn_zoom_to_layer_attribute_list):
    #Acces to the list of layers
    dataframe = map.ListDataFrames(mxd)[0]        
    layers = map.ListLayers(mxd,"",dataframe)
    if btn_layer.isChecked()==True:

        # Check out any necessary licenses
        arcpy.CheckOutExtension("3D")
        arcpy.CheckOutExtension('Spatial')
        arcpy.env.overwriteOutput=True
        
        #Join Input data
        progressBar.setValue(1)

        shp_path = str(input_files_path)
        
        inFeatures = shp_path
        weather_variables = ['temp_mit', 'temp_max', 'temp_min', 'prec', 'prec', 'hume', 'pres']
        vble = weather_variables[i]
        Z_value = vble
        print Z_value
        outRaster = "interpolation_maps/"+str(vble)
        cellSize = 300
        kModel = "Spherical 663.040376"

        for layer in layers: #(group of layer name is read as one layer else)
            if layer.name == administrative_layer_list[2].text():
                arcpy.env.mask = layer.dataSource
                arcpy.env.extent = "626638.8673 4190956.536 815377.0266 4519162.5229"
                #arcpy.Kriging_3d(inFeatures, Z_value, outRaster, kModel, cellSize, "VARIABLE 12", "")
                arcpy.Idw_3d(inFeatures, Z_value, outRaster, cellSize, "2", "VARIABLE 12", "")                
        #In order to automatically change the Source directory of the .shp inside the .mxd file i define the next code line this is assuming that the user doesn't change the directory manually in the .mxd
        last_workspace_path = str(arcpy.env.workspace)
        mxd.findAndReplaceWorkspacePaths(last_workspace_path,arcpy.env.workspace)

        
        #Enable weather layer
        progressBar.setValue(3)
        for layer in layers: #(group of layer name is read as one layer else)
            check_enable_layer (layer, btn_layer, True) #function created before            

            #Enable other layers
            progressBar.setValue(4)
            for administrative_layer in administrative_layer_list:
                check_enable_layer(layer, administrative_layer, True)
            for other_layer in other_layer_list:
                check_enable_layer(layer, other_layer, True)
            
        
        #Draws graphic elements
        progressBar.setValue(5)
        draw_graphic_maps(mxd, graphic_list) #function created before

        #Zoom to
        progressBar.setValue(6)
        zoom_to_value(dataframe, btn_zoom_to_layer_list, layers, \
                      btn_zoom_to_layer_attribute_list) #function created before 
                
        #Export map
        progressBar.setValue(7)
        export_maps(mxd, btn_layer, btn_export_pdf, \
                    btn_export_png) #function created before 

        #Disable layers (It's important due to clean de template for the next map)
        for layer in layers: #(group of layer name is read as one layer else)
            check_enable_layer (layer, btn_layer, False)
            for administrative_layer in administrative_layer_list:
                check_enable_layer(layer, administrative_layer, False)
            for other_layer in other_layer_list:
                check_enable_layer(layer, other_layer, False)

#################
### INTERFACE ###
#################
            
#load the file .ui
form = uic.loadUiType("MapsGenerator.ui")[0]

class MyDialogClass(QtGui.QDialog, form):
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        self.setupUi(self)

        #connections of events with functions
        self.btn_shp_path.clicked.connect(self.get_shp_file)
        self.btn_run.clicked.connect(self.run)
        self.btn_cancel.clicked.connect(self.cancel)

        #Progress bar
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(7)        

        #Enable and disable widgets automaticaly
        self.check_temp_mit.clicked.connect(self.enable_choose_map_buttons)
        self.check_temp_max.clicked.connect(self.enable_choose_map_buttons)
        self.check_temp_min.clicked.connect(self.enable_choose_map_buttons)
        self.check_prec50.clicked.connect(self.enable_choose_map_buttons)
        self.check_prec150.clicked.connect(self.enable_choose_map_buttons)
        self.check_hume.clicked.connect(self.enable_choose_map_buttons)
        self.check_pres.clicked.connect(self.enable_choose_map_buttons)

        #Enable and disable zoom widgets automaticaly
        self.rbtn_zoom_to_regional.clicked.connect(self.enable_zoom_values_cmb)
        self.rbtn_zoom_to_province.clicked.connect(self.enable_zoom_values_cmb)
        self.rbtn_zoom_to_comarca.clicked.connect(self.enable_zoom_values_cmb)
        #self.rbtn_zoom_to_municipality.clicked.connect(self.enable_zoom_values_cmb)
        
        #Load comarca values for the Qcombobox of zooming
        self.rbtn_zoom_to_comarca.clicked.connect(self.load_comarca_values_cmb)
        #self.rbtn_zoom_to_municipality.clicked.connect(self.load_municipality_values_cmb)
        

    ####################################
    ### ENABLE AND DISABLE FUNCTIONS ###
    ####################################
        
    def enable_choose_map_buttons(self):
        #Temp_mit
        if self.check_temp_mit.isChecked() == False:
            self.check_temp_mit_png.setEnabled(False)
            self.check_temp_mit_pdf.setEnabled(False)
            self.lbl_temp_mit.setEnabled(False)
        elif self.check_temp_mit.isChecked() == True:
            self.check_temp_mit_png.setEnabled(True)
            self.check_temp_mit_pdf.setEnabled(True)
            self.lbl_temp_mit.setEnabled(True)

##        btn_png_list = [self.check_temp_mit_png, self.check_temp_max_png, \
##                          self.check_temp_min_png, self.check_prec50_png, \
##                          self.check_prec150_png, self.check_hume_png, \
##                          self.check_pres_png]
##        btn_pdf_list = [self.check_temp_mit_pdf, self.check_temp_max_pdf, \
##                          self.check_temp_min_pdf, self.check_prec50_pdf, \
##                          self.check_prec150_pdf, self.check_hume_pdf, \
##                          self.check_pres_pdf]
##        variable_check_run = False
##        for btn in btn_png_list:
##            if btn.isChecked() == True:
##                variable_check_run = True
##            else:
##                variable_check_run = False
##        for btn in btn_pdf_list:
##            if btn.isChecked() == True:
##                variable_check_run = True
##            else:
##                variable_check_run = False
##        if variable_check_run == True:
##            btn_run.setEnabled(True)

        
        
        #Temp_max
        if self.check_temp_max.isChecked() == False:
            self.check_temp_max_png.setEnabled(False)
            self.check_temp_max_pdf.setEnabled(False)
            self.lbl_temp_max.setEnabled(False)            
        elif self.check_temp_max.isChecked() == True:
            self.check_temp_max_png.setEnabled(True)
            self.check_temp_max_pdf.setEnabled(True)
            self.lbl_temp_max.setEnabled(True)            
        #Temp_min
        if self.check_temp_min.isChecked() == False:
            self.check_temp_min_png.setEnabled(False)
            self.check_temp_min_pdf.setEnabled(False)
            self.lbl_temp_min.setEnabled(False)            
        elif self.check_temp_min.isChecked() == True:
            self.check_temp_min_png.setEnabled(True)
            self.check_temp_min_pdf.setEnabled(True)
            self.lbl_temp_min.setEnabled(True)            
        #Prec_50
        if self.check_prec50.isChecked() == False:
            self.check_prec50_png.setEnabled(False)
            self.check_prec50_pdf.setEnabled(False)
            self.lbl_prec50.setEnabled(False)            
        elif self.check_prec50.isChecked() == True:
            self.check_prec50_png.setEnabled(True)
            self.check_prec50_pdf.setEnabled(True)
            self.lbl_prec50.setEnabled(True)            
        #Prec_150
        if self.check_prec150.isChecked() == False:
            self.check_prec150_png.setEnabled(False)
            self.check_prec150_pdf.setEnabled(False)
            self.lbl_prec150.setEnabled(False)            
        elif self.check_prec150.isChecked() == True:
            self.check_prec150_png.setEnabled(True)
            self.check_prec150_pdf.setEnabled(True)
            self.lbl_prec150.setEnabled(True)            
        #Hume
        if self.check_hume.isChecked() == False:
            self.check_hume_png.setEnabled(False)
            self.check_hume_pdf.setEnabled(False)
            self.lbl_hume.setEnabled(False)            
        elif self.check_hume.isChecked() == True:
            self.check_hume_png.setEnabled(True)
            self.check_hume_pdf.setEnabled(True)
            self.lbl_hume.setEnabled(True)            
        #Pres
        if self.check_pres.isChecked() == False:
            self.check_pres_png.setEnabled(False)
            self.check_pres_pdf.setEnabled(False)
            self.lbl_pres.setEnabled(False)            
        elif self.check_pres.isChecked() == True:
            self.check_pres_png.setEnabled(True)
            self.check_pres_pdf.setEnabled(True)
            self.lbl_pres.setEnabled(True)            

    #ZOOM ENABLING FUNCTIONS
            
    def enable_zoom_values_cmb(self):
        #Zoom to region
        if self.rbtn_zoom_to_regional.isChecked() == True:
            self.cmb_zoom_to_region.setEnabled(True)
            self.cmb_zoom_to_province.setEnabled(False)
            self.cmb_zoom_to_comarca.setEnabled(False)
            self.cmb_zoom_to_municipality.setEnabled(False)
        #Zoom to province
        elif self.rbtn_zoom_to_province.isChecked() == True:
            self.cmb_zoom_to_region.setEnabled(False)
            self.cmb_zoom_to_province.setEnabled(True)
            self.cmb_zoom_to_comarca.setEnabled(False)
            self.cmb_zoom_to_municipality.setEnabled(False)
        #Zoom to comarca
        elif self.rbtn_zoom_to_comarca.isChecked() == True:
            self.cmb_zoom_to_region.setEnabled(False)
            self.cmb_zoom_to_province.setEnabled(False)
            self.cmb_zoom_to_comarca.setEnabled(True)
            self.cmb_zoom_to_municipality.setEnabled(False)
            
##        #Zoom to municipality
##        elif self.rbtn_zoom_to_municipality.isChecked() == True:
##            self.cmb_zoom_to_region.setEnabled(False)
##            self.cmb_zoom_to_province.setEnabled(False)
##            self.cmb_zoom_to_comarca.setEnabled(False)
##            self.cmb_zoom_to_municipality.setEnabled(True)


    def load_comarca_values_cmb(self):
        list1 = []
        #Acces to the MDX file
        path_mxd = r"MapasInterpolacion.mxd"
        mxd = map.MapDocument(path_mxd)
        #Acces to the list of layers
        dataframe = map.ListDataFrames(mxd)[0]        
        layers = map.ListLayers(mxd,"",dataframe)
        for layer in layers:
            #if layer.name == btn_layer.text():
            if layer.name == self.rbtn_zoom_to_comarca.text():
                cursor = arcpy.da.SearchCursor(layer, ['COMARCA_'])
                self.cmb_zoom_to_comarca.clear()
                for row in cursor:
                    self.cmb_zoom_to_comarca.addItems(row)

##    def load_municipality_values_cmb(self):
##        list1 = []
##        #Acces to the MDX file
##        path_mxd = r"MapasInterpolacion.mxd"
##        mxd = map.MapDocument(path_mxd)
##        #Acces to the list of layers
##        dataframe = map.ListDataFrames(mxd)[0]        
##        layers = map.ListLayers(mxd,"",dataframe)
##        for layer in layers:
##            #if layer.name == btn_layer.text():
##            if layer.name == self.rbtn_zoom_to_municipality.text():
##                cursor = arcpy.da.SearchCursor(layer, ['ROTULO'])
##                self.cmb_zoom_to_municipality.clear()
##                for row in cursor:
##                    self.cmb_zoom_to_municipality.addItems(row)
##        

    
    ########################
    ### BUTTON FUNCTIONS ###
    ########################
    def get_shp_file(self):
        #Open file. Only SHP files can be chosen
        fname = QFileDialog.getOpenFileName(self, 'Open file', '.',\
                                            "Shapefile /files (*.shp)")
        #Get SHP file path
        self.txt_shp_path.setText(fname)
        #Enable MAP OPTIONS
        self.tabWidget.setEnabled(True)
        self.btn_run.setEnabled(True)        
        
    def run(self):
        #Acces to the MDX file
        path_mxd = r"MapasInterpolacion.mxd"
        mxd = map.MapDocument(path_mxd)     

        #Save buttons on lists
        progressBar = [self.progressBar]
        
        input_files_path = [self.txt_shp_path.text()]
        
        weather_layer_list = [self.check_temp_mit, self.check_temp_max, \
                          self.check_temp_min, self.check_prec50, \
                          self.check_prec150, self.check_hume, \
                          self.check_pres]
        
        btn_png_list = [self.check_temp_mit_png, self.check_temp_max_png, \
                          self.check_temp_min_png, self.check_prec50_png, \
                          self.check_prec150_png, self.check_hume_png, \
                          self.check_pres_png]
        btn_pdf_list = [self.check_temp_mit_pdf, self.check_temp_max_pdf, \
                          self.check_temp_min_pdf, self.check_prec50_pdf, \
                          self.check_prec150_pdf, self.check_hume_pdf, \
                          self.check_pres_pdf]
        administrative_layer_list = [self.check_insert_regions_shp, \
                                 self.check_insert_provinces_shp, \
                                 self.check_insert_comarcas_shp, \
                                 self.check_insert_municipalities_shp]
        other_layer_list = [self.check_insert_hydro_shp, \
                        self.check_insert_cities_shp, \
                        self.check_insert_stations_shp, \
                        self.check_insert_hillshade_shp]          
        graphic_list = [self.check_logo, self.check_date, \
                        self.check_legend, self.check_scale]

        btn_zoom_to_layer_list = [self.rbtn_zoom_to_regional, \
                                  self.rbtn_zoom_to_province, \
                                  self.rbtn_zoom_to_comarca, \
                                  self.rbtn_zoom_to_municipality]

        btn_zoom_to_layer_attribute_list= [self.cmb_zoom_to_region, \
                                           self.cmb_zoom_to_province, \
                                           self.cmb_zoom_to_comarca, \
                                           self.cmb_zoom_to_municipality]
        
        i = 0 #Contador
        for weather_layer in weather_layer_list:
            #Create thematic maps
            create_thematic_map(progressBar[0], mxd, input_files_path[0], i, weather_layer, btn_pdf_list[i], \
                                btn_png_list[i], administrative_layer_list, \
                                other_layer_list, graphic_list, \
                                btn_zoom_to_layer_list, \
                                btn_zoom_to_layer_attribute_list)            
            i += 1
        

    def cancel(self):
        self.close()


app = QtGui.QApplication(sys.argv)
myDialog = MyDialogClass(None)
myDialog.show()
app.exec_()
