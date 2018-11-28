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
        def shelterType(familyType, familyFullName, startRow):
            header = [familyFullName, " ", 'Sheltered ES', 'Sheltered TH', 'Unsheltered', 'Totals']
            #write worksheet header
            worksheet_data.write_row(('A'+(str(3+ startRow))), header)

            #Emergency Shelter
            dfES = familyType[familyType[11]=='Emergency Shelter']
            dfESHH = dfES[58].nunique()
            dfESunq = len(dfES.index)
            #Transitional Housing
            dfTH = familyType[familyType[11] == 'Transitional Housing']
            dfTHHH = dfTH[58].nunique()
            dfTHunq = len(dfTH.index)
            #Safe Haven
            dfSH = familyType[familyType[11] == 'Safe Haven']
            dfSHHH = dfSH[58].nunique()
            dfSHunq = len(dfSH.index)
            #Unsheltered
            dfUN = familyType[familyType[11].isin(unsheltered)]
            dfUNHH = dfUN[58].nunique()
            dfUNunq = len(dfUN.index)

            #HH and uniue
            household = ['Total Number of Households', " ",dfESHH, dfTHHH, dfUNHH]
            unique = ['Total Number of Persons', " ",dfESunq, dfTHunq, dfUNunq]
            #writetoxls
            worksheet_data.write_row(('A'+(str(4 + startRow))), household)
            worksheet_data.write_row(('A'+(str(5 + startRow))), unique)

            #age
            dfESu18 = len(dfES[dfES[13]<18].index)
            dfESu24 = len(dfES[dfES[13].between(17,25, inclusive=False)].index)
            dfESo24 = len(dfES[dfES[13]>24].index)
            dfTHu18 = len(dfTH[dfTH[13]<18].index)
            dfTHu24 = len(dfTH[dfTH[13].between(17,25, inclusive=False)].index)
            dfTHo24 = len(dfTH[dfTH[13]>24].index)
            dfUNu18 = len(dfUN[dfUN[13]<18].index)
            dfUNu24 = len(dfUN[dfUN[13].between(17,25, inclusive=False)].index)
            dfUNo24 = len(dfUN[dfUN[13]>24].index)
            ################ age
            u18 = ["", "Under Age 18", dfESu18, dfTHu18, dfUNu18]
            u24 = ["", "Age 18-24", dfESu24, dfTHu24, dfUNu24]
            o24 = ["", "Over Age 24", dfESo24, dfESo24, dfUNo24]
            #write age to sheet
            worksheet_data.write_row(('A'+(str(6 + startRow))), u18)
            worksheet_data.write_row(('A'+(str(7 + startRow))), u24)
            worksheet_data.write_row(('A'+(str(8 + startRow))), o24)

            #gender
            dfESF = len(dfES[dfES[17]=='Female'].index)
            dfESM = len(dfES[dfES[17]=='Male'].index)
            dfEST = len(dfES[dfES[17]== "Transgender"].index)
            dfESN = len(dfES[dfES[17]== "Don't identify as Male, Female, or Transgender"].index)
            dfTHF = len(dfTH[dfTH[17]=='Female'].index)
            dfTHM = len(dfTH[dfTH[17]=='Male'].index)
            dfTHT = len(dfTH[dfTH[17]== "Transgender"].index)
            dfTHN = len(dfES[dfES[17]== "Don't identify as Male, Female, or Transgender"].index)
            dfUNF = len(dfUN[dfUN[17]=='Female'].index)
            dfUNM = len(dfUN[dfUN[17]=='Male'].index)
            dfUNT = len(dfUN[dfUN[17]== "Transgender"].index)
            dfUNN = len(dfES[dfES[17]== "Don't identify as Male, Female, or Transgender"].index)
            ############### gender
            gender = ["Gender", '(adults and children)']
            female = [" ", "Female",dfESF, dfTHF, dfUNF]
            male = [" ", "Male",dfESM, dfTHM, dfUNF]
            trans = [" ", "Transgender", dfEST, dfTHT, dfUNT]
            noncon = ["", "Gender Non-Conforming", dfESN, dfTHN, dfUNN]
            totgen = [" ", "Total number of persons for which gender is known"]                 ##need to sum here
            #write gender
            worksheet_data.write_row(('A'+(str(9 + startRow))), gender)
            worksheet_data.write_row(('A'+(str(10 + startRow))), female)
            worksheet_data.write_row(('A'+(str(11 + startRow))), male)
            worksheet_data.write_row(('A'+(str(12 + startRow))), trans)
            worksheet_data.write_row(('A'+(str(13 + startRow))), noncon)
            worksheet_data.write_row(('A'+(str(14 + startRow))), totgen)

            #Ethnicity and race
            dfESF = dfTH[58].nunique()
            dfESM = dfTH[58].nunique()
            dfEST = dfTH[58].nunique()
            dfESN = len(dfES[dfES[17]== "Don't identify as Male, Female, or Transgender"].index)
            dfTHF = len(dfTH[dfTH[17]=='Female'].index)
            dfTHM = len(dfTH[dfTH[17]=='Male'].index)
            dfTHT = len(dfTH[dfTH[17]== "Transgender"].index)
            dfTHN = len(dfES[dfES[17]== "Don't identify as Male, Female, or Transgender"].index)
            dfUNF = len(dfUN[dfUN[17]=='Female'].index)
            dfUNM = len(dfUN[dfUN[17]=='Male'].index)
            dfUNT = len(dfUN[dfUN[17]== "Transgender"].index)
            dfUNN = len(dfES[dfES[17]== "Don't identify as Male, Female, or Transgender"].index)


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
        
        worksheet_data = workbook.add_worksheet("data")
        worksheet_data.merge_range('A1:F1', 'PRE-EXTRAPOLATED DATA', merge_format)
        worksheet_data.merge_range('A2:F2', 'ALL HOUSEHOLDS', merge_format)

        worksheet_data.set_column(1,7, 15)
        worksheet_data.set_column(0,0,40 )
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
               # ADCH = ADCH.append(ch)
            elif len(ad.index)==0 and len(ch.index)>0:
                CHFAM = CHFAM.append(ch)
            elif len(ad.index)>0 and len(ch.index)==0:
                ADNOCH = ADNOCH.append(ad)
        arcpy.AddMessage(len(ADCH.index))
        arcpy.AddMessage(len(ADNOCH.index))

        ##shelter type
        shelterType(ADCH, 'Households with At Least One Adult and One Child', 0)
        #Emergency Shelter
        

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
        shelterType(noChildren, 'Households without Children', 27)
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
        shelterType(childOnly, 'Households with only Chidlren (under18)', 54)
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
       # print(len(youthUnaccompanied.index))
       
        #ppl under 24
        ##shelter type
        shelterType(youthUnaccompanied, ' Unaccompanied Youth Households', 127 )
        ####Demographics
        #####age
        #####gender
        #####ethnicity
        #####race
        #####chronic homelessness status

        ############################################Parenting youth                                                         14
        ##done name is CHFAM
       # print(len(UNYTH.index)) 
        ##shelter type
       # shelterType(CHFAM, 'Parenting Youth Households', 152)
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

  