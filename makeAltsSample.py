from robofab.world import CurrentFont

alts = ['a.alt',  'A.swash',  'B.swash',  'C.alt',  'E.alt',  'E.altswash',  'E.swash',  'F.alt',  'F.altswash',  'F.swash',  'G.alt',  'h.swash',  'H.swash',  'J.alt',  'L.alt',  'm.swash',  'n.swash',  'P.swash',  'Q.alt',  'R.swash',  'R.swash2',  'S.alt',  'T.alt',  'Z.alt']

to_make = {'a':['acute', 'breve', 'circumflex', 'dieresis', 'grave', 'macron', 'ring', 'tilde'], 'A':['acute', 'breve', 'circumflex', 'dieresis', 'grave', 'macron', 'ring', 'tilde'], 'C':['acute', 'caron', 'circumflex', 'dotaccent'], 'E':['acute', 'caron', 'circumflex', 'dieresis', 'dotaccent', 'grave', 'macron', ], 'G':['breve', 'circumflex', 'commaaccent', 'dotaccent'], 'h':['circumflex'], 'H':['circumflex' ], 'J':['circumflex'], 'L':['acute', 'caron', 'commaaccent'], 'n':['acute', 'caron', 'commaaccent', 'tilde'], 'R':['acute', 'caron', 'commaaccent'], 'S':['acute', 'caron', 'circumflex', 'commaaccent'], 'T':['caron', 'uni021A'], 'Z':['acute', 'caron', 'dotaccent'],}

to_make_half = {'a':['aogonek'], 'A':['Aogonek'], 'C':['Ccedilla'], 'E':['Eogonek'], 'h':['hbar'], 'H':['Hbar'], 'L':['Lslash'], 'S':['Scedilla'], 'T':['Tcommaaccent'],}

font = CurrentFont()

print 'Making glyphs...'

for glyph in alts:
    base, extension = glyph.split('.')
    if base in to_make:
        for g in to_make[base]:
            if g == 'uni021A':
                old_name = 'uni021A'
                new_name = 'uni021A.' + extension
            else:
                old_name = base + g
                new_name = old_name + '.' + extension
            if new_name not in font:
                font.newGlyph(new_name)
                font[new_name].appendGlyph(font[glyph])
                old_comp = font[old_name].components
                offset = ()
                scale = ()
                if len(old_comp) != 0:
                    for c in old_comp:
                        if c.baseGlyph == g:
                            offset = c.offset
                            scale = c.scale
                        if base == 'L' and g == 'caron' and c.baseGlyph == 'caronSlovak':
                            offset = c.offset
                            scale = c.scale
                            g = 'caronSlovak'
                        if g == 'uni021A' and c.baseGlyph == 'commaaccent':
                            offset = c.offset
                            scale = c.scale
                            g = 'commaaccent'
                print 'Made: ' + new_name
                if offset != () and scale != ():
                    font[new_name].appendComponent(g, offset, scale)
                    font[new_name].width = font[old_name].width
                    font[new_name].mark = 200
                else:
                    font[new_name].mark = 100
                
    if base in to_make_half:
        for g in to_make_half[base]:
            new_name = g + '.' + extension
            if new_name not in font:
                font.newGlyph(new_name)
                font[new_name].appendGlyph(font[glyph])
                font[new_name].width = font[base].width
                font[new_name].mark = 100
font.update()
print 'done'