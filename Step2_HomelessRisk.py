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
7   To later revise any of this, right-click to the tool's name and select Properties.
"""

# Import necessary modules
import sys, os, string, math, arcpy, traceback
import arcpy.stats as SS


try:
    # Request user input of data type = Feature Layer, direction = Input, and
    # Obtained from = (initial prompt for shapefile name)
    polygonLayer = arcpy.GetParameterAsText(0)

    #fields to use in analysis
    fields = arcpy.GetParameterAsText(1)

    #output
    output = arcpy.GetParameterAsText(4)

    #get count of variables and use top 25%
    featureCount = ((arcpy.GetCount_management(polygonLayer))*.025)


    SS.SimilaritySearch(subsetFeature, polygonLayer, riskSurface, "NO_COLLAPSE", "MOST_SIMILAR", "ATTRIBUTE_VALUES", featureCount, "F5yearincrements_pop60_cy_p;AgeRisk;raceandhispanicorigin_minoritycy_p", None)





except Exception as e:
    # If unsuccessful, end gracefully by indicating why
    arcpy.AddError('\n' + "Script failed because: \t\t" + e.message )
    # ... and where
    exceptionreport = sys.exc_info()[2]
    fullermessage   = traceback.format_tb(exceptionreport)[0]
    arcpy.AddError("at this location: \n\n" + fullermessage + "\n")

