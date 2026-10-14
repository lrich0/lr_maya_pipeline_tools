# Backlog — ul_pipelineTools

Ordered roughly by severity. Bugs first, then refactors, then extensions.

## Bugs

### 1. UI callbacks broken / signature mismatches — CLOSED (removed)
`floatingWindow()` wired buttons with broken string callbacks
(`bc='publishAll()'` against `publishAll(dir)`, and bare names that only
resolve in `__main__`).

**Resolved by deletion.** `floatingWindow()` was never on the shelf, so
nothing could reach it. Removed from `ul_pipelineTools.py` along with
`rsGeoSettingsWindow()` and its `setObjID` / `setTess` / `setDisp` /
`setVis` stubs. The shelf is now the only interface and its buttons pass
arguments correctly, so no live caller is affected.

A floating window may be revisited later — see CLAUDE.md. If it comes
back, callbacks must be Python callables / `functools.partial`.

*Verify in Maya:* `importlib.reload(ul_pipelineTools)` — module should
import clean with no NameError; every shelf button still fires.

### 2. Variable shadowing bug in `makeViewportShader` — DONE
In the UDIM branch, `size = len(imgName)` shadowed the function's
`size=512` parameter. If a UDIM texture was processed before a non-UDIM
texture in the same run, the later `img.resize(size, size, 1)` resized
to the string length instead of 512.

**Fixed:** local renamed to `nameLength`; `im = imgName[:nameLength - 4]`
now reads from the rename. The `size` parameter is no longer clobbered.

