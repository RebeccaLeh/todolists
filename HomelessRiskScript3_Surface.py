"""
THIS SCRIPT RUNS A HOMELESS RISK ANALYSIS

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
        Input Workspace     Workspace           Input
        Output Risk         Feature Layer       Output
        Field Names         Fields              Input
        Output Reference    Feature Layer       Output

7   To later revise any of this, right-click to the tool's name and select Properties.
"""

# Import necessary modules
import sys, os, string, math, arcpy, traceback, numpy
import arcpy.stats as SS

arcpy.env.overwriteOutput = True

try:

    #####################Define Parameters #####################################

    # Request user input of data type = Feature Layer, direction = Input, and
    # Obtained from = (initial prompt for layer name)
    #polygon layer
    polygonLayer = arcpy.GetParameterAsText(0)

    # Request user input of data type = field (multiple), direction = Input, and
    # Obtained from = (initial prompt for field names)
    #fieldnames 
    fieldNames = arcpy.GetParameterAsText(1)
    
    arcpy.AddMessage(fieldNames)
    # Request user input of data type = field (multiple), direction = Intput, and
    # Obtained from = (initial prompt for fields to reverse)
    #otherFields 
    try:
        otherFields = arcpy.GetParameterAsText(2)
    except:
        otherFields = None

    # Request user input of data type = Layer, direction = Output, and
    # Obtained from = (initial prompt for output name)
    #output 
    outputLayer = arcpy.GetParameterAsText(3)

    ################################Run Analysis #####################################################
    #create table to be used by summary statistics
    summaryTable = arcpy.CreateTable_management("in_memory", "table1")

    #Max values to switch direction of any high values to low as specified from the paramter
    def calculate_max(table,field):
        na = arcpy.da.TableToNumPyArray(table,field)
        return numpy.amax(na[field])

    #if otherFields != None: 
    try: 
        list = []
        words = otherFields.split(';')
        for i in words:
            list.append(i)
        for name in words:
            max = calculate_max(polygonLayer, name)
            arcpy.AddMessage(max)
            arcpy.CalculateField_management(polygonLayer, name, '{max}-(!{field}!)'.format(max=100, field=name))
    except:
        pass
    
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
    arcpy.SubsetFeatures_ga(polygonLayer, "worstTract", None, 1, "ABSOLUTE_VALUE")

    #Create two dictionaries with values for the worst tract and the summary table 
    #dictionary 1
    values = {}
    with arcpy.da.SearchCursor(summaryTable, "*") as cursor:
        for row in cursor:
            i=0
            for field in cursor.fields:
                values[field]=row[i]
                i+=1
    #dictionary 2
    layerFields = {}
    with arcpy.da.SearchCursor("worstTract", "*") as cursor2:
        for a_row in cursor2:
            i=0
            for field in cursor2.fields:
                layerFields[field]=a_row[i]
                i+=1
    
    #get matching fields and transfer values from summary statistics table to susbet feature
    for key in values:
        for field in layerFields:
            if key[4:35] == field[:31]:
                with arcpy.da.UpdateCursor("worstTract", [field]) as cursor3:
                    arcpy.AddMessage(cursor3)
                    for f_row in cursor3:
                        f_row[0] = values[key]
                        cursor3.updateRow(f_row) 
    
    ##Similarity Search
    SS.SimilaritySearch("worstTract", polygonLayer, "in_memory/simsearch", "NO_COLLAPSE", "MOST_SIMILAR", "ATTRIBUTE_VALUES", 0, fieldNames)

    #in memory input
    arcpy.CopyFeatures_management(polygonLayer, outputLayer)

    #make layer of input or addjoin
    arcpy.MakeFeatureLayer_management(outputLayer, 'outLayer')

    #fields to add to output
    newFields = "SIM_RANK", "SIM_INDEX", "LABEL_RANK", "CANDID"
    
    #get OBJID for both layers to use in join
    objID = arcpy.da.Describe('outLayer')['OIDFieldName']
    objIDinMEM = arcpy.da.Describe("in_memory/simsearch")['OIDFieldName']

    #Join two tables together and transfer fields over to output
    arcpy.AddJoin_management('outLayer', objID, "in_memory/simsearch", "CAND_ID")
    arcpy.CalculateField_management('outLayer', "SIM_RANK", "!SIMRANK!", "PYTHON3")
    arcpy.CalculateField_management('outLayer', "SIM_INDEX", "!SIMINDEX!", "PYTHON3")
    arcpy.CalculateField_management('outLayer', "LABEL_RANK", "!LABELRANK!", "PYTHON3")
    arcpy.CalculateField_management('outLayer', "CANDID", "!CAND_ID!", "PYTHON3")

    #remove the join adn move to a permament output file
    arcpy.RemoveJoin_management('outLayer')

except Exception as e:
    # If unsuccessful, end gracefully by indicating why
    arcpy.AddError('\n' + "Script failed because: \t\t" + e.message )
    # ... and where
    exceptionreport = sys.exc_info()[2]
    fullermessage   = traceback.format_tb(exceptionreport)[0]
    arcpy.AddError("at this location: \n\n" + fullermessage + "\n")
