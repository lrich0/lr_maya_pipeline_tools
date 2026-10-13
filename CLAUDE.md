# CLAUDE.md — Unlisted Maya Pipeline Tools

## What this is

In-house Maya pipeline tools for the "Unlisted" workflow (VFX/animation
production, shared with pipeline work at RMIT). Tools are launched from
Maya shelf buttons and cover:

- Scene versioning and publishing (`versionUp`, `publishAll`, `publishSelected`)
- Camera / Alembic / reference exports
- Cross-scene copy/paste via a temp file
- Shader export/relink via proxy-plane trick (`exportShaders` / `relinkShaders`)
- Viewport shader baking with texture downres + UDIM support (`makeViewportShader`)

## Interface — shelf only

`prefs/shelves/shelf_Unlisted.mel` is **the** interface. Every shelf
button calls a function in `ul_pipelineTools`; there is no other entry
point and no in-Maya UI.

The two floating windows (`floatingWindow`, `rsGeoSettingsWindow`, plus
its `setObjID` / `setTess` / `setDisp` / `setVis` stubs) were **removed** —
neither was wired to a shelf button, both had broken string callbacks,
and the Redshift geo window was almost entirely unimplemented.

**A floating-window interface may be revisited later**, but is not
wanted now. Don't add windows, tabs, or dialogs unless asked. New work
goes in as a shelf-callable function.

## Environment & hard constraints

- **Runtime is Maya's embedded Python** (Python 3, Maya 2022+). Code uses
  `maya.cmds`, `maya.mel`, and `maya.api.OpenMaya.MImage`.
- **Maya is not available to the agent, so you can't run or test this
  code.** Do not add `pip install maya` or mock imports into the module
  itself. Static analysis, careful reading, and reasoning about Maya API
  behavior are the verification tools. Flag anything that needs in-Maya
  testing in your summary so a human can verify.
- Scripts must remain **shelf-button friendly**: importable as a module
  (`import ul_pipelineTools`) with functions callable as
  `ul_pipelineTools.funcName()`. If a floating UI is ever revisited, its
  callbacks must be Python callables or `functools.partial`, never bare
  string callbacks — that is what broke the old `floatingWindow`.
- Windows paths appear in places (`D:/CACHE/...`). Studio machines are
  Windows; RMIT lab machines may not be. Prefer configurable paths over
  hardcoded ones, but don't break the existing Windows workflow.

## Renderer support

**Arnold (MtoA) is the primary renderer** — most students render with
Arnold. **Redshift is secondary** and must keep working; do not remove
or break existing `rs*` handling.

- Arnold per-shape attributes use the `ai` prefix (e.g. `aiOpaque`,
  `aiSubdivType`, `aiVisibleInDiffuseReflection`); Redshift uses `rs`.
  Anywhere the code copies or filters render-stat attributes by the
  `rs` prefix (`exportShaders`, `relinkShaders`), it must handle `ai`
  attributes the same way.
- Shading group slots: Arnold materials connect via the SG's
  `aiSurfaceShader` attribute; Redshift via `rsSurfaceShader`; both
  renderers also respect the plain `surfaceShader` slot. Code that
  detects material type by node name (e.g. the `'Redshift'` check in
  `makeViewportShader`) needs an equivalent Arnold path — Arnold
  material node types start with `ai` (e.g. `aiStandardSurface`).
- Attribute name mapping differs: Redshift materials use
  `diffuse_color`; `aiStandardSurface` uses `baseColor` (and `base` as
  weight). Don't assume Redshift attribute names on Arnold nodes.
- The `ai*` / `rs*` attributes only exist when the respective plugin
  (mtoa / redshift4maya) is loaded. Tools must degrade gracefully —
  check `mc.pluginInfo('mtoa', q=True, loaded=True)` (and likewise for
  Redshift) or check attribute existence before get/set, and warn
  rather than traceback if a renderer isn't available. Never
  auto-load render plugins from these tools.
- When adding renderer-specific logic, structure it so a third renderer
  could be added later (e.g. a prefix/slot lookup, not scattered
  if-Redshift checks). New renderer-facing features should be built and
  tested Arnold-first, then extended to Redshift.

