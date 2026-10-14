import maya.cmds as mc
import os
import getpass
import maya.mel as mel
from maya.api.OpenMaya import MImage

def saveAndBackup():
    # currentScene = mc.file(query=True, sceneName=True)
    # call the built in incremental save function in maya
    mel.eval("source incrementalSaveScene;")
    mel.eval("incrementalSaveScene;")

def versionUp():
    """Save the current scene as the next version, e.g. shot010_anim_v003.mb -> shot010_anim_v004.mb.

    USAGE: shelf button. Keeps the scene's file type (.ma or .mb).
    If the scene has no _v### version token, offers to save it as name_v001.
    If the next version already exists, asks: save as the next free version,
    overwrite, or cancel.
    """
    #version up the current file without publishing
    #save current version first
    #mel.eval("source incrementalSaveScene;")
    #mel.eval("incrementalSaveScene;")

    currentScene = mc.file(query=True, sceneName=True)
    if not currentScene:
        mc.warning('versionUp: scene has not been saved yet - save it as name_v001.mb first')
        return

    currentName = mc.file(query=True, sceneName=True, shortName=True)
    baseName, ext = os.path.splitext(currentName)

    fileTypes = {'.ma': 'mayaAscii', '.mb': 'mayaBinary'}
    fileType = fileTypes.get(ext.lower())
    if not fileType:
        mc.warning('versionUp: "' + currentName + '" is not a .ma or .mb scene')
        return

    #version token is the last "_v" followed by digits, right before the extension
    head, sep, currentVersion = baseName.rpartition('_v')
    if not sep or not currentVersion.isdigit():
        firstName = baseName + '_v001' + ext
        answer = mc.confirmDialog(title='Version Up',
                                  message='No version token found in "' + currentName + '".\n\nSave as ' + firstName + '?',
                                  button=['Save as _v001', 'Cancel'],
                                  defaultButton='Save as _v001', cancelButton='Cancel', dismissString='Cancel')
        if answer != 'Save as _v001':
            return
        head = baseName
        newVersion = '001'
    else:
        length = len(currentVersion)
        newVersion = str(int(currentVersion) + 1).zfill(length)

    sceneDir = os.path.dirname(currentScene)
    incrementScene = sceneDir + '/' + head + "_v" + newVersion + ext
    #publishScene = currentScene.replace("_working","published")

    #next version already on disk - ask rather than silently overwrite
    if os.path.exists(incrementScene):
        freeVersion = newVersion
        freeScene = incrementScene
        while os.path.exists(freeScene):
            freeVersion = str(int(freeVersion) + 1).zfill(len(newVersion))
            freeScene = sceneDir + '/' + head + "_v" + freeVersion + ext

        answer = mc.confirmDialog(title='Version Up',
                                  message=os.path.basename(incrementScene) + ' already exists.\n\n'
                                          'Next free version is ' + os.path.basename(freeScene) + '.',
                                  button=['Save as v' + freeVersion, 'Overwrite', 'Cancel'],
                                  defaultButton='Save as v' + freeVersion, cancelButton='Cancel', dismissString='Cancel')
        if answer == 'Overwrite':
            pass
        elif answer == 'Save as v' + freeVersion:
            incrementScene = freeScene
        else:
            return

    mc.file( rename=incrementScene)
    mc.file( save=True, type=fileType )
    mel.eval('addRecentFile "'+incrementScene+'" "'+fileType+'";')
        
# Saves the current file and exports everything in the scene as a new file in the published folder
# doesnt work if the file exists outside of the Unlisted workflow
def publishAll(dir):
    currentScene = mc.file(query=True, sceneName=True)
    currentName = mc.file(query=True, sceneName=True, shortName=True)
    filePathList = currentScene.split('/')
    #remove file name
    filePathList.pop()
    
    #remove _working directory
    if(filePathList[-1]=='_working'):    
        filePathList.pop()
    
    #rebuild basepath to file    
    baseFilePath = ''
    for item in filePathList:
        baseFilePath = baseFilePath + item + '/'
    if(dir == 'Animation Exports'):
        publishScene = baseFilePath + dir + "/" + currentName.split('.')[0] + "/" + currentName
    else:
        publishScene = baseFilePath + dir + "/" + currentName
    # call the built in incremental save function in maya
    #mel.eval("source incrementalSaveScene;")
    #mel.eval("incrementalSaveScene;")
    
    #save the published file
    mc.file( publishScene, type='mayaBinary', exportAll=True, preserveReferences=True ) 
    mel.eval("print \"// File exported as: ' " + publishScene + " //\"")

