import sys, os, string, math, arcpy, traceback, numpy, json, tempfile
import arcpy.stats as SS

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [CreateHomelessnessRiskSurface, ProgramDesign, ProgramRankings]

###############################################################################################################################
############################################################### RISK LAYER #########################################################
#################################################################################################################################

class CreateHomelessnessRiskSurface(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Create Homelessness Risk Surface"
        self.description = "This tool creates a risk surface"
        self.canRunInBackground = False

    def getParameterInfo(self):
        inputLayer = arcpy.Parameter(
            displayName = "Input Features",
            name = "in_features",
            datatype = "GPFeatureLayer",
            parameterType = "Required",
            direction = "Input")
        inputLayer.filter.list = ["Polygon"]

        outputLayer = arcpy.Parameter(
            displayName="Output Feature Layer",
            name="out_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")

        riskFactors = arcpy.Parameter(
            displayName="Risk Factors (High Value)",
            name="risk_factors",
            datatype="Field",
            parameterType="Required",
            direction="Input",
            multiValue=True)
        riskFactors.filter.list = ["Long", "Short", "Double", "Single"]
        riskFactors.parameterDependencies = [inputLayer.name]

        revFields = arcpy.Parameter(
            displayName="Risk Factors (Low Value)",
            name="reverse_fields",
            datatype="Field",
            parameterType="Optional",
            direction="Input",
            multiValue=True)
        revFields.filter.list = ["Long", "Short", "Double", "Single"] 
        revFields.parameterDependencies = [inputLayer.name]

        params = [inputLayer, outputLayer, riskFactors, revFields]

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
        inputLayer, outputLayer, riskFactors, revFields  = parameters

        polygonLayer = inputLayer.valueAsText

        fieldNames = riskFactors.valueAsText

        if revFields.value:
            otherFields = revFields.valueAsText
        
        outputLayer = outputLayer.valueAsText
        
       #####################################create sum statistics and assing values to new polygon #####################################################
        arcpy.SetProgressorLabel("Finding worst values for each risk factor..") 
       
       #create table to be used by summary statistics
        summaryTable = arcpy.CreateTable_management("in_memory", "table1")

        #Max values to switch direction of any high values to low as specified from the paramter
        def calculate_max(table,field):
            na = arcpy.da.TableToNumPyArray(table,field)
            return numpy.amax(na[field])

        #if otherFields != None: 
        try: 
            rev_fields = otherFields.split(';')
            for name in rev_fields:
                maxNum = calculate_max(polygonLayer, name)
                arcpy.CalculateField_management(polygonLayer, name, '{maxi}-(!{field}!)'.format(maxi=maxNum, field=name))
        except:
            pass
    
        # Create list of values to use in summary statistics 
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
        arcpy.SubsetFeatures_ga(polygonLayer, "in_memory/worstTract", None, 1, "ABSOLUTE_VALUE")

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
        with arcpy.da.SearchCursor("in_memory/worstTract", "*") as cursor2:
            for a_row in cursor2:
                i=0
                for field in cursor2.fields:
                    layerFields[field]=a_row[i]
                    i+=1
    
        #get matching fields and transfer values from summary statistics table to subset feature
        #compare the field names, because sum stats adds MAX_ to the beginning of each field name we use substrings
        for key in values:
            for field in layerFields:
                if key[4:35] == field[:31]:
                    with arcpy.da.UpdateCursor("in_memory/worstTract", [field]) as cursor3:
                        for f_row in cursor3:
                            f_row[0] = values[key]
                            cursor3.updateRow(f_row) 
       
       ##################################### Run Similarity Search #####################################################
        arcpy.SetProgressorLabel("Ranking each polygon based on your risk factors ...") 

        ##Similarity Search
        SS.SimilaritySearch("in_memory/worstTract", polygonLayer, "in_memory/simsearch", "NO_COLLAPSE", "MOST_SIMILAR", "ATTRIBUTE_VALUES", 0, fieldNames)

       ##################################### write to output file #####################################################
       
        #in memory input
        arcpy.CopyFeatures_management(polygonLayer, outputLayer)

        #make layer of input or addjoin
        arcpy.MakeFeatureLayer_management(outputLayer, 'outLayer')

        arcpy.SetProgressorLabel("Writing ranked list to a new output feature layer...") 

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


####################################tell user which nulls were not included using a warning ########################################
        nextLs = fieldNames.replace(";"," IS NULL Or ")
        nextLs = nextLs +" IS NULL"
        arcpy.SelectLayerByAttribute_management(polygonLayer, "NEW_SELECTION", nextLs)
       
        desc = arcpy.Describe(polygonLayer)
        if len(desc.FIDSet)>0:
            arcpy.AddWarning("The following features contained Null values and were excluded from the analysis: {}".format(desc.FIDSet.split(";")))
        arcpy.SelectLayerByAttribute_management(polygonLayer, "CLEAR_SELECTION")

        #################################### set symbology ########################################

        symbJSON = r'{"type":"CIMLayerDocument","version":"2.2.0","build":12813,"layers":["CIMPATH=map1/emptytracts_enrichlayer_risk.xml"],"layerDefinitions":[{"type":"CIMFeatureLayer","name":"symbologyLyr","uRI":"CIMPATH=map1/emptytracts_enrichlayer_risk.xml","sourceModifiedTime":{"type":"TimeInstant"},"useSourceMetadata":true,"description":"EmptyTracts_EnrichLayer_Risk","layerElevation":{"type":"CIMLayerElevationSurface","mapElevationID":"{94F1530C-B20A-4243-9E54-E59918C40C96}"},"expanded":true,"layerType":"Operational","showLegends":true,"visibility":true,"displayCacheType":"Permanent","maxDisplayCacheAge":5,"showPopups":true,"serviceLayerID":-1,"refreshRate":-1,"refreshRateUnit":"esriTimeUnitsSeconds","autoGenerateFeatureTemplates":true,"featureElevationExpression":"0","featureTable":{"type":"CIMFeatureTable","displayField":"TRACT","editable":true,"dataConnection":{"type":"CIMStandardDataConnection","workspaceConnectionString":"DATABASE=.\\MyProject.gdb","workspaceFactory":"FileGDB","dataset":"EmptyTracts_EnrichLayer_Risk","datasetType":"esriDTFeatureClass"},"studyAreaSpatialRel":"esriSpatialRelUndefined","searchOrder":"esriSearchOrderSpatial"},"htmlPopupEnabled":true,"selectable":true,"featureCacheType":"Session","labelClasses":[{"type":"CIMLabelClass","expression":"$feature.TRACT","expressionEngine":"Arcade","featuresToLabel":"AllVisibleFeatures","maplexLabelPlacementProperties":{"type":"CIMMaplexLabelPlacementProperties","featureType":"Polygon","avoidPolygonHoles":true,"canOverrunFeature":true,"canPlaceLabelOutsidePolygon":true,"canRemoveOverlappingLabel":true,"canStackLabel":true,"connectionType":"Unambiguous","constrainOffset":"NoConstraint","contourAlignmentType":"Page","contourLadderType":"Straight","contourMaximumAngle":90,"enableConnection":true,"featureWeight":0,"fontHeightReductionLimit":4,"fontHeightReductionStep":0.5,"fontWidthReductionLimit":90,"fontWidthReductionStep":5,"graticuleAlignmentType":"Straight","keyNumberGroupName":"Default","labelBuffer":15,"labelLargestPolygon":false,"labelPriority":-1,"labelStackingProperties":{"type":"CIMMaplexLabelStackingProperties","stackAlignment":"ChooseBest","maximumNumberOfLines":3,"minimumNumberOfCharsPerLine":3,"maximumNumberOfCharsPerLine":24,"separators":[{"type":"CIMMaplexStackingSeparator","separator":" ","splitAfter":true},{"type":"CIMMaplexStackingSeparator","separator":",","visible":true,"splitAfter":true}]},"lineFeatureType":"General","linePlacementMethod":"OffsetCurvedFromLine","maximumLabelOverrun":80,"maximumLabelOverrunUnit":"Point","minimumFeatureSizeUnit":"Map","multiPartOption":"OneLabelPerPart","offsetAlongLineProperties":{"type":"CIMMaplexOffsetAlongLineProperties","placementMethod":"BestPositionAlongLine","labelAnchorPoint":"CenterOfLabel","distanceUnit":"Percentage","useLineDirection":true},"pointExternalZonePriorities":{"type":"CIMMaplexExternalZonePriorities","aboveLeft":4,"aboveCenter":2,"aboveRight":1,"centerRight":3,"belowRight":5,"belowCenter":7,"belowLeft":8,"centerLeft":6},"pointPlacementMethod":"AroundPoint","polygonAnchorPointType":"GeometricCenter","polygonBoundaryWeight":0,"polygonExternalZones":{"type":"CIMMaplexExternalZonePriorities","aboveLeft":4,"aboveCenter":2,"aboveRight":1,"centerRight":3,"belowRight":5,"belowCenter":7,"belowLeft":8,"centerLeft":6},"polygonFeatureType":"General","polygonInternalZones":{"type":"CIMMaplexInternalZonePriorities","center":1},"polygonPlacementMethod":"HorizontalInPolygon","primaryOffset":1,"primaryOffsetUnit":"Point","removeExtraWhiteSpace":true,"repetitionIntervalUnit":"Map","rotationProperties":{"type":"CIMMaplexRotationProperties","rotationType":"Arithmetic","alignmentType":"Straight"},"secondaryOffset":100,"strategyPriorities":{"type":"CIMMaplexStrategyPriorities","stacking":1,"overrun":2,"fontCompression":3,"fontReduction":4,"abbreviation":5},"thinningDistanceUnit":"Point","truncationMarkerCharacter":".","truncationMinimumLength":1,"truncationPreferredCharacters":"aeiou"},"name":"Class 1","priority":-1,"standardLabelPlacementProperties":{"type":"CIMStandardLabelPlacementProperties","featureType":"Line","featureWeight":"Low","labelWeight":"High","numLabelsOption":"OneLabelPerName","lineLabelPosition":{"type":"CIMStandardLineLabelPosition","above":true,"inLine":true,"parallel":true},"lineLabelPriorities":{"type":"CIMStandardLineLabelPriorities","aboveStart":3,"aboveAlong":3,"aboveEnd":3,"centerStart":3,"centerAlong":3,"centerEnd":3,"belowStart":3,"belowAlong":3,"belowEnd":3},"pointPlacementMethod":"AroundPoint","pointPlacementPriorities":{"type":"CIMStandardPointPlacementPriorities","aboveLeft":2,"aboveCenter":2,"aboveRight":1,"centerLeft":3,"centerRight":2,"belowLeft":3,"belowCenter":3,"belowRight":2},"rotationType":"Arithmetic","polygonPlacementMethod":"AlwaysHorizontal"},"textSymbol":{"type":"CIMSymbolReference","symbol":{"type":"CIMTextSymbol","blockProgression":"TTB","depth3D":1,"extrapolateBaselines":true,"fontEffects":"Normal","fontEncoding":"Unicode","fontFamilyName":"Tahoma","fontStyleName":"Regular","fontType":"Unspecified","haloSize":1,"height":10,"hinting":"Default","horizontalAlignment":"Left","kerning":true,"letterWidth":100,"ligatures":true,"lineGapType":"ExtraLeading","symbol":{"type":"CIMPolygonSymbol","symbolLayers":[{"type":"CIMSolidFill","enable":true,"color":{"type":"CIMRGBColor","values":[0,0,0,100]}}]},"textCase":"Normal","textDirection":"LTR","verticalAlignment":"Bottom","verticalGlyphOrientation":"Right","wordSpacing":100,"billboardMode3D":"FaceNearPlane"}},"useCodedValue":true,"visibility":true,"iD":-1}],"renderer":{"type":"CIMClassBreaksRenderer","barrierWeight":"High","breaks":[{"type":"CIMClassBreak","label":"≤391","patch":"Default","symbol":{"type":"CIMSymbolReference","symbol":{"type":"CIMPolygonSymbol","symbolLayers":[{"type":"CIMSolidFill","enable":true,"color":{"type":"CIMRGBColor","values":[240,249,232,100]}}]}},"upperBound":391},{"type":"CIMClassBreak","label":"≤782","patch":"Default","symbol":{"type":"CIMSymbolReference","symbol":{"type":"CIMPolygonSymbol","symbolLayers":[{"type":"CIMSolidFill","enable":true,"color":{"type":"CIMRGBColor","values":[204,235,197,100]}}]}},"upperBound":782},{"type":"CIMClassBreak","label":"≤1173","patch":"Default","symbol":{"type":"CIMSymbolReference","symbol":{"type":"CIMPolygonSymbol","symbolLayers":[{"type":"CIMSolidFill","enable":true,"color":{"type":"CIMRGBColor","values":[168,221,181,100]}}]}},"upperBound":1173},{"type":"CIMClassBreak","label":"≤1563","patch":"Default","symbol":{"type":"CIMSymbolReference","symbol":{"type":"CIMPolygonSymbol","symbolLayers":[{"type":"CIMSolidStroke","enable":true,"capStyle":"Round","joinStyle":"Round","lineStyle3D":"Strip","miterLimit":10,"width":0.7,"color":{"type":"CIMRGBColor","values":[110,110,110,0]}},{"type":"CIMSolidFill","enable":true,"color":{"type":"CIMRGBColor","values":[123,204,196,100]}}]}},"upperBound":1563},{"type":"CIMClassBreak","label":"≤1953","patch":"Default","symbol":{"type":"CIMSymbolReference","symbol":{"type":"CIMPolygonSymbol","symbolLayers":[{"type":"CIMSolidStroke","enable":true,"capStyle":"Round","joinStyle":"Round","lineStyle3D":"Strip","miterLimit":10,"width":0.7,"color":{"type":"CIMRGBColor","values":[110,110,110,0]}},{"type":"CIMSolidFill","enable":true,"color":{"type":"CIMRGBColor","values":[67,162,202,100]}}]}},"upperBound":1953},{"type":"CIMClassBreak","label":"≤2343","patch":"Default","symbol":{"type":"CIMSymbolReference","symbol":{"type":"CIMPolygonSymbol","symbolLayers":[{"type":"CIMSolidStroke","enable":true,"capStyle":"Round","joinStyle":"Round","lineStyle3D":"Strip","miterLimit":10,"width":0.7,"color":{"type":"CIMRGBColor","values":[110,110,110,0]}},{"type":"CIMSolidFill","enable":true,"color":{"type":"CIMRGBColor","values":[8,104,172,100]}}]}},"upperBound":2343}],"classBreakType":"GraduatedColor","classificationMethod":"Quantile","colorRamp":{"type":"CIMFixedColorRamp","colorSpace":{"type":"CIMICCColorSpace","url":"Default RGB"},"colors":[{"type":"CIMRGBColor","colorSpace":{"type":"CIMICCColorSpace","url":"Default RGB"},"values":[240,249,232,100]},{"type":"CIMRGBColor","colorSpace":{"type":"CIMICCColorSpace","url":"Default RGB"},"values":[204,235,197,100]},{"type":"CIMRGBColor","colorSpace":{"type":"CIMICCColorSpace","url":"Default RGB"},"values":[168,221,181,100]},{"type":"CIMRGBColor","colorSpace":{"type":"CIMICCColorSpace","url":"Default RGB"},"values":[123,204,196,100]},{"type":"CIMRGBColor","colorSpace":{"type":"CIMICCColorSpace","url":"Default RGB"},"values":[67,162,202,100]},{"type":"CIMRGBColor","colorSpace":{"type":"CIMICCColorSpace","url":"Default RGB"},"values":[8,104,172,100]}]},"field":"SIM_RANK","minimumBreak":1,"numberFormat":{"type":"CIMNumericFormat","alignmentOption":"esriAlignLeft","alignmentWidth":0,"roundingOption":"esriRoundNumberOfDecimals","roundingValue":0,"zeroPad":true},"showInAscendingOrder":false,"heading":"Risk Rank","sampleSize":10000,"defaultSymbol":{"type":"CIMSymbolReference","symbol":{"type":"CIMPolygonSymbol","symbolLayers":[{"type":"CIMSolidStroke","enable":true,"capStyle":"Round","joinStyle":"Round","lineStyle3D":"Strip","miterLimit":10,"width":0.7,"color":{"type":"CIMRGBColor","values":[110,110,110,100]}},{"type":"CIMSolidFill","enable":true,"color":{"type":"CIMRGBColor","values":[130,130,130,100]}}]}},"defaultLabel":"<out of range>","polygonSymbolColorTarget":"Fill","exclusionLabel":"<excluded>","exclusionSymbol":{"type":"CIMSymbolReference","symbol":{"type":"CIMPolygonSymbol","symbolLayers":[{"type":"CIMSolidStroke","enable":true,"capStyle":"Round","joinStyle":"Round","lineStyle3D":"Strip","miterLimit":10,"width":0.7,"color":{"type":"CIMRGBColor","values":[110,110,110,100]}},{"type":"CIMSolidFill","enable":true,"color":{"type":"CIMRGBColor","values":[255,0,0,100]}}]}},"useExclusionSymbol":false,"normalizationType":"Nothing"},"scaleSymbols":true,"snappable":true,"symbolLayerDrawing":{"type":"CIMSymbolLayerDrawing"}}],"elevationSurfaces":[{"type":"CIMMapElevationSurface","elevationMode":"BaseGlobeSurface","name":"Ground","verticalExaggeration":1,"mapElevationID":"{94F1530C-B20A-4243-9E54-E59918C40C96}","color":{"type":"CIMRGBColor","values":[255,255,255,100]},"surfaceTINShadingMode":"Smooth","visibility":true}]}'

        lyrx_json = symbJSON
        #use temporary file location to create json file and dump in script as json text
        with tempfile.NamedTemporaryFile(delete=False) as temp_lyrx:
            temp_lyrx.write(lyrx_json.encode())
        #rename file to appropriate name with lyrx ending
        lyrx_path = "{0}.lyrx".format(temp_lyrx.name)
        os.rename(temp_lyrx.name, lyrx_path)
        #set paramter symbology
        parameters[1].symbology = lyrx_path



###############################################################################################################################
############################################################### PROGRAM DESIGN #########################################################
#################################################################################################################################

class ProgramDesign(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Program Design"
        self.description = "This tool creates a risk surface"
        self.canRunInBackground = False

    def getParameterInfo(self):
        polygon = arcpy.Parameter(
            displayName = "Input Features",
            name = "polygon _layer",
            datatype = "GPFeatureLayer",
            parameterType = "Required",
            direction = "Input")
        polygon.filter.list = ["Polygon"]

        outFeats = arcpy.Parameter(
            displayName="Output Feature Layer",
            name="out_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")

        flds = arcpy.Parameter(
            displayName="Contributing factors",
            name="field_names",
            datatype="Field",
            parameterType="Required",
            direction="Input",
            multiValue=True)
        flds.filter.list = ["Long", "Short", "Double", "Single"]
        flds.parameterDependencies = [polygon.name]

        newFld = arcpy.Parameter(
            displayName="Program Name",
            name="new_indicator",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        finNum = arcpy.Parameter(
            displayName="Number of Results",
            name="num_results",
            datatype="GPLong",
            parameterType="Required",
            direction="Input")

        params = [polygon, outFeats, flds, newFld, finNum]

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
        polygon, outFeats, flds, newfld, finNum = parameters

        #rename parameters to match code 
        polygonLayer = polygon.valueAsText
        fields = flds.valueAsText
        aliasName = newfld.valueAsText
        finalNum = finNum.valueAsText
        outputLayer = outFeats.valueAsText

        ##############################################################summary statistics, new polygon with sum values##########################################################
        arcpy.SetProgressorLabel("Finding the highest possible values for each risk factor...") 

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
        #compare the field names, because sum stats adds MAX_ to the beginning of each field name we use substrings
        
        for key in values:
            for field in layerFields:
                if key[4:35] == field[:31]:
                    with arcpy.da.UpdateCursor("in_memory/worstTract", [field]) as cursor3:
                        for f_row in cursor3:
                            f_row[0] = values[key]
                            cursor3.updateRow(f_row) 

        #########################################use 25% of input to run similarity search ############################################################
        arcpy.SetProgressorLabel("Ranking result polygons against risk factors...") 

        #get count of variables and use top 25%
        featureCount = int(arcpy.GetCount_management(polygonLayer).getOutput(0))

        #select top 25% from risk layer 
        arcpy.SelectLayerByAttribute_management(polygonLayer, "NEW_SELECTION", "SIM_RANK< {percent}".format(percent=finalNum))

        #Similarity Search
        SS.SimilaritySearch("in_memory/worstTract", polygonLayer, "in_memory/simsearch", "NO_COLLAPSE", "MOST_SIMILAR", "ATTRIBUTE_VALUES", 0, fields)

        #clear selection
        arcpy.SelectLayerByAttribute_management(polygonLayer, "CLEAR_SELECTION")

        #############################################################################add field and assign value############################################################
        arcpy.SetProgressorLabel("Adding new program name field to your output feature layer...") 

        #copy features to in memory workspace 
        arcpy.CopyFeatures_management(polygonLayer, outputLayer)

        #make output layer to use for join 
        arcpy.MakeFeatureLayer_management(outputLayer, 'outLayer')

        #get objid for new layer
        objID = arcpy.da.Describe('outLayer')['OIDFieldName']

        ###Look into switching similarity result as an appended field back into a layer"
        arcpy.AddJoin_management('outLayer', objID, 'in_memory/simsearch', 'CAND_ID')

        fieldName = arcpy.ValidateFieldName(aliasName)

        #addField for the program name 
        arcpy.AddField_management('outLayer', fieldName, "Short", "","", "",aliasName)
        
        arcpy.SetProgressorLabel("Assigning a ranked value to each result polygon...") 

        #calculateNewField
        #arcpy.CalculateField_management('outLayer', fieldNa,"!SIMRANK!", "PYTHON3",  codeBlock)

        #code block used to change null values back to 0
        codeBlock2 = """
def updateValue(value):
    if value == None:
        return None
    else: return value """

        #update values
        arcpy.CalculateField_management('outLayer', fieldName, 'updateValue(!SIMRANK!)', "PYTHON3",  codeBlock2)

        #remove join 
        arcpy.RemoveJoin_management('outLayer')

        ######################Change Field Name used in Symbology Layer#####################################################
        symbJSON2 = r'{"type":"CIMLayerDocument","version":"2.2.0","build":12813,"layers":["CIMPATH=homelessness_prevetion/enrichedpolicedistricts_risk11.xml"],"layerDefinitions":[{"type":"CIMFeatureLayer","name":"EnrichedPoliceDistricts_Risk11","uRI":"CIMPATH=homelessness_prevetion/enrichedpolicedistricts_risk11.xml","sourceModifiedTime":{"type":"TimeInstant"},"useSourceMetadata":true,"description":"EnrichedPoliceDistricts_Risk11","layerElevation":{"type":"CIMLayerElevationSurface","mapElevationID":"{32AD7EE0-C78E-4D6D-9A31-F9A889D70571}"},"expanded":true,"layerType":"Operational","showLegends":true,"visibility":true,"displayCacheType":"Permanent","maxDisplayCacheAge":5,"showPopups":true,"serviceLayerID":-1,"refreshRate":-1,"refreshRateUnit":"esriTimeUnitsSeconds","autoGenerateFeatureTemplates":true,"featureElevationExpression":"0","featureTable":{"type":"CIMFeatureTable","displayField":"District","editable":true,"dataConnection":{"type":"CIMStandardDataConnection","workspaceConnectionString":"DATABASE=.\\homelessprevention.gdb","workspaceFactory":"FileGDB","dataset":"EnrichedPoliceDistricts_Risk11","datasetType":"esriDTFeatureClass"},"studyAreaSpatialRel":"esriSpatialRelUndefined","searchOrder":"esriSearchOrderSpatial"},"htmlPopupEnabled":true,"selectable":true,"featureCacheType":"Session","labelClasses":[{"type":"CIMLabelClass","expression":"$feature.TRACT","expressionEngine":"Arcade","featuresToLabel":"AllVisibleFeatures","maplexLabelPlacementProperties":{"type":"CIMMaplexLabelPlacementProperties","featureType":"Polygon","avoidPolygonHoles":true,"canOverrunFeature":true,"canPlaceLabelOutsidePolygon":true,"canRemoveOverlappingLabel":true,"canStackLabel":true,"connectionType":"Unambiguous","constrainOffset":"NoConstraint","contourAlignmentType":"Page","contourLadderType":"Straight","contourMaximumAngle":90,"enableConnection":true,"featureWeight":0,"fontHeightReductionLimit":4,"fontHeightReductionStep":0.5,"fontWidthReductionLimit":90,"fontWidthReductionStep":5,"graticuleAlignmentType":"Straight","keyNumberGroupName":"Default","labelBuffer":15,"labelLargestPolygon":false,"labelPriority":-1,"labelStackingProperties":{"type":"CIMMaplexLabelStackingProperties","stackAlignment":"ChooseBest","maximumNumberOfLines":3,"minimumNumberOfCharsPerLine":3,"maximumNumberOfCharsPerLine":24,"separators":[{"type":"CIMMaplexStackingSeparator","separator":" ","splitAfter":true},{"type":"CIMMaplexStackingSeparator","separator":",","visible":true,"splitAfter":true}]},"lineFeatureType":"General","linePlacementMethod":"OffsetCurvedFromLine","maximumLabelOverrun":80,"maximumLabelOverrunUnit":"Point","minimumFeatureSizeUnit":"Map","multiPartOption":"OneLabelPerPart","offsetAlongLineProperties":{"type":"CIMMaplexOffsetAlongLineProperties","placementMethod":"BestPositionAlongLine","labelAnchorPoint":"CenterOfLabel","distanceUnit":"Percentage","useLineDirection":true},"pointExternalZonePriorities":{"type":"CIMMaplexExternalZonePriorities","aboveLeft":4,"aboveCenter":2,"aboveRight":1,"centerRight":3,"belowRight":5,"belowCenter":7,"belowLeft":8,"centerLeft":6},"pointPlacementMethod":"AroundPoint","polygonAnchorPointType":"GeometricCenter","polygonBoundaryWeight":0,"polygonExternalZones":{"type":"CIMMaplexExternalZonePriorities","aboveLeft":4,"aboveCenter":2,"aboveRight":1,"centerRight":3,"belowRight":5,"belowCenter":7,"belowLeft":8,"centerLeft":6},"polygonFeatureType":"General","polygonInternalZones":{"type":"CIMMaplexInternalZonePriorities","center":1},"polygonPlacementMethod":"HorizontalInPolygon","primaryOffset":1,"primaryOffsetUnit":"Point","removeExtraWhiteSpace":true,"repetitionIntervalUnit":"Map","rotationProperties":{"type":"CIMMaplexRotationProperties","rotationType":"Arithmetic","alignmentType":"Straight"},"secondaryOffset":100,"strategyPriorities":{"type":"CIMMaplexStrategyPriorities","stacking":1,"overrun":2,"fontCompression":3,"fontReduction":4,"abbreviation":5},"thinningDistanceUnit":"Point","truncationMarkerCharacter":".","truncationMinimumLength":1,"truncationPreferredCharacters":"aeiou"},"name":"Class 1","priority":-1,"standardLabelPlacementProperties":{"type":"CIMStandardLabelPlacementProperties","featureType":"Line","featureWeight":"Low","labelWeight":"High","numLabelsOption":"OneLabelPerName","lineLabelPosition":{"type":"CIMStandardLineLabelPosition","above":true,"inLine":true,"parallel":true},"lineLabelPriorities":{"type":"CIMStandardLineLabelPriorities","aboveStart":3,"aboveAlong":3,"aboveEnd":3,"centerStart":3,"centerAlong":3,"centerEnd":3,"belowStart":3,"belowAlong":3,"belowEnd":3},"pointPlacementMethod":"AroundPoint","pointPlacementPriorities":{"type":"CIMStandardPointPlacementPriorities","aboveLeft":2,"aboveCenter":2,"aboveRight":1,"centerLeft":3,"centerRight":2,"belowLeft":3,"belowCenter":3,"belowRight":2},"rotationType":"Arithmetic","polygonPlacementMethod":"AlwaysHorizontal"},"textSymbol":{"type":"CIMSymbolReference","symbol":{"type":"CIMTextSymbol","blockProgression":"TTB","depth3D":1,"extrapolateBaselines":true,"fontEffects":"Normal","fontEncoding":"Unicode","fontFamilyName":"Tahoma","fontStyleName":"Regular","fontType":"Unspecified","haloSize":1,"height":10,"hinting":"Default","horizontalAlignment":"Left","kerning":true,"letterWidth":100,"ligatures":true,"lineGapType":"ExtraLeading","symbol":{"type":"CIMPolygonSymbol","symbolLayers":[{"type":"CIMSolidFill","enable":true,"color":{"type":"CIMRGBColor","values":[0,0,0,100]}}]},"textCase":"Normal","textDirection":"LTR","verticalAlignment":"Bottom","verticalGlyphOrientation":"Right","wordSpacing":100,"billboardMode3D":"FaceNearPlane"}},"useCodedValue":true,"visibility":true,"iD":-1}],"renderer":{"type":"CIMClassBreaksRenderer","backgroundSymbol":{"type":"CIMSymbolReference","symbol":{"type":"CIMPolygonSymbol","symbolLayers":[{"type":"CIMSolidStroke","enable":true,"capStyle":"Round","joinStyle":"Round","lineStyle3D":"Strip","miterLimit":10,"width":0.7,"color":{"type":"CIMRGBColor","values":[166,166,166,100]}},{"type":"CIMSolidFill","enable":true,"color":{"type":"CIMRGBColor","values":[166,166,166,0]}}]}},"barrierWeight":"High","breaks":[{"type":"CIMClassBreak","label":"≤5","patch":"Default","symbol":{"type":"CIMSymbolReference","symbol":{"type":"CIMPointSymbol","symbolLayers":[{"type":"CIMVectorMarker","enable":true,"anchorPointUnits":"Relative","dominantSizeAxis3D":"Z","size":5,"billboardMode3D":"FaceNearPlane","frame":{"xmin":-2,"ymin":-2,"xmax":2,"ymax":2},"markerGraphics":[{"type":"CIMMarkerGraphic","geometry":{"curveRings":[[[0,2],{"a":[[0,2],[5.091292E-16,0],0,1]}]]},"symbol":{"type":"CIMPolygonSymbol","symbolLayers":[{"type":"CIMSolidStroke","enable":true,"capStyle":"Round","joinStyle":"Round","lineStyle3D":"Strip","miterLimit":10,"width":0.3,"color":{"type":"CIMRGBColor","values":[0,38,115,100]}},{"type":"CIMGradientFill","enable":true,"angle":90,"colorRamp":{"type":"CIMPolarContinuousColorRamp","fromColor":{"type":"CIMRGBColor","values":[31,116,187,100]},"toColor":{"type":"CIMRGBColor","values":[190,232,255,100]},"interpolationSpace":"HSV","polarDirection":"Auto"},"gradientMethod":"Buffered","gradientSize":75,"gradientSizeUnits":"Relative","gradientType":"Discrete","interval":36}]}}],"respectFrame":true}],"haloSize":1,"scaleX":1,"angleAlignment":"Display"}},"upperBound":5},{"type":"CIMClassBreak","label":"≤9","patch":"Default","symbol":{"type":"CIMSymbolReference","symbol":{"type":"CIMPointSymbol","symbolLayers":[{"type":"CIMVectorMarker","enable":true,"anchorPointUnits":"Relative","dominantSizeAxis3D":"Z","size":7.3333335,"billboardMode3D":"FaceNearPlane","frame":{"xmin":-2,"ymin":-2,"xmax":2,"ymax":2},"markerGraphics":[{"type":"CIMMarkerGraphic","geometry":{"curveRings":[[[0,2],{"a":[[0,2],[5.091292E-16,0],0,1]}]]},"symbol":{"type":"CIMPolygonSymbol","symbolLayers":[{"type":"CIMSolidStroke","enable":true,"capStyle":"Round","joinStyle":"Round","lineStyle3D":"Strip","miterLimit":10,"width":0.3,"color":{"type":"CIMRGBColor","values":[0,38,115,100]}},{"type":"CIMGradientFill","enable":true,"angle":90,"colorRamp":{"type":"CIMPolarContinuousColorRamp","fromColor":{"type":"CIMRGBColor","values":[31,116,187,100]},"toColor":{"type":"CIMRGBColor","values":[190,232,255,100]},"interpolationSpace":"HSV","polarDirection":"Auto"},"gradientMethod":"Buffered","gradientSize":75,"gradientSizeUnits":"Relative","gradientType":"Discrete","interval":36}]}}],"respectFrame":true}],"haloSize":1,"scaleX":1,"angleAlignment":"Display"}},"upperBound":9},{"type":"CIMClassBreak","label":"≤13","patch":"Default","symbol":{"type":"CIMSymbolReference","symbol":{"type":"CIMPointSymbol","symbolLayers":[{"type":"CIMVectorMarker","enable":true,"anchorPointUnits":"Relative","dominantSizeAxis3D":"Z","size":12,"billboardMode3D":"FaceNearPlane","frame":{"xmin":-2,"ymin":-2,"xmax":2,"ymax":2},"markerGraphics":[{"type":"CIMMarkerGraphic","geometry":{"curveRings":[[[0,2],{"a":[[0,2],[5.091292E-16,0],0,1]}]]},"symbol":{"type":"CIMPolygonSymbol","symbolLayers":[{"type":"CIMSolidStroke","enable":true,"capStyle":"Round","joinStyle":"Round","lineStyle3D":"Strip","miterLimit":10,"width":0.3,"color":{"type":"CIMRGBColor","values":[0,38,115,100]}},{"type":"CIMGradientFill","enable":true,"angle":90,"colorRamp":{"type":"CIMPolarContinuousColorRamp","fromColor":{"type":"CIMRGBColor","values":[31,116,187,100]},"toColor":{"type":"CIMRGBColor","values":[190,232,255,100]},"interpolationSpace":"HSV","polarDirection":"Auto"},"gradientMethod":"Buffered","gradientSize":75,"gradientSizeUnits":"Relative","gradientType":"Discrete","interval":36}]}}],"respectFrame":true}],"haloSize":1,"scaleX":1,"angleAlignment":"Display"}},"upperBound":13}],"classBreakType":"GraduatedSymbol","classificationMethod":"Quantile","colorRamp":{"type":"CIMPolarContinuousColorRamp","colorSpace":{"type":"CIMICCColorSpace","url":"Default RGB"},"fromColor":{"type":"CIMHSVColor","values":[60,100,96,100]},"toColor":{"type":"CIMHSVColor","values":[0,100,96,100]},"interpolationSpace":"HSV","polarDirection":"Auto"},"field":"warthog","minimumBreak":1,"numberFormat":{"type":"CIMNumericFormat","alignmentOption":"esriAlignLeft","alignmentWidth":0,"roundingOption":"esriRoundNumberOfDecimals","roundingValue":0,"zeroPad":true},"showInAscendingOrder":false,"heading":"warthog","sampleSize":10000,"defaultSymbol":{"type":"CIMSymbolReference","symbol":{"type":"CIMPolygonSymbol","symbolLayers":[{"type":"CIMSolidStroke","enable":true,"capStyle":"Round","joinStyle":"Round","lineStyle3D":"Strip","miterLimit":10,"width":0.7,"color":{"type":"CIMRGBColor","values":[110,110,110,100]}},{"type":"CIMSolidFill","enable":true,"color":{"type":"CIMRGBColor","values":[130,130,130,100]}}]}},"defaultLabel":"<out of range>","polygonSymbolColorTarget":"Fill","exclusionLabel":"<excluded>","exclusionSymbol":{"type":"CIMSymbolReference","symbol":{"type":"CIMPolygonSymbol","symbolLayers":[{"type":"CIMSolidStroke","enable":true,"capStyle":"Round","joinStyle":"Round","lineStyle3D":"Strip","miterLimit":10,"width":0.7,"color":{"type":"CIMRGBColor","values":[110,110,110,100]}},{"type":"CIMSolidFill","enable":true,"color":{"type":"CIMRGBColor","values":[255,0,0,100]}}]}},"useExclusionSymbol":false,"normalizationType":"Nothing"},"scaleSymbols":true,"snappable":true}],"elevationSurfaces":[{"type":"CIMMapElevationSurface","elevationMode":"BaseGlobeSurface","name":"Ground","verticalExaggeration":1,"mapElevationID":"{32AD7EE0-C78E-4D6D-9A31-F9A889D70571}","color":{"type":"CIMRGBColor","values":[255,255,255,100]},"surfaceTINShadingMode":"Smooth","visibility":true}]}'        
        data = json.loads(symbJSON2)
        fredName = data["layerDefinitions"][0]["renderer"]["field"]
        headName = data["layerDefinitions"][0]["renderer"]["heading"]
        data["layerDefinitions"] [0]["renderer"]["field"] = str(fieldName)
        data["layerDefinitions"][0]["renderer"]["heading"] = str(fieldName)
        symbJSON3 = json.dumps(data)

        lyrx_json2 = symbJSON3
        with tempfile.NamedTemporaryFile(delete=False) as temp_lyrx:
            temp_lyrx.write(lyrx_json2.encode())
        lyrx_path = "{0}.lyrx".format(temp_lyrx.name)
        os.rename(temp_lyrx.name, lyrx_path)
        parameters[1].symbology = lyrx_path

        return

###############################################################################################################################
###################################################### PROGRAM RANKINGS #########################################################
#################################################################################################################################

class ProgramRankings(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Program Rankings"
        self.description = "This tool creates final program rankings"
        self.canRunInBackground = False

    def getParameterInfo(self):
        polygon = arcpy.Parameter(
            displayName = "Input Features",
            name = "polygon_layer",
            datatype = "GPFeatureLayer",
            parameterType = "Required",
            direction = "Input")
        polygon.filter.list = ["Polygon"]

        outFeats = arcpy.Parameter(
            displayName="Output Feature Layer",
            name="out_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")

        value_table = arcpy.Parameter(
            displayName="Fields and Weights",
            name="value_table",
            datatype="GPValueTable",
            parameterType="Required",
            direction="Input")

        value_table.columns = ([["Field", "Program"], ["Double", "Weight"]])
        value_table.filters[0].list = ["Long", "Short", "Double", "Single"]
        value_table.filters[1].type = "Range"
        value_table.filters[1].list = [1,100]

        value_table.parameterDependencies = [polygon.name]

        params = [polygon, outFeats, value_table] 

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        if not parameters[2].altered:
            parameters[2].values
  # *******************************************************************************************************************************************     
  
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        input = parameters[0].valueAsText
        outLayer = parameters[1].ValueAsText
        #copy features to in memory workspace 
        arcpy.CopyFeatures_management(input, outLayer)

        #make output layer to use for join 
        arcpy.MakeFeatureLayer_management(outLayer, 'outLayer')

        #input layer
        moca = parameters[2].valueAsText

        arcpy.SetProgressorLabel("Multiplying each program by its weight...") 

        ##the following string manipulation is to get the input into the right format to use in calculate field for the weighting
        #split field names
        fieldSplits = moca.split(';')

        #split again
        newOne = []

        #append field names to list 
        #for x in fieldSplit:
        for item in fieldSplits:
            newOne.append(item.split())
        
        theSum = 0.0
        for x in newOne:
            if x[1] == 0:
                x[1] == 1
            elif x[1] == '#':
                x[1] == '1'

        for x in newOne:
            theSum = theSum + float(x[1])
        for x in newOne:
            x[1] = float(x[1])/theSum
        
        #create formatting for calculate fields
        for x in newOne:
            x[1] = "!"+x[0]+"!"+"*"+str(x[1])

        #calculate fields - multiple weights by fields 
        arcpy.CalculateFields_management('outLayer', "PYTHON3", newOne)

        #add field for final scoring
        arcpy.AddField_management('outLayer', "FinalScore")

        arcpy.SetProgressorLabel("Creating a Final Score and adding that field to your output feature layer...") 

        #the following list manipulation is to get the input into the right formatting for calculating a final score 
        list2 = []
        for x in newOne:
            list2.append(x[0]) 
        
        ls3 = []
        for x in list2:
            ls3.append("!"+x+"!"+"+")
        length = "/"+str(len(ls3))
        ls4 = "".join(map(str,ls3))
        ls4 = ls4[:-1]+length

        arcpy.CalculateField_management('outLayer', 'FinalScore', ls4, "PYTHON3" )

        symbJSON4 = r'{"type":"CIMLayerDocument","version":"2.2.0","build":12813,"layers":["CIMPATH=homelessness_prevetion/enrichedpolicedistricts_risk12.xml"],"layerDefinitions":[{"type":"CIMFeatureLayer","name":"EnrichedPoliceDistricts_Risk12","uRI":"CIMPATH=homelessness_prevetion/enrichedpolicedistricts_risk12.xml","sourceModifiedTime":{"type":"TimeInstant"},"useSourceMetadata":true,"description":"EnrichedPoliceDistricts_Risk12","layerElevation":{"type":"CIMLayerElevationSurface","mapElevationID":"{32AD7EE0-C78E-4D6D-9A31-F9A889D70571}"},"expanded":true,"layerType":"Operational","showLegends":true,"visibility":true,"displayCacheType":"Permanent","maxDisplayCacheAge":5,"showPopups":true,"serviceLayerID":-1,"refreshRate":-1,"refreshRateUnit":"esriTimeUnitsSeconds","autoGenerateFeatureTemplates":true,"featureElevationExpression":"0","featureTable":{"type":"CIMFeatureTable","displayField":"District","editable":true,"dataConnection":{"type":"CIMStandardDataConnection","workspaceConnectionString":"DATABASE=.\\homelessprevention.gdb","workspaceFactory":"FileGDB","dataset":"EnrichedPoliceDistricts_Risk12","datasetType":"esriDTFeatureClass"},"studyAreaSpatialRel":"esriSpatialRelUndefined","searchOrder":"esriSearchOrderSpatial"},"htmlPopupEnabled":true,"selectable":true,"featureCacheType":"Session","labelClasses":[{"type":"CIMLabelClass","expression":"$feature.TRACT","expressionEngine":"Arcade","featuresToLabel":"AllVisibleFeatures","maplexLabelPlacementProperties":{"type":"CIMMaplexLabelPlacementProperties","featureType":"Polygon","avoidPolygonHoles":true,"canOverrunFeature":true,"canPlaceLabelOutsidePolygon":true,"canRemoveOverlappingLabel":true,"canStackLabel":true,"connectionType":"Unambiguous","constrainOffset":"NoConstraint","contourAlignmentType":"Page","contourLadderType":"Straight","contourMaximumAngle":90,"enableConnection":true,"featureWeight":0,"fontHeightReductionLimit":4,"fontHeightReductionStep":0.5,"fontWidthReductionLimit":90,"fontWidthReductionStep":5,"graticuleAlignmentType":"Straight","keyNumberGroupName":"Default","labelBuffer":15,"labelLargestPolygon":false,"labelPriority":-1,"labelStackingProperties":{"type":"CIMMaplexLabelStackingProperties","stackAlignment":"ChooseBest","maximumNumberOfLines":3,"minimumNumberOfCharsPerLine":3,"maximumNumberOfCharsPerLine":24,"separators":[{"type":"CIMMaplexStackingSeparator","separator":" ","splitAfter":true},{"type":"CIMMaplexStackingSeparator","separator":",","visible":true,"splitAfter":true}]},"lineFeatureType":"General","linePlacementMethod":"OffsetCurvedFromLine","maximumLabelOverrun":80,"maximumLabelOverrunUnit":"Point","minimumFeatureSizeUnit":"Map","multiPartOption":"OneLabelPerPart","offsetAlongLineProperties":{"type":"CIMMaplexOffsetAlongLineProperties","placementMethod":"BestPositionAlongLine","labelAnchorPoint":"CenterOfLabel","distanceUnit":"Percentage","useLineDirection":true},"pointExternalZonePriorities":{"type":"CIMMaplexExternalZonePriorities","aboveLeft":4,"aboveCenter":2,"aboveRight":1,"centerRight":3,"belowRight":5,"belowCenter":7,"belowLeft":8,"centerLeft":6},"pointPlacementMethod":"AroundPoint","polygonAnchorPointType":"GeometricCenter","polygonBoundaryWeight":0,"polygonExternalZones":{"type":"CIMMaplexExternalZonePriorities","aboveLeft":4,"aboveCenter":2,"aboveRight":1,"centerRight":3,"belowRight":5,"belowCenter":7,"belowLeft":8,"centerLeft":6},"polygonFeatureType":"General","polygonInternalZones":{"type":"CIMMaplexInternalZonePriorities","center":1},"polygonPlacementMethod":"HorizontalInPolygon","primaryOffset":1,"primaryOffsetUnit":"Point","removeExtraWhiteSpace":true,"repetitionIntervalUnit":"Map","rotationProperties":{"type":"CIMMaplexRotationProperties","rotationType":"Arithmetic","alignmentType":"Straight"},"secondaryOffset":100,"strategyPriorities":{"type":"CIMMaplexStrategyPriorities","stacking":1,"overrun":2,"fontCompression":3,"fontReduction":4,"abbreviation":5},"thinningDistanceUnit":"Point","truncationMarkerCharacter":".","truncationMinimumLength":1,"truncationPreferredCharacters":"aeiou"},"name":"Class 1","priority":-1,"standardLabelPlacementProperties":{"type":"CIMStandardLabelPlacementProperties","featureType":"Line","featureWeight":"Low","labelWeight":"High","numLabelsOption":"OneLabelPerName","lineLabelPosition":{"type":"CIMStandardLineLabelPosition","above":true,"inLine":true,"parallel":true},"lineLabelPriorities":{"type":"CIMStandardLineLabelPriorities","aboveStart":3,"aboveAlong":3,"aboveEnd":3,"centerStart":3,"centerAlong":3,"centerEnd":3,"belowStart":3,"belowAlong":3,"belowEnd":3},"pointPlacementMethod":"AroundPoint","pointPlacementPriorities":{"type":"CIMStandardPointPlacementPriorities","aboveLeft":2,"aboveCenter":2,"aboveRight":1,"centerLeft":3,"centerRight":2,"belowLeft":3,"belowCenter":3,"belowRight":2},"rotationType":"Arithmetic","polygonPlacementMethod":"AlwaysHorizontal"},"textSymbol":{"type":"CIMSymbolReference","symbol":{"type":"CIMTextSymbol","blockProgression":"TTB","depth3D":1,"extrapolateBaselines":true,"fontEffects":"Normal","fontEncoding":"Unicode","fontFamilyName":"Tahoma","fontStyleName":"Regular","fontType":"Unspecified","haloSize":1,"height":10,"hinting":"Default","horizontalAlignment":"Left","kerning":true,"letterWidth":100,"ligatures":true,"lineGapType":"ExtraLeading","symbol":{"type":"CIMPolygonSymbol","symbolLayers":[{"type":"CIMSolidFill","enable":true,"color":{"type":"CIMRGBColor","values":[0,0,0,100]}}]},"textCase":"Normal","textDirection":"LTR","verticalAlignment":"Bottom","verticalGlyphOrientation":"Right","wordSpacing":100,"billboardMode3D":"FaceNearPlane"}},"useCodedValue":true,"visibility":true,"iD":-1}],"renderer":{"type":"CIMClassBreaksRenderer","backgroundSymbol":{"type":"CIMSymbolReference","symbol":{"type":"CIMPolygonSymbol","symbolLayers":[{"type":"CIMSolidStroke","enable":true,"capStyle":"Round","joinStyle":"Round","lineStyle3D":"Strip","miterLimit":10,"width":0.7,"color":{"type":"CIMRGBColor","values":[166,166,166,100]}},{"type":"CIMSolidFill","enable":true,"color":{"type":"CIMRGBColor","values":[166,166,166,0]}}]}},"barrierWeight":"High","breaks":[{"type":"CIMClassBreak","label":"≤5","patch":"Default","symbol":{"type":"CIMSymbolReference","symbol":{"type":"CIMPointSymbol","symbolLayers":[{"type":"CIMVectorMarker","enable":true,"anchorPointUnits":"Relative","dominantSizeAxis3D":"Z","size":5,"billboardMode3D":"FaceNearPlane","frame":{"xmin":-2,"ymin":-2,"xmax":2,"ymax":2},"markerGraphics":[{"type":"CIMMarkerGraphic","geometry":{"x":0,"y":0},"symbol":{"type":"CIMPointSymbol","symbolLayers":[{"type":"CIMVectorMarker","enable":true,"anchorPointUnits":"Relative","dominantSizeAxis3D":"Z","size":4,"billboardMode3D":"FaceNearPlane","frame":{"xmin":-2,"ymin":-2,"xmax":2,"ymax":2},"markerGraphics":[{"type":"CIMMarkerGraphic","geometry":{"curveRings":[[[0,2],{"a":[[0,2],[1.07156596E-16,0],0,1]}]]},"symbol":{"type":"CIMPolygonSymbol","symbolLayers":[{"type":"CIMSolidStroke","enable":true,"capStyle":"Round","joinStyle":"Round","lineStyle3D":"Strip","miterLimit":10,"width":0.3,"color":{"type":"CIMRGBColor","values":[76,0,115,100]}},{"type":"CIMGradientFill","enable":true,"angle":90,"colorRamp":{"type":"CIMPolarContinuousColorRamp","fromColor":{"type":"CIMRGBColor","values":[132,0,168,100]},"toColor":{"type":"CIMRGBColor","values":[215,181,216,100]},"interpolationSpace":"HSV","polarDirection":"Auto"},"gradientMethod":"Buffered","gradientSize":75,"gradientSizeUnits":"Relative","gradientType":"Discrete","interval":36}]}}],"respectFrame":true}],"haloSize":0,"scaleX":1,"angleAlignment":"Display"}}],"respectFrame":true}],"haloSize":1,"scaleX":1,"angleAlignment":"Display"}},"upperBound":5},{"type":"CIMClassBreak","label":"≤9","patch":"Default","symbol":{"type":"CIMSymbolReference","symbol":{"type":"CIMPointSymbol","symbolLayers":[{"type":"CIMVectorMarker","enable":true,"anchorPointUnits":"Relative","dominantSizeAxis3D":"Z","size":7.3333335,"billboardMode3D":"FaceNearPlane","frame":{"xmin":-2,"ymin":-2,"xmax":2,"ymax":2},"markerGraphics":[{"type":"CIMMarkerGraphic","geometry":{"x":0,"y":0},"symbol":{"type":"CIMPointSymbol","symbolLayers":[{"type":"CIMVectorMarker","enable":true,"anchorPointUnits":"Relative","dominantSizeAxis3D":"Z","size":4,"billboardMode3D":"FaceNearPlane","frame":{"xmin":-2,"ymin":-2,"xmax":2,"ymax":2},"markerGraphics":[{"type":"CIMMarkerGraphic","geometry":{"curveRings":[[[0,2],{"a":[[0,2],[1.07156596E-16,0],0,1]}]]},"symbol":{"type":"CIMPolygonSymbol","symbolLayers":[{"type":"CIMSolidStroke","enable":true,"capStyle":"Round","joinStyle":"Round","lineStyle3D":"Strip","miterLimit":10,"width":0.3,"color":{"type":"CIMRGBColor","values":[76,0,115,100]}},{"type":"CIMGradientFill","enable":true,"angle":90,"colorRamp":{"type":"CIMPolarContinuousColorRamp","fromColor":{"type":"CIMRGBColor","values":[132,0,168,100]},"toColor":{"type":"CIMRGBColor","values":[215,181,216,100]},"interpolationSpace":"HSV","polarDirection":"Auto"},"gradientMethod":"Buffered","gradientSize":75,"gradientSizeUnits":"Relative","gradientType":"Discrete","interval":36}]}}],"respectFrame":true}],"haloSize":0,"scaleX":1,"angleAlignment":"Display"}}],"respectFrame":true}],"haloSize":1,"scaleX":1,"angleAlignment":"Display"}},"upperBound":9},{"type":"CIMClassBreak","label":"≤13","patch":"Default","symbol":{"type":"CIMSymbolReference","symbol":{"type":"CIMPointSymbol","symbolLayers":[{"type":"CIMVectorMarker","enable":true,"anchorPointUnits":"Relative","dominantSizeAxis3D":"Z","size":12,"billboardMode3D":"FaceNearPlane","frame":{"xmin":-2,"ymin":-2,"xmax":2,"ymax":2},"markerGraphics":[{"type":"CIMMarkerGraphic","geometry":{"x":0,"y":0},"symbol":{"type":"CIMPointSymbol","symbolLayers":[{"type":"CIMVectorMarker","enable":true,"anchorPointUnits":"Relative","dominantSizeAxis3D":"Z","size":4,"billboardMode3D":"FaceNearPlane","frame":{"xmin":-2,"ymin":-2,"xmax":2,"ymax":2},"markerGraphics":[{"type":"CIMMarkerGraphic","geometry":{"curveRings":[[[0,2],{"a":[[0,2],[1.07156596E-16,0],0,1]}]]},"symbol":{"type":"CIMPolygonSymbol","symbolLayers":[{"type":"CIMSolidStroke","enable":true,"capStyle":"Round","joinStyle":"Round","lineStyle3D":"Strip","miterLimit":10,"width":0.3,"color":{"type":"CIMRGBColor","values":[76,0,115,100]}},{"type":"CIMGradientFill","enable":true,"angle":90,"colorRamp":{"type":"CIMPolarContinuousColorRamp","fromColor":{"type":"CIMRGBColor","values":[132,0,168,100]},"toColor":{"type":"CIMRGBColor","values":[215,181,216,100]},"interpolationSpace":"HSV","polarDirection":"Auto"},"gradientMethod":"Buffered","gradientSize":75,"gradientSizeUnits":"Relative","gradientType":"Discrete","interval":36}]}}],"respectFrame":true}],"haloSize":0,"scaleX":1,"angleAlignment":"Display"}}],"respectFrame":true}],"haloSize":1,"scaleX":1,"angleAlignment":"Display"}},"upperBound":13}],"classBreakType":"GraduatedSymbol","classificationMethod":"Quantile","colorRamp":{"type":"CIMPolarContinuousColorRamp","colorSpace":{"type":"CIMICCColorSpace","url":"Default RGB"},"fromColor":{"type":"CIMHSVColor","values":[60,100,96,100]},"toColor":{"type":"CIMHSVColor","values":[0,100,96,100]},"interpolationSpace":"HSV","polarDirection":"Auto"},"field":"FinalScore","minimumBreak":1,"numberFormat":{"type":"CIMNumericFormat","alignmentOption":"esriAlignLeft","alignmentWidth":0,"roundingOption":"esriRoundNumberOfDecimals","roundingValue":0,"zeroPad":true},"showInAscendingOrder":false,"heading":"FinalScore","sampleSize":10000,"defaultSymbol":{"type":"CIMSymbolReference","symbol":{"type":"CIMPolygonSymbol","symbolLayers":[{"type":"CIMSolidStroke","enable":true,"capStyle":"Round","joinStyle":"Round","lineStyle3D":"Strip","miterLimit":10,"width":0.7,"color":{"type":"CIMRGBColor","values":[110,110,110,100]}},{"type":"CIMSolidFill","enable":true,"color":{"type":"CIMRGBColor","values":[130,130,130,100]}}]}},"defaultLabel":"<out of range>","polygonSymbolColorTarget":"Fill","exclusionLabel":"<excluded>","exclusionSymbol":{"type":"CIMSymbolReference","symbol":{"type":"CIMPolygonSymbol","symbolLayers":[{"type":"CIMSolidStroke","enable":true,"capStyle":"Round","joinStyle":"Round","lineStyle3D":"Strip","miterLimit":10,"width":0.7,"color":{"type":"CIMRGBColor","values":[110,110,110,100]}},{"type":"CIMSolidFill","enable":true,"color":{"type":"CIMRGBColor","values":[255,0,0,100]}}]}},"useExclusionSymbol":false,"normalizationType":"Nothing"},"scaleSymbols":true,"snappable":true}],"elevationSurfaces":[{"type":"CIMMapElevationSurface","elevationMode":"BaseGlobeSurface","name":"Ground","verticalExaggeration":1,"mapElevationID":"{32AD7EE0-C78E-4D6D-9A31-F9A889D70571}","color":{"type":"CIMRGBColor","values":[255,255,255,100]},"surfaceTINShadingMode":"Smooth","visibility":true}]}'
        lyrx_json3 = symbJSON4
        with tempfile.NamedTemporaryFile(delete=False) as temp_lyrx:
            temp_lyrx.write(lyrx_json3.encode())
        lyrx_path = "{0}.lyrx".format(temp_lyrx.name)
        os.rename(temp_lyrx.name, lyrx_path)
        parameters[1].symbology = lyrx_path

        return