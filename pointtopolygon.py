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

    output_folder = arcpy.GetParameterAsText(7)
    # Request user input of data type = table, direction = Input, and
    # Obtained from = (initial prompt for shapefile name)
    #polygonLayer = arcpy.GetParameterAsText(0)
    
    outputLayer = arcpy.GetParameterAsText(6)
    # Request user input of data type = table, direction = Input, and
    # Obtained from = (initial prompt for shapefile name)
    
    #add optional parameters
    try: 
        domViolence = arcpy.GetParameterAsText(1)
        arcpy.AddMessage("Adding Sexual Crime data to your polygons")
    except:
        domViolence = None

    try:
        # Mental Illness
        mentalIllness = arcpy.GetParameterAsText(2)
    except:
        mentalIllness = None
    
    try:
        # substance
        substanceAbuse = arcpy.GetParameterAsText(3)
    except:
        substanceAbuse = None

    try:
        # other
        otherData = arcpy.GetParameterAsText(4)
    except:
        substanceAbuse = None
    
    #field to change
    fieldName = "Point_Count"

    # Summarize point layer by polygon layer
    if domViolence != None:
        layer = arcpy.SummarizeWithin_analysis(polygonLayer, domViolence, outputLayer, "KEEP_ALL", None, None, None, None, "NO_MIN_MAJ", "NO_PERCENT", None)
    
    #print field names.. we can see the new point_count layer is not showing 
    ls = [f.name for f in arcpy.ListFields(outputLayer)]
    arcpy.AddMessage(ls)
    
    #Rename field in output to domViolence
    arcpy.AlterField_management(outputLayer, fieldName, "domvVolence", "Domestic Violence", "LONG", 4, "NULLABLE", "DO_NOT_CLEAR")
   
    #if mentalIllness != None:
    #    arcpy.analysis.SummarizeWithin(polygonLayer, "mentalIllness", "RiskFactors", "KEEP_ALL", None, None, None, "NO_MIN_MAJ", "NO_PERCENT", None)

    #    #Rename field in output to domViolence
    #    arcpy.management.AlterField(polygonLayer, "Point_Count", "mentalIllness", "Domestic Violence", "LONG", 4, "NULLABLE", "DO_NOT_CLEAR")

    #if substanceAbuse != None:
    #    arcpy.analysis.SummarizeWithin("polygonLayer", "substanceAbuse", "RiskFactors", "KEEP_ALL", None, None, None, "NO_MIN_MAJ", "NO_PERCENT", None)

    #    #Rename field in output to domViolence
    #    arcpy.management.AlterField("riskfactors100", "Point_Count", "substanceAbuse", "Domestic Violence", "LONG", 4, "NULLABLE", "DO_NOT_CLEAR")

    #if otherData != None:
    #    arcpy.analysis.SummarizeWithin("polygonLayer", "otherData", "RiskFactors", "KEEP_ALL", None, None, None, "NO_MIN_MAJ", "NO_PERCENT", None)

    #    #Rename field in output to domViolence
    #    arcpy.management.AlterField("riskfactors100", "Point_Count", "otherData", "Domestic Violence", "LONG", 4, "NULLABLE", "DO_NOT_CLEAR")
   
except Exception as e:
    # If unsuccessful, end gracefully by indicating why
    arcpy.AddError('\n' + "Script failed because: \t\t" + e.message )
    # ... and where
    exceptionreport = sys.exc_info()[2]
    fullermessage   = traceback.format_tb(exceptionreport)[0]
    arcpy.AddError("at this location: \n\n" + fullermessage + "\n")
