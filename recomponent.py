import os
import unicodedata
from defcon import Font, UnicodeData, Component
from defcon.tools import unicodeTools

# Tool that walks a directory of UFOs and makes them componted again. This is very strict, things have to match 100%, 
# but it does get you some of the way done for recomponenting a font.
# It relies on unicode decompsition to know what pieces to try as components for a glyph.


# a mapping of unicodes to accent names. Edit as need be.
accent_mapping = {u'\u0300': ['grave'], u'\u0301': ['acute'], u'\u0302': ['circumflex'], u'\u0303': ['tilde'], u'\u0304': ['macron'], u'\u0305': ['macron'], u'\u0306': ['breve'], u'\u0307': ['dotaccent'], u'\u0308': ['dieresis'], u'\u030A': ['ring'], u'\u030B': ['hungarumlaut'], u'\u030C': ['caron', 'space_uni0326'], u'\u0327': ['cedilla'], u'\u0328': ['ogonek'], u'\u0326': ['space_uni0326']}

# glyphs that you want to have a second look at. 
double_check = {'space.lining': ['space'], 'dollar.lining': ['dollar'], 'cent.lining': ['cent'], 'Euro.lining': ['Euro'], 'sterling.lining': ['sterling'], 'yen.lining': ['yen'], 'florin.lining': ['florin'], 'zero.lining': ['zero'], 'one.lining': ['one'], 'two.lining': ['two'], 'three.lining': ['three'], 'four.lining': ['four'], 'five.lining': ['five'], 'six.lining': ['six'], 'seven.lining': ['seven'], 'eight.lining': ['eight'], 'nine.lining': ['nine'],}

# Glyphs that are composites that a unicode decomposition isn't going to pick up on
composites = {'oneeighth': ['one', 'fraction', 'eight'], 'onesixth': ['one', 'fraction', 'six'], 'onefifth': ['one', 'fraction', 'five'], 'onethird': ['one', 'fraction', 'three'], 'threeeighths': ['three', 'fraction', 'eight'], 'twofifths': ['two', 'fraction', 'five'], 'threefifths': ['three', 'fraction', 'five'], 'fiveeighths': ['five', 'fraction', 'eight'], 'twothirds': ['two', 'fraction', 'three'], 'fourfifths': ['four', 'fraction', 'five'], 'fivesixths': ['five', 'fraction', 'six'], 'seveneighths': ['seven', 'fraction', 'eight'], 'guillemotleft': ['guilsinglleft'], 'guillemotright': ['guilsinglright'], 'onehalf': ['one', 'fraction', 'two'], 'onequarter': ['one', 'fraction', 'four'], 'threequarters': ['three', 'fraction', 'four'], 'germandbls.scRound': ['S.sc'], 'germandbls.sc': ['S.sc'], }

def _make_test_glyph():
    import robofab.world
    f = robofab.world.RFont()
    newGlyph = f.newGlyph("test_glyph", clear=True)
    newGlyph.width = 150
    pen = newGlyph.getPen()
    pen.moveTo((0,0))
    pen.lineTo((10,0))
    pen.lineTo((20,20))
    pen.lineTo((0,30))
    pen.lineTo((0,0))
    pen.closePath()
    newGlyph.update()
    return newGlyph
    
