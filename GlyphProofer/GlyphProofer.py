from AppKit import *
import os
import time
from PyObjCTools import AppHelper
from defcon import Font
from extractor import extractUFO
import vanilla
from defconAppKit.windows.baseWindow import BaseWindowController
from reportlab.pdfgen import canvas
from reportlab.platypus.paragraph import Paragraph
from reportlab.lib.styles import ParagraphStyle
from fontTools.pens.basePen import BasePen

import objc
objc.setVerbose(True)


class GlyphProoferAppDelegate(NSObject):

    def applicationDidFinishLaunching_(self, notification):
        GlyphProoferWindow()

class UFOPathFormatter(NSFormatter):

    def stringForObjectValue_(self, obj):
        if obj is None or isinstance(obj, NSNull):
            return ""
        return os.path.basename(obj)

    def objectValueForString_(self, string):
        return string

class GlyphProoferWindow(BaseWindowController):
    
    def __init__(self):
        width = 300
        
        # Main Window
        self.w = vanilla.Window((width, 400), "Glyph Proofer", minSize=(width, 300), maxSize=(width, 1000))
        
        # Add a drop-able font list
        columnDescriptions = [dict(title="path", formatter=UFOPathFormatter.alloc().init())]
        self.w.fontList = vanilla.List((15, 15, -15, -50), [], columnDescriptions=columnDescriptions, showColumnTitles=False, enableDelete=True, drawFocusRing=False, otherApplicationDropSettings=dict(type=NSFilenamesPboardType, operation=NSDragOperationCopy, callback=self.dropFontCallback))
        
        self.w.makePDFButton = vanilla.Button((-120, -37, -16, 20), "Generate PDF", callback=self.makePDFButtonCallback)
        self.setUpBaseWindowBehavior()
        self.w.open()

    def dropFontCallback(self, sender, dropInfo):
        acceptedFonts = [".ufo", ".ttf", ".otf"]
        isProposal = dropInfo["isProposal"]
        paths = dropInfo["data"]
        paths = [dict(path=path) for path in paths if os.path.splitext(path)[-1].lower() in acceptedFonts]
        paths = [path for path in paths if path not in self.w.fontList]
        if not paths:
            return False
        if not isProposal:
            self.w.fontList.extend(paths)
        return True

    def makePDFButtonCallback(self, sender):
        validPaths = []
        for d in self.w.fontList:
            path = d["path"]
            if os.path.exists(path):
                validPaths.append(path)
        if len(validPaths) > 0:
            from reportlab.lib.pagesizes import LETTER
            fonts = getFonts(validPaths)
            names = getNames(fonts)
            path = findAvailableFileName(os.path.expanduser("~/Desktop"), "report", "pdf")
            makePDF(names, fonts, LETTER, path)
        
        
def makeFileName(directory, baseName, extension, counter=None):
    if counter:
        b = "%s %d.%s" % (baseName, counter, extension)
    else:
        b = "%s.%s" % (baseName, extension)
    return os.path.join(directory, b)

def findAvailableFileName(directory, baseName, extension, counter=0):
    # add number
    if counter:
        fileName = makeFileName(directory, baseName, extension, counter)
    # no number
    else:
        fileName = makeFileName(directory, baseName, extension)
    # recurse if necessary
    if os.path.exists(fileName):
        fileName = findAvailableFileName(directory, baseName, extension, counter+1)
    # done
    return fileName
    
def getFonts(paths):
    """Takes in paths, gives list of fonts"""
    fonts = []
    for path in paths:
        if os.path.splitext(path)[-1].lower() == ".ufo":
            font = Font(path)
        else:
            font = Font()
            extractUFO(path, font, doKerning=False)
        fonts.append(font)
    fonts.sort(key=lambda weight: font.info.openTypeOS2WeightClass)
    return fonts

