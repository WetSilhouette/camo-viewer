# AGENTS.md — camo-viewer

Guidance for anyone (human or agent) working in this repo. Read
`CONCEPT.md` first for what this mod is; this file is about *how* to
work on it.

## Current phase: docs/planning only

**No code yet.** Wait for explicit go-ahead before writing any
implementation (Phase 0 scaffolding in `TASKS.md` or later). Research,
probing, and note-taking are fine and encouraged now.

## Research discipline (carried over from this workspace's other mod)

A sibling project in this workspace (`../wotstat-spotting`, whose old
research notes were moved into `_reference/wotstat-spotting-notes/`
when this project's docs were set up) learned this the hard way across
several sessions: **unsourced claims about game internals rot fast and
waste time.** Apply the same discipline here:

- Every non-obvious technical claim added to `NOTES.md` needs a
  source: a specific file + line from a decompiled-source lookup, or a
  direct quote from this machine's own `python.log`, or "confirmed
  live in-game on `<date>`." Guesses are allowed but must be labeled
  `# TODO(api-verify)` or "unconfirmed" until checked.
- Prefer checking **this exact client version** over trusting general
  knowledge or older/other-version notes. Current build per
  `python.log`: `WorldOfTanks(x64) 2.3.1.1505`. UI internals
  (Scaleform vs. DevilsUI, specific view/component names) are exactly
  the kind of thing that changes between versions — don't assume
  anything here carries over from older WoT knowledge without
  checking.
- When a public decompiled-source repo is used, pin to the branch that
  actually matches this build, not just the nearest-sounding tag.

## Tools available for research

- **`_reference/wot-src-eu/`** — local clone of
  `github.com/izeberg/wot-src`, branch `EU` (user-provided source,
  ~1.8GB, not committed anywhere — `sources/` is decompiled Python,
  `sources-as3/` is decompiled ActionScript/Flash). Already used
  successfully for Phase 1 (see `NOTES.md` §7a) — grep this directly
  instead of re-cloning or browsing GitHub. Pinned to whatever commit
  was checked out when cloned; re-`git pull` if findings seem stale
  against a newer client patch. Reports client build `2.3.1.1.#910`,
  close to but not exactly this machine's `2.3.1.1505` — same branch,
  treat as very-likely-accurate but not byte-exact confirmed.
- **`../WoT_ModDevTools`** — local `clientUnpacker.py` (Client Data
  utility) can extract and decompile this exact installed client's
  `.pkg` files (including `gui-part*.pkg`, which is where the
  Customization screen's UI assets/scripts would live) into real
  source under `ClientData/<gameVersion>/`. This is the most reliable
  way to answer the Scaleform-vs-DevilsUI question and find real
  view/component class names for *this* build, since it decompiles
  the actual installed client rather than relying on a public repo
  that may be pinned to a different version.
- Public decompiled-source repos (as used by the sibling project,
  see `_reference/wotstat-spotting-notes/NOTES.md` §14 for the branch
  that matched that project's client version) — useful as a faster
  first pass, but verify anything load-bearing against the local
  unpacker output before relying on it.
- `python.log` at
  `~/Library/Application Support/Wargaming.net Game Center/Bottles/wargaminggamecenter64/drive_c/Games/World_of_Tanks_EU/python.log`
  — reload after any manual in-game test; this is the primary feedback
  channel for confirming a hook actually fires and what a probed value
  actually is.

## Reference implementations in this workspace

- **`../wotstat-vegetation`** — confirmed-working mod skeleton to
  model this project's scaffolding on:
  - Entry point: `res/scripts/client/gui/mods/mod_<name>.py` with
    `init()`/`fini()`, importing a `<Name>` class from a same-named
    package directory (e.g. `wotstatVegetation/WotstatVegetation.py`
    for id `wotstat.vegetation`). This project should follow the same
    shape: id `silhouette.camoViewer` in `meta.xml`, Python package
    `camoViewer/` (dots aren't valid in Python module names, hence the
    camelCase-no-dot folder convention).
  - Key binding: `from gui import InputHandler`, then
    `InputHandler.g_instance.onKeyUp += self.handleKeyUpEvent`, with a
    handler that checks `event.key` against `Keys.KEY_<X>` — this is
    the confirmed pattern to use for the Space-toggle instead of
    guessing at a different input API.
  - `meta.xml` + `build.sh` templating (`{{VERSION}}` substitution,
    `python2 -m compileall`, zip into `.wotmod`) — copy this project's
    shape rather than the one under `_reference/`, since it's simpler
    and doesn't carry the other mod's debug-flag templating this
    project doesn't need (unless a debug flag turns out useful here
    too — evaluate during Phase 0).
- **`_reference/wotstat-spotting-notes/`** — moved-aside notes from an
  unrelated mod (vehicle spotting-checkpoint visualization, not
  camos). Its **camo/spotting-specific findings do not apply here** —
  don't reuse conclusions like `DebugDrawer` usage or
  `visibilityCheckPoints` formulas, they're for a different feature
  domain (3D world-space rendering vs. this project's 2D
  screen-space UI work). It **is** worth skimming for
  general-infrastructure patterns that hold across any WoT mod in this
  workspace: the build/packaging pipeline, `BigWorld`/engine basics,
  and the general "verify against the real client, cite sources"
  discipline this file is asking you to continue.

## Code architecture convention (once code starts)

Keep pure logic (item filtering/sorting, any future favorites-list
persistence shape, data transforms) in modules with **zero game-API
imports**, so it's testable directly with plain `python3`/`python2` in
isolation. Keep game-API glue (view hooking, `InputHandler` wiring,
whatever DevilsUI/Scaleform-specific code Phase 1 research turns up)
in separate modules. Same split the sibling project used
(`core/geometry.py` pure vs. `core/transform.py` glue) — mirror the
pattern, don't copy the files.

## Fair-play/safety note

This mod only changes how existing, already-owned cosmetic items are
*browsed* — no hidden game state is read, no gameplay values are
changed, nothing is transmitted anywhere. Lower-risk category than a
mod reading live vehicle geometry. Still worth a quick sanity check of
current Wargaming mod policy before any public distribution, but this
shouldn't block development.