def _make_test_glyphs():
    import robofab.world
    f = robofab.world.RFont()
    newGlyph = f.newGlyph("test_glyph", clear=True)
    newGlyph.width = 150
    pen = newGlyph.getPen()
    pen.moveTo((0,0))
    pen.lineTo((10,0))
    pen.lineTo((20,20))
    pen.lineTo((0,30))
    pen.lineTo((0,0))
    pen.closePath()
    newGlyph.update()
    accentedGlyph = f.newGlyph("test_glyph_accented", clear=True)
    accentedGlyph.width = 150
    pen = accentedGlyph.getPen()
    pen.moveTo((0,0))
    pen.lineTo((10,0))
    pen.lineTo((20,20))
    pen.lineTo((0,30))
    pen.lineTo((0,0))
    pen.closePath()
    pen.moveTo((5,35))
    pen.lineTo((10,35))
    pen.lineTo((10,40))
    pen.lineTo((5,40))
    pen.lineTo((5,35))
    pen.closePath()
    pen.moveTo((15,35))
    pen.lineTo((20,35))
    pen.lineTo((20,40))
    pen.lineTo((15,40))
    pen.lineTo((15,35))
    pen.closePath()
    accentedGlyph.update()
    componetGlyph = f.newGlyph("test_glyph_component", clear=True)
    componetGlyph.width = 200
    pen = componetGlyph.getPen()
    pen.moveTo((25,55))
    pen.lineTo((30,55))
    pen.lineTo((30,60))
    pen.lineTo((25,60))
    pen.lineTo((25,55))
    pen.closePath()
    pen.moveTo((35,55))
    pen.lineTo((40,55))
    pen.lineTo((40,60))
    pen.lineTo((35,60))
    pen.lineTo((35,55))
    pen.closePath()
    componetGlyph.update()
    componetGlyphWrong = f.newGlyph("test_glyph_component_wrong", clear=True)
    componetGlyphWrong.width = 200
    pen = componetGlyphWrong.getPen()
    pen.moveTo((25,55))
    pen.lineTo((30,55))
    pen.lineTo((30,60))
    pen.lineTo((25,60))
    pen.lineTo((25,55))
    pen.closePath()
    pen.moveTo((40,60))
    pen.lineTo((45,60))
    pen.lineTo((45,65))
    pen.lineTo((40,65))
    pen.lineTo((40,60))
    pen.closePath()
    componetGlyphWrong.update()
    return newGlyph, accentedGlyph, componetGlyph, componetGlyphWrong
    

def _findAvailablePathName(path):
    import time
    folder = os.path.dirname(path)
    fileName = os.path.basename(path)
    fileName, extension = os.path.splitext(fileName)
    stamp = time.strftime("%Y-%m-%d %H-%M-%S %Z")
    newFileName = "%s (%s)%s" % (fileName, stamp, extension)
    newPath = os.path.join(folder, newFileName)
    # intentionally break to prevent a file overwrite
    # this could happen if the user has a director full
    # of files with future time stamped file names.
    # not likely, but avoid it all the same.
    assert not os.path.exists(newPath)
    return newPath

def _get_pt_digest(glyph):
    """
    Returns a list of tuples that represent the (x,y) difference between the last point and the current point.
    This starts with the first point in the contour compared with the last point, and then the second point compared to the first, etc.
    
    >>> glyph = _make_test_glyph()
    >>> _get_pt_digest(glyph)
    [(0, [(0, 30), (-10, 0), (-10, -20), (20, -10)])]
    """
    digest = []
    for contour in glyph:
        contour_digest = []
        for i, point in enumerate(contour):
            if i is 0:
                contour_digest.append((contour[len(contour)-1].x-point.x, contour[len(contour)-1].y-point.y))
            else:
                contour_digest.append((contour[i-1].x-point.x, contour[i-1].y-point.y))
        digest.append((glyph.contourIndex(contour), contour_digest))
    return digest

def _shift_in_place(l, n):
    """
    Shifts a list in place with n as the number of slots to shift the head
    
    >>> _shift_in_place([1,2,3,4], 1)
    [2, 3, 4, 1]
    >>> _shift_in_place([1,2,3,4], 2)
    [3, 4, 1, 2]
    """
    
    n = n % len(l)
    head = l[:n]
    l[:n] = []
    l.extend(head)
    return l

