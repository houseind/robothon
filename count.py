# Counts the total number of glyphs of all the fonts in a directory tree

import os
from defcon import Font
from extractor import extractUFO


count = 0
fontCount = 0
employees = 11

for dirname, dirnames, filenames in os.walk(os.getcwd()):
    for fn in filenames:
        if fn.endswith('.otf') or fn.endswith('.ttf'):
            fontCount += 1
            fp = os.path.join(dirname, fn)
            font = Font()
            extractUFO(fp, font)
            count += len(font)
            print "Running total: %s glyphs in %s fonts." % (count, fontCount)
            
print """___________________________________________________
Final count: %s glyphs in %s fonts. %d glyphs per employee (gpe)""" % (count, fontCount, count/employees)