# Extracted verbatim from shelf_Unlisted.mel
#   label: "BakeCrocodie" (overlay "BakeCroc")
#          annotation "Bake Crocodile Rig to FBX"
#   label: "Select All Croc Controls" (overlay "AllCtrls")
#          annotation "Select all controls of the currently selected crocodile"
#   label: "Key All Croc Controls" (overlay "KeyCtrls")
#          annotation "Key all controls of the currently selected crocodile"
#
# NEEDS REVISITING:
#  - show-specific: hardcoded "Croc|joint_group", "Face_BS", "Eye_L_BS",
#    "Eye_R_BS" and an explicit delete list of rig groups. Tied to one asset.
#  - bakeCrocodile is the third copy of the dup/bake/FBX-export pattern
#    (see ul_tmp_exportSkeletonFBX.py and ul_tmp_bakeToDuplicate.py)
#  - the delete list references full paths under "Croc|", so it breaks if
#    the asset is renamed or referenced under a different namespace
#  - select/key pair duplicates ul_tmp_selectAnimControls.py with ":animSet"
#    instead of ":AnimCTRLS" — strong argument for one set-driven tool
#  - retire with the show, or generalise into "bake rig for export" driven
#    by a named set on the rig rather than hardcoded group paths
#  - sel[0] IndexErrors on an empty selection in all three
#
# The three bodies below were separate shelf buttons; each ran as a script,
# not as a function. Wrapped here only to keep them in one file — bodies
# are otherwise unchanged.


def bakeCrocodile():
    ##Export Crocodile FBX - export skin and joints as FBX for houdini, with blendshapes

    import maya.cmds as mc
    import os
    import maya.mel as mel

    sel = mc.ls(sl=True)

    ns = sel[0].split(":")

    #set start and end bake options to timeline
    start = mc.playbackOptions(q=True, min=True)
    end = mc.playbackOptions(q=True, max=True)

    #duplicate special and then parent under world
    dup = mc.duplicate(sel, rr=True, instanceLeaf=False, ic=True, un=True)

    #bake the driven channels
    bakegrp = ["Croc|joint_group", "Face_BS", "Eye_L_BS", "Eye_R_BS"]
    delgrp = ["Croc|ctrl_group", "Croc|rig_group", "Croc|extra_group", "Croc|setting_group", "Croc|joint_group|joint_group_scaleConstraint1","Croc|joint_group|L_leg_fr_ori_thigh_group","Croc|joint_group|L_leg_bk_ori_thigh_group","Croc|joint_group|R_leg_fr_ori_thigh_group","Croc|joint_group|R_leg_bk_ori_thigh_group"]
    mc.bakeResults(bakegrp, sm=True, t=(start,end), hi="below", sb=1, osr=1, dic=True, pok=True, sac=False, ral=False, rba=False, bol=False, mr=True, cp=False, shape=True)

    mc.delete(delgrp)

    #file name stuff
    currentScene = mc.file(query=True, sceneName=True)
    currentName = mc.file(query=True, sceneName=True, shortName=True)
    currentFolder = currentScene.replace(currentName,"")

    #create a directory for export if it doesn't already exist
    checkDir = os.path.exists(currentFolder + "FBX Export")
    if not (checkDir):
        os.makedirs(currentFolder + "FBX Export")

    fbxScene = currentFolder + "FBX Export/" + currentName.split('.')[0] + "_" + ns[0]

    mc.select(dup)

    #export to fbx
    mc.file(fbxScene, force=True, options="v=0;", typ="FBX export", pr=True, es=True)

    #delete the duplicated objects
    mc.delete(dup)


def selectAllCrocControls():
    import maya.cmds as mc

    sel = mc.ls(selection=True)

    ns = sel[0].split(":")

    mc.select(ns[0] + ":animSet")


def keyAllCrocControls():
    ##Key all Crocodile Controls
    import maya.cmds as mc

    sel = mc.ls(selection=True)

    ns = sel[0].split(":")

    mc.select(ns[0] + ":animSet")

    mc.setKeyframe()
    mc.select(sel)
