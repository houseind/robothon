# Combine kerning from two UFOs

import os
from robofab.ufoLib import UFOReader, UFOWriter


def combineKerning(path1, path2, destPath, WORRY=False):
    """
        This is a rather nasty tool, but it does the job. Give it two UFOs
        that you want to combine the kerning from. It'll go through, and combine
        the kerning of two UFOs.
        
        If WORRY is set to True, it will enforce a rule that one can't add together
        kerning that has groups which contain different members.
        
        It finishes by writing out a 'dummy' UFO, one that contains no glyphs, but only
        the groups and kerning info for the combined kerning. One must go in a open the
        UFO package to grab the kerning and put in into a UFO with the glyphs combined.
        
        This way, at least, the source UFOs are not touched, incase one needs to beat
        a retreat to the source UFOs.
    
    """
    
    ufo1 = UFOReader(path1)
    groups1 = ufo1.readGroups()
    kerning1 = ufo1.readKerning()
    ufo2 = UFOReader(path2)
    groups2 = ufo2.readGroups()
    kerning2 = ufo2.readKerning()
    combinedKerning = dict(kerning1)
    
    for pair, value in kerning2.items():
        if pair in combinedKerning:
            assert value == combinedKerning[pair]
        combinedKerning[pair] = value
    combinedGroups = {}
    for groups in (groups1, groups2):
        for name, group in groups.items():
            if not name.startswith("@MMK_"):
                continue
            if name in combinedGroups and WORRY:
                assert group == combinedGroups[name]
                combinedGroups[name] = group
            else:
                combinedGroups[name] = group
    ufo = UFOWriter(destPath)
    ufo.writeKerning(combinedKerning)
    ufo.writeGroups(combinedGroups)


path1 = "Path to UFO"
path2 = "Path to UFO"
destPath = "Path to result UFO"

combineKerning(path1, path2, destPath)