#needs an output directory. Default is published, alts are Animation Export
def publishSelected(dir):
    # call the built in incremental save function in maya
    # mel.eval("source incrementalSaveScene;")
    # mel.eval("incrementalSaveScene;")
    sel = mc.ls(sl=True)
    if sel:
        currentScene = mc.file(query=True, sceneName=True)
        currentName = mc.file(query=True, sceneName=True, shortName=True)
        filePathList = currentScene.split('/')
        #remove file name
        filePathList.pop()
        
        #remove _working directory
        if(filePathList[-1]=='_working'):    
            filePathList.pop()
        
        #rebuild basepath to file    
        baseFilePath = ''
        for item in filePathList:
            baseFilePath = baseFilePath + item + '/'
        if(dir == 'Animation Exports'):
            publishScene = baseFilePath + dir + "/" + currentName.split('.')[0] + "/" + currentName
        else:
            publishScene = baseFilePath + dir + "/" + currentName

        #save the published file
        mc.file( publishScene, type='mayaBinary', exportSelected=True, preserveReferences=True )
        #print('File exported as: ' + publishScene)
        mel.eval("print \"// File exported as: ' " + publishScene + " //\"")
        #mc.warning('File exported as: ' + publishScene, n=True)
    else:
        mc.warning('// nothing is selected. Export cancelled //')
        
def exportCamera(ref=False):
    # call the built in incremental save function in maya
    # mel.eval("source incrementalSaveScene;")
    # mel.eval("incrementalSaveScene;")
    sel = mc.ls(sl=True)
    if sel:
        currentScene = mc.file(query=True, sceneName=True)
        currentName = mc.file(query=True, sceneName=True, shortName=True)

        shotName = currentName.split('_')[0]
        
        #suffix = currentName.split("_v")
        #currentVersion = suffix[1].split(".")
        
        projectDirectory = mc.workspace(q=True, rd=True)
        currentScene = os.path.abspath(mc.file(query=True, sceneName=True))
        if 'scene' in mc.workspace(q=True, frl=True):
            sceneDirectory = os.path.join(projectDirectory, mc.workspace(fre='scene'))
        else:
            #no 'scene' file rule in this project - fall back to the scene file's own folder
            sceneDirectory = os.path.dirname(mc.file(query=True, sceneName=True))
            print('// exportCamera: project has no "scene" file rule - using ' + sceneDirectory + ' //')
        #print(sceneDirectory)


        camFilePath = sceneDirectory +'/camera/' + shotName +'/'


        #find the highest existing version for this shot - compare as numbers, not
        #by list order, so v010 beats v009 and v1000 beats v999
        fileList = mc.getFileList(filespec=shotName + '_cam_v*.mb', folder=camFilePath) or []
        latestVersion = 0
        for camFile in sorted(fileList):
            fileVersion = os.path.splitext(camFile)[0].rpartition('_v')[2]
            if fileVersion.isdigit():
                latestVersion = max(latestVersion, int(fileVersion))
        version = latestVersion + 1
        camFileName = shotName + '_cam_v' + str(version).zfill(3) + '.mb'
        #save the published file
        if not (ref):
            mc.file( camFilePath + camFileName, type='mayaBinary', exportSelected=True, preserveReferences=True )
        else:
            mc.file( camFilePath + camFileName, type='mayaBinary', exportAsReference=True )
        #print('File exported as: ' + publishScene)
        mel.eval("print \"// File exported as: ' " + camFilePath + camFileName + " //\"")
        #mc.warning('File exported as: ' + publishScene, n=True)
    else:
        mc.warning('// nothing is selected. Export cancelled //')