def _get_bounding_bounds(glyph, contour_list):
    """
    Need a way to take in a bunch of contours and get the overall bounding bounds, to compare widths/heights with 
    a componet to be sure that you don't replace something that may have the same contours, but arranged differntly
    
    >>> glyph, accentedGlyph, accent, accent_wrong = _make_test_glyphs()
    >>> _get_bounding_bounds(glyph, [0])
    (0, 0, 20, 30)
    >>> _get_bounding_bounds(accentedGlyph, [0,1])
    (0, 0, 20, 40)
    >>> _get_bounding_bounds(accentedGlyph, [0,1,2])
    (0, 0, 20, 40)
    >>> _get_bounding_bounds(accentedGlyph, [2])
    (15, 35, 20, 40)
    """
    start = glyph[contour_list[0]].bounds
    for c in contour_list:
        xMin, yMin, xMax, yMax = glyph[c].bounds
        if start[0] < xMin: xMin = start[0]
        if start[1] < yMin: yMin = start[1]
        if start[2] > xMax: xMax = start[2]
        if start[3] > yMax: yMax = start[3]
        start = xMin, yMin, xMax, yMax
    return start

def _digest_equal(d1, d2):
    """
    Looks to see if two digests are the same. First step is easy, then it sifts
    the second digest around in place to see if the start points were just different.
    
    >>> _digest_equal([(0,10), (10,0), (0,10), (-10,0)],[(0,10), (10,0), (0,10), (-10,0)])
    True
    >>> _digest_equal([(0,10), (10,0), (0,10), (-10,0)],[(10,0), (0,10), (-10,0), (0,10)])
    True
    >>> _digest_equal([(0,10), (10,0), (0,10), (-10,0)],[(0,10), (10,0), (0,10), (0,0)])
    False
    """
    if d1 == d2:
        return True
    else:
        count = len(d2)
        while count > 0:
            count = count-1
            d2 = _shift_in_place(d2,1)
            if d1 == d2:
                return True
        return False


def _decompose_helper(font, uniValue, parts):
    letterCategories = ("Ll", "Lu", "Lt", "Lo")
    try:
        c = unichr(uniValue)
    # see not in category function
    except ValueError:
        return -1
    decomposition = unicodedata.decomposition(c)
    if decomposition.startswith("<"):
        return -1
    if " " not in decomposition:
        return -1
    parts_internal = decomposition.split(" ")
    unichrs = [unichr(int(i, 16)) for i in parts_internal if i]
    letters = [ord(i) for i in unichrs if unicodedata.category(i) in letterCategories]
    parts = parts + [i for i in unichrs if i not in letters]
    if len(letters) != 1:
        return -1
    decomposedUniValue = letters[0]
    if _decompose_helper(font, decomposedUniValue, parts) != -1:
        furtherDecomposedUniValue, furtherParts = _decompose_helper(font, decomposedUniValue, parts)
        if _decompose_helper(font, furtherDecomposedUniValue, furtherParts) != -1:
            furtherFurtherDecomposedUniValue, furtherFurtherParts = _decompose_helper(font, furtherDecomposedUniValue, furtherParts)
            decomposedUniValue = furtherFurtherDecomposedUniValue
            parts = furtherFurtherParts
        else:
            decomposedUniValue = furtherDecomposedUniValue
            parts = furtherParts
    return decomposedUniValue, parts


def decompose_glyph(font, glyphname, glyphs, allowPseudoUnicode=True):
    if allowPseudoUnicode:
        uniValue = UnicodeData.pseudoUnicodeForGlyphName(font, glyphname)
    else:
        uniValue = UnicodeData.unicodeForGlyphName(font, glyphname)
    if uniValue is None:
        return [glyphname, ]
    else:
        decomposed = _decompose_helper(font, uniValue, [])
        if decomposed == -1:
            parts = -1
        else:
            parts = []
            for g in decomposed[1]:
                if g in accent_mapping.keys():
                    for a in accent_mapping[g]:
                        parts.append(a)
                elif font.glyphNameForUnicode(ord(g)) is not None:
                    parts.append(font.glyphNameForUnicode(ord(g)))
        possible_components = []
        if parts is not None and parts != -1:
            for part in parts:
                if part in glyphs:
                    for x in glyphs[part]:
                        possible_components.append(x)
                else:
                    if part not in possible_components:
                        possible_components.append(part)
        return possible_components

        
