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

##############################################################summary statistics operations##########################################################
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
arcpy.SubsetFeatures_ga(polygonLayer, "in_memory/worstTract", None, 1, "ABSOLUTE_VALUE")

#Create two dictionaries with values for the worst tract and the summary table 
#dictionary1
values = {}
with arcpy.da.SearchCursor(summaryTable, "*") as cursor:
    for row in cursor:
        i=0
        for field in cursor.fields:
            values[field]=row[i]
            i+=1

#dictionary 2
layerFields = {}
with arcpy.da.SearchCursor("in_memory/worstTract", "*") as cursor2:
    for a_row in cursor2:
        i=0
        for field in cursor2.fields:
            layerFields[field]=a_row[i]
            i+=1

#get matching fields and transfer values from summary statistics table to susbet feature               
for key in values:
    for field in layerFields:
        if key[4:35] == field[:31]:
            with arcpy.da.UpdateCursor("in_memory/worstTract", [field]) as cursor3:
                for f_row in cursor3:
                    f_row[0] = values[key]
                    cursor3.updateRow(f_row) 

#########################################input values############################################################

#get count of variables and use top 25%
featureCount = int(arcpy.GetCount_management(polygonLayer).getOutput(0))

#in this analysis we will only use the worst 25% of tracts for generating homelessness to look at potential sitings for nrew projects           
projCount = ((featureCount)*0.25)

#select top 25% from risk layer 
arcpy.SelectLayerByAttribute_management(polygonLayer, "NEW_SELECTION", "SIM_RANK< {percent}".format(percent=projCount))

#Similarity Search
SS.SimilaritySearch("in_memory/worstTract", polygonLayer, "in_memory/simsearch", "NO_COLLAPSE", "MOST_SIMILAR", "ATTRIBUTE_VALUES", 100, fields)

#clear selection
arcpy.SelectLayerByAttribute_management(polygonLayer, "CLEAR_SELECTION")

#copy features to in memory workspace 
arcpy.CopyFeatures_management(polygonLayer, outputLayer)

#make output layer to use for join 
arcpy.MakeFeatureLayer_management(outputLayer, 'outLayer')

#get objid for new layer
objID = arcpy.da.Describe('outLayer')['OIDFieldName']

###Look into switching similarity result as an appended field back into a layer"
arcpy.AddJoin_management('outLayer', objID, 'in_memory/simsearch', 'CAND_ID')

#############################################################################add field and assign value############################################################

#addField for the project name 
arcpy.AddField_management('outLayer', newField, "Short", 0)

#code block used to change match values to 1
codeBlock = """
def calFld(num, fld):
    if fld < num:
        a = 1
    else:
        a = 0
    return a"""

#calculateNewField
arcpy.CalculateField_management('outLayer', newField, "calFld({numRes}, !SIMRANK!)".format(numRes=finalNum), "PYTHON3",  codeBlock)

#code block used to change null values back to 0
codeBlock2 = """
def updateValue(value):
    if value == None:
        return'0'
    else: return value """

#update values
arcpy.CalculateField_management('outLayer', newField, 'updateValue(!{newField}!)'.format(newField=newField) , "PYTHON3",  codeBlock2)

#remove join 
arcpy.RemoveJoin_management('outLayer')

#except Exception as e:
#    # If unsuccessful, end gracefully by indicating why
#    arcpy.AddError('\n' + "Script failed because: \t\t" + e.message )
#    # ... and where
#    exceptionreport = sys.exc_info()[2]
#    fullermessage   = traceback.format_tb(exceptionreport)[0]
#    arcpy.AddError("at this location: \n\n" + fullermessage + "\n")

