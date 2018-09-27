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
    outputLayer = arcpy.GetParameterAsText(2)

    #nameofnewfield
    newField = arcpy.GetParameterAsText(3)

    #final# to consider
    finalNum = arcpy.GetParameterAsText(4)

    #########################################input values############################################################

    #get count of variables and use top 25%
    featureCount = int(arcpy.GetCount_management(polygonLayer).getOutput(0))
          
    projCount = (featureCount)*.25

    #select top 25% from risk layer 
    arcpy.SelectLayerByAttribute_management(polygonLayer, "NEW_SELECTION", 'SIMRANK < {percent}'.format(percent=projCount))

    #copy selected features
    topTracts = arcpy.MakeFeatureLayer_management(polygonLayer, "topTracts")

    #clear selection
    arcpy.SelectLayerByAttribute_management(polygonLayer, "CLEAR_SELECTION")

    arcpy.AddMessage(topTracts)

    ####################################################delete unwanted fields##########################################################################
    #arcpy.DeleteField_management(topTracts, ["SIMRANK", "SIMINDEX", "LABELRANK", "MATCH_ID", "CAN_ID"])

    addFields = [f.name for f in arcpy.ListFields(topTracts)]
    arcpy.AddMessage(addFields)
    ##############################################################summary statistics operations##########################################################
    
    #fields to append to output###Does not include double fields.... this is a problem because population is double. 
    lsFields = []
    for field in arcpy.ListFields(topTracts):
        if field.type in ('Integer','Single','SmallInteger','String'):
            lsFields.append(field.name)
            addFields = ';'.join(str(f) for f in lsFields)

    #create table to be used by summary statistics
    summaryTable = arcpy.CreateTable_management("in_memory", "table1")

    # Create list of values to use in suummary statistics opeartion
    #create empty list
    sumStatFields = []

    #split field names
    fieldSplit = fields.split(';')

    #append field names to list 
    for x in fieldSplit:
        sumStatFields.append([x,"MAX"])

    ##Summary Statistics on all relevant fields
    arcpy.Statistics_analysis(polygonLayer, summaryTable, sumStatFields)

    ##Subset Features create one singular feature on which to add on the summary stats
    arcpy.SubsetFeatures_ga(polygonLayer, "worstTract", None, 1, "ABSOLUTE_VALUE")

    #Create two dictionaries with values for the worst tract and the summary table 
    values = {}
    with arcpy.da.SearchCursor(summaryTable, "*") as cursor:
        for row in cursor:
            i=0
            for field in cursor.fields:
                values[field]=row[i]
                i+=1
    
    layerFields = {}
    with arcpy.da.SearchCursor("worstTract", "*") as cursor2:
        for a_row in cursor2:
            i=0
            for field in cursor2.fields:
                layerFields[field]=a_row[i]
                i+=1
                
    for key in values:
        for field in layerFields:
            if key[4:35] == field[:31]:
                with arcpy.da.UpdateCursor("worstTract", [field]) as cursor3:
                    arcpy.AddMessage(cursor3)
                    for f_row in cursor3:
                        f_row[0] = values[key]
                        cursor3.updateRow(f_row) 

    #Similarity Search
    SS.SimilaritySearch("worstTract", polygonLayer, outputLayer, "NO_COLLAPSE", "MOST_SIMILAR", "ATTRIBUTE_VALUES", 100, fields, fields)
    
    ##############################################################################add field and assign value############################################################

    #addField for the project name 
    arcpy.AddField_management(outputLayer, newField, "Short", 0)

    arcpy.CalculateField_management(outputLayer, newField, 0, "PYTHON3", None ) 

    #calculateNewField
    arcpy.SelectLayerByAttribute_management(outputLayer, "NEW_SELECTION", 'SIMRANK < {result}'.format(result=finalNum), None)

    #calculate field assigning 1 to all selected polygons 
    #
    # NOT WORKING
    #
    arcpy.CalculateField_management(outputLayer, newField, 1, "PYTHON3", None ) 
    
    #clear the selection
    arcpy.SelectLayerByAttribute_management(outputLayer, "CLEAR_SELECTION")

except Exception as e:
    # If unsuccessful, end gracefully by indicating why
    arcpy.AddError('\n' + "Script failed because: \t\t" + e.message )
    # ... and where
    exceptionreport = sys.exc_info()[2]
    fullermessage   = traceback.format_tb(exceptionreport)[0]
    arcpy.AddError("at this location: \n\n" + fullermessage + "\n")

