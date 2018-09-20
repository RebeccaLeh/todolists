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

arcpy.env.overwriteOutput = True

try:
    # Request user input of data type = Feature Layer, direction = Input, and
    # Obtained from = (initial prompt for layer name)
    #polygon layer
    polygonLayer = arcpy.GetParameterAsText(0)

    # Request user input of data type = workspace, direction = Input, and
    # Obtained from = (initial prompt for workspace name)
    #workspace 
    workspace = arcpy.GetParameterAsText(1)

    # Request user input of data type = Layer, direction = Output, and
    # Obtained from = (initial prompt for output name)
    #output 
    outputLayer = arcpy.GetParameterAsText(2)

    # Request user input of data type = Layer, direction = Output, and
    # Obtained from = (initial prompt for output name)
    #output 
    #worstTracts = arcpy.GetParameterAsText(3)

    # Request user input of data type = field (multiple), direction = Input, and
    # Obtained from = (initial prompt for field names)
    #fieldnames 
    fieldNames = arcpy.GetParameterAsText(3)

    #create table to be used by summary statistics
    summaryTable = arcpy.CreateTable_management("in_memory", "table1")

    #Risk Surface
    if 'F5yearincrements_pop50_cy_p' in [f.name for f in arcpy.ListFields(polygonLayer)]: 
        #add field AgeRisk
        arcpy.AddField_management(polygonLayer, 'AgeRisk', "DOUBLE", field_alias='Age Risk')

        ##Calculate fields AgeRisk, and flip ranking for marrital status
        arcpy.CalculateField_management(polygonLayer, 'AgeRisk', '(!F5yearincrements_pop50_cy_p!) +(!F5yearincrements_pop60_cy_p!) + (!F5yearincrements_pop55_cy_p!)', "PYTHON3")
        arcpy.CalculateField_management(polygonLayer, 'maritalstatustotals_married_cy_p', '100-(!maritalstatustotals_married_cy_p!)')

        #add agerisk to fields being queried 
        otherfield= ';AgeRisk'
        fieldNames = fieldNames+otherfield
    
    # Create list of values to use in suummary statistics opeartion
    #create empty list
    sumStatFields = []
    #split field names
    fieldSplit = fieldNames.split(';')

    #append field names to list 
    for x in fieldSplit:
        sumStatFields.append([x,"MAX"])

    ##Summary Statistics on all relevant fields
    arcpy.Statistics_analysis(polygonLayer, summaryTable, sumStatFields)

    ##Subset Features create one singular feature on which to add on the summary stats
    subsetFeature = arcpy.SubsetFeatures_ga(polygonLayer, (workspace+'worstTract') , None, 1, "ABSOLUTE_VALUE")

    #replace max values from fields with max values 
    values = {}
    with arcpy.da.SearchCursor(summaryTable, "*") as cursor:
        for row in cursor:
            i=0
            for field in cursor.fields:
                values[field]=row[i]
                i+=1

    layerFields = {}
    with arcpy.da.SearchCursor(subsetFeature, "*") as cursor2:
        for a_row in cursor2:
            i=0
            for field in cursor2.fields:
                layerFields[field]=a_row[i]
                i+=1
                
    for key in values:
        for field in layerFields:
            if key[4:35] == field[:31]:
                with arcpy.da.UpdateCursor(subsetFeature, [field]) as cursor3:
                    arcpy.AddMessage(cursor3)
                    for f_row in cursor3:
                        f_row[0] = values[key]
                        cursor3.updateRow(f_row)
     
     #Set worstTracts as an additional output location

#    [field.name for field in arcpy.ListFields("feature")] 
 

    arcpy.AddMessage(layerFields)

    subsetvalues = {}
    with arcpy.da.SearchCursor(subsetFeature, "*") as cursor4:
        for row in cursor4:
            i=0
            for field in cursor4.fields:
                subsetvalues[field]=row[i]
                i+=1


    arcpy.AddMessage("THIS IS THE SUBSET FIELD NAMES" + str(subsetvalues))
    featureCount = arcpy.GetCount_management(polygonLayer)

    polygonvalues = {}
    with arcpy.da.SearchCursor(polygonLayer, "*") as cursor5:
        for row in cursor5:
            i=0
            for field in cursor5.fields:
                polygonvalues[field]=row[i]
                i+=1

    arcpy.AddMessage("THIS IS THE POLYGON FIELD NAMES" + str(polygonvalues))

    
    arcpy.AddMessage(featureCount)

    ##Similarity Search
    SS.SimilaritySearch(subsetFeature, polygonLayer, outputLayer, "NO_COLLAPSE", "MOST_SIMILAR", "ATTRIBUTE_VALUES", 10000, fieldNames)

except Exception as e:
    # If unsuccessful, end gracefully by indicating why
    arcpy.AddError('\n' + "Script failed because: \t\t" + e.message )
    # ... and where
    exceptionreport = sys.exc_info()[2]
    fullermessage   = traceback.format_tb(exceptionreport)[0]
    arcpy.AddError("at this location: \n\n" + fullermessage + "\n")