def compare_glyph(font, glyph, component_glyph):
    """
    Looks at a glyph and a possible componet to see if there is a match
    Returns the lowest and leftest corner of the outlines the componet is replacing & the contour number, if it can
    
    >>> glyph, accentedGlyph, accent, accent_wrong = _make_test_glyphs()
    >>> compare_glyph(font, glyph, accent)
    False
    >>> compare_glyph(font, accentedGlyph, glyph)
    ((0, 0), [0])
    >>> compare_glyph(font, accentedGlyph, accent)
    ((5, 35), [1, 2])
    >>> compare_glyph(font, accentedGlyph, accentedGlyph)
    ((0, 0), [0, 1, 2])
    >>> compare_glyph(font, accentedGlyph, accent_wrong)
    False
    """
    search = []
    contours_replaced = []
    
    # make sure that a componet glyph isn't a componet itself
    if len(component_glyph) is 0 and len(component_glyph.components) is not 0:
        component_glyph = font[component_glyph.components[0].baseGlyph]
    glyph_digest = _get_pt_digest(glyph)
    component_digest = _get_pt_digest(component_glyph)
    for d in component_digest:
        for d1 in glyph_digest:
            if _digest_equal(d1[1], d[1]):
                search.append((d1[0], d[0]))
                if d1[0] not in contours_replaced:
                    contours_replaced.append(d1[0])
            else:
                pass
    test = {}
    for x in search:
        if x[1] not in test:
            test[x[1]] = x[0]
    if len(search) is not 0 and len(test) is len(component_glyph):
        # Need to figure out if we've hit the case of contours matching
        # but they aren't actually equal in terms of placement (think
        # of a dieresis that has had the distance between dots changed)
        componet_bounds = component_glyph.bounds
        replace_bounds = _get_bounding_bounds(glyph, [x[0] for x in search])
        if componet_bounds[2] - componet_bounds[0] == replace_bounds[2] - replace_bounds[0] and componet_bounds[3] - componet_bounds[1] == replace_bounds[3] - replace_bounds[1]:
            start = (glyph[search[0][0]].bounds[0], glyph[search[0][0]].bounds[1])
            for i in search:
                if glyph[i[0]].bounds[0] < start[0]:
                    start = (glyph[i[0]].bounds[0], start[1])
                if glyph[i[0]].bounds[1] < start[1]:
                    start = (start[0], glyph[i[0]].bounds[1])
            return start, contours_replaced
        else:
            return -1
    else:
        return -1

