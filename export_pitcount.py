import xlsxwriter , os

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [ExcelOutput]

###############################################################################################################################
############################################################### RISK LAYER #########################################################
#################################################################################################################################

class ExcelOutput(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Create Output of Data"
        self.description = "This tool creates a data output for HUD reporting on PIT count"
        self.canRunInBackground = False

    def getParameterInfo(self):
        inputLayer = arcpy.Parameter(
            displayName = "Input Features",
            name = "in_features",
            datatype = "GPFeatureLayer",
            parameterType = "Required",
            direction = "Input")
        inputLayer.filter.list = ["Polygon"]

        outputLocation = arcpy.Parameter(
            displayName="Output Location",
            name="out_xlsx",
            datatype="DEFFile",
            parameterType="Required",
            direction="Output")

        params = [inputLayer, outputLayer]

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
        arcpy.AddMessage("preparing Excel file...")
        
        inputLayer, outputLayer = parameters
        pitCount = inputLayer.valueAsText

        #get field names to use in query 
        fields = arcpy.ListFields(pitCount)
        fieldNames = []

        for field in fields:
            fieldNames.append(field.name)
        arcpy.AddMessage(fieldNames)

        #do one search cursor to get all data into a list 
        dataList = []
        with arcpy.da.SearchCursor(pitCount, "*") as cursor:
            for row in cursor:
                dataList.append(row)

                for tip of leaf:
                    for leaf in branch
                        for branch in tree   tip for branch in tree for leaf in branch for tip in branch
                ####strip none as needed 
        def stripNone(data):
            if isinstance(data, dict):
                return {k:stripNone(v) for k, v in data.items() if k is not None and v is not None}
            elif isinstance(data, list):
                return [stripNone(item) for item in data if item is not None]
            elif isinstance(data, tuple):
                return tuple(stripNone(item) for item in data if item is not None)
            elif isinstance(data, set):
                return {stripNone(item) for item in data if item is not None}
            else:
                return data
        stripNone(dataList)


        #Adults
        adults = [age for row in dataList for y,age in enumerate(row) if row[13]> 17]
        for row in dataList:
            if row[13] in enumerate dataList> 18:
                row

        ages = [row for x, x in enumerate(row) if  for row in dataList]

unsheltered = ['Vehicle', 'UnderBridge_Overpass', 'Street', 'Park', 'Outdoors', 'BustStation_Airport', 'AbandonedBuilding']
        
        
        ##################using Pandas get each type of household into a seprate list 
import pandas as df
panda = df.DataFrame(dataList)
#Emergency Shelter
dfES = panda[panda[11]=='Emergency Shelter']
#Transitional Housing
dfTH = panda[panda[11] == 'Transitional Housing']
#Safe Haven
dfSH = panda[panda[11] == 'Safe Haven']
#Unsheltered
dfUN = panda[panda[11].isin(unsheltered)]


        
#Unique Households and seperate them into families and single 
HH =  panda[58].unique()
for ID in HH:
    HHSep = panda.loc[panda[58] == ID]
    if len(HHSep)>1:
        family = family.append(HHSep)
    else:
        single = single.append(HHSep)
    
#Get Family Type


U18Fam = family[family[13]<18]
YouthFam = family[family[13].between(17,25, inclusive=False)]


ADFam = family[family[13]>24]




        #get list of unique family names 
        for listing in family:
            if listing = 1
                if age >17 single adult
                if age<18 to 24  
            if listing >1
                if age>17 and age <17 fam with child    
                if arg<17and age <17 child with child  


    
    HHSep.iloc[HHSep[13]<18]
        if len(HHSep)>1:
            pd.concat(family,HHSep)
        else:
            pd.concat(single,HHSep)

    




        #get households with at least one adult and one child
        dfADCH = panda[panda[13]]
        ##shelter type
        ###HH
        ##Individuals
        ####Demographics
        #####age
        #####gender
        #####ethnicity
        #####race
        #####chronic homelessness status
         
        #get households with no children
        #Unique Households and seperate them into families and single 
HH =  panda[58].unique()
for ID in HH:
    HHSep = panda.loc[panda[58] == ID]
    if HHSep[HHSep[13]>17]:
        houseNOCH = houseNOH.append(HHSep)

HH =  panda[58].unique()
for ID in HH:
    HHSep = panda.loc[panda[13] > 17]
    houseNOCH = houseNOH.append(HHSep)
        ##shelter type
        ###HH
        ##Individuals
        ####Demographics
        #####age
        #####gender
        #####ethnicity
        #####race
        #####chronic homelessness status

        #Get households with only children
        ##shelter type
        ###HH
        ##Individuals
        ####Demographics
        #####age
        #####gender
        #####ethnicity
        #####race
        #####chronic homelessness status
        
        #Veterans
        #households with children
        ##shelter type
        ###HH
        ##Individuals
        ####Demographics
        #####age
        #####gender
        #####ethnicity
        #####race
        #####chronic homelessness status 

        #households without children
        ##shelter type
        ###HH
        ##Individuals
        ####Demographics
        #####age
        #####gender
        #####ethnicity
        #####race
        #####chronic homelessness status

        #youth 
        #ppl under 24
        ##shelter type
        ####Demographics
        #####age
        #####gender
        #####ethnicity
        #####race
        #####chronic homelessness status

        #Parenting youth
        ####18-24
        #########Parents
        #########Children
        ####under 18
        #########Parents
        #########Children
        #########Parent Demographics below:
        ####Demographics
        #####age
        #####gender
        #####ethnicity
        #####race
        #####chronic homelessness status
        
        ###Adult aids, mental illness etc.
        workbook = xlsxwriter.Workbook(PITCount_Summary)
        worksheet = workbook.add_worksheet()

        for item, cost in (expense):
            worksheet.write(row,col,    )
            worksheet.write(row, col+1, cost)
            row +=1
        
        workbook.close()

      
        return