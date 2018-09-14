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

arcpy.env.overwriteOutput = True

try:
    # Request user input of data type = Feature Layer, direction = Input, and
    # Obtained from = (initial prompt for shapefile name)
    polygonLayer = arcpy.GetParameterAsText(0)

    #create table to be used by summary statistics
    summaryStatistics = arcpy.CreateTable_management("in_memory", "table1")

    #workspace
    workspace = arcpy.GetParameterAsText(2)

    #subset feature layer
    subsetFeature = arcpy.MakeFeatureLayer_management(polygonLayer, "subsetFeature")

    #Risk Surface
    riskSurface = arcpy.GetParameterAsText(3)

    if 'F5yearincrements_pop50_cy_p' in [f.name for f in arcpy.ListFields(polygonLayer)]: 
        #add field AgeRisk
        arcpy.AddField_management(polygonLayer, 'AgeRisk', "DOUBLE", field_alias='Age Risk')

        ##Calculate fields AgeRisk, and flip ranking for marrital status
        arcpy.CalculateField_management(polygonLayer, 'AgeRisk', '(!F5yearincrements_pop50_cy_p!) +(!F5yearincrements_pop60_cy_p!) + (!F5yearincrements_pop55_cy_p!)', "PYTHON3")
        arcpy.CalculateField_management(polygonLayer, 'maritalstatustotals_married_cy_p', '100-(!maritalstatustotals_married_cy_p!)')
    
    ##Summary Statistics on all relevant fields
    arcpy.Statistics_analysis(polygonLayer, summaryStatistics,[["AgeRisk", "MAX"],["healthinsurancecoverage_acs35nohi", "MAX"],["ownerrenter_renter_cy_p", "MAX"],["raceandhispanicorigin_minoritycy_p", "MAX"],["atrisk_acshhbpov_p", "MAX"],["atrisk_acshhdis_p", "MAX"],["atrisk_acssnap_p", "MAX"],["populationtotals_popdens10", "MAX"],["housingcosts_acsgrnti50_p", "MAX"],["maritalstatustotals_married_cy_p", "MAX"]])

    ##Subset Features
    arcpy.SubsetFeatures_ga(polygonLayer, subsetFeature, None, 1, "ABSOLUTE_VALUE")
    arcpy.AddMessage(subsetFeature)

    ##Delete Fields

    ##MAX_ Relate

    #replace max values from fields with max values 
    
    values = {}
    with arcpy.da.SearchCursor(summaryStatistics, "*") as cursor:
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
    arcpy.AddMessage(layerFields)
    
    for key in values:
        for field in layerFields:
            if key[4:35] == field[:31]:
                arcpy.AddMessage("It's a match!")
                with arcpy.da.UpdateCursor(subsetFeature, [field]) as cursor3:
                    arcpy.AddMessage(cursor3)
                    for f_row in cursor3:
                        f_row[0] = values[key]
                        cursor3.updateRow(f_row)

    ##Similarity Search
    arcpy.SimilaritySearch_stats(subsetFeature, polygonLayer, riskSurface, "NO_COLLAPSE", "MOST_SIMILAR", "ATTRIBUTE_VALUES", 0, "UNEMP_CY;UNEMPRT_CY;ChangeUnempRate", None)

except Exception as e:
    # If unsuccessful, end gracefully by indicating why
    arcpy.AddError('\n' + "Script failed because: \t\t" + e.message )
    # ... and where
    exceptionreport = sys.exc_info()[2]
    fullermessage   = traceback.format_tb(exceptionreport)[0]
    arcpy.AddError("at this location: \n\n" + fullermessage + "\n")
