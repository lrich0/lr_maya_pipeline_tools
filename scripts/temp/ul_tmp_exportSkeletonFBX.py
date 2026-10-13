# Extracted verbatim from shelf_Unlisted.mel
#   label:      "Export Skeleton FBX"
#   annotation: "Export skeleton animation, removing namespaces"
#
# NEEDS REVISITING:
#  - near-identical to ul_tmp_bakeToDuplicate.py; one function with an
#    export on/off flag should replace both
#  - no selection guard (sel could be empty)
#  - mc.parent(dup, w=True) throws if already a world child (the sibling
#    copy wraps this in try/except)
#  - writes to "<sceneFolder>/FBX Export/" with no _working handling
#  - crashes on an unsaved scene (currentName is '')
#  - despite the annotation, nothing here removes namespaces

##Export FBX - intended use is to export baked skeleton animation for game engines / Houdini
##It duplicate specials the selected objects, removing the namespace and parenting under the world to remove any extra
##hierarchy that may cause issues in the intended package. It then bakes the animation, then deletes the duplicated object once exported.
import maya.cmds as mc
import os
import maya.mel as mel


sel = mc.ls(sl=True)

#set start and end bake options to timeline
start = mc.playbackOptions(q=True, min=True)
end = mc.playbackOptions(q=True, max=True)

#duplicate special and then parent under world
dup = mc.duplicate(sel, rr=True, instanceLeaf=False, ic=True)
mc.parent(dup, w=True)

#bake the driven channels
mc.bakeResults(dup, sm=True, t=(start,end), hi="below", sb=1, osr=1, dic=True, pok=True, sac=False, ral=False, rba=False, bol=False, mr=True, cp=False, shape=True)

#file name stuff
currentScene = mc.file(query=True, sceneName=True)
currentName = mc.file(query=True, sceneName=True, shortName=True)
currentFolder = currentScene.replace(currentName,"")

#create a directory for export if it doesn't already exist
checkDir = os.path.exists(currentFolder + "FBX Export")
if not (checkDir):
    os.makedirs(currentFolder + "FBX Export")

fbxScene = currentFolder + "FBX Export/" + currentName.split('.')[0]

mc.select(dup)

#export to fbx
mc.file(fbxScene, force=True, options="v=0;", typ="FBX export", pr=True, es=True)

#delete the duplicated objects
mc.delete(dup)