def getNames(fonts):
    """Takes in a list of font objects and writes out XML list of glyphs"""    
    names = []
    for font in fonts:
        for k in font.keys():
            if k not in names:
                names.append(k)
    names.sort()
    return names
    
class ReportLabPen(BasePen):

    def __init__(self, glyphSet, canvas):
        BasePen.__init__(self, glyphSet)
        self.path = canvas.beginPath()

    def _moveTo(self, (x,y)):
        self.path.moveTo(x,y)

    def _lineTo(self, (x,y)):
        self.path.lineTo(x,y)

    def _curveToOne(self, (x1,y1), (x2,y2), (x3,y3)):
        self.path.curveTo(x1, y1, x2, y2, x3, y3)

    def _closePath(self):
        pass
        
def makePDF(names, fonts, pageSize, path):
    width, height = pageSize
    margin = 36
    resultsLeft = 100
    resultsRight = width - margin
    startTop = height - 75

    blankLineHeight = 20
    entryHeight = 20
    glyphEntryHeight = 48

    minorLine = .3
    majorLine = 1
    
    glyphSpacing = 120
    
    settings = {
        "date" : time.asctime(),

        "width" : width,
        "height" : height,
        "margin" : margin,
        "labelRight" : 90,
        "resultsLeft" : resultsLeft,
        "resultsRight" : resultsRight,
        "resultsWidth" : resultsRight - resultsLeft,
        "labelWidth" : width - margin - resultsLeft,
        "contentWidth" : width - (margin * 2),
        "startTop" : startTop,

        "regularFont" : "Helvetica",
        "boldFont" : "Helvetica-Bold",
        "textPointSize" : 10,
        "textLeading" : 15,
        "entryHeight" : entryHeight,

        "glyphPointSize" : 48,
        "glyphEntryHeight" : glyphEntryHeight,

        "minorLine" : minorLine,
        "majorLine" : majorLine,
        
        "glyphSpacing" : glyphSpacing,

    }

    basicStyle = ParagraphStyle("BasicReport")
    basicStyle.fontName = settings["regularFont"]
    basicStyle.fontSize = settings["textPointSize"]
    basicStyle.leading = settings["textLeading"]
    
    pdf = canvas.Canvas(path, pagesize=pageSize)
    
    _drawTemplate(pdf, settings)
    
    flatResults = []
    currentTop = startTop
    
    head = [u"Fonts tested:", ]
    for font in fonts:
        head.append(u"%s: %s" % (font.info.postscriptFullName, font.path))
    flatResults.append(("head", head))
    flatResults.append(("blank line", None))
    
    for name in names:
        flatResults.append(("line", majorLine))
        flatResults.append(("note", name))
        flatResults.append(("line", majorLine))
        flatResults.append(("blank line", None))
        flatResults.append(("blank line", None))
        flatResults.append(("glyph", name))

    lines = []
    for tag, content in flatResults:
        if tag == "line":
            lines.append((currentTop, content))
        elif tag == "blank line":
            currentTop -= blankLineHeight
        elif tag == "head":
            entities = [
                ("&", "&amp;"),
                ("<", "&lt;"),
                (">", "&gt;"),
                ('"', "&quot;"),
                ("'", "&apos;"),
            ]
            pdf.setFillColorRGB(0, 0, 0)
            textObject = pdf.beginText(margin, currentTop - 13)
            textObject.setFont(settings["boldFont"], settings["textPointSize"], leading=12)
            start = textObject.getY()
            for line in content:
                if line != content[0]:
                    textObject.setFont(settings["regularFont"], settings["textPointSize"], leading=12)
                for b, a in entities:
                    content = line.replace(b, a)
                textObject.textLine(line)
            end = textObject.getY()
            pdf.drawText(textObject)
            currentTop -= (start - end)
        elif tag == "note":
            entities = [
                ("&", "&amp;"),
                ("<", "&lt;"),
                (">", "&gt;"),
                ('"', "&quot;"),
                ("'", "&apos;"),
            ]
            for b, a in entities:
                content = content.replace(b, a)
            p = Paragraph(content, basicStyle)
            w, h = p.wrap(settings["resultsWidth"], 5000)
            rH = h + ((h / settings["textLeading"]) * 5)
            if rH > 20:
                rH -= ((rH / 20) - 1) * 5
            if currentTop - (rH + glyphEntryHeight + blankLineHeight * 2) < margin:
                lines = _finishPage(pdf, lines, settings)
                _drawTemplate(pdf, settings)
                currentTop = startTop
            _drawHighlightBox(pdf, currentTop, rH, settings)
            p.drawOn(pdf, settings["resultsLeft"], currentTop - h - 3)
            _drawLabel(pdf, currentTop, "glyph:", settings)
            currentTop -= rH
        else:
            # make sure that we have room to start all this
            if currentTop - glyphEntryHeight < margin:
                lines = _finishPage(pdf, lines, settings)
                _drawTemplate(pdf, settings)
                currentTop = startTop
            _drawGlyphs(pdf, content, currentTop, fonts, settings)
            currentTop -= glyphEntryHeight
    for top, weight in lines:
        _drawLine(pdf, top, weight, settings)
    pdf.save()