'''
Returns the per-user copy/paste temp file path: c:/scratch/<username>/mayatemp/copypaste.mb
Windows-only. The username keeps students on a shared machine from colliding
on (or reading) each other's clipboard file. Pass makeDir=True to create the
mayatemp folder on demand (the copy side does; the paste side just reads).
Returns None if makeDir is asked for but the folder can't be created —
students can only write inside their own c:/scratch/<username> folder, so a
missing username folder or a locked scratch drive fails cleanly with a warning
rather than a traceback.
'''
def copyPasteTempFile(makeDir=False):
    user = getpass.getuser()
    userDir = 'c:/scratch/' + user
    tempDir = userDir + '/mayatemp'
    if makeDir and not os.path.exists(tempDir):
        # students can write inside c:/scratch/<username> but not create it,
        # so bail with a clear message if their scratch folder isn't there.
        if not os.path.exists(userDir):
            mc.warning('Your scratch folder ' + userDir + ' does not exist. Copy cancelled.')
            return None
        try:
            os.makedirs(tempDir)
        except OSError:
            mc.warning('Could not create ' + tempDir + '. Copy cancelled.')
            return None
    return tempDir + '/copypaste.mb'

'''
copies selected to a per-user temp file (c:/scratch/<username>/mayatemp/copypaste.mb)
'''
def copyToTempFile(tempScene=None):
    # call the built in incremental save function in maya
    # mel.eval("source incrementalSaveScene;")
    # mel.eval("incrementalSaveScene;")
    if tempScene is None:
        tempScene = copyPasteTempFile(makeDir=True)
        if tempScene is None:
            return
    sel = mc.ls(sl=True)
    if sel:
        #save the copy file
        mc.file( tempScene, type='mayaBinary', exportSelected=True, preserveReferences=True,f=True )
        mel.eval("print \"// Selection Copied to: ' " + tempScene + " //\"")

    else:
        mc.warning('// nothing is selected. Export cancelled //')

'''
Imports content from a per-user temp file (c:/scratch/<username>/mayatemp/copypaste.mb)
'''
def pasteFromTempFile(tempScene=None):
    if tempScene is None:
        tempScene = copyPasteTempFile()
    if(os.path.exists(tempScene)):
        imported = mc.file(tempScene,i=True, ns='ns___copypaste')
        #print(imported)
        #namespaceToDelete = imported.split(':')[0]
        namespaceToDelete = 'ns___copypaste'
        mc.namespace (set=namespaceToDelete)
        mc.namespace(force=True,moveNamespace=(':ns___copypaste',':'))
        #mc.delete(mc.namespaceInfo (listOnlyDependencyNodes=True))
        mc.namespace (set=':')
        mc.namespace(force=True,rm=namespaceToDelete)
    else:
        mc.warning('No temp scene found. Aborting.')
    
'''
#Export selected animation to alembic
#needs an output directory. Default is published, alts are Animation Export. Preferred for animation out is 'Animation Exports'
'''

def exportSelectedABC(dir):
    # call the built in incremental save function in maya
    # mel.eval("source incrementalSaveScene;")
    # mel.eval("incrementalSaveScene;")
    sel = mc.ls(sl=True)
    if sel:
        currentScene = mc.file(query=True, sceneName=True)
        currentName = mc.file(query=True, sceneName=True, shortName=True)
        filePathList = currentScene.split('/')
        
        #remove file name
        filePathList.pop()
        
        #remove _working directory if it exists
        if(filePathList[-1]=='_working'):    
            filePathList.pop()
        
        #rebuild basepath to file    
        baseFilePath = ''
        for item in filePathList:
            baseFilePath = baseFilePath + item + '/'

        abcScene = '"' + baseFilePath + dir + '/' + currentName.split('.')[0] + '/' + currentName.split('.')[0] + '.abc"'
        abcFolder = baseFilePath + dir + '/' + currentName.split('.')[0] + '/'
        
        #abcScene = abcScene.replace('/',"\\")
        
        #print(abcScene)
        #save the published file
        #mc.file( publishScene, type='mayaBinary', exportSelected=True, preserveReferences=True )
        start = mc.playbackOptions(q=True, min=True)

        end = mc.playbackOptions(q=True, max=True)
        
        sel = mc.ls(sl=True, long=True)
        root = ''
        for items in sel:
            root = root + ' -root ' + items
        print(root)   
        print (abcScene) 
        print (abcFolder) 

        checkDir = os.path.exists(abcFolder)
        if not (checkDir):
            os.makedirs(abcFolder)

        outVars = "-frameRange " + str(start) + " " + str(end) +" -stripNamespaces -uvWrite -writeColorSets -writeFaceSets -writeVisibility -eulerFilter -autoSubd -writeUVSets -dataFormat ogawa" + root + " -file " + abcScene
        print(outVars)

        mc.AbcExport(j=outVars)
        #print('Alembic Exported: ' + abcScene)
        mel.eval("print \"// Alembic exported as: " + abcScene.replace('"','') + " \"")
        #mc.AbcExport(h=True)
    else:
        mc.warning('// nothing is selected. Export cancelled //')

