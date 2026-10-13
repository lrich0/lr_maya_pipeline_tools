# Extracted verbatim from shelf_Unlisted.mel
#   label:      "Bake Selected to Duplicate"
#   annotation: "Bake Selected"
#
# NEEDS REVISITING:
#  - this is a FORK of ul_tmp_exportSkeletonFBX.py, not a separate tool:
#    identical code with the export and delete lines commented out, plus a
#    try/except around the world-parent. Merge the two.
#  - the header comment below is copy-pasted from the FBX exporter and does
#    not describe what this button actually does (it bakes and leaves the
#    duplicate in the scene)
#  - it still builds fbxScene and creates an empty "FBX Export" folder even
#    though it never exports

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
try:
	mc.parent(dup, w=True)
except:
	print("already a child of the world")

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
#mc.file(fbxScene, force=True, options="v=0;", typ="FBX export", pr=True, es=True)

#delete the duplicated objects
#mc.delete(dup)