def recomponet(path_to_orignal, path_to_new=None):
    assert os.path.exists(path_to_orignal)
    font = Font(path_to_orignal)
    if path_to_new is not None:
        assert os.path.exists(path_to_new)
        font.save(path_to_new)
        font = Font(path_to_new)
    else:
        new_path = _findAvailablePathName(path_to_orignal)
        font.save(new_path)
        font = Font(new_path)

    ordered_glyphs = {}
    clean_up = []
    for key in font.keys():
        parts = key.split('.')
        if len(parts) == 1:
            part = key
            if key.endswith('comb'):
                part = key[:-4]
                clean_up.append(key)
            if part not in ordered_glyphs:
                ordered_glyphs[part] = [key, ]
            else:
                glyphs = ordered_glyphs[part]
                if key not in glyphs:
                    glyphs.append(key)
                    ordered_glyphs[part] = glyphs
        else:
            part = parts[0]
            if part.endswith('comb'):
                part = parts[0][:-4]
                clean_up.append(key)
            if part not in ordered_glyphs:
                ordered_glyphs[part] = [key, ]
            else:
                glyphs = ordered_glyphs[part]
                if key not in glyphs:
                    glyphs.append(key)
                    ordered_glyphs[part] = glyphs
    for i in clean_up:
        if i not in ordered_glyphs:
            part = i[:-4]
            if part in ordered_glyphs:
                glyphs = ordered_glyphs[part]
                ordered_glyphs[i] = glyphs
    
    # Cleanup for the i
    i = ordered_glyphs['i']
    i.append('dotlessi')
    ordered_glyphs['i'] = i
    
    # Additional cleanup for the pesky commaaccent
    if 'uni0327' not in ordered_glyphs:
        ordered_glyphs['uni0327'] = ['uni0326', ]
    else:
        if 'uni0326' not in ordered_glyphs['uni0327']:
            glyphs = ordered_glyphs['uni0327']
            glyphs.append('uni0326')
            ordered_glyphs['uni0327'] = glyphs
    found = []
    for glyph in font:
        if len(glyph) is not 0:
            parts = decompose_glyph(font.unicodeData, glyph.name, ordered_glyphs)
            if len(parts) > 1:
                print 'normal'
                print glyph.name
                for part in parts:
                    if part in font.keys() and compare_glyph(font, glyph, font[part]) is not -1:
                        orgin, delete = compare_glyph(font, glyph, font[part])
                        if len(font[part]) is 0 and len(font[part].components) is not 0:
                            part = font[part].components[0].baseGlyph
                        found.append(glyph.name)
                        for x in [glyph[x] for x in delete]:
                            glyph.removeContour(x)
                        component = Component()
                        component.baseGlyph = part
                        glyph.appendComponent(component)
                        xMin, yMin, xMax, yMax = component.bounds
                        moveX = orgin[0] - xMin
                        moveY = orgin[1] - yMin
                        component.move((moveX, moveY))
            elif glyph.name in double_check.keys():
                parts = double_check[glyph.name]
                print glyph.name
                print 'double check'
                print parts
                for part in parts:
                    print part
                    if part in font.keys() and compare_glyph(font, glyph, font[part]) is not -1:
                        orgin, delete = compare_glyph(font, glyph, font[part])
                        if len(font[part]) is 0 and len(font[part].components) is not 0:
                            part = font[part].components[0].baseGlyph
                        found.append(glyph.name)
                        for x in [glyph[x] for x in delete]:
                            glyph.removeContour(x)
                        component = Component()
                        component.baseGlyph = part
                        glyph.appendComponent(component)
                        xMin, yMin, xMax, yMax = component.bounds
                        moveX = orgin[0] - xMin
                        moveY = orgin[1] - yMin
                        component.move((moveX, moveY))
                        print 'done'
                        break
                    else:
                        print part
                        print 'did not check out'
            elif glyph.name in composites.keys():
                preparts = composites[glyph.name]
                parts = []
                for p in preparts:
                    parts.append(p)
                    if p in ordered_glyphs:
                        for x in ordered_glyphs[p]:
                            parts.append(x)
                print glyph.name
                print 'composite'
                print parts
                for part in parts:
                    if compare_glyph(font, glyph, font[part]) is not -1:
                        orgin, delete = compare_glyph(font, glyph, font[part])
                        if len(font[part]) is 0 and len(font[part].components) is not 0:
                            part = font[part].components[0].baseGlyph
                        found.append(glyph.name)
                        for x in [glyph[x] for x in delete]:
                            glyph.removeContour(x)
                        component = Component()
                        component.baseGlyph = part
                        glyph.appendComponent(component)
                        xMin, yMin, xMax, yMax = component.bounds
                        moveX = orgin[0] - xMin
                        moveY = orgin[1] - yMin
                        component.move((moveX, moveY))
    font.save()
    print 'Found:'
    print ' '
    for x in found:
        print x
    print '----------------'
    print str(len(found)) + ' Glyphs'


def walk(someFolder, extension):
    extension = extension.lower()
    files = []
    names = os.listdir(someFolder)
    for n in names:
        p = os.path.join(someFolder, n)
        if n.lower().find(extension) <> -1:
            files.append(p)
    return files

def main():
    fonts = walk(os.getcwd(), '.ufo')
    for font in fonts:
        print font
        recomponet(font)

if __name__ == "__main__":
    main()