def exportToReference():
    sel=mc.ls(sl=True)
    # check if it is something selected otherwise it gets an error;
    # a message can be printed if case nothing is selected
    if sel:
        #multipleFilters = "Maya Binary (*.mb);;"
        filename = mc.fileDialog2(fileFilter="Maya Binary (*.mb);;", dialogStyle=2)
        #print('trying to write the file')
        #print(filename[0])
        mc.file( filename[0], type='mayaBinary', exportAsReference=True )
 
 
        #mc.file( rename=filename[0] )
        #mc.file( save=True, type='mayaAscii' )
    else:
        mc.warning('// nothing is selected. Export cancelled //')
 
            
def exportToCustom():
    sel=mc.ls(sl=True)
    # check if it is something selected otherwise it gets an error;
    # a message can be printed if case nothing is selected
    if sel:
        #multipleFilters = "Maya Binary (*.mb);;"
        filename = mc.fileDialog2(fileFilter="Maya Binary (*.mb);;", dialogStyle=2)
        #print('trying to write the file')
        #print(filename[0])
        mc.file( filename[0], type='mayaBinary', exportSelected=True )
 
 
        #mc.file( rename=filename[0] )
        #mc.file( save=True, type='mayaAscii' )
    else:
        mc.warning('// nothing is selected. Export cancelled //')

'''
#exportShaders()
#USEAGE: Select objects you want to export shaders for relinking later and run script
'''
def exportShaders():
    sel = mc.ls(sl=True)
    if sel:
        # get all shapes in selection:
        shapesInSel =  mc.ls(dag=1,o=1,s=1,sl=1)

        # get shading groups from shapes:
        shadingGrps = mc.listConnections(shapesInSel,type='shadingEngine')

        #get the shaders:
        currentScene = mc.file(query=True, sceneName=True, shortName=True)
        sceneName = currentScene.split(".")[0]

        #create the shader list group
        sgListExists = mc.objExists('sgList__'+sceneName)
        if(sgListExists):
            print('deleting and starting fresh!')
            mc.delete('sgList__'+sceneName)
            prnt = mc.createNode('transform',name='sgList__'+sceneName)
        else:
            prnt = mc.createNode('transform',name='sgList__'+sceneName)

        #hide the sgList parent    
        mc.setAttr(prnt+'.visibility', 0)
        
        i = 0
        for shape in shapesInSel:

            #store the shading group for the current shape
            sg = mc.listConnections(shape,type='shadingEngine')
            
            #check to see if we have geo or not
            if(sg == None):
                print("non-geo selected. skipping " + shape)
            else:
                geo = mc.polyPlane(sw=1,sh=1)
                #remove namespaces and rename to shading group proxy nomenclature
                geo = mc.rename('sg___' + shape.split(':')[-1] + '___')
            
                mc.sets(geo+"Shape", e=True, forceElement = sg[0] )     
                        
                for attr in mc.listAttr( shape, r=True ):
                    fullAttr = geo+'Shape.'+attr
                    #print(theAttr[:2])
                    if(attr[:2] == 'rs'):
                        if((attr == 'rsMatteShadowColor') or (attr == 'rsReflectionTraceSet') or (attr == 'rsRefractionTraceSet')):
                            dummy = 0
                            
                        else:
                            newVal = mc.getAttr(shape+'.'+attr)
                            mc.setAttr(fullAttr,newVal)

                mc.parent(geo, prnt, shape=True)
        
            i = i + 1
            

        ###start the export###
        mc.select(sel, replace=True)
        sgall = mc.listConnections(sel,type='shadingEngine')

        #select the shading groups and the annotations
        mc.select(shadingGrps, replace=True, allDagObjects=False, noExpand=True)
        mc.select(prnt, add=True)

        #get the selection
        sel=mc.ls(sl=True)
            # check if it is something selected otherwise it gets an error;
            # a message can be printed if case nothing is selected
            
        #set up file export and do the thing    
        if sel:
            multipleFilters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"
            #filename = mc.fileDialog2(fileFilter=multipleFilters, dialogStyle=2)
            currentScene = mc.file(query=True, sceneName=True)
            currentName = mc.file(query=True, sceneName=True, shortName=True)
            splitName = currentName.split('.')
        
            newName = splitName[0]+'_shaders'
            filePathList = currentScene.split('/')
            
            #remove file name
            filePathList.pop()
            
            #remove _working directory if it exists
            if(filePathList[-1]=='_working'):    
                filePathList.pop()

            #rebuild basepath to file    
            baseFilePath = ''
            for item in filePathList:
                baseFilePath = baseFilePath + item + '/'
                
            baseFilePath = baseFilePath + 'publishedShaders/'     
            newFile = baseFilePath + newName    

            mc.file( newFile, type='mayaBinary', exportSelected=True )
            
            mc.delete(prnt)
            mel.eval("print \"// Shaders Exported to: ' " + newFile +" //\"")
        else:
            mc.warning('// nothing is selected. Export cancelled //')
    else:
        mc.warning('// nothing is selected. Export cancelled //')


