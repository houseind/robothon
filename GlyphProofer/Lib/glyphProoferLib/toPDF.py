import os
import time
from reportlab.pdfgen import canvas
from reportlab.platypus.paragraph import Paragraph
from reportlab.lib.styles import ParagraphStyle
from fontTools.pens.basePen import BasePen
try:
    from cElementTree import fromstring
except ImportError:
    from elementtree.ElementTree import fromstring


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
    
    glyphSpacing = 10
    
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

        "glyphPointSize" : 36,
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
    
    for name in names:
        flatResults.append(("line", majorLine))
        flatResults.append(("note", name))
        flatResults.append(("line", majorLine))
        flatResults.append(("blank line", None))
        flatResults.append(("glyph", name))
        flatResults.append(("blank line", None))

    lines = []
    for tag, content in flatResults:
        if tag == "line":
            lines.append((currentTop, content))
        elif tag == "blank line":
            currentTop -= blankLineHeight
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
            if currentTop - rH < margin:
                lines = _finishPage(pdf, lines, settings)
                _drawTemplate(pdf, settings)
                currentTop = startTop
            _drawHighlightBox(pdf, currentTop, rH, settings)
            p.drawOn(pdf, settings["resultsLeft"], currentTop - h - 3)
            _drawLabel(pdf, currentTop, "Glyph", settings)
            currentTop -= rH
        else:
            # make sure that we have room to start all this
            if currentTop - glyphEntryHeight < margin:
                lines = _finishPage(pdf, lines, settings)
                _drawTemplate(pdf, settings)
                currentTop = startTop
            _drawGlyphs(pdf, content, currentTop, fonts)
            currentTop -== glyphEntryHeight
    for top, weight in lines:
        _drawLine(pdf, top, weight, settings)
    pdf.save()

def _finishPage(pdf, lines, settings):
    for top, weight in lines:
        _drawLine(pdf, top, weight, settings)
    pdf.showPage()
    _drawLine(pdf, settings["startTop"], settings["minorLine"], settings)
    return [(settings["startTop"], lines[-1][1])]

def _drawGlyphs(pdf, name, top, fonts):
    pdf.saveState()
    pdf.translate(settings["resultsLeft"], top - 25)
    upm = fonts[0].info.unitsPerEm
    scale = float(settings["glyphPointSize"]) / upm
    pdf.scale(scale, scale)
    pdf.translate(0, -fonts[0].info.descender)
    for font in fonts:
        if name not in font:
            name = ".notdef"
        glyph = font[name]
        w = glyph.width
        pen = ReportLabPen(font, pdf)
        glyph.draw(pen)
        pdf.drawPath(pen.path, stroke=False, fill=True)
        pdf.translate(float(w + settings["glyphSpacing"], 0)
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
    