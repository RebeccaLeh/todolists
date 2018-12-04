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

        relationshipID = arcpy.Parameter(
            displayName="Relationship to Head of Household",
            name="relationship",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        relationshipID.parameterDependencies = [inputLayer.name]

        sleep_loc = arcpy.Parameter(
            displayName="Sleep Location",
            name="sleep",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        sleep_loc.parameterDependencies = [inputLayer.name]

        ageofInd = arcpy.Parameter(
            displayName="Age",
            name="asdf",
            datatype="Field",
            parameterType="Required",
            direction="Input")

        genderofInd = arcpy.Parameter(
            displayName="Gender",
            name="fdxv",
            datatype="Field",
            parameterType="Required",
            direction="Input")

        ethnofInd = arcpy.Parameter(
            displayName="Ethnicity",
            name="werfsd",
            datatype="Field",
            parameterType="Required",
            direction="Input")

        raceInd = arcpy.Parameter(
            displayName="Race",
            name="iolkj",
            datatype="Field",
            parameterType="Required",
            direction="Input")

        parID = arcpy.Parameter(
            displayName="Parent ID (GUID of HH)",
            name="tgbxs",
            datatype="Field",
            parameterType="Required",
            direction="Input")

        timesHom = arcpy.Parameter(
            displayName="Number of Times Homeless",
            name="aweds",
            datatype="Field",
            parameterType="Required",
            direction="Input")

        daysHom = arcpy.Parameter(
            displayName="Number of Days Homeless",
            name="zcvs",
            datatype="Field",
            parameterType="Required",
            direction="Input")

        totDaysHom = arcpy.Parameter(
            displayName="Number of Days Homeless (over last 3 years)",
            name="sdfzs",
            datatype="Field",
            parameterType="Required",
            direction="Input")

        vetInd = arcpy.Parameter(
            displayName="Veteran Status",
            name="sdfzv",
            datatype="Field",
            parameterType="Required",
            direction="Input")

        shelteredInd = arcpy.Parameter(
            displayName="Sheltered Individuals",
            name="weru",
            datatype="Field",
            parameterType="Required",
            direction="Input")

        HIVInd = arcpy.Parameter(
            displayName="HIV/AIDS Status",
            name="jpioi",
            datatype="Field",
            parameterType="Required",
            direction="Input")

        mentInd = arcpy.Parameter(
            displayName="Mental Illness",
            name="hklhj",
            datatype="Field",
            parameterType="Required",
            direction="Input")

        subInd = arcpy.Parameter(
            displayName="Substance Abuse",
            name="hjklh",
            datatype="Field",
            parameterType="Required",
            direction="Input")

        domInd = arcpy.Parameter(
            displayName="Homeless Because of Domestic Violence",
            name="lkhj",
            datatype="Field",
            parameterType="Required",
            direction="Input")

        timesHom = arcpy.Parameter(
            displayName="Number of Times Homeless",
            name="hjkln",
            datatype="Field",
            parameterType="Required",
            direction="input")

        params = [inputLayer, outputLocation, relationshipID , sleep_loc, ageofInd, genderofInd, ethnofInd, raceInd, parID, timesHom, daysHom, totDaysHom, vetInd, shelteredInd, HIVInd, mentInd, subInd, domInd, timesHom]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        fields = {x.name for x in arcpy.Describe(parameters[0].valueAsText).fields}
        fieldNames = ("relationship",2)
        def  fieldIs(field, param):
            if field in fields:
                parameters[param].value = field 
        fieldIs("relationship",2)
        fieldIs("sleep_location_individual",3)
        fieldIs("age",4)
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        arcpy.AddMessage("preparing Excel file...")
        
        inputLayer, outputLocation, relationshipID , sleep_loc, ageofInd, genderofInd, ethnofInd, raceInd, parID, timesHom, daysHom, totDaysHom, vetInd, shelteredInd, HIVInd, mentInd, subInd, domInd, timesHom = parameters
        pitCount = inputLayer.valueAsText
        xLocate = outputLocation.valueAsText


        relate1 =
        sleeplo1 =
        age1 =
        gend1 =
        ethn1 = 
        race1 =
        parid1 =
        timhom1 =
        numday1 =
        totdayhom1 =
        vet1 =
        shelt1 =
        hiv1 =
        mental1 =
        substan1 =
        domvi1 =

        ###SHELTER TYPE Function
          
        def headingvET(familyType, familyFullName, startRow):

                header = [familyFullName, " ", 'Sheltered ES', 'Sheltered TH', 'Sheltered SH', 'Unsheltered', 'Totals']
                #write worksheet header
                worksheet_data.write_row(('A'+(str(3+ startRow))), header, cell_format_title)
            
                #Emergency Shelter
                dfES = familyType[familyType[11]=='Emergency Shelter']
                dfESV = len(dfES[dfES[23]=="Yes"].index)
                dfESHH = dfES[58].nunique()
                dfESunq = len(dfES.index)
                #Transitional Housing
                dfTH = familyType[familyType[11] == 'Transitional Housing']
                dfTHV = len(dfTH[dfTH[23]=="Yes"].index)
                dfTHHH = dfTH[58].nunique()
                dfTHunq = len(dfTH.index)
                #Safe Haven
                dfSH = familyType[familyType[11] == 'Safe Haven']
                dfSHHH = dfSH[58].nunique()
                dfSHV = len(dfSH[dfSH[23]=="Yes"].index)
                dfSHunq = len(dfSH.index)
                #Unsheltered
                dfUN = familyType[familyType[12]=="No"]
                dfUNHH = dfUN[58].nunique()
                dfUNV = len(dfUN[dfUN[23]=="Yes"].index)
                dfUNunq = len(dfUN.index)

                #HH and uniue
                household = ['Total Number of Households', " ",dfESHH, dfTHHH, dfSHHH, dfUNHH]
                unique = ['Total Number of Persons', " ",dfESunq, dfTHunq, dfSHunq, dfUNunq]
                vets = ['Total number of Veterans', "", dfESV, dfTHV, dfSHV, dfUNV]
                #writetools
                worksheet_data.write_row(('A'+(str(4 + startRow))), household)
                worksheet_data.write_row(('A'+(str(5 + startRow))), unique)
                worksheet_data.write_row(('A'+(str(6+ startRow))), vets)
        def heading(familyType, familyFullName, startRow):

            header = [familyFullName, " ", 'Sheltered ES', 'Sheltered TH', 'Sheltered SH', 'Unsheltered', 'Totals']
            #write worksheet header
            worksheet_data.write_row(('A'+(str(3+ startRow))), header, cell_format_title)
            
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
            dfUN = familyType[familyType[12]=="No"]
            dfUNHH = dfUN[58].nunique()
            dfUNunq = len(dfUN.index)

            #HH and uniue
            household = ['Total Number of Households', " ",dfESHH, dfTHHH, dfSHHH, dfUNHH]
            unique = ['Total Number of Persons', " ",dfESunq, dfTHunq, dfSHunq, dfUNunq]
            #writetools
            worksheet_data.write_row(('A'+(str(4 + startRow))), household)
            worksheet_data.write_row(('A'+(str(5 + startRow))), unique)
            #age
            dfESu18 = len(dfES[dfES[13]<18].index)
            dfESu24 = len(dfES[dfES[13].between(17,25, inclusive=False)].index)
            dfESo24 = len(dfES[dfES[13]>24].index)
            dfTHu18 = len(dfTH[dfTH[13]<18].index)
            dfTHu24 = len(dfTH[dfTH[13].between(17,25, inclusive=False)].index)
            dfTHo24 = len(dfTH[dfTH[13]>24].index)
            dfSHu18 = len(dfSH[dfSH[13]<18].index)
            dfSHu24 = len(dfSH[dfSH[13].between(17,25, inclusive=False)].index)
            dfSHo24 = len(dfSH[dfSH[13]>24].index)
            dfUNu18 = len(dfUN[dfUN[13]<18].index)
            dfUNu24 = len(dfUN[dfUN[13].between(17,25, inclusive=False)].index)
            dfUNo24 = len(dfUN[dfUN[13]>24].index)

            ################ age
            u18 = ["", "Under Age 18", dfESu18, dfTHu18, dfSHu18, dfUNu18]
            u24 = ["", "Age 18-24", dfESu24, dfTHu24, dfSHu24, dfUNu24]
            o24 = ["", "Over Age 24", dfESo24, dfESo24, dfSHo24, dfUNo24]
            #write age to sheet
            worksheet_data.write_row(('A'+(str(6 + startRow))), u18)
            worksheet_data.write_row(('A'+(str(7 + startRow))), u24)
            worksheet_data.write_row(('A'+(str(8 + startRow))), o24)

        def demograph(familyType, extraWords, startRow):
                bold = workbook.add_format({'bold':True})

                #chronic
                disab = familyType[(familyType[31]=="Yes") | (familyType[32]=="Yes") | (familyType[36]=="Yes")]
                chro = disab[(disab[26]=="4 or more times") & (disab[27]>364)]
                chro1 = disab[disab[25]>364]
                chro2 = chro1.append(chro)
                uniqChro = chro2[58].unique()
                #create an empty dataframe to use 
                chronic = familyType[(familyType[31]=="nonsense")]
                if len(uniqChro)>1:
                    for ID in uniqChro:
                        HHSep = familyType[familyType[58]==ID]
                        chronic.append(HHSep)

                #Emergency Shelter
                dfES = familyType[familyType[11]=='Emergency Shelter']
                dfESChro = len(chronic[chronic[11]=="Emergency Shelter"].index)
                dfESChH = chronic[chronic[11]=="Emergency Shelter"].nunique()
                dfESHH = dfES[58].nunique()
                dfESunq = len(dfES.index)
                #Transitional Housing
                dfTH = familyType[familyType[11] == 'Transitional Housing']
                dfTHHH = dfTH[58].nunique()
                dfTHChro = len(chronic[chronic[11]=="Transitional Housing"].index)
                dfTHChH = chronic[chronic[11]=="Transitional Housing"].nunique()
                dfTHunq = len(dfTH.index)
                #Safe Haven
                dfSH = familyType[familyType[11] == 'Safe Haven']
                dfSHHH = dfSH[58].nunique()
                dfSHChro = len(chronic[chronic[11]=="Safe Haven"].index)
                dfSHChH = chronic[chronic[11]=="Safe Haven"].nunique()
                dfSHunq = len(dfSH.index)
                #Unsheltered
                dfUN = familyType[familyType[12]=="No"]
                dfUNHH = dfUN[58].nunique()
                dfUNChro = len(chronic[chronic[12]=="No"].index)
                dfUNChH = chronic[chronic[12]=="No"].index.nunique()
                dfUNunq = len(dfUN.index)

                #gender
                dfESF = len(dfES[dfES[17]=='Female'].index)
                dfESM = len(dfES[dfES[17]=='Male'].index)
                dfEST = len(dfES[dfES[17]== "Transgender"].index)
                dfESN = len(dfES[dfES[17]== "Don't identify as Male, Female, or Transgender"].index)
                dfTHF = len(dfTH[dfTH[17]=='Female'].index)
                dfTHM = len(dfTH[dfTH[17]=='Male'].index)
                dfTHT = len(dfTH[dfTH[17]== "Transgender"].index)
                dfTHN = len(dfTH[dfTH[17]== "Don't identify as Male, Female, or Transgender"].index)
                dfSHF = len(dfSH[dfSH[17]=='Female'].index)
                dfSHM = len(dfSH[dfSH[17]=='Male'].index)
                dfSHT = len(dfSH[dfSH[17]== "Transgender"].index)
                dfSHN = len(dfSH[dfSH[17]== "Don't identify as Male, Female, or Transgender"].index)
                dfUNF = len(dfUN[dfUN[17]=='Female'].index)
                dfUNM = len(dfUN[dfUN[17]=='Male'].index)
                dfUNT = len(dfUN[dfUN[17]== "Transgender"].index)
                dfUNN = len(dfUN[dfUN[17]== "Don't identify as Male, Female, or Transgender"].index)
                ############### gender
                gender = ["Gender", extraWords]
                female = [" ", "Female",dfESF, dfTHF, dfSHF, dfUNF]
                male = [" ", "Male",dfESM, dfTHM, dfSHM,  dfUNM]
                trans = [" ", "Transgender", dfEST, dfTHT, dfSHT, dfUNT]
                noncon = ["", "Gender Non-Conforming", dfESN, dfTHN, dfSHT, dfUNN]
                totgen = [" ", "Total number of persons for which gender is known"]                 ##need to sum here
                #write gender
                worksheet_data.write_row(('A'+(str(9 + startRow))), gender, bold)
                worksheet_data.write_row(('A'+(str(10 + startRow))), female)
                worksheet_data.write_row(('A'+(str(11 + startRow))), male)
                worksheet_data.write_row(('A'+(str(12 + startRow))), trans)
                worksheet_data.write_row(('A'+(str(13 + startRow))), noncon)
                worksheet_data.write_row(('A'+(str(14 + startRow))), totgen)
                
                #ethnicity
                ethnicity = 14
                dfESHis = len(dfES[dfES[ethnicity]== "1"].index)
                dfESNohi = len(dfES[dfES[ethnicity]== "No"].index)
                dfTHHis = len(dfTH[dfTH[ethnicity]== "1"].index)
                dfTHNohi = len(dfTH[dfTH[ethnicity]== "No"].index)
                dfSHHis = len(dfSH[dfSH[ethnicity]== "1"].index)
                dfSHNohi = len(dfSH[dfSH[ethnicity]== "No"].index)
                dfUNHis = len(dfUN[dfUN[ethnicity]== "1"].index)
                dfUNNohi = len(dfUN[dfUN[ethnicity]== "No"].index)
                #compile
                ethn = ["Ethnicity", extraWords]
                NOspan = ["", "Non-Hispanic/Non-Latino", dfESNohi, dfTHNohi, dfSHNohi, dfUNNohi]
                span = [ "", "Hispanic/Latino", dfESHis, dfTHHis, dfSHHis, dfUNHis]
                totspan = ["", "Total number of persons for which ethnicity is known"]                  ###need to sum
                #write
                worksheet_data.write_row(('A'+(str(15 +startRow))), ethn, bold) 
                worksheet_data.write_row(('A'+(str(16 + startRow))), NOspan) 
                worksheet_data.write_row(('A'+(str(17 + startRow))), span)
                worksheet_data.write_row(('A'+(str(18 + startRow))), totspan)

                race = 15
                #Ethnicity and race
                dfESWh = len(dfES[dfES[race]== "White"].index)
                dfESBl = len(dfES[dfES[race]== "Black"].index)
                dfESAs = len(dfES[dfES[race]== "Asian"].index)
                dfESAi = len(dfES[dfES[race]== "AmercanIndian"].index)
                dfESHi = len(dfES[dfES[race]=="NativeHawaiian"].index)
                dfESMul  = len(dfES[dfES[race].str.contains(',')].index)
                dfTHWh = len(dfTH[dfTH[race]== "White"].index)
                dfTHBl = len(dfTH[dfTH[race]== "Black"].index)
                dfTHAs = len(dfES[dfTH[race]== "Asian"].index)
                dfTHAi = len(dfTH[dfTH[race]== "AmercanIndian"].index)
                dfTHHi = len(dfTH[dfTH[race]=="NativeHawaiian"].index)
                dfTHMul  = len(dfTH[dfTH[race].str.contains(',')].index)
                dfSHWh = len(dfSH[dfSH[race]== "White"].index)
                dfSHBl = len(dfSH[dfSH[race]== "Black"].index)
                dfSHAs = len(dfSH[dfSH[race]== "Asian"].index)
                dfSHAi = len(dfSH[dfSH[race]== "AmercanIndian"].index)
                dfSHHi = len(dfSH[dfSH[race]=="NativeHawaiian"].index)
                dfSHMul  = len(dfSH[dfSH[race].str.contains(',')].index)
                dfUNWh = len(dfUN[dfUN[race]== "White"].index)
                dfUNBl = len(dfUN[dfUN[race]== "Black"].index)
                dfUNAs = len(dfUN[dfUN[race]== "Asian"].index)
                dfUNAi = len(dfUN[dfUN[race]== "AmercanIndian"].index)
                dfUNHi = len(dfUN[dfUN[race]=="NativeHawaiian"].index)
                dfUNMul  = len(dfUN[dfUN[race].str.contains(',')].index)
         
                #summup
                racehead = ["Race", extraWords]
                white = ["", "White", dfESWh, dfTHWh, dfSHWh, dfUNWh]
                black = ["", "Black of African-American", dfESBl, dfTHBl, dfSHBl, dfUNBl]
                asian = ["", "Asian", dfESAs, dfTHAs, dfSHAs, dfUNAs]
                amerInd = ["", "American Indian or Alaskan Native", dfESAi, dfTHAi, dfSHAi, dfUNAi]
                paci = ["", "Native Hawaiian or Other Pacific Islander", dfESHi, dfTHHi, dfSHHi, dfUNHi]
                mult = ["", "Multiple Races", dfESMul, dfTHMul, dfSHMul, dfUNMul]
                totrac= ["", "Total Number of persons for which race is known"]                                 ##need to calculate
                #WRITE WORKSHEET
                worksheet_data.write_row(('A'+(str(19 + startRow))), racehead, bold)
                worksheet_data.write_row(('A'+(str(20 + startRow))), white)
                worksheet_data.write_row(('A'+(str(21 + startRow))), black)
                worksheet_data.write_row(('A'+(str(22 + startRow))), asian)
                worksheet_data.write_row(('A'+(str(23 + startRow))), amerInd)
                worksheet_data.write_row(('A'+(str(24 + startRow))), paci)
                worksheet_data.write_row(('A'+(str(25 + startRow))), mult)
                worksheet_data.write_row(('A'+(str(26 + startRow))), totrac)


            #habitual
                chronicHom = ["", "Total Number of Households", 0,0,0,0]
                chronicHH = ["", "Total Number of Persons", 0,0,0,0]
                if len(chronic)>0:
                    chronicHH = ["", "Total Number of Households", dfESChH, dfTHChH, dfSHChH, dfUNChH]
                    chronicHom = ["", "Total Number of Persons",dfESChro, dfTHChro, dfSHChro, dfUNChro]
                chronicHead = ["Chronically Homeless", "(all)"]
                
                worksheet_data.write_row(('A'+(str(27 + startRow))), chronicHead, bold)
                worksheet_data.write_row(('A'+(str(28 + startRow))), chronicHom)
                worksheet_data.write_row(('A'+(str(29 + startRow))), chronicHH)
        #get field names to use in query 
        fields = arcpy.ListFields(pitCount)
        fieldNames = []

        for field in fields:
            fieldNames.append(field.name)

        #do one search cursor to get all data into a list 
        dataList = []
        with arcpy.da.SearchCursor(pitCount, "*") as cursor:
            for row in cursor:
                dataList.append(row)        
        
        ##################using Pandas get each type of household into a seprate list 
        panda = df.DataFrame(dataList)
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

        #########seprate sub groups (not family units)
        U18Fam = family[family[13]<18]
        YTHFam = family[family[13]<25]
        ADYFam = family[family[13]>17]
        ADFam = family[family[13]>24]

        ########do the same for singles (not family units)
        ADSing = single[single[13]>17]
        CHSing = single[single[13]<18]
        YTSing = single[single[13]<24]
        
        workbook = xlsxwriter.Workbook(xLocate)
        #####Format options
        # Create a format to use in the merged range.
        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': 'gray',
            'font_size':14,
            'font_color':"white"})
        #title header
        bold = workbook.add_format({'bold':True})
        worksheet_data = workbook.add_worksheet("Interview Data")
        worksheet_data.merge_range('A1:G1', 'PRE-EXTRAPOLATED DATA', merge_format)
        worksheet_data.merge_range('A2:G2', 'ALL HOUSEHOLDS', merge_format)
        worksheet_data.merge_range('A84:G84', "VETERAN HOUSEHOLDS", merge_format)
        worksheet_data.merge_range('A134:G134', "YOUTH HOUSEHOLDS", merge_format)
        worksheet_data.merge_range('A192:G192', "ADDITIONAL HOMELESS POPULATIONS", merge_format)
        #column names
        worksheet_data.set_column(2,7, 15)
        worksheet_data.set_column(1,1,30)
        worksheet_data.set_column(0,0,40, bold )
        #usable formating for title of sub headings
        cell_format_title = workbook.add_format({'bold':True, 'bg_color':'#C0C0C0'})
        cell_format_total = workbook.add_format({'bold':True})
        #set totals to bold
        worksheet_data.set_column(6, 6, None, cell_format_total)

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
                ADCH.append(ch)
               # ADCH = ADCH.append(ch)
            elif len(ad.index)==0 and len(ch.index)>0:
                CHFAM = CHFAM.append(ch)
            elif len(ad.index)>0 and len(ch.index)==0:
                ADNOCH = ADNOCH.append(ad)

        ##shelter type
        heading(ADCH, 'Households with At Least One Adult and One Child', 0)
        demograph(ADCH, "(adults & children)", 0)
        #####chronic homelessness status
         
        ###########################################get households with no children                                                      295 
        noChildren = ADNOCH.append(ADSing)     

        ##shelter type
        heading(noChildren, 'Households without Children', 27)
        demograph(noChildren, "", 27)
        ##########################################Get households with only children                                                     0

        #families with children
        childOnly = CHFAM.append(CHSing)
        
        ##shelter type
        heading(childOnly, 'Households with only Chidlren (under18)', 54)
        demograph(childOnly, "", 54)
        ############################################Veterans
        veteran = 23
 
        vets = df.DataFrame()
        allVets = panda.loc[panda[veteran]=="Yes"]
        uniqVets = allVets[58].unique()
        for ID in uniqVets:
            HHSep = panda.loc[panda[58] == ID]
            vets = vets.append(HHSep)
        vetNOCH = df.DataFrame()
        vetCH = df.DataFrame()
        U18Vet = vets[vets[13]<18]
        ADVet = vets[vets[13]>17]
        for ID in uniqVets:
            ch = U18Vet.loc[U18Vet[58] == ID]
            ad = ADVet.loc[ADVet[58] == ID]
            if len(ad.index)>0 and len(ch.index)>0:
                vetCH = vetCH.append(ad)
                vetCH.append(ch)
            elif len(ad.index)>0 and len(ch.index)==0:
                vetNOCH = vetNOCH.append(ad)
        vetsofvetCH = vetCH[vetCH[veteran]=="Yes"]
        vetsofvetNOCH = vetNOCH[vetNOCH[veteran]=="Yes"]
        #households with children
        headingvET(vetCH, "Veteran HH with At Least One Adult and One Child", 82)
        demograph(vetsofvetCH, "(Veterans Only)", 79)
        ############################################veterans households without childre
        ##shelter type
        headingvET(vetNOCH, "Veteran HH without Children", 106)
        demograph(vetsofvetNOCH, "(Veterans Only)", 104)
        #####chronic homelessness status

        ############################################youth unaccompanied                                                      
        UNYTH = df.DataFrame()
        for ID in HH:
            yt = YTHFam.loc[YTHFam[58] == ID]
            ad = ADFam.loc[ADFam[58] == ID]
            if len(yt.index)>0 and len(ad.index)==0:
                UNYTH = UNYTH.append(yt)

        ###Get parenting youth seprate from more than one yth living together 
        PARYth = df.DataFrame()
        NOparyth = df.DataFrame()
        ythNum = UNYTH[58].unique()
        childrenof = df.DataFrame()
        for ID in ythNum:
            HHSep = UNYTH.loc[UNYTH[58] ==ID]
            lenfam = HHSep[HHSep[6]=="Child"]
            if len(lenfam.index)>0:
                PARYth = PARYth.append(HHSep)
                childrenof = childrenof.append(lenfam)
            else:
                NOparyth = NOparyth.append(HHSep)
        ythUnaccSi = UNYTH.append(YTSing)
        ythUnacc = ythUnaccSi.append(NOparyth)

        def parYthWrite(familyType, title, startRow):
            unique = ["", title, 0, 0 , 0 , 0]
            if len(familyType)>0:
                #Emergency Shelter
                dfES = familyType[familyType[11]=='Emergency Shelter']
                dfESunq = len(dfES.index)
                #Transitional Housing
                dfTH = familyType[familyType[11] == 'Transitional Housing']
                dfTHunq = len(dfTH.index)
                #Safe Haven
                dfSH = familyType[familyType[11] == 'Safe Haven']
                dfSHunq = len(dfSH.index)
                #Unsheltered
                dfUN = familyType[familyType[12]=="No"]
                dfUNunq = len(dfUN.index)

                #HH and uniue
                unique = ["",title,dfESunq, dfTHunq, dfSHunq, dfUNunq]
            #writetools
            worksheet_data.write_row(('A'+(str(startRow))), unique)
        
        heading(ythUnacc, "Unaccompanied Youth Households", 132)
        ###unaccompanied youth write out 
        demograph(ythUnacc, "(unaccompanied youth)", 132)
       
        #####chronic homelessness status

        ############################################Parenting youth                                                         14
        ##shelter type
        headerPar = ["Parenting Youth Households", " ", 'Sheltered ES', 'Sheltered TH', 'Sheltered SH', 'Unsheltered', 'Totals']
                #write worksheet header
        worksheet_data.write_row(('A162'), headerPar, cell_format_title)
        parentsOnly = PARYth[PARYth[6].isnull()]
        parentsover18 = parentsOnly[parentsOnly[13]>17]
        parentsunder18 = parentsOnly[parentsOnly[13]<18]
        
        parentsoveruniq= parentsover18[58].unique()
        otheruniq = childrenof[58].unique()
        parentsunderuniq= parentsunder18[58].unique()
        childofYth = df.DataFrame()
        childofChild = df.DataFrame()
        for ID in parentsoveruniq:
            youthFam = childrenof.loc[childrenof[58]==ID]
            childofYth = childofYth.append(youthFam)
        for ID in parentsunderuniq:
            childFam = childrenof.loc[childrenof[58]==ID]
            childofChild =  childofChild.append(childFam)

        parYthWrite(parentsunder18, "Number of parenting youth under Age 18",167)
        parYthWrite(parentsover18, "Number of parenting youth Age 18-24",169)
        parYthWrite(childofYth, "       Children in HH with parenting youth Age 18-24", 170)
        parYthWrite(childofChild, "     Children in HH with parenting youth under Age 18",168)
        demograph(parentsOnly, "(youth parents only)", 162)
        #####chronic homelessness status
        
        def parYthTop(familyType, title, startRow):
            unique = [title, "", 0, 0 , 0 , 0]
            if len(familyType)>0:
                #Emergency Shelter
                dfES = familyType[familyType[11]=='Emergency Shelter']
                dfESunq = len(dfES.index)
                #Transitional Housing
                dfTH = familyType[familyType[11] == 'Transitional Housing']
                dfTHunq = len(dfTH.index)
                #Safe Haven
                dfSH = familyType[familyType[11] == 'Safe Haven']
                dfSHunq = len(dfSH.index)
                #Unsheltered
                dfUN = familyType[familyType[12]=="No"]
                dfUNunq = len(dfUN.index)
                #HH and uniue
                unique = [title,"", dfESunq, dfTHunq, dfSHunq, dfUNunq]

            #writetools
            worksheet_data.write_row(('A'+(str(startRow))), unique)

        parYthTop(parentsOnly, "Total Number of Parenting Youth Households", 163)
        parYthTop(PARYth, "Total Number of Persons in Parenting Youth Households", 164)
        parYthTop(parentsOnly, "Total Parenting Youth", 165)
        parYthTop(childrenof, "Total Children in Parenting Youth Household", 166)
        ##############################################Adult aids, mental illness etc.
        ####Final Formatting
        #gender
        def sumppl(column, i):
                formula = "{=SUM("+column+(str(i-4)+":"+column+(str(i-1))+")}")
                worksheet_data.write_array_formula(column+(str(i))+column+(str(i)), formula)
        #ethnicity
        def sumeth(column, i):
                formula = "{=SUM("+column+(str(i-2)+":"+column+(str(i-1))+")}")
                worksheet_data.write_array_formula(column+(str(i))+column+(str(i)), formula)
        #race
        def sumrace(column, i):
                formula = "{=SUM("+column+(str(i-6)+":"+column+(str(i-1))+")}")
                worksheet_data.write_array_formula(column+(str(i))+column+(str(i)), formula)
        #groups
        totgend = {("C",14), ("D",14),("E",14), ("F",14),("C",41), ("D",41),("E",41), ("F",41),("C",68), ("D",68),("E",68), ("F",68),("C",93), ("D",93), ("E",93), ("F",93),("C",118), ("D",118),("E",118), ("F",118),("C",146), ("D",146),("E",146), ("F",146),("C",176), ("D",176),("E",176), ("F",176)}
        toteth = {("C",18), ("D",18),("E",18), ("F",18),("C",45), ("D",45),("E",45), ("F",45),("C",72), ("D",72),("E",72), ("F",72),("C",97), ("D",97), ("E",97), ("F",97),("C",122), ("D",122),("E",122), ("F",122),("C",150), ("D",150),("E",150), ("F",150),("C",180), ("D",180),("E",180), ("F",180)}
        totrace = {("C",26), ("D",26),("E",26), ("F",26),("C",53), ("D",53),("E",53), ("F",53),("C",80), ("D",80),("E",80), ("F",80),("C",105), ("D",105), ("E",105), ("F",105),("C",130), ("D",130),("E",130), ("F",130),("C",158), ("D",158),("E",158), ("F",158),("C",188), ("D",188),("E",188), ("F",188)}
        for (a,b) in totgend:
            sumppl(a,b)
        for (a,b) in toteth:
            sumeth(a,b)
        for (a,b) in totrace:
            sumrace(a,b)
        ##final summation
        rows = list(range(4,30))
        rows2 = list(range(31,57))
        rows3 = list(range(58,84))
        rows4 = list(range(86,109))
        rows5 = list(range(110,134))
        rows6 = list(range(136,162))
        rows7 = list(range(163,192))
        rows8 = list(range(192,197))
        def rowsum(rows):
            for i in rows:
                formula = "{=SUM(C"+(str(i)+":F"+(str(i))+")}")
                worksheet_data.write_array_formula('G'+(str(i))+'G'+(str(i)), formula)
        rowsum(rows)
        rowsum(rows2)
        rowsum(rows3)
        rowsum(rows4)
        rowsum(rows5)
        rowsum(rows6)
        rowsum(rows7)
        rowsum(rows8)

        HIV = panda[panda[36]=="Yes"]
        DoVi = panda[panda[38] =="Yes"]
        ment = panda[panda[31]=="Yes"]
        sub = panda[panda[30]=="Yes"]
       
        def adultD(thing, name, row):
            dfES = len(thing[thing[11]=='Emergency Shelter'].index)
            dfSH = len(thing[thing[11] == 'Safe Haven'].index)
            dfUN = len(thing[thing[12]=="No"].index)
            all =  [name, "", dfES, "NA", dfSH, dfUN] 
            worksheet_data.write_row(('A'+(str(row))), all)

        header = ["", " ", 'Sheltered ES', 'Sheltered TH', 'Sheltered SH', 'Unsheltered', 'Totals']
        #write worksheet header
        worksheet_data.write_row('A193', header, cell_format_title)
        
        adultD(ment, "Adults with Serious Mental Illness", 194)
        adultD(sub, "Adults with a Substance Abuse Disorder", 195)
        adultD(HIV, "Adults with HIV/AIDS", 196)
        adultD(DoVi, "Adult Survivors of Domestic Violence", 197)

        #write
        workbook.close()
      
        return



    ##############################scratch