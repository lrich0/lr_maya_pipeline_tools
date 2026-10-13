# Extracted verbatim from shelf_Unlisted.mel
#   label: "GetX" (overlay "GetX", annotation "User Script") - sourceType MEL
#   label: "SetX" (overlay "SetX", annotation "SetX")        - sourceType MEL
#
# These two buttons were MEL, not Python. They are NOT ported here — the
# original source is preserved below as-is so nothing is silently changed.
# A Python rewrite is the revisit task.
#
# NEEDS REVISITING:
#  - $t and $r are never declared global, so this works only by accident of
#    MEL's scoping in the shelf's execution context; anything else in the
#    session using those names clobbers the stored transform
#  - no selection guard on either half
#  - SetX silently does nothing sensible if GetX was never run
#  - a Python version should hold the value in a module-level variable (or
#    an optionVar, if it should survive a Maya restart) and store/apply
#    world translate + rotate for the current selection
#
# --- original GetX command (MEL) ---------------------------------------
#   //get xform
#   float $t[] = `xform -q -ws -t`;
#   float $r[] = `xform -q -ws -ro`;
#
# --- original SetX command (MEL) ---------------------------------------
#   //set xform
#   xform -ws -t $t[0] $t[1] $t[2];
#   xform -ws -ro $r[0] $r[1] $r[2];
# -----------------------------------------------------------------------
