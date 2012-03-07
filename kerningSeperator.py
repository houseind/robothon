# Separate out kerning by unicode script value

import os
from defcon import Font

def separate(fontPath, unicodeScript, DELETE=False):
    """ Takes a font and removes any kerning that isn't either a group kern or
        a kern with a glyph from the specified unicode script category. See
        http://www.unicode.org/Public/6.1.0/ucd/Scripts.txt for a list of possible
        values for the script.
        
        By default the script will not actually delete anything, but will list what
        it would delete. Set DELETE to True if you want the script to delete pairs.
        
        If DELETE is set to True, the input UFO will be modified, use with caution.
    """
    font = Font(fontPath)
    
    for pair, value in sorted(font.kerning.items()):
        if pair[0].startswith("@") or pair[1].startswith("@"):
            pass
        elif font.unicodeData.scriptForGlyphName(pair[0]) != unicodeScript and font.unicodeData.scriptForGlyphName(pair[1]) != unicodeScript:
            if DELETE:
                print str(pair) + " deleted"
                del font.kerning[pair]
            else:
                print str(pair) + " would be deleted"
    if DELETE:
        font.save()
        print "Saved UFO."


separate("Path to font", "Script", DELETE=False)