#USAGE: In any order, select the locator that contains the object assignment list, and all the geo you need to assign to. Run the script!
def relinkShaders():
    sel = mc.ls('::sgList__*',sl=True)

    shapesInSel =  mc.ls(dag=True,objectsOnly=True,shapes=True,sl=True)


    #get the shading group object assignments

    sgList = []
    objList = []
    for item in shapesInSel:
        isShaderProxy = item.find('sg___')
        if(mc.nodeType(item)=='mesh'):
            if(isShaderProxy >= 0):
                sgList.append(item)
            else:
                objList.append(item)

    #get shader connected to sgList items
    shadingGrps = mc.listConnections(sgList,type='shadingEngine')

    #ignore namespaces and match objects to the sgList, then assign the shader
    for sObj in sgList:
        #remove the namespace on the object assignment for later comparison with oObj
        sName = sObj.split(':')[-1]
        sName = sName.replace('sg___','')
        sName = sName.replace('___Shape','')
        
        #get the connnected shading group
        sg = mc.listConnections(sObj,type='shadingEngine')
        
        #match to the selected objects, making sure to ignore namespaces
        for oObj in objList:
            oName = oObj.split(':')[-1]
            
            success = False
            if(oName == sName):
                #assign the shader
                if not (success):
                    if(mc.objExists(sg[0])):
                        mc.sets(oObj, e=True, forceElement = sg[0] )
                        #set the redshift values
                        for attr in mc.listAttr( oObj, r=True ):
                            fullAttr = oObj+'.'+attr
                            if(attr[:2] == 'rs'):
                                if((attr == 'rsMatteShadowColor') or (attr == 'rsReflectionTraceSet') or (attr == 'rsRefractionTraceSet')):
                                    dummy = 0
                                else:
                                    newVal = mc.getAttr(sObj+'.'+attr)
                                    mc.setAttr(fullAttr,newVal)
                    else:
                        print(sg + ' shadingGroup doesnt exist, ignoring')
                    success = True
                
                else:
                    print('something happened?? some kind of error with assigning the shading group. Possibly namespaces')


def renameSG():
    sel = mc.ls(sl=True)
    for item in sel:
        sg = mc.listConnections(item,type='shadingEngine')
        mc.rename(sg,item + 'SG')

