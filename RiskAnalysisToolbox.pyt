import sys, os, string, math, arcpy, traceback, numpy
import arcpy.stats as SS

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [RiskLayer, pointtoPoly, newSurface]


class pointtoPoly(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Add point data"
        self.description = "This tool creates a risk surface"
        self.canRunInBackground = False

    def getParameterInfo(self):
        polygon = arcpy.Parameter(
            displayName = "Input Census",
            name = "in_features",
            datatype = "GPFeatureLayer",
            parameterType = "Required",
            direction = "Input")
        polygon.filter.list = ["Polygon"]

        domestic = arcpy.Parameter(
            displayName = "Domestic Violence",
            name = "domestic",
            datatype = "GPFeatureLayer",
            parameterType = "Optional",
            direction = "Input")
        domestic.filter.list = ["Multipoint"]

        mental = arcpy.Parameter(
            displayName = "Severe Mental Illness",
            name = "mental",
            datatype = "GPFeatureLayer",
            parameterType = "Optional",
            direction = "Input")
        mental.filter.list = ["Multipoint"]

        substance = arcpy.Parameter(
            displayName = "Substance Abuse",
            name = "substance",
            datatype = "GPFeatureLayer",
            parameterType = "Optional",
            direction = "Input")
        substance.filter.list = ["Multipoint"]

        addit = arcpy.Parameter(
            displayName = "Additional Related Data",
            datatype = "GPFeatureLayer",
            parameterType = "Optional",
            direction = "Input")
        addit.filter.list = ["Multipoint"]

        output = arcpy.Parameter(
            displayName="Output Polygon",
            name="out_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")

        params = [polygon, domestic, mental, substance, addit, output]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return 

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        polygon, domestic, mental, substance, addit, output = parameters

        #create an output layer
        arcpy.CopyFeatures_management(polygonLayer, outputLayer)
        arcpy.MakeFeatureLayer_management(outputLayer, 'output')

        #get objID value for join layer
        objID = arcpy.da.Describe('output')['OIDFieldName']

        #using parameter attributes, look for data in all point fields, if data exists, write new field to output
        #and assign value based on spatial join 
        for x in parameters[1:-1]:
            if x.value:
                mem = "in_memory/"+(x.name)
                arcpy.AddMessage(mem)
                arcpy.SpatialJoin_analysis('output', (x.valueAsText), mem)
                arcpy.AddJoin_management('output', objID, mem, 'TARGET_FID')
                arcpy.AddField_management('output',(str(x.name)),  "LONG", field_alias=(x.displayName)) 
                arcpy.CalculateField_management('output', (str(x.name)), "!Join_Count!", "PYTHON3")
                arcpy.RemoveJoin_management('output')   
        return 

class RiskLayer(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Risk Layer"
        self.description = "This tool creates a risk surface"
        self.canRunInBackground = False

    def getParameterInfo(self):
        inputLayer = arcpy.Parameter(
            displayName = "Input Census",
            name = "in_features",
            datatype = "GPFeatureLayer",
            parameterType = "Required",
            direction = "Input")
        inputLayer.filter.list = ["Polygon"]

        riskFactors = arcpy.Parameter(
            displayName="Risk Factors",
            name="risk_factors",
            datatype="Field",
            parameterType="Required",
            direction="Input",
            multiValue=True)
        riskFactors.filter.list
        
        riskFactors.parameterDependencies = [inputLayer.name]

        revFields = arcpy.Parameter(
            displayName="Reverse Values of Specified Fields",
            name="reverseFields",
            datatype="Field",
            parameterType="Optional",
            direction="Input",
            multiValue=True)
        inputLayer.filter.list

        revFields.parameterDependencies = [inputLayer.name]

        # Third parameter
        outputLayer = arcpy.Parameter(
            displayName="Output Features",
            name="out_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")

        params = [inputLayer, riskFactors, revFields, outputLayer]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        inputLayer, riskFactors, revFields, outputLayer = parameters

        polygonLayer = inputLayer.valueAsText

        fieldNames = riskFactors.valueAsText

        if revFields.value:
            otherFields = revFields.valueAsText
        
        outputLayer = outputLayer.valueAsText
        
       #####################################create sum statistics and assing values to new polygon #####################################################
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
                arcpy.CalculateField_management(polygonLayer, name, 'max-(!{field}!)'.format(field=name))
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
       
       ##################################### Run Similarity Search #####################################################

        ##Similarity Search
        SS.SimilaritySearch("worstTract", polygonLayer, "in_memory/simsearch", "NO_COLLAPSE", "MOST_SIMILAR", "ATTRIBUTE_VALUES", 0, fieldNames)

       ##################################### write to output file #####################################################
       
        #in memory input
        arcpy.CopyFeatures_management(polygonLayer, outputLayer)

        #make layer of input or addjoin
        arcpy.MakeFeatureLayer_management(outputLayer, 'outLayer')

        #fields to add to output
        arcpy.AddField_management("outLayer", "SIM_RANK", "LONG", field_alias='Risk Rank')
        arcpy.AddField_management("outLayer", "CANDID", "LONG", field_alias='Matching OBJID')

        #get OBJID for both layers to use in join
        objID = arcpy.da.Describe('outLayer')['OIDFieldName']
        objIDinMEM = arcpy.da.Describe("in_memory/simsearch")['OIDFieldName']

        #Join two tables together and transfer fields over to output
        arcpy.AddJoin_management('outLayer', objID, "in_memory/simsearch", "CAND_ID")
        arcpy.CalculateField_management('outLayer', "SIM_RANK", "!SIMRANK!", "PYTHON3")
        arcpy.CalculateField_management('outLayer', "CANDID", "!CAND_ID!", "PYTHON3")

        #remove the join adn move to a permament output file
        arcpy.RemoveJoin_management('outLayer')

        return

class newSurface(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "New Surface"
        self.description = "This tool creates a risk surface"
        self.canRunInBackground = True

    def getParameterInfo(self):
        polygon = arcpy.Parameter(
            displayName = "Polygon Layer",
            name = "polygonLayer",
            datatype = "GPFeatureLayer",
            parameterType = "Required",
            direction = "Input")
        polygon.filter.list = ["Polygon"]

        flds = arcpy.Parameter(
            displayName="Fields",
            name="fieldNames",
            datatype="Field",
            parameterType="Required",
            direction="Input",
            multiValue=True)
        flds.filter.list
        flds.parameterDependencies = [polygon.name]

        newFld = arcpy.Parameter(
            displayName="New Indicator Name",
            name="newIndicator",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        finNum = arcpy.Parameter(
            displayName="Number of Results",
            name="numResults",
            datatype="GPLong",
            parameterType="Required",
            direction="Input")

        outFeats = arcpy.Parameter(
            displayName="Output Features",
            name="out_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")

        params = [polygon, flds, newFld, finNum, outFeats]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        polygon, flds, newfld, finNum, outFeats = parameters

        #rename parameters to match code 
        polygonLayer = polygon.valueAsText
        fields = flds.valueAsText
        newField = newfld.valueAsText
        finalNum = finNum.valueAsText
        outputLayer = outFeats.valueAsText

        ##############################################################summary statistics, new polygon with sum values##########################################################
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

        #########################################use 25% of input to run similarity search ############################################################

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

        #############################################################################add field and assign value############################################################
        #copy features to in memory workspace 
        arcpy.CopyFeatures_management(polygonLayer, outputLayer)

        #make output layer to use for join 
        arcpy.MakeFeatureLayer_management(outputLayer, 'outLayer')

        #get objid for new layer
        objID = arcpy.da.Describe('outLayer')['OIDFieldName']

        ###Look into switching similarity result as an appended field back into a layer"
        arcpy.AddJoin_management('outLayer', objID, 'in_memory/simsearch', 'CAND_ID')

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

        return