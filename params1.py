##################Python Toolbox#########################

class Toolbox(object):
    def __init__(self):
        self.label =  "Homeless Risk Surface"
        self.alias  = "risk_surface"

        # List of tool classes associated with this toolbox
        self.tools = [risk_surface] 

class CalculateSinuosity(object):
    def __init__(self):
        self.label       = "Calculate Sinuosity"
        self.description = "This tool measures the relative risk of becoming Homeless" + \
                           "by comparing risk attributes accross a feature layer."

    def getParameterInfo(self):
        #Define parameter definitions

        # Input Features parameter
        polygonLayer = arcpy.Parameter(
            displayName="Input Census",
            name="in_feature",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        
        in_features.filter.list = ["Polygon"]

        # Sinuosity Field parameter
        fieldNames = arcpy.Parameter(
            displayName="Risk Factors",
            name="riskFactors",
            datatype="Field",
            parameterType="Required",
            parameterDependencies = "polygonLayer",
            direction="Input",
            multiValue = True)
        
        #sinuosity_field.value = "sinuosity"
        
        # Sinuosity Field parameter
        otherFields = arcpy.Parameter(
            displayName="Other Fields",
            name="otherFields",
            datatype="Field",
            parameterType="Required",
            parameterDependencies = "polygonLayer",
            direction="Input",
            multiValue = True)

        # Derived Output Features parameter
        outputLayer = arcpy.Parameter(
            displayName="Output Features",
            name="outputLayer",
            datatype="GPFeatureLayer",
            parameterType="Derived",
            direction="Output")
        
        out_features.parameterDependencies = [in_features.name]
        out_features.schema.clone = True

        parameters = [polygonLayer, fieldNames, otherFields, outputLayer]
        
        return parameters

    def isLicensed(self): #optional
        return True

    def updateParameters(self, parameters): #optional
        if parameters[0].altered:
            parameters[1].value = arcpy.ValidateFieldName(parameters[1].value,
                                                          parameters[0].value)
        return

    def updateMessages(self, parameters): #optional
        return

    def execute(self, parameters, messages):
        inFeatures  = parameters[0].valueAsText
        fieldName   = parameters[1].valueAsText
        
        if fieldName in ["#", "", None]:
            fieldName = "sinuosity"

        arcpy.AddField_management(inFeatures, fieldName, 'DOUBLE')

        expression = '''
