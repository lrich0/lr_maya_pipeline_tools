# Extracted verbatim from shelf_Unlisted.mel
#   label: "Select Anim Ctrls" (overlay "AllCtrls")
#          annotation "Select All Character Controls from currently selected"
#   label: "Set Key on All"    (overlay "KeyAll")
#          annotation "Set Keyframes on all character controls"
#
# NEEDS REVISITING:
#  - hardcoded rig node names: ":AnimCTRLS", ":Fingers_L_CTRLS1",
#    ":Fingers_R_CTRLS1". Only works on one specific rig.
#  - same shape as the Croc buttons in ul_tmp_crocodileRig.py — both are
#    really "select this rig's anim set", differing only in set names.
#    One tool driven by a configurable set name replaces all four.
#  - sel[0] IndexErrors on an empty selection
#  - assumes the selection is namespaced; sel[0].split(":")[0] on an
#    un-namespaced node returns the node name, not a namespace
#  - setKey body is the select body plus two lines; merge them
#
# The two bodies below were separate shelf buttons; each ran as a script,
# not as a function. Wrapped here only to keep them in one file — bodies
# are otherwise unchanged.


def selectAnimCtrls():
    import maya.cmds as mc

    sel = mc.ls(selection=True)

    ns = sel[0].split(":")
    #print(ns)

    mc.select(ns[0] + ":AnimCTRLS")
    mc.select(ns[0] + ":Fingers_L_CTRLS1", add=True)
    mc.select(ns[0] + ":Fingers_R_CTRLS1", add=True)


def setKeyOnAll():
    import maya.cmds as mc

    sel = mc.ls(selection=True)

    ns = sel[0].split(":")
    #print(ns)

    mc.select(ns[0] + ":AnimCTRLS")
    mc.select(ns[0] + ":Fingers_L_CTRLS1", add=True)
    mc.select(ns[0] + ":Fingers_R_CTRLS1", add=True)

    mc.setKeyframe()
    mc.select(sel)
