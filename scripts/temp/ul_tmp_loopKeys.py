# Extracted verbatim from shelf_Unlisted.mel
#   two buttons, both with annotation:
#     "Copy's last key in the playback range to the first frame"
#   label: "Copy First Key to Last"  -> firstToLast() below (overlay "FtoL")
#   label: "Copy Last Key To First"  -> lastToFirst() below (overlay "LtoF")
#
# NEEDS REVISITING:
#  - BOTH shelf buttons carried the same annotation, so one was mislabelled.
#    The code differs (see the copyKey/pasteKey times) and matches the
#    labels, not the annotations. Confirm intent before rebuilding.
#  - the two bodies are identical apart from swapped start/end; one function
#    with a direction flag covers both
#  - no selection guard
#  - both header comments are the same copy-pasted text
#
# The two bodies below were separate shelf buttons; each ran as a script,
# not as a function. Wrapped here only to keep them in one file — bodies
# are otherwise unchanged.


def firstToLast():
    ##for looping animation, will copy first key of the current playback range and paste it to the last frame in the playback range

    import maya.cmds as mc
    import os
    import maya.mel as mel


    sel = mc.ls(sl=True)

    #set start and end bake options to timeline
    start = mc.playbackOptions(q=True, min=True)
    end = mc.playbackOptions(q=True, max=True)

    #copy and paste keys
    mc.copyKey(sel,time=(start,start))
    mc.pasteKey(sel,time=(end,end))


def lastToFirst():
    ##for looping animation, will copy first key of the current playback range and paste it to the last frame in the playback range

    import maya.cmds as mc
    import os
    import maya.mel as mel


    sel = mc.ls(sl=True)

    #set start and end bake options to timeline
    start = mc.playbackOptions(q=True, min=True)
    end = mc.playbackOptions(q=True, max=True)

    #copy and paste keys
    mc.copyKey(sel,time=(end,end))
    mc.pasteKey(sel,time=(start,start))