def makeViewportShader(size=512):
    sel = mc.ls(sl=True)

    if sel:
        for item in sel:
            #print(mc.nodeType(item))
            sg = mc.listConnections(item,type='shadingEngine')

            #print(sg)

            if not (sg):
                print('making new shading group')
                sg = mc.sets(name=item+'SG', empty=True, renderable=True, noSurfaceShader=True)
            else:
                sg = sg[0]
                
            #print(sg)    
            
            #mc.nodeType(item).find('Redshift')
            if(mc.nodeType(item).find('Redshift')>=0):
                mc.connectAttr(item + '.outColor', sg + '.rsSurfaceShader', force=True)
                
            if not (mc.objExists('vp___'+item)):
                vpMat = mc.shadingNode('lambert', name='vp___'+item, asShader=True)
                check = 'Overwrite'
            else:
                #mc.delete('vp___'+item)
                #check = mc.confirmDialog(b=['Overwrite','Cancel'], cb="cancel", message="A viewport shader already exists for this selection. Overwrite?")
                check = 'Overwrite'
            
            if(check == 'Overwrite'):
                mc.delete('vp___'+item)
                vpMat = mc.shadingNode('lambert', name='vp___'+item, asShader=True)
                mc.connectAttr(vpMat + '.outColor', sg + '.surfaceShader', force=True)
                
                #check to see if diffuse color has an incoming connection
                diffuseColor = mc.connectionInfo(item+'.diffuse_color', sfd=True)  
                
                #if there's no incoming connection to the diffuse color, set the lambert's color to be the diffuse color
                if(diffuseColor == ''):
                    col = mc.getAttr(item+'.diffuse_color')
                    #print(col[0])
                    #print('no input connection to diffusecolor') 
                    mc.setAttr(vpMat+'.colorR',mc.getAttr(item+'.diffuse_colorR'))
                    mc.setAttr(vpMat+'.colorG',mc.getAttr(item+'.diffuse_colorG'))
                    mc.setAttr(vpMat+'.colorB',mc.getAttr(item+'.diffuse_colorB'))
                elif(diffuseColor != ''):
                    inType = mc.nodeType(diffuseColor)
                    
                    #if its a file going in, duplicate the file node, resize the images and connect.
                    if(inType == 'file'):
                        nodeName = diffuseColor.split('.')[0]
                        #print('do the image stuff')
                        print('vp___'+nodeName)
                        if(mc.objExists('vp___'+nodeName)):
                            print('file node exists!')
                            mc.delete('vp___'+nodeName)
                        else:
                            print('file node doesnt exist :(')
                        newFile = mc.duplicate(diffuseColor, name='vp___'+nodeName,ic=True, rc=True)
                        #print(newFile)
                        mc.setAttr(newFile[0]+'.uvTileProxyQuality',1)
                        
                        
                        path = mc.getAttr(newFile[0]+'.fileTextureName')
                        
                        imgName = path.split('/')[-1]
                        dirList = path.split('/')
                        
                        if(len(dirList) > 1):
                            dirList.pop()
                        dir = ''
                        for items in dirList:
                            dir = dir + items + '/' 
                        
                        imgFormat = imgName.split('.')[-1]
                        imgName = imgName.split('.')[0]
                        
                        #do udim checks
                        udimCheck = mc.getAttr(newFile[0]+'.uvTilingMode')
                        if(udimCheck==3): #do udim processing
                            origUdimVal = imgName.split('_')[-1]
                            for i in range(10):
                                for j in range(10):
                                    udimVal = str(i+10).zfill(2) + str(j).zfill(2)
                                    img = MImage()
                                    readPath = dir + imgName.replace(origUdimVal, udimVal) + '.' + imgFormat
                                    
                                    #strip the trailing udim digits off the name.
                                    #named nameLength, NOT size - reusing 'size'
                                    #here overwrote the size parameter for the
                                    #rest of the call (see ISSUES.md #2)
                                    nameLength = len(imgName)
                                    im = imgName[:nameLength - 4]
                                    #del im[-4:]
                                    if(os.path.exists(readPath)):
                                        newImgName = im + '__vp' + '_' + udimVal + '.' + imgFormat
                                        img = MImage()
                                        img.readFromFile(readPath)
                                        img.resize(512,512,1)
                                        img.writeToFile(dir + newImgName, imgFormat)
                                        
                                    #img.readFromFile(readPath)
                                    #print (img)
                        #if we have a normal style of texture
                        else:
                            newImgName = imgName + '___vp' + '.' + imgFormat
    
                            img = MImage()
                            img.readFromFile(path)
                            
                            img.resize(size,size,1)
                            img.writeToFile(dir + newImgName, imgFormat)
                        mc.setAttr(newFile[0]+'.fileTextureName',dir + newImgName, type='string')
                        mc.connectAttr(newFile[0]+'.outColor', vpMat+'.color', force=True)
    
                    #if its not a file going in, just reconnect it
                    else:
                        mc.connectAttr(diffuseColor, vpMat+'.color', force=True)
                    #print(baseColor)          
                else:
                    print("skipping")
