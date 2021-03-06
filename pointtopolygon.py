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
    
    #######################pull object ID field name ###########################################
    objID = arcpy.da.Describe(polygonLayer)['OIDFieldName']

    arcpy.AddMessage(objID)
    #list fo all possible layers and check for each one and if so write them to a new list, if not than do nothing. 
  
    #search for paste funciton concatanate 
    # one list of layer info and one name of layer as string
    # for x in listOFNames do function
    #function that does all the below
    # def createNew(layerName, layerData)
    potentials = domViolence, mentalIllness, substanceAbuse, otherData
    
    layerName = []
    layerData = []
    for x in potentials:
        if x != 99999:
            layerName.append(x[0:5])
            layerData.append(x)
    arcpy.AddMessage(layerName)
    arcpy.AddMessage(layerData)

    for x in range(len(layerName)-1):
        if layerData[x] != 99999:
            mem = "in_memory/"+layerName[x]
            arcpy.SpatialJoin_analysis(inputLayer, layerData[x], mem)
            arcpy.AddJoin_management(inputLayer, objID, mem, 'TARGET_FID')
            arcpy.AddField_management(inputLayer,layerName[x],  "LONG") 
            arcpy.CalculateField_management(inputLayer, layerName[x], "!Join_Count!", "PYTHON3")
            arcpy.RemoveJoin_management(inputLayer)
    
    arcpy.CopyFeatures_management("in_memory/input", outputLayer)
except Exception as e:
    # If unsuccessful, end gracefully by indicating why
    arcpy.AddError('\n' + "Script failed because: \t\t" + e.message )
    # ... and where
    exceptionreport = sys.exc_info()[2]
    fullermessage   = traceback.format_tb(exceptionreport)[0]
    arcpy.AddError("at this location: \n\n" + fullermessage + "\n")
