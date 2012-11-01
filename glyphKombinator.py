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
        else:
        	print "Skipping %s" % glyph.name
    ufo1.save(destPath)
    print "Combined UFO saved at %s" % destPath


def isUFOpath(ufoPath):
	if os.path.isdir(ufoPath):
		if (len(ufoPath) > 4) and (ufoPath[-4:] in ['.ufo','.UFO']):
			return True
	return False


def getFontPath(string):
	fontPath = raw_input("Path to %s: " % string).strip()
	while not isUFOpath(fontPath):
		print "Not a valid path to a UFO font. Please try again."
		fontPath = raw_input("Path to %s: " % string).strip()
	return fontPath


if __name__=='__main__':
	path1 = getFontPath("first UFO")
	path2 = getFontPath("second UFO")
	
	if path1 != path2:
		destPath = path1.replace(path1[-4:], "_KOMB_" + path1[-4:])
		combineGlyphs(path1, path2, destPath)
	else:
		print "The two paths provided are the same UFO font!"