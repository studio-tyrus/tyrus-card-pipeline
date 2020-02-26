from element import Element
import os
import svgutils.transform as sg
import xml.etree.ElementTree as ET
from wand.image import Image
       
def createArtFileOfPiece(game, gameCompose, component, pieceGamedata, artMetaData, outputDirectory):
    if game == None:
        print("game cannot be None.")
        return
    
    if component == None:
        print("component cannot be None.")
        return

    if artMetaData == None:
        print("artMetaData cannot be None.")
        return

    if pieceGamedata == None:
        print("pieceGamedata cannot be None.")
        return

    if outputDirectory == None: 
        print("outputDirectory cannot be None.")
        return

    templateFilesDirectory = gameCompose["artTemplatesDirectory"]
    artFile = Element("%s/%s.svg" % (templateFilesDirectory, artMetaData["templateFilename"])) 

    addOverlays(artFile, artMetaData["overlays"], game, gameCompose, component, pieceGamedata)

    artFileOutputName = ("%s-%s" % (component["name"], pieceGamedata["name"]))
    artFileOutputFilepath = "%s/%s.svg" % (outputDirectory, artFileOutputName)
    artFile.dump(artFileOutputFilepath)
    
    textReplaceInFile(artFileOutputFilepath, artMetaData["textReplacements"], game, component, pieceGamedata)
    updateStylesInFile(artFileOutputFilepath, artMetaData["styleUpdates"], game, component, pieceGamedata)

    exportSvgToJpg(artFileOutputFilepath, artFileOutputName, outputDirectory)

def addOverlays(artFile, overlays, game, gameCompose, component, pieceGamedata):
    if artFile == None:
        print("artFile cannot be None.")
        return

    if overlays == None: 
        print("overlays cannot be None.")
        return

    if game == None:
        print("game cannot be None.")
        return
    
    if component == None:
        print("component cannot be None.")
        return

    if pieceGamedata == None:
        print("pieceGamedata cannot be None.")
        return

    overlayFilesDirectory = gameCompose["artInsertsDirectory"]

    for overlay in overlays:
        overlayName = getScopedValue(overlay, game, component, pieceGamedata)
        if overlayName != None and overlayName != "":
            graphicsInsert = Element("%s/%s.svg" % (overlayFilesDirectory, overlayName))
            artFile.placeat(graphicsInsert, 0.0, 0.0)

def textReplaceInFile(filepath, textReplacements, game, component, pieceGamedata):
    if filepath == None:
        print("filepath cannot be None.")
        return

    if textReplacements == None: 
        print("textReplacements cannot be None.")
        return

    if game == None:
        print("game cannot be None.")
        return
    
    if component == None:
        print("component cannot be None.")
        return

    if pieceGamedata == None:
        print("pieceGamedata cannot be None.")
        return
    
    contents = ""
    with open(filepath, 'r') as f:
        contents = f.read()
        for textReplacement in textReplacements:
            key = "{%s}" % textReplacement["key"]
            value = getScopedValue(textReplacement, game, component, pieceGamedata)
            value = processValueFilters(value, textReplacement)
            contents = contents.replace(key, value)

    with open(filepath,'w') as f:
        f.write(contents)

def processValueFilters(value, textReplacement):
    if "filters" in textReplacement:
        for filter in textReplacement["filters"]:
            if filter == "toUpper":
                value = value.upper()
    return value

def updateStylesInFile(filepath, styleUpdates, game, component, pieceGamedata):
    if filepath == None:
        print("filepath cannot be None.")
        return

    if styleUpdates == None: 
        print("styleUpdates cannot be None.")
        return

    if game == None:
        print("game cannot be None.")
        return
    
    if component == None:
        print("component cannot be None.")
        return

    if pieceGamedata == None:
        print("pieceGamedata cannot be None.")
        return
    
    tree = ET.parse(filepath).getroot()
    
    for styleUpdate in styleUpdates:
        findById = styleUpdate["id"]
        sh = tree.find(".//*[@id='%s']" % findById)
        
        value = getScopedValue(styleUpdate, game, component, pieceGamedata)

        cssKey = styleUpdate["cssValue"]
        replaceStyleWith = "%s:%s" % (cssKey, value)
        sh.set('style', replaceStyleWith)

    with open(filepath,'w') as f:
        f.write(ET.tostring(tree))

def getScopedValue(scopedValue, game, component, pieceGamedata):
    if scopedValue == None:
        print("scopedValue cannot be None.")
        return

    if game == None:
        print("game cannot be None.")
        return
    
    if component == None:
        print("component cannot be None.")
        return

    if pieceGamedata == None:
        print("pieceGamedata cannot be None.")
        return
    
    scope = scopedValue["scope"]
    source = scopedValue["source"]

    if scope == "game":
        return game[source]
    
    if scope == "component":
        return component[source]

    return pieceGamedata[source]

def exportSvgToJpg(filepath, name, outputDirectory):
    with Image(filename=filepath, resolution=1148, colorspace="rgb") as image:
        image.resize(825,1125)
        image.save(filename='%s/%s.jpg' % (outputDirectory, name))