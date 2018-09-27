"""
THIS SCRIPT SETS THE MAX TABLE VALUE TO THE TABLE FEATURE LAYER VALUE

To create an ArcToolbox tool with which to execute this script, do the following.
1   In  ArcMap > Catalog > Toolboxes > My Toolboxes, either select an existing toolbox
    or right-click on My Toolboxes and use New > Toolbox to create (then rename) a new one.
2   Drag (or use ArcToolbox > Add Toolbox to add) this toolbox to ArcToolbox.
3   Right-click on the toolbox in ArcToolbox, and use Add > Script to open a dialog box.
4   In this Add Script dialog box, use Label to name the tool being created, and press Next.
5   In a new dialog box, browse to the .py file to be invoked by this tool, and press Next.
6   In the next dialog box, specify the following inputS (using dropdown menus wherever possible)
    before pressing OK or Finish.
        DISPLAY NAME        DATA TYPE           PROPERTY>DIRECTION>VALUE    PROPERTY>OBTAINEDFROM>VALUE  
        Input Polygons      Feature Layer       Input
        Input Points        Feature Layer       Input     
#       Input Points2       Feature Layer       Input
#       Input Points3       Feature Layer       Input
#       Output Polygons     Feature Layer       Output
7   To later revise any of this, right-click to the tool's name and select Properties.
"""


# Import necessary modules
import sys, os, string, math, arcpy, traceback

#add outputs to map 
arcpy.addOutputsToMap = True

try:
    polygonLayer = arcpy.GetParameterAsText(0)
    
    #add optional parameters
    #def assignNull(num, name):
    if len(arcpy.GetParameterAsText(1))==0:
        domViolence = 99999
    else:
        domViolence = arcpy.GetParameterAsText(1)

    if len(arcpy.GetParameterAsText(2))==0:
        mentalIllness = 99999
    else:
        mentalIllness = arcpy.GetParameterAsText(2)
    
    if len(arcpy.GetParameterAsText(3))==0:
        substanceAbuse = 99999
    else:
        substanceAbuse = arcpy.GetParameterAsText(3)

    if len(arcpy.GetParameterAsText(4))==0:
        otherData = 99999
    else:
        otherData = arcpy.GetParameterAsText(4)

    # output layer
    outputLayer = arcpy.GetParameterAsText(5)

    # Summarize point layer by polygon layer

    #define the input layer 
    inputLayer = arcpy.MakeFeatureLayer_management(polygonLayer, "in_memory/input")
    
    if domViolence != 99999:
        arcpy.SpatialJoin_analysis(inputLayer, domViolence, "in_memory/domvio")
        arcpy.AddJoin_management(inputLayer, 'OBJECTID', 'in_memory/domvio', 'TARGET_FID')
        arcpy.AddField_management(inputLayer,"domVio",  "LONG") 
        arcpy.CalculateField_management(inputLayer, "domVio", "!Join_Count!", "PYTHON3")
        arcpy.RemoveJoin_management(inputLayer)
    
    if mentalIllness != 99999:
        #summarize points by poygon layer
        arcpy.SpatialJoin_analysis(inputLayer, mentalIllness, "in_memory/mental")
        arcpy.AddJoin_management(inputLayer, 'OBJECTID', 'in_memory/mental', 'TARGET_FID')
        arcpy.AddField_management(inputLayer,"mentalIllness",  "LONG") 
        arcpy.CalculateField_management(inputLayer, "mentalIllness", "!Join_Count!", "PYTHON3")
        arcpy.RemoveJoin_management(inputLayer)

    if substanceAbuse != 99999:
    #    #summarize points by poygon layer
        arcpy.SpatialJoin_analysis(inputLayer, substanceAbuse, "in_memory/substance")
        arcpy.AddJoin_management(inputLayer, 'OBJECTID', 'in_memory/substance', 'TARGET_FID')
        arcpy.AddField_management(inputLayer,"substanceAbuse",  "LONG") 
        arcpy.CalculateField_management(inputLayer, "substanceAbuse", "!Join_Count!", "PYTHON3")
        arcpy.RemoveJoin_management(inputLayer)

    if otherData != 99999:
        arcpy.SpatialJoin_analysis(inputLayer, otherData, "in_memory/otherData")
        arcpy.AddJoin_management(inputLayer, 'OBJECTID', 'in_memory/otherData', 'TARGET_FID')
        arcpy.AddField_management(inputLayer,"otherData",  "LONG") 
        arcpy.CalculateField_management(inputLayer, "otherData", "!Join_Count!", "PYTHON3")
        arcpy.RemoveJoin_management(inputLayer)
    
    arcpy.CopyFeatures_management("in_memory/input", outputLayer)
except Exception as e:
    # If unsuccessful, end gracefully by indicating why
    arcpy.AddError('\n' + "Script failed because: \t\t" + e.message )
    # ... and where
    exceptionreport = sys.exc_info()[2]
    fullermessage   = traceback.format_tb(exceptionreport)[0]
    arcpy.AddError("at this location: \n\n" + fullermessage + "\n")
