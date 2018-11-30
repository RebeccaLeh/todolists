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

        ###SHELTER TYPE Function
          
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
                worksheet_data.write_row(('A'+(str(9 + startRow))), gender)
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
                ethn = ["Ethnicity"]
                span = ["Ethnicity", extraWords]
                NOspan = ["", "Non-Hispanic/Non-Latino", dfESNohi, dfTHNohi, dfSHNohi, dfUNNohi]
                span = [ "", "Hispanic/Latino", dfESHis, dfTHHis, dfSHHis, dfUNHis]
                totspan = ["", "Total number of persons for which ethnicity is known"]                  ###need to sum
                #write
                worksheet_data.write_row(('A'+(str(15 +startRow))), ethn) 
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
                dfESMul  = len(dfES[dfES[race]=='Multiple'].index)
                dfTHWh = len(dfTH[dfTH[race]== "White"].index)
                dfTHBl = len(dfTH[dfTH[race]== "Black"].index)
                dfTHAs = len(dfES[dfTH[race]== "Asian"].index)
                dfTHAi = len(dfTH[dfTH[race]== "AmercanIndian"].index)
                dfTHHi = len(dfTH[dfTH[race]=="NativeHawaiian"].index)
                dfTHMul  = len(dfTH[dfTH[race]=='Multiple'].index)
                dfSHWh = len(dfSH[dfSH[race]== "White"].index)
                dfSHBl = len(dfSH[dfSH[race]== "Black"].index)
                dfSHAs = len(dfSH[dfSH[race]== "Asian"].index)
                dfSHAi = len(dfSH[dfSH[race]== "AmercanIndian"].index)
                dfSHHi = len(dfSH[dfSH[race]=="NativeHawaiian"].index)
                dfSHMul  = len(dfSH[dfSH[race]=='Multiple'].index)
                dfUNWh = len(dfUN[dfUN[race]== "White"].index)
                dfUNBl = len(dfUN[dfUN[race]== "Black"].index)
                dfUNAs = len(dfUN[dfUN[race]== "Asian"].index)
                dfUNAi = len(dfUN[dfUN[race]== "AmercanIndian"].index)
                dfUNHi = len(dfUN[dfUN[race]=="NativeHawaiian"].index)
                dfUNMul  = len(dfUN[dfUN[race]=='Multiple'].index)
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
                worksheet_data.write_row(('A'+(str(19 + startRow))), racehead)
                worksheet_data.write_row(('A'+(str(20 + startRow))), white)
                worksheet_data.write_row(('A'+(str(21 + startRow))), black)
                worksheet_data.write_row(('A'+(str(22 + startRow))), asian)
                worksheet_data.write_row(('A'+(str(23 + startRow))), amerInd)
                worksheet_data.write_row(('A'+(str(24 + startRow))), paci)
                worksheet_data.write_row(('A'+(str(25 + startRow))), mult)
                worksheet_data.write_row(('A'+(str(26 + startRow))), totrac)

                #chronic
                disab = familyType[(familyType[31]=="Yes") | (familyType[32]=="Yes") | (familyType[36]=="Yes")]
                chro = disab[(disab[26]=="4 or more times") & (disab[27]>364)]
                chro1 = disab[disab[25]>364]
                chro2 = chro1.append(chro)
                uniqChro = chro2[58].unique()
                chronic = df.DataFrame()
                for ID in uniqChro:
                    HHSep = familyType[familyType[58]=="ID"]
                    chronic.append(HHSep)
            #habitual
                #dfES

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
        worksheet_data = workbook.add_worksheet("Interview Data")
        worksheet_data.merge_range('A1:G1', 'PRE-EXTRAPOLATED DATA', merge_format)
        worksheet_data.merge_range('A2:G2', 'ALL HOUSEHOLDS', merge_format)
        worksheet_data.merge_range('A84:G84', "VETERAN HOUSEHOLDS", merge_format)
        worksheet_data.merge_range('A135:G135', "YOUTH HOUSEHOLDS", merge_format)
        #column names
        worksheet_data.set_column(2,7, 15)
        worksheet_data.set_column(1,1,30)
        worksheet_data.set_column(0,0,40 )
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
        
        demograph(vetsofvetCH, "(Veterans Only)", 80)
        ############################################veterans households without childre
        ##shelter type
        heading(vetNOCH, "Veteran HH without Children", 106)
        demograph(vetsofvetNOCH, "(Veterans Only)", 105)
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
        for ID in ythNum:
            HHSep = UNYTH.loc[UNYTH[58] ==ID]
            lenfam = HHSep[HHSep[6]=="Child"]
            if len(lenfam.index)>0:
                PARYth = PARYth.append(HHSep)
            else:
                NOparyth = NOparyth.append(HHSep)
        ythUnaccSi = UNYTH.append(YTSing)
        ythUnacc = ythUnaccSi.append(NOparyth)

        ###unaccompanied youth write out 
        demograph(ythUnacc, "(unaccompanied youth)", 135)
       
        #####chronic homelessness status

        ############################################Parenting youth                                                         14
        ##shelter type
        headerPar = ["Parenting Youth Households", " ", 'Sheltered ES', 'Sheltered TH', 'Sheltered SH', 'Unsheltered', 'Totals']
                #write worksheet header
        worksheet_data.write_row(('A155'), headerPar, cell_format_title)

        parentsOnly = PARYth[PARYth[6].isnull()]
        parentsover18 = parentsOnly[parentsOnly[13]>17]
        parentsunder18 = parentsOnly[parentsOnly[13]<18]

        for ID in parentsover18:
            youthFam = PARYth[PARYth[58]==ID]
            childofYth = youthFam[youthFam[6]=="Child"]
        for ID in parentsunder18:
            childFam = PARYth[PARYth[58]==ID]
            childofChild = childFam[childFam[6]=="Child"]
        def parYthWrite(dataField, title, row):
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
        parYthWrite(parentsunder18, "Number of parenting youth under Age 18",160)
        #header(PARYth, 'Parenting Youth Households', 152)
        demograph(parentsOnly, "(youth parents only)", 164)
        #####chronic homelessness status
        
        ##############################################Adult aids, mental illness etc.

        worksheet_data.write_array_formula("C14:F14", "{=SUM(C10:C13, F:10:F13)}")
        def sumppl(column, i):
                formula = "{=SUM("+column+(str(i-4)+":"+column+(str(i-1))+")}")
                worksheet_data.write_array_formula(column+(str(i))+column+(str(i)), formula)
        totgend = {("C",14), ("D",14),("E",14), ("F",14),("C",41), ("D",41),("E",41), ("F",41),("C",64), ("D",64),("E",64), ("F",64),("C",89), ("D",89), ("E",89), ("F",89),("C",114), ("D",114),("E",114), ("F",114),("C",140), ("D",140),("E",140), ("F",140),("C",169), ("D",169),("E",169), ("F",169)}
        for a,b in totgend:
            sumppl(a,b)
        ##final summation
        rows = list(range(4,29))
        rows2 = list(range(31,56))
        rows3 = list(range(58,82))

        def rowsum(rows):
            for i in rows:
                formula = "{=SUM(C"+(str(i)+":F"+(str(i))+")}")
                worksheet_data.write_array_formula('G'+(str(i))+'G'+(str(i)), formula)
        rowsum(rows)
        rowsum(rows2)
        rowsum(rows3)
        #worksheet_data.write_array_formula('G5:G5', "{=SUM(C5:F5)}")
        workbook.close()

      
        return



    ##############################scratch

  