### Decided: separate shelf buttons per renderer

Renderer-facing tools get **one shelf button per renderer** rather than
one auto-detecting button — e.g. an Arnold "Export Shaders" and a
Redshift "Export Shaders". Rationale: no redundant setup work is done
for a renderer that isn't in the scene, and the artist stays in control
of which path runs instead of relying on detection heuristics.

Implication for the module: the underlying functions take the renderer
as an argument (`exportShaders('arnold')` / `exportShaders('redshift')`)
with a lookup table for the prefix, SG slot, and colour-attribute names.
Keep the no-argument form working for existing studio shelves.

Arnold support is incomplete — see ISSUES 14–16.

## Copy/paste temp path

Copy/paste uses a per-user Windows temp path; see ISSUES #5.

## scripts/temp — extracted shelf scripts, all need revisiting

Inline Python that used to live in `shelfButton -command` blocks has been
lifted **verbatim** into `scripts/temp/` and removed from the shelf. See
`scripts/temp/README.md`.

Nothing in there is fixed, tested, or ported — it is the original code,
unescaped. **All of it needs revisiting**; some element of each is
worth keeping. Per-file notes list what's wrong. Recurring themes: the
dup/bake/FBX-export block appears three times, rig tools hardcode set
and group names, and none guard an empty selection. Do not put any of it
back on the shelf as-is.

## Directory conventions (the "Unlisted" workflow)

Working scenes ideally live in a `_working` folder with versioned names:

```
<project>/<asset-or-shot>/
    _working/                  shot010_anim_v003.mb   <- artists work here
    published/                 shot010_anim_v003.mb   <- publishAll/Selected output
    Animation Exports/<scene>/ shot010_anim_v003.mb, shot010_anim_v003.abc
    publishedShaders/          <scene>_shaders.mb
    scenes/camera/<shot>/      <shot>_cam_v###.mb
```
ideal workflow is as outlined:
- Version token is `_v` + zero-padded int, before the extension.
- Publish paths are derived by stripping the filename and `_working`
  segment from the current scene path. Four functions duplicate this
  logic — a shared helper is a wanted refactor (Issue #7).

- HOWEVER, the below should be taken into consideration:
  - The `_working` folder is the **studio** convention and is OPTIONAL.
  Publish paths strip the filename and, *if present*, a trailing
  `_working` segment. Student scenes may live anywhere; tools must not
  assume `_working` exists, and must degrade gracefully — outputs are
  simply created as siblings of the scene file in that case.
- Filename conventions (`_v###` version token, `<shot>_...` prefix) are
  also not guaranteed for student files. Tools that parse filenames
  must validate and warn ("no version token found — save as
  name_v001.mb first") instead of throwing tracebacks. Never crash on
  an untitled/unsaved scene.


## Naming conventions in scene data

- `sgList__<sceneName>` — hidden transform holding shader-assignment proxies
- `sg___<shapeName>___` — proxy plane carrying a shading group assignment
- `vp___<materialName>` — generated viewport lambert
- `vp___<fileNodeName>` — duplicated file node for downres'd textures
- `___vp` / `__vp_<udim>` — suffix on downres'd texture files
- `ns___copypaste` — temp namespace used by paste

Do not change these prefixes without updating both the export and
relink/cleanup sides.

## Code style

- Keep it plain and readable — the audience is TDs/artists, not software
  engineers. No heavy abstractions, no external dependencies.
- Preserve function names: shelf buttons at the studio call them by name.
  If a signature must change, keep backwards-compatible defaults
  (e.g. `def publishAll(dir='published')`).
- `dir` shadows a builtin in several signatures; when touching those
  functions rename the parameter but keep a compatible positional order.
- Add docstrings in the existing simple style (USAGE line for
  artist-facing tools).

## Workflow for this repo

- Work through `ISSUES.md` — it is the backlog. Mark items done with a
  short note of what changed.
- One issue (or one tightly-related group) per commit.
- Since nothing can be executed here, every change should come with a
  short "how to verify in Maya" note in the commit message or ISSUES.md.
