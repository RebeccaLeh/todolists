
polygonLayer = arcpy.GetParameterAsText(0)
try:
    # substance
    switch = arcpy.GetParameterAsText(1)
except:
        switch = None
#switch = arcpy.GetParameterAsText(1)

def calculate_max(table,field):
    na = arcpy.da.TableToNumPyArray(table,field)
    return numpy.maximum([field])

list = []

words = switch.split(';')
for i in words:
    list.append(i)

arcpy.AddMessage(list)
if switch != None: 
    for name in words:
        arcpy.AddMessage(name)
        #max = calculate_max(polygonLayer, name)
        arcpy.CalculateField_management(polygonLayer, name, '{max}-(!{field}!)'.format(max=max, field=name))
