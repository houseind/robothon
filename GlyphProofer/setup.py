from distutils.core import setup
import py2app
import os

plist = dict(
    CFBundleIdentifier = "com.benkiel.GlyphProofer",
    LSMinimumSystemVersion = "10.6.0",
    CFBundleShortVersionString = "1.0.0",
    CFBundleVersion = "1.0.0",
    NSHumanReadableCopyright = "Copyright 2011 Ben Kiel. All rights reserved."
    )

dataFiles = [
        'Resources/English.lproj',
        ]

setup(
    data_files=dataFiles,
    app=[dict(script="GlyphProofer.py", plist=plist)]
    )