def _finishPage(pdf, lines, settings):
    for top, weight in lines:
        _drawLine(pdf, top, weight, settings)
    pdf.showPage()
    _drawLine(pdf, settings["startTop"], settings["minorLine"], settings)
    return [(settings["startTop"], lines[-1][1])]

def _drawGlyphs(pdf, name, top, fonts, settings):
    pdf.saveState()
    pdf.translate(settings["resultsLeft"], top - 25)
    upm = fonts[0].info.unitsPerEm
    scale = float(settings["glyphPointSize"]) / upm
    pdf.scale(scale, scale)
    pdf.translate(0, -fonts[0].info.descender)
    for font in fonts:
        if name not in font:
            glyph = font[".notdef"]
        else:
            glyph = font[name]
        w = glyph.width
        pen = ReportLabPen(font, pdf)
        glyph.draw(pen)
        pdf.setFillColorRGB(0, 0, 0)
        pdf.drawPath(pen.path, stroke=False, fill=True)
        pdf.translate(float(w + settings["glyphSpacing"]), 0)
    pdf.restoreState()
    
def _drawLine(pdf, top, weight, settings):
    pdf.setFillColorRGB(0, 0, 0)
    pdf.setLineWidth(weight)
    pdf.line(settings["margin"], top, settings["resultsRight"], top)
    
def _drawHighlightBox(pdf, t, h, settings):
    pdf.setFillColorRGB(.95, .95, .95)
    pdf.rect(settings["margin"], t-h, settings["contentWidth"], h, stroke=False, fill=True)

def _drawLabel(pdf, top, text, settings):
    pdf.setFont(settings["regularFont"], settings["textPointSize"], leading=settings["textLeading"])
    pdf.setFillColorRGB(.5, .5, .5)
    pdf.drawRightString(settings["labelRight"], top - 13, text)
    
def _drawTemplate(pdf, settings):
    barHeight = 18
    barBottom = settings["height"] - settings["margin"] - barHeight
    barLeft = settings["margin"]
    barWidth = settings["width"] - (settings["margin"] * 2)
    pdf.setFillColorRGB(0, 0, 0)
    pdf.rect(barLeft, barBottom, barWidth, barHeight, stroke=False, fill=True)
    pdf.setFillColorRGB(1, 1, 1)
    pdf.setFont(settings["boldFont"], 8)
    text = u"%s" % (settings["date"])
    pdf.drawString(barLeft + 5, barBottom + 7, text)
    pdf.drawRightString(barLeft + barWidth - 5, barBottom + 7, str(pdf.getPageNumber()))
    
if __name__ == "__main__":
    AppHelper.runEventLoop()