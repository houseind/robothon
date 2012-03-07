import os
from defcon import Font

def combineGlyphs(path1, path2, destPath):
    """
        Combines the glyphs of two UFOs and saves result to a new ufo.
        This only combines glyphs, so the first UFO path should be the one
        that you want all the metadata from.
    """
    
    ufo1 = Font(path1)
    ufo2 = Font(path2)
    added_glyphs = []
    for glyph in ufo2:
        if glyph.name not in ufo1:
            print "Inserting %s" % glyph.name
            ufo1.insertGlyph(glyph)
            added_glyphs.append(glyph.name)
    ufo1.save(destPath)

path1 = "Path to UFO"
path2 = "Path to UFO"
destPath = "Path to final UFO"

combineGlyphs(path1, path2, destPath)