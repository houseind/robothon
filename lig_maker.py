from robofab.world import CurrentFont
from robofab.gString import splitAccent

position = {'Aacute':['acute', (318, 0)], 'Abreve':['breve', (248, 0)], 'Acircumflex':['circumflex', (255, 0)], 'Adieresis':['dieresis', (239, 0)], 'Atilde':['tilde', (240, 0)], 'Agrave':['grave', (183, 0)], 'Amacron':['macron', (239, 0)], 'Jcircumflex':['circumflex', (387, 0)], 'Lacute':['acute', (156, 0)], 'Lcaron':['caron', (91, 0)], 'Lcommaaccent':['commaaccent', (209, 0)], 'Tcaron':['caron', (276, 0)], 'uni021A':['commaaccent', (269, 0)], 'Tcommaaccent':['cedilla', (231, 0)], }

accented = {'A':['A','Aacute', 'Abreve', 'Acircumflex', 'Adieresis', 'Atilde', 'Agrave', 'Amacron',], 'J':['J','Jcircumflex'], 'L':['L','Lacute', 'Lcaron', 'Lcommaaccent',], 'T':['T','Tcaron', 'uni021A', 'Tcommaaccent',]} 

base = ['A_T', 'T_A', 'A_T_A', 'F_J', 'P_J', 'T_J', 'L_T', 'T_AE', 'Thorn_J', 'A_T_AE', 'Lslash_T', 'Aring_T', 'T_Aring', 'Aring_T_A', 'A_T_Aring', 'Aring_T_Aring', 'Aogonek_T', 'T_Aogonek', 'Aogonek_T_A', 'A_T_Aogonek', 'Aogonek_T_Aogonek',]

font = CurrentFont()

def combinations(lists):
    if not lists: return [ [] ]
    more = combinations(lists[1:])
    return [ [i]+js for i in lists[0] for js in more ]

for lig in base:
    parts = lig.split('_')
    temp = []
    for x in parts:
        if x in accented.keys():
            temp.append(accented[x])
        else:
            temp.append([x])
    toMake = combinations(temp)
    for i in toMake:
        name = ''
        for x in i:
            name = name + '_' + x
        name = name[1:]
        if name not in font.keys():
            font.newGlyph(name)
            font[name].appendComponent(lig)
            font[name].mark = 200
            font[name].rightMargin = 20
            glyphs = name.split('_')
            previous = ''
            index = 1
            for n in glyphs:
                if n in position.keys():
                    if index == 1:
                        font[name].appendComponent(position[n][0], position[n][1])
                    if index == 2:
                        if splitAccent(n)[0] == 'J':
                            p = (position[n][1][0] + 854, position[n][1][1])
                        elif previous == 'A':
                            p = (position[n][1][0] + 865, position[n][1][1])
                        elif previous == 'L':
                            p = (position[n][1][0] + 781, position[n][1][1])
                        else:
                            p = (position[n][1][0] + 921, position[n][1][1])
                        font[name].appendComponent(position[n][0], p)
                    if index == 3:
                        p = (position[n][1][0] + 1786, position[n][1][1])
                        font[name].appendComponent(position[n][0], p)
                previous = splitAccent(glyphs[0])[0]
                index = index + 1
font.update()
print 'done'