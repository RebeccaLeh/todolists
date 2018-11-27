import xlsxwriter , os, arcpy, sys, string, math, traceback, numpy
import pandas as df

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
        self.label = "Create Excel Output"
        self.description = "This tool creates a data output for HUD reporting on PIT count"
        self.canRunInBackground = False

    def getParameterInfo(self):
        inputLayer = arcpy.Parameter(
            displayName = "Input Features",
            name = "in_features",
            datatype = "GPFeatureLayer",
            parameterType = "Required",
            direction = "Input")

        outputLocation = arcpy.Parameter(
            displayName="Output Location",
            name="out_xlsx",
            datatype="DEFile",
            parameterType="Required",
            direction="Output")

        params = [inputLayer, outputLocation]

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
        
        inputLayer, outputLocation = parameters
        pitCount = inputLayer.valueAsText
        xLocate = outputLocation.valueAsText

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

        unsheltered = ['Vehicle', 'UnderBridge_Overpass', 'Street', 'Park', 'Outdoors', 'BustStation_Airport', 'AbandonedBuilding']
        
        
        ##################using Pandas get each type of household into a seprate list 
        panda = df.DataFrame(dataList)

        ###SHELTER TYPE Function
        def shelterType(familyType, familyFullName, row):

            #Emergency Shelter
            dfES = familyType[familyType[11]=='Emergency Shelter']
            dfESHH = dfES[58].unique()
            dfESunq = len(dfES.index)

            #Transitional Housing
            dfTH = familyType[familyType[11] == 'Transitional Housing']
            dfTHHH = dfTHHH[58].unique()
            dfTHunq = len(dfTH.index)
            #Safe Haven
            dfSH = familyType[familyType[11] == 'Safe Haven']
            dfSHHH = dfSHHH[58].unique()
            dfSHunq = len(dfSH.index)
            #Unsheltered
            dfUN = familyType[familyType[11].isin(unsheltered)]
            dfUNHH = dfUNHH[58].unique()
            dfUNunq = len(dfUN.index)
    
        #Unique Households and seperate them into families and single 
        family = df.DataFrame()
        single = df.DataFrame()
        HH =  panda[58].unique()
        for ID in HH:
            HHSep = panda.loc[panda[58] == ID]
            if len(HHSep)>1:
                family = family.append(HHSep)
            else:
                single = single.append(HHSep)
    
        #Get Family Type

        #########seprate sub groups 
        U18Fam = family[family[13]<18]
        #YouthFam = family[family[13].between(17,25, inclusive=False)] # don't need this yet, using same variable for all youth
        YTHFam = family[family[13]<25]
        ADYFam = family[family[13]>17]
        ADFam = family[family[13]>24]

        ########do the same for singles
        ADSing = single[single[13]>17]
        CHSing = single[single[13]<18]
        YTSing = single[single[13]<24]
        
        workbook = xlsxwriter.Workbook(xLocate)
        # Create a format to use in the merged range.
        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': 'pink'})
        n=5
        worksheet_data = workbook.add_worksheet("data")
      #  worksheet_data.write('A1', 'PRE-EXTRAPOLATED DATA')
      #  worksheet_data.write('A2', "ALL HOUSEHOLDS")
        worksheet_data.merge_range('A1:F1', 'PRE-EXTRAPOLATED DATA', merge_format)
        worksheet_data.merge_range('A2:F2', 'ALL HOUSEHOLDS', merge_format)
        worksheet_data.write(('A'+(str(3+n))), 8)
        ############################################get households with at least one adult and one child                                            116
        ##through this we also get HH with prenting youth
        ADCH = df.DataFrame()
        CHFAM = df.DataFrame()
        ADNOCH = df.DataFrame()
        for ID in HH:
            ch = U18Fam.loc[U18Fam[58] == ID]
            ad = ADYFam.loc[ADYFam[58] == ID]
            if len(ad.index)>0 and len(ch.index)>0:
                ADCH = ADCH.append(ad)
                ADCH = ADCH.append(ch)
            elif len(ad.index)==0 and len(ch.index)>0:
                CHFAM = CHFAM.append(ch)
            elif len(ad.index)>0 and len(ch.index)==0:
                ADNOCH = ADNOCH.append(ad)
        print(len(ADCH.index))

        ##shelter type

        #Emergency Shelter
        shelterType(ADCH)

        ###HH

        ##Individuals

        ####Demographics

        #####age
        #####gender
        #####ethnicity
        #####race
        #####chronic homelessness status
         
        ############################################get households with no children                                                      295
        #Unique Households and seperate them into families and single 
        #ADNOCH #families with no children
        #ADSing # single adults
        noChildren = ADNOCH.append(ADSing)     

        ##shelter type
        shelterType(noChildren)
        ###HH
        ##Individuals
        ####Demographics
        #####age
        #####gender
        #####ethnicity
        #####race
        #####chronic homelessness status


        ##########################################Get households with only children                                                     0

        #families of children
        #CHFAM ###done
        #single children
        #CHSing
        childOnly = CHFAM.append(CHSing)
        
        ##shelter type
        shelterType(childOnly)
        ###HH
        ##Individuals
        ####Demographics
        #####age
        #####gender
        #####ethnicity
        #####race
        #####chronic homelessness status
        
        ############################################Veterans
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

        ############################################veterans households without children
       
        ##shelter type
        ###HH
        ##Individuals
        ####Demographics
        #####age
        #####gender
        #####ethnicity
        #####race
        #####chronic homelessness status

        ############################################youth unaccompanied                                                         47
        UNYTH = df.DataFrame()
        for ID in HH:
            yt = YTHFam.loc[YTHFam[58] == ID]
            ad = ADFam.loc[ADFam[58] == ID]
            if len(yt.index)>0 and len(ad.index)==0:
                UNYTH = UNYTH.append(yt)

        youthUnaccompanied = UNYTH.append(YTSing)
        print(len(youthUnaccompanied.index))
       
        #ppl under 24
        ##shelter type
        shelterType(youthUnaccompanied)
        ####Demographics
        #####age
        #####gender
        #####ethnicity
        #####race
        #####chronic homelessness status

        ############################################Parenting youth                                                         14
        ##done name is CHFAM
        print(len(UNYTH.index)) 
        ##shelter type
        shelterType(CHFAM)
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
        
        ##############################################Adult aids, mental illness etc.
        workbook = xlsxwriter.Workbook(PITCount_Summary)
        worksheet = workbook.add_worksheet()

        for item, cost in (expense):
            worksheet.write(row,col,    )
            worksheet.write(row, col+1, cost)
            row +=1
        
        workbook.close()

      
        return



    ##############################scratch

    #        #get list of unique family names 
    #    for listing in family:
    #        if listing = 1
    #            if age >17 single adult
    #            if age<18 to 24  
    #        if listing >1
    #            if age>17 and age <17 fam with child    
    #            if arg<17and age <17 child with child  


    #                for tip of leaf:
    #                for leaf in branch
    #                    for branch in tree   tip for branch in tree for leaf in branch for tip in branch
    #            ####strip none as needed 
    #    def stripNone(data):
    #        if isinstance(data, dict):
    #            return {k:stripNone(v) for k, v in data.items() if k is not None and v is not None}
    #        elif isinstance(data, list):
    #            return [stripNone(item) for item in data if item is not None]
    #        elif isinstance(data, tuple):
    #            return tuple(stripNone(item) for item in data if item is not None)
    #        elif isinstance(data, set):
    #            return {stripNone(item) for item in data if item is not None}
    #        else:
    #            return data
    #    stripNone(dataList)


    #    #Adults
    #    adults = [age for row in dataList for y,age in enumerate(row) if row[13]> 17]
    #    for row in dataList:
    #        if row[13] in enumerate dataList> 18:
    #            row

    #    ages = [row for x, x in enumerate(row) if  for row in dataList]

