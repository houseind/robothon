# Compare kerning from two OTF/TTFs

import os
from compositor import Font

def get_flat_kerning(font):
    """ 
    Gives the kerning for the font. This is slow, you have been warned.
    """
    kerning = {}
    
    count = 0
    total = len(font.keys())
    checks = [int(total * 0.25), int(total * 0.5), int(total * 0.75)]
    
    for glyph in font.keys():
        for glyph_two in font.keys():
            pair = [glyph, glyph_two]
            if font.process(pair)[0].xAdvance != 0:
                assert pair not in kerning.keys()
                kerning[(pair[0], pair[1])] = font.process(pair)[0].xAdvance
        count += 1
        if count == checks[0]:
            print "One quarter done"
        if count == checks[1]:
            print "Half done"
        if count == checks[2]:
            print "Three quarters done"
            
    
    return kerning

def compare(flat_kerning, compare_font, deviation):
    """
    Compares the kerning from flat_kerning to compare_flat_kerning and
    returns a list of pairs that either are not in compare_flat_kerning
    or have a value in compre_flat_kerning that is greater than the
    value for deviation.
    """
    
    pair_list = []
    pairs_missing = []
    
    for pair in flat_kerning.keys():
        value_compare = compare_font.process([pair[0], pair[1]])[0].xAdvance
        if value_compare == 0 and abs(flat_kerning[pair]) > deviation:
            pairs_missing.append(pair)
        else:
            if abs(value_compare - flat_kerning[pair]) > deviation:
                pair_list.append(pair)
    
    return pair_list, pairs_missing

def run(fontPathOne, fontPathTwo, DEVIATION=0):
    print "Ingesting first font."
    firstFont = Font(fontPathOne)
    print "Font loaded, dissecting kerning now."
    firstKerning = get_flat_kerning(firstFont)
    print "Font ingested, loading second font."
    secondFont = Font(fontPathTwo)
    print "Loaded second font. Comparing kerning."
    pair_list, pairs_missing = compare(firstKerning, secondFont, DEVIATION)
    print str(len(pairs_missing)) + " Pairs from the first font are missing from the second font"
    print str(len(pair_list)) + " Pairs are different between the two fonts"
    print ""
    print "Missing Pairs:"
    for p in pairs_missing:
        print p[0] + ", " + p[1]
    print ""
    print "Pairs that are different:"
    for p in pair_list:
        print p[0] + ", " + p[1]



path1 = "path to font"
path2 = "path to font"
run(path1, path2)

