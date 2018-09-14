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
        Max Values Table?   Table               Input
        Tables values       Feature Layer       Input 
        Output Layer        Feature Layer       Output
7   To later revise any of this, right-click to the tool's name and select Properties.
"""

# Import necessary modules
import sys, os, string, math, arcpy, traceback
 
try:
    # Request user input of data type = feature layer, direction = Input, and
    # Obtained from = (initial prompt for feature layer name)
    nameOfFeatureLayer = arcpy.GetParameterAsText(1)
    arcpy.AddMessage("The values in" + nameOfFeatureLayer)
    
    # Request user input of data type = table, direction = Input, and
    # Obtained from = (initial prompt for table name)
    nameOfTable = arcpy.GetParameterAsText(0)
    arcpy.AddMessage("will be replaced with the values from table that's called" + nameOfTable)

    # Create an enumeration of searchable records from the shapefiles attribute table
    #tableFields = str(arcpy.ListFields(nameOfTable))
    #layerFields = str(arcpy.ListFields(nameOfFeatureLayer))
    
    values = {}
    with arcpy.da.SearchCursor(nameOfTable, "*") as cursor:
        for row in cursor:
            i=0
            for field in cursor.fields:
                values[field]=row[i]
                i+=1

    layerFields = {}
    with arcpy.da.SearchCursor(nameOfFeatureLayer, "*") as cursor2:
        for a_row in cursor2:
            i=0
            for field in cursor2.fields:
                layerFields[field]=a_row[i]
                i+=1
    arcpy.AddMessage(layerFields)
    
    for key in values:
        for field in layerFields:
            if key[4:35] == field[:31]:
                arcpy.AddMessage("It's a match!")
                with arcpy.da.UpdateCursor(nameOfFeatureLayer, [field]) as cursor3:
                    arcpy.AddMessage(cursor3)
                    for f_row in cursor3:
                        f_row[0] = values[key]
                        cursor3.updateRow(f_row)

except Exception as e:
    # If unsuccessful, end gracefully by indicating why
    arcpy.AddError('\n' + "Script failed because: \t\t" + e.message )
    # ... and where
    exceptionreport = sys.exc_info()[2]
    fullermessage   = traceback.format_tb(exceptionreport)[0]
    arcpy.AddError("at this location: \n\n" + fullermessage + "\n")
