# scripts/temp — extracted shelf scripts

These files were lifted **verbatim** out of inline `shelfButton -command`
blocks in `prefs/shelves/shelf_Unlisted.mel` and removed from the shelf.

Nothing here has been fixed, tested, or ported. The code is exactly as it
was on the shelf, unescaped back into readable Python. Original button
label and annotation are recorded at the top of each file.

**All of these need revisiting.** Some element of each is worth keeping,
but none should go back on the shelf as-is — see the per-file notes and
the "Extracted shelf tools" section in `ISSUES.md`.

| File | Origin button(s) |
|---|---|
| `ul_tmp_exportSkeletonFBX.py` | Export Skeleton FBX |
| `ul_tmp_bakeToDuplicate.py` | Bake Selected to Duplicate |
| `ul_tmp_loopKeys.py` | Copy First Key to Last / Copy Last Key To First |
| `ul_tmp_xformClipboard.py` | GetX / SetX (MEL — not ported) |
| `ul_tmp_selectAnimControls.py` | Select Anim Ctrls / Set Key on All |
| `ul_tmp_crocodileRig.py` | BakeCrocodile / Select All Croc Controls / Key All Croc Controls |
| `ul_tmp_connectTextureToMaterial.py` | (unlabelled `AAA_CarMat` button) |