*Verify in Maya:* select two materials — one UDIM-textured, one with a
single texture — with the UDIM one first, run `makeViewportShader()`,
and confirm the non-UDIM `___vp` texture is 512x512 (before the fix it
came out at roughly the character-length of the UDIM texture's name).

**Still open, deliberately not changed** (needs a call — behaviour change
when `size != 512`): the UDIM branch hardcodes `img.resize(512,512,1)`
instead of using `size`, so `makeViewportShader(1024)` gives 1024px
non-UDIM textures but 512px UDIM ones. One-line fix once confirmed.

**Also spotted nearby, not fixed:** if the UDIM loop matches no files on
disk, `newImgName` is never assigned and the following
`mc.setAttr(... newImgName ...)` raises `UnboundLocalError`. Same if a
non-UDIM texture path doesn't exist. Needs a guard.

### 3. `versionUp` fragility — DONE
- Hard-crashes (IndexError) on filenames without `_v`.
- Always saves as mayaBinary even if the scene is `.ma`.
- No guard for unsaved/untitled scenes (`sceneName` returns '').
Add validation + a user-facing warning instead of a traceback.

**Fixed:**
- Untitled scene → `mc.warning` ("save it as name_v001.mb first"), no save.
- Version token is now the *last* `_v` + digits before the extension
  (`rpartition`), so names like `shot_village_v003.mb` work; a missing or
  non-numeric token warns with a suggested name instead of crashing.
- File type follows the extension (`.ma` → mayaAscii, `.mb` →
  mayaBinary), also passed to `addRecentFile`; anything else warns.
- New path is built from `os.path.dirname` + new name rather than
  `str.replace`, which could also rewrite a matching folder name.
- Padding width still follows the existing token (unchanged behaviour).
- Docstring added.

**Still open, not changed:** if the next version already exists on disk
(e.g. versioning up v003 when v004 exists) it is silently overwritten —
same as before. Needs a decision: warn and abort, confirm dialog, or skip
to the next free number.

*Verify in Maya:* (a) new untitled scene → warning, nothing saved;
(b) `test.mb` → warning suggesting `test_v001.mb`; (c) `shot_v003.ma` →
`shot_v004.ma` saved as ASCII (open in a text editor); (d)
`shot_village_v009.mb` → `shot_village_v010.mb`; (e) File > Recent Files
lists the new version.

### 4. `exportCamera` issues
- `sceneDirectory` is only assigned inside `if 'scene' in workspace
  fileRules` → NameError if the rule is missing.
- Version padding: new version re-pads to the *previous* file's padding
  length, and the first version goes through a different code path.
  Normalize to `zfill(3)` everywhere.
- Assumes `getFileList` returns sorted results; sort explicitly before
  taking `[-1]`, and only match `*_cam_v*.mb`.
- ~~Not wired into the UI at all~~ — it *is* on the shelf, as two buttons
  (`exportCamera(False)` / `exportCamera(True)`). The NameError path is
  therefore live and artist-reachable.

### 5. Hardcoded temp path in copy/paste tools — DONE
Was `D:/CACHE/maya/temp/copypaste.mb` ("set to work for Hugo").

Decision (user, 2026-08-03): hardcode to a per-user Windows path
`c:/scratch/<username>/mayatemp/copypaste.mb`. Windows-only for now —
Mac is explicitly out of scope. No env var / `tempfile` indirection
wanted; the username segment is what prevents students colliding on (or
reading) each other's clipboard file on a shared machine.

What changed:
- New helper `copyPasteTempFile(makeDir=False)` builds the path from
  `getpass.getuser()`; `makeDir=True` creates the `mayatemp` folder on
  demand. Students can only write inside their own `c:/scratch/<username>`
  folder (not create it, not touch other folders), so the helper warns
  and returns None — and copy aborts cleanly — if that folder is missing
  or the scratch drive is locked, rather than tracebacking.
- `copyToTempFile` / `pasteFromTempFile` now default `tempScene=None` and
  fall back to the helper (copy creates the dir, paste only reads). The
  explicit-path override is kept for backwards compatibility.
- Both shelf buttons had the old path dropped from their `-command`
  args, so the new default rules.

**Verify in Maya:** reload the shelf, select something, hit Copy — a
`c:/scratch/<you>/mayatemp/copypaste.mb` should be written (folder
created if absent) and the script editor prints the path. Hit Paste in
another scene — content comes in under (then out of) `ns___copypaste`.
Cross-machine paste is not addressed (local disk); confirm that's
acceptable for the RMIT workflow.

### 6. `relinkShaders` logic errors
- `success` flag is reset inside the inner loop so the guard is dead code.
- No `break` after a match; harmless now but wasteful and misleading.
- `mc.ls('::sgList__*', sl=True)` result (`sel`) is never used.
Clean up; consider warning when a proxy finds no matching geo.

### 7. Duplicate path-building logic
`publishAll`, `publishSelected`, `exportSelectedABC`, `exportShaders`
all rebuild the base path with the same strip-filename /
strip-`_working` loop. Extract a `getPublishBasePath()` helper
(use `os.path` / `pathlib` instead of manual '/' joins, but keep
forward slashes for Maya).

### 8. Misc small ones
- `publishAll` / `publishSelected` don't create the output folder if it
  doesn't exist (unlike `exportSelectedABC` which does).
- `mel.eval("print ...")` string interpolation will break on paths
  containing quotes; prefer `om.MGlobal.displayInfo` or `print`.
- `renameSG` passes a *list* from `listConnections` straight into
  `mc.rename` and will misbehave with multiple SGs / None.
- `exportToReference` / `exportToCustom` crash if the file dialog is
  cancelled (`filename` is None → `filename[0]`).
- ~~Repeated `mc.textFieldButtonGrp('tfb', ...)`~~ — moot, removed with
  `floatingWindow` (Issue 1).
- ~~`rsGeoSettingsWindow` bakes slider values at build time~~ — moot,
  removed with the window (Issue 1).

## Extensions

### 9. Redshift geo settings window — DROPPED
`setObjID`, `setTess`, `setDisp`, `setVis` were stubs and the window was
unreachable. Removed rather than finished (Issue 1). Per-object render
settings may return later as shelf-callable functions with no UI, or as
part of a revisited floating window — not currently wanted.

### 10. Consolidated UI — DROPPED
Both windows are gone; the shelf is the interface. See CLAUDE.md
"Interface — shelf only". Revisit only if a floating window is wanted.

### 11. Publish manifest / logging
Write a small sidecar (JSON) next to each publish recording source
scene, user, date, Maya version — useful for the RMIT teaching context
to show provenance.

### 12. Configurable studio settings
A tiny `ul_config.py` (or JSON) for: temp copy/paste path, publish
folder names, version padding, viewport texture size. Defaults preserve
current behavior.

### 13. Docstrings + shelf install helper
Docstrings on every artist-facing function, plus a `installShelf()`
helper that builds an "Unlisted" shelf with buttons for the main tools,
so colleagues can bootstrap with two lines in the script editor.

## Arnold support (HIGH PRIORITY — Arnold is the primary renderer)

The module is Redshift-only in practice. On an Arnold scene the shader
tools silently do the wrong thing or traceback. Design decision: **one
shelf button per renderer**, functions take the renderer as an argument
with a prefix/slot/attribute lookup table — see CLAUDE.md "Decided:
separate shelf buttons per renderer".

### 14. `makeViewportShader` breaks on Arnold materials
- Material-type detection is `mc.nodeType(item).find('Redshift')`, so an
  `aiStandardSurface` never matches and never gets connected to the SG's
  `aiSurfaceShader` slot.
- It then reads `item + '.diffuse_color'` / `.diffuse_colorR/G/B`
  unconditionally. Those attributes don't exist on `aiStandardSurface`
  (it uses `baseColor` / `baseColorR..B`, with `base` as the weight), so
  `connectionInfo` / `getAttr` **throws** on any Arnold material.
- Needs a per-renderer map: node-type prefix (`ai` / `Redshift`), SG slot
  (`aiSurfaceShader` / `rsSurfaceShader`), and colour attribute
  (`baseColor` / `diffuse_color`). Consider multiplying `baseColor` by
  `base` for a truer viewport approximation.

### 15. `exportShaders` / `relinkShaders` only copy `rs*` attributes
Both filter render-stat attributes with `attr[:2] == 'rs'`, so Arnold's
`ai*` per-shape attributes (`aiOpaque`, `aiSubdivType`,
`aiVisibleInDiffuseReflection`, …) are never carried onto the proxy plane
or restored on relink. Arnold users lose all per-object render settings
silently — no warning, no error.

Also needs an Arnold equivalent of the existing skip-list
(`rsMatteShadowColor`, `rsReflectionTraceSet`, `rsRefractionTraceSet`) —
those are skipped because they're non-numeric / string-set attributes;
the `ai*` set has comparable ones to identify.

### 16. No plugin-loaded guards
`ai*` and `rs*` attributes only exist when mtoa / redshift4maya are
loaded. Check `mc.pluginInfo('mtoa', q=True, loaded=True)` (and
likewise Redshift) or test attribute existence before get/set, and warn
rather than traceback. Never auto-load a render plugin from these tools.

## Newly found bugs (not previously listed)

### 17. `makeViewportShader` reads the wrong shading group in a multi-selection — DONE
Inside `for item in sel:` the lookup was
`sg = mc.listConnections(sel, type='shadingEngine')` — it passed `sel`,
the whole selection, not `item`. With more than one material selected
every iteration picked `sg[0]`, the first shading group found across the
entire selection, so all generated viewport lamberts were wired to one SG.

**Fixed:** lookup is now `mc.listConnections(item, type='shadingEngine')`.
Single-material behaviour is unchanged.

*Verify in Maya:* select two materials on different objects, run
`makeViewportShader()`, confirm each object gets its own `vp___` lambert
rather than both objects changing together.

### 18. `makeViewportShader` writes downres'd textures beside the source
Output path is `dir + newImgName` where `dir` is the source texture's own
folder, so `___vp` / `__vp_<udim>` files land in `sourceimages/` next to
the originals — then get picked up by publishes and texture collection.
Should write to a dedicated subfolder (e.g. `sourceimages/_vp/`) or a
project-level cache dir.

## Extracted shelf tools (`scripts/temp/`) — all need revisiting

Inline Python lifted verbatim out of `shelfButton -command` blocks and
removed from the shelf. Nothing has been fixed or tested. See
`scripts/temp/README.md` and the per-file header notes.

### 19. Consolidate the dup/bake/FBX-export block
`ul_tmp_exportSkeletonFBX.py`, `ul_tmp_bakeToDuplicate.py` and
`bakeCrocodile()` in `ul_tmp_crocodileRig.py` are three copies of the
same duplicate → bake → export-FBX pattern. One function with an
export on/off flag replaces all three. None guard an empty selection;
none handle `_working`; all crash on an unsaved scene. Note the FBX
exporter's annotation claims it removes namespaces — it doesn't.

### 20. Consolidate the rig select/key tools
`ul_tmp_selectAnimControls.py` (`:AnimCTRLS`, `:Fingers_L/R_CTRLS1`) and
the Croc pair (`:animSet`) are the same tool with different hardcoded set
names. One set-name-driven function replaces all four. All `IndexError`
on an empty selection and assume the selection is namespaced.

### 21. Loop-key tools: confirm intent, then merge
`ul_tmp_loopKeys.py` — both original buttons carried the *same*
annotation, so one was mislabelled. The code matches the labels, not the
annotations. Confirm which direction is wanted, then collapse to one
function with a direction flag.

### 22. GetX / SetX needs a Python rewrite
`ul_tmp_xformClipboard.py` — original MEL preserved, not ported. Relies
on undeclared MEL globals `$t` / `$r` that any other script can clobber.
Rewrite storing world translate/rotate in a module variable (or optionVar
if it should survive a restart), with selection guards.

### 23. Salvage the texture-connect snippet
`ul_tmp_connectTextureToMaterial.py` — a one-off with a hardcoded
material and texture path. The reusable part is the place2dTexture → file
node wiring. Generalise to take material + image path, drive the 20
`connectAttr` calls from a name-pair loop, and use the renderer-aware
colour slot from Issue 14.

## Removed from the shelf (no longer this repo's problem)

- **Export Anim MultiOut** → `aAnimExporter_01()` and **Relink
  References** → `aReferenceReLinker_01()`. Both MEL procs are absent
  from this repo, so the buttons were dead. `aAnimExporter_01` is
  described as the original comprehensive exporter (all formats +
  playblasts) and may be worth tracking down before rewriting that
  ground.
- **Anim Retarget**, **Digit Mirror Control**, **StudioLibrary** —
  third-party, wired with machine-specific absolute paths under
  `C:\Users\Luke - WS\Downloads\`. To be handled later in another format.

## How to verify (no Maya in the sandbox)

For each change, add a note here or in the commit message describing
the in-Maya test, e.g.:
- Issue 1: `importlib.reload(ul_pipelineTools)` imports clean; every
  shelf button fires in an unsaved scene and a saved `_working` scene.
- Issue 2: run `makeViewportShader()` on a selection containing one
  UDIM-textured and one single-texture material; confirm both `__vp`
  textures are 512x512.
