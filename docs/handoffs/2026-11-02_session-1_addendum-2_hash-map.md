# Addendum 2 to the 2026-11-02 session 1 handoff: commit hash map

On 2026-11-02 the first commit's title was reworded (the user's decision).
The old title was "Initial commit: maya tools as found (33 files,
unmodified)", which was wrong on two counts:

- that commit held only this folder's files, not 33 files across the old `maya` repo;
- it already included the earlier #1, #2 and #5 fixes, so it wasn't unmodified.

The new title is "Initial commit: RMIT Pipeline Tools, split from maya
(includes earlier #1, #2, #5 fixes)". The commit body, authors and dates
are unchanged.

To reword a commit, git has to rewrite every commit after it, so all the
hashes changed. The changes in each commit stayed the same; `git diff`
between the old and new tips was empty. The new history was then
force-pushed to `origin` (`lrich0/lr_maya_pipeline_tools`). This was
safe because nobody else had cloned the repo yet (confirmed by the user).

The handoff, the first addendum, and commit messages in other repos still
quote the **old** hashes. Use this table to translate them:

| Old | New | Commit |
|---|---|---|
| `154b6d8` | `9a6ee1d` | Initial commit (reworded) |
| `54b9c92` | `e07898f` | CLAUDE.md tidy (brief 2) |
| `6d03652` | `6bc9757` | #17 makeViewportShader per-material SG |
| `243a633` | `ac1c443` | #3 versionUp guards |
| `bd5f005` | `58e6063` | #3 versionUp confirm dialogs |
| `2db3c90` | `f9c7675` | #4 exportCamera |
| `6558871` | `803f945` | #3 dialog wording tweaks |
| `1346a31` | `f0a64d4` | .gitignore |
| `5ebce0f` | `69d84c0` | Save & Backup icon (user) |
| `c748357` | `df1817b` | Session handoff |
| `085c6ff` | `e889f4f` | Addendum 1 |

Old hashes quoted outside this repo:

- `D:\_dev\maya`, commit `e3bea83`: "pairs with RMIT Pipeline Tools
  `1346a31`". That commit is now `f0a64d4`.
- `D:\_dev`, commit `98839bb`: same pairing.

Those commit messages were left unchanged.
