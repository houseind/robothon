# InDesign CS5 Tagged Text


# Very basic setup for CS5 tagged text. Full spec is here: http://help.adobe.com/en_US/indesign/cs/taggedtext/indesign_cs5_taggedtext.pdf
# Note that <cSpecialGlyph> is not in that spec, however.

head = """<ASCII-MAC>
<Version:7.5><FeatureSet:InDesign-Roman><ColorTable:=<Black:COLOR:CMYK:Process:0,0,0,1>>
<DefineParaStyle:NormalParagraphStyle=<Nextstyle:NormalParagraphStyle>>
"""
paragraph = "<ParaStyle:NormalParagraphStyle>"

# This is awfully long, but gets the job done
glyph = "<cTypeface:%(style)s><cLigatures:0><cFont:%(family)s><cSpecialGlyph:%(glyph)s><cOTFContAlt:0><0xFFFD><cTypeface:><cLigatures:><cFont:><cSpecialGlyph:><cOTFContAlt:>"


from robofab.world import CurrentFont

font = CurrentFont()
path = font.path.split('.')[0] + '.txt'

family = font.info.openTypeNamePreferredFamilyName
style = font.info.openTypeNamePreferredSubfamilyName

out = head + paragraph

naked = font.naked()

for g in naked.glyphs:
    out = out + glyph % ({'family': family, 'style': style, 'glyph': g.index})
    
f = open(path, 'w')
f.write(out)
f.close()

