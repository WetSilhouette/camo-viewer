# NOTES.md — camo-viewer research findings

Living document, fresh for this project (the previous NOTES.md found
in this folder was for an unrelated mod, `wotstat.spotting` — moved to
`_reference/wotstat-spotting-notes/`, see `AGENTS.md`). Every entry
here should be sourced (decompiled file + line, or a direct
`python.log` quote, or "confirmed live in-game on `<date>`") — treat
anything else in this codebase as unverified until it gets an entry
here, per `AGENTS.md`'s research discipline.

---

## Status: Phase 1 (research) not yet started

Nothing about the Customization screen's actual UI implementation has
been checked yet. Everything below is either (a) confirmed
general-infrastructure fact, reused from a working sibling mod in this
workspace, or (b) an explicitly open question. See `TASKS.md` Phase 1
for the concrete next steps.

---

## 1. Confirmed: local client environment

- Installed game build, from `python.log` line 4:
  `WorldOfTanks(x64) 2.3.1.1505 #2586949`, path
  `C:/Games/World_of_Tanks_EU/win64/WorldOfTanks.exe`.
- Mods load from
  `C:/Games/World_of_Tanks_EU/mods/2.3.1.1/` (confirmed by
  `python.log` line 24 successfully loading
  `wotstat.spotting_0.0.2.wotmod` from that exact path — i.e. the
  `<gameVersion>` folder segment for this build is `2.3.1.1`, not the
  full `2.3.1.1505`).
- `res_mods/2.3.1.1/` is checked first and reported "not found" for
  this install (`python.log` line 23) — `mods/2.3.1.1/` is the one
  that's actually in use here.

## 2. Confirmed: mod skeleton pattern (from `../wotstat-vegetation`)

Source: direct read of
`wotstat-vegetation/res/scripts/client/gui/mods/mod_wotstatVegetation.py`,
`wotstat-vegetation/meta.xml`, and
`wotstat-vegetation/res/scripts/client/gui/mods/wotstatVegetation/WotstatVegetation.py`.

- Entry point file `mod_<PackageName>.py` directly under
  `res/scripts/client/gui/mods/`, minimal:
  ```python
  from .wotstatVegetation.WotstatVegetation import WotstatVegetation

  def init():
    global wotstatVegetation
    wotstatVegetation = WotstatVegetation()

  def fini():
    wotstatVegetation.dispose()
  ```
- `meta.xml` shape:
  ```xml
  <root>
    <id>wotstat.vegetation</id>
    <version>{{VERSION}}</version>
    <name>wotstat.vegetation</name>
    <description>Vegetation utilities by WotStat</description>
  </root>
  ```
  `{{VERSION}}` is substituted by `build.sh` at build time (`perl -i
  -pe` substitution, per the reference `build.sh` in
  `_reference/wotstat-spotting-notes/`, same mechanism).
- **Applied to this project**: id should be `silhouette.camoViewer`
  per user decision, Python package folder `camoViewer/` (no dot —
  dots aren't valid in Python package/module names, hence
  `wotstat.vegetation` the id vs. `wotstatVegetation` the folder).

## 3. Confirmed: key-binding pattern (from `../wotstat-vegetation`)

Source:
`wotstat-vegetation/res/scripts/client/gui/mods/wotstatVegetation/WotstatVegetation.py`,
grep-confirmed lines:
```python
from gui import InputHandler
...
InputHandler.g_instance.onKeyUp += self.handleKeyUpEvent
...
def handleKeyUpEvent(self, event):
  ...
  if event.key not in (Keys.KEY_F2, Keys.KEY_F3):
    return
  ...
  if event.key == Keys.KEY_F2:
    ...
  elif event.key == Keys.KEY_F3:
    ...
```
This is a **confirmed-working** pattern in this exact client
environment (this mod is installed and running per `python.log`'s mod
load line) — use `Keys.KEY_SPACE` the same way rather than researching
a different input API from scratch. Still need to confirm (Phase 1)
that this fires correctly when the Customization screen specifically
has focus, and that it doesn't double-fire alongside the game's own
existing Space handling for the vehicle carousel (different screen,
but worth explicitly checking, not assuming).

## 4. Confirmed: local decompilation tooling available

`../WoT_ModDevTools/ClientData/utility/clientUnpacker.py` — extracts
and decompiles this exact installed client's `.pkg` files (config
lists `gui-part1.pkg`, `gui-part2.pkg`, `gui-part3.pkg`, `scripts.pkg`
by default; Customization-screen assets/scripts likely live in one of
the `gui-part*.pkg` files, unconfirmed which one specifically — Phase
1 task). Needs Python 3.8+ to run the unpacker itself, ships its own
Python 2.7 64-bit for decompiling scripts. Outputs to
`ClientData/<gameVersion>/`. This is the primary tool for Phase 1's
core question (Scaleform vs. DevilsUI) since it decompiles *this*
build directly rather than relying on a public repo pinned to a
possibly-different version.

## 5. Open questions (Phase 1 targets — see `TASKS.md`)

- [ ] Is the Customization screen (Camouflage/2D Styles tabs
      specifically) Scaleform/Flash or DevilsUI/Cohtml in build
      `2.3.1.1505`? **The single most important open question** — it
      determines the entire technical approach for every later phase.
- [ ] Which `.pkg` file(s) contain the Customization screen's
      script/view code, for a targeted `clientUnpacker.py` extraction
      instead of decompiling everything?
- [ ] Python-side view/plugin class name(s) for the Camouflage and 2D
      Styles carousels, and their item data provider.
- [ ] How the vehicle carousel's own Space expand/collapse is
      implemented — is the expanded grid a distinct, reusable
      component, or something bespoke to the vehicle list?
- [ ] Exact close/collapse trigger for the vehicle grid (Space again?
      Esc? click-outside?) — determines what the camo version should
      do to match.
- [ ] Whether Space is truly unbound in every sub-state of the
      Customization screen (e.g. while a text field has focus
      somewhere on that screen), not just the general case the user
      has already confirmed from experience.

## 6. Confirmed: Phase 0 shipped a real bug — DEBUG_MODE is a bool, not a string

Source: `python.log`, session starting `2026-08-11 08:43:19`, line 283:
```
debug_utils.HandledError: (TypeError("cannot concatenate 'str' and 'bool' objects",), ())
```
Traceback pinpoints `camoViewer/CamoViewer.py`, line 9, inside
`__init__`.

**Root cause**: `build.sh`'s templating does
`perl -i -pe "s/'{{DEBUG_MODE}}'/True/g"` — it substitutes the
*quoted* placeholder `'{{DEBUG_MODE}}'` with the *unquoted* literal
`True`/`False`. After build, `DEBUG_MODE` is therefore a real Python
`bool`, not a string — confirmed intentional, matching
`wotstat-vegetation`'s own usage (`DEBUG_MODE` there is only ever used
in an `if DEBUG_MODE:` check, never string-concatenated). Phase 0's
first `CamoViewer.py` used `'...' + DEBUG_MODE` in a log call, which
is invalid once `DEBUG_MODE` is a bool. Fixed by wrapping with
`str(DEBUG_MODE)`. **Lesson for any future code touching
`DEBUG_MODE`**: always treat it as a bool (`if DEBUG_MODE:`), never
string-concatenate it directly.

**Also confirmed (useful going forward): what actually happens when a
mod's `init()` throws.** The traceback shows the call chain
`scripts/client/gui/mods/__init__.py` → `_callModMethod` →
`forEach` → each mod's `init()`, and the exception surfaces as
`debug_utils.HandledError` — i.e. **the mods-loading framework wraps
each mod's `init()` individually and one mod's exception does not stop
the others or the client from continuing to boot**: `python.log`
line 273 shows `wotstat.spotting` also logged its own unrelated
double-init guard message in the same session, and line 298 shows
`Game loaded in 22.443 seconds and 53 steps` shortly after our
exception — the client reached the lobby. Worth remembering: a mod
exception during `init()` is a *silent* partial failure (that mod's
`__init__` just doesn't finish, no crash dialog), not a hard crash —
always check `python.log` after any manual test, don't rely on the
client "looking fine" as proof a mod initialized correctly.

## 7a. Phase 1 findings — Session 1, `izeberg/wot-src` (branch `EU`)

Local clone at `_reference/wot-src-eu/` (partial-clone attempt fell back
to a full checkout, ~1.8GB total — `sources/` is the full decompiled
Python client, `sources-as3/` is decompiled ActionScript 3/Flash,
`sources/version.xml` reports `v.2.3.1.1 #910` / client build
`2594806`, close to but not an exact match for this machine's actual
installed build `2.3.1.1505` (`#2586949`) — same `2.3.1` branch,
probably a slightly earlier point patch. Treat findings here as
very-likely-correct for this build, not byte-exact confirmed).

### THE BIG ANSWER: Customization screen is Scaleform/DAAPI, not DevilsUI

Directly confirmed from source, not inferred:
- `sources/res/scripts/client/gui/Scaleform/daapi/view/lobby/customization/customization_bottom_panel.py`:
  `class CustomizationBottomPanel(CustomizationBottomPanelMeta)` —
  `CustomizationBottomPanelMeta(BaseDAAPIComponent)` — this is the
  Python-side controller for the exact carousel strip in screenshot 3
  (camo/2D-styles items at the bottom of the Customization screen).
  It talks to a compiled `.swf` movie via `as_*S()` methods that call
  `self.flashObject.as_*(...)` — the textbook Scaleform/DAAPI pattern,
  not DevilsUI.
- `customization_carousel.py`:
  `class CustomizationCarouselDataProvider(SortableDAAPIDataProvider)`
  — same confirmation from the data-provider side.
- **Correction to an earlier wrong guess in this file**: I initially
  hypothesized (from directory names alone, before reading actual
  code) that since `gui/impl/lobby/hangar/...` uses the newer
  `impl`/DevilsUI naming convention, the vehicle carousel might be
  DevilsUI while Customization stayed Scaleform. **Wrong** — checked
  directly: `sources/res/scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/basic/tank_carousel.py`
  has `class TankCarousel(TankCarouselMeta)`, same DAAPI pattern.
  **Both the vehicle carousel and the Customization carousel are
  Scaleform.** The `impl`/DevilsUI code under `gui/impl/lobby/hangar/`
  is real, but it's for *other* hangar panels (crew, equipment,
  filters sidebar, vehicle stats presenters) — not the tank carousel
  widget itself. Lesson: don't infer UI framework from directory
  naming conventions alone, always check the actual base class of the
  concrete view.

### Confirmed: the data layer is already fully in-memory, no pagination concerns

`CarouselCache`/`CustomizationCarouselDataProvider` in
`customization_carousel.py` load **all** items for the current
vehicle/tab/season into memory up front (`__initItemsData`), then
filter/sort/group in Python. `itemCount` (currently visible after
filters) vs. `totalItemCount` (all) are both already tracked and
already shown to the player today as a "12 / 400" label (matches the
"0/400" counters visible in screenshot 3). **Good news for Phase 3**:
a "full grid" view doesn't need any new data-fetching work — the
complete item list for a tab is already sitting in
`CustomizationCarouselDataProvider.collection` the moment the tab is
open; the problem is purely one of *rendering*, not *data access*.

### Confirmed: rich filter infrastructure already exists in-game

`customization_carousel.py`'s `FilterTypes`/`__initFilters()`: historic
/ non-historic / fantastical (disjunction filter), owned-in-inventory,
currently-applied, "used up on another vehicle", editable vs.
non-editable 2D styles, progression-only, rarity, and (for projection
decals) form-factor — plus a group/bookmark dropdown per tab. **This
directly informs the Phase 5 backlog "filters" feature**: much of what
a "favorites/filters" feature would want already exists as real,
working server-driven filter criteria (`REQ_CRITERIA.CUSTOMIZATION.*`)
— extending our own mod's filtering could mean reusing/reading these
existing criteria rather than reinventing item metadata from scratch.
No "favorites"/starred-items concept found anywhere in this file or
its imports — consistent with the original assumption that favorites
would need to be built from nothing (a new small persisted ID set,
e.g. via `AccountSettings`, the same settings-storage system this file
already uses for other small per-account flags like
`CUSTOMIZATION_TABS_VISITED`).

### IMPORTANT — the compiled carousel `.swf` has no grid/expand capability to reuse

This is the critical finding for feasibility, not just an implementation detail:

- `CustomizationBottomPanelMeta.py` (the full list of Python↔Flash
  entry points for this exact widget) has **no row-count, grid, or
  expand/collapse method at all** — compare to the *vehicle* carousel's
  `TankCarouselMeta.as_rowCountS(value)` /
  `as_useExtendedCarouselS(value)`, which **do** exist for that
  *different* widget. The Customization carousel's compiled Flash
  asset was simply never built with a multi-row/grid mode — there's no
  hidden flag to flip from Python.
- Confirmed further from the AS3 side (`sources-as3/gui_lobby/.../vehicleCustomization/`):
  `CustomizationCarouselLayoutController.as` and
  `CustomizationCarouselLayoutRenderer.as` (the actual layout/rendering
  logic for this widget) only ever compute single-row scroll-arrow
  positions — no row/column/wrap concept anywhere in either file.
- Also checked: Space-key handling for the *vehicle* carousel's own
  expand behavior (the screenshots' reference behavior) is **not**
  implemented via `command_mapping.xml` (that file's `KEY_SPACE`
  entries are battle-only vehicle-control commands, e.g.
  `CMD_BLOCK_TRACKS`) and **not** a literal `Keyboard.SPACE` match
  inside any carousel-related AS3 file. Likely explanation (not fully
  confirmed): Scaleform's CLIK UI framework
  (`common/scripts/scaleform/clik/managers/InputDelegate.as`, which
  does reference `Keyboard.SPACE`) treats Space as a generic
  "activate the currently focused component" key — i.e. the vehicle
  carousel's expand toggle is probably just a focusable button that
  Space happens to activate like any other focused button, not a
  hangar-specific keybinding we could point at and copy. **Practical
  upshot: we don't need to reverse-engineer WG's exact Space-routing
  mechanism** — our own mod's key hook (confirmed working
  `InputHandler.g_instance.onKeyUp` pattern, §3) can drive whatever
  expand/collapse action we end up building, independent of how
  vanilla WG wires it.

### The real open question this raises (not yet resolved — needs a decision, see chat)

Since there's no latent grid mode to unlock, presenting a genuine
multi-row grid for Camo/2D Styles means **rendering UI that doesn't
exist in the shipped client at all**. Options, none yet chosen:

1. **New Scaleform content**: author a new `.swf` (Adobe Flex
   SDK/`mxmlc` + AS3) as either a patch to the existing movie or a new
   standalone overlay window. Matches the existing screen's native
   look for free, but needs real Flash tooling/skills this project
   doesn't have set up yet, and loading a *new* custom movie into the
   lobby (vs. patching an existing one) is itself unresearched.
2. **New DevilsUI content**: build the grid as a `gui.impl`
   (Cohtml/HTML+JS+Python-viewmodel) window instead, sitting
   *alongside* the Scaleform Customization screen rather than inside
   it, opened/closed on Space, fed by our own Python glue reading the
   same already-in-memory item data `customization_carousel.py` uses.
   Likely far more approachable than Flex/AS3 for this project, but
   whether third-party mods can register a genuinely new `gui.impl`
   view (`R.views.*` resource IDs look build-time-generated by WG's
   own tooling) is itself unresearched and could turn out to be just
   as blocked.
3. **Scope pivot**: drop the "true multi-row grid" goal for v1 and
   find a smaller win achievable with existing, already-wired
   Scaleform capabilities (e.g. surfacing the existing filter/group
   popover more prominently) — a real option, but a change from
   `CONCEPT.md`'s stated v1 goal, not something to decide unilaterally.

## 7b. Phase 1 findings — Session 1 continued: the DevilsUI resource pipeline is plain HTML/CSS/JS, not a compiled black box

Follow-up to §7a's open fork (new Scaleform vs. new DevilsUI vs. scope
pivot). Instead of guessing, inspected this machine's actual installed
client packages directly (`res/packages/gui-part1..4.pkg` — confirmed
plain zip archives via Python's `zipfile`, no special tooling needed).

**File-type census across all 4 `gui-part*.pkg`** (~1.3-1.5GB each):
51671 `.png`, 4323 `.dds`, **637 `.swf`**, **614 `.js`**, **515
`.css`**, **448 `.html`**, plus a handful of raw `.ts` (TypeScript),
`.swc`, `.mjs`, `.prettierrc`, `.stylelintignore` files — leftover
dev-tooling artifacts from WG's own build, strong independent
confirmation the DevilsUI layer really is authored as a normal
JS/TS/web-tooling project, not some proprietary compiled format.

**Traced the exact resolution chain for a concrete example**
(`R.views.mono.lobby.select_vehicle = DynAccessor(445)`, found in
§7a's `SelectVehicleWindow` example):
- `gui-part1.pkg` contains
  `gui/gameface/_dist/production/mono/lobby/views/select_vehicle/select_vehicle.html`
  + `.../select_vehicle.html/bundle.js`
  (a webpack-style compiled JS bundle — the *build output*, not
  something we'd need to reproduce by hand).
- `gui-part3.pkg` contains `gui/unbound/res_map.json` (~17MB, JSON5 —
  has trailing commas, not strict JSON) — this is the manifest the
  boot log's `[WULF] UiResourceManager: parse resources from
  gui/unbound/res_map.json` line (seen in every session's
  `python.log`) is loading. Its `select_vehicle` entry, keyed by
  **hex** `"1bd"` (`0x1bd == 445` decimal — matches the Python
  `DynAccessor(445)` exactly):
  ```json
  "1bd": {"type": "Layout",
          "path": "coui://gui/gameface/_dist/production/mono/lobby/select_vehicle/select_vehicle.html",
          "parameters": {"entrance": "select_vehicle", "extension": "", "impl": "gameface"}}
  ```
- `coui://` is Coherent Labs' "Coherent UI"/Gameface custom URL
  scheme — confirms (matches `python.log`'s own `[Gameface]
  GfResourceSystem` lines) that DevilsUI really is a Chromium-class
  HTML/CSS/JS renderer (Coherent Gameface), and views are loaded the
  same way a browser loads a URL: point it at an HTML file.

**Why this matters for the Phase 1 fork**: the full chain is now
concretely understood end-to-end — Python `DynAccessor(N)` → hex key
`N` in a human-readable JSON manifest → `coui://` URL → a real,
individually-addressable `.html`/`.css`/`.js` file. This is a
dramatically more approachable target than Scaleform: authoring plain
HTML/CSS/JS needs no special SDK (unlike Flex/`mxmlc` + AS3 for
Scaleform, for which no equally-clean "just add a file, list it in a
manifest" mechanism has been found). We would not need to reproduce
WG's own webpack/TS build step — Gameface just needs valid web
content at a resolvable path, and we can hand-write plain HTML/CSS/JS
directly. This directly supports recommending the DevilsUI path over
Scaleform for this project (see chat), given the user has no prior
experience with either and asked for the most guaranteed route.

**Still open — the actual remaining blocker, narrower than before**:
whether a third-party mod can get the engine to load a *new*
`coui://` path at all. Two candidate mechanisms, neither confirmed
yet:
1. Whether the client's existing `mods/<gameVersion>/` overlay
   mechanism (already confirmed working for `.py`/`.pyc` under
   `res/scripts/...`, per every `python.log` so far) also overlays
   plain resource files under `res/gui/...` / `res/unbound/...` the
   same way — i.e. could a `.wotmod` ship its own
   `gui/unbound/res_map.json` (merged or overriding) plus its own new
   `gui/gameface/.../camoViewer/*.html` files, the same pattern WG's
   own views use.
2. Whether `frameworks.wulf`'s window/view APIs
   (`windows_system/window.py`, `windows_system/windows_manager.py`,
   `ViewSettings`/`ViewImpl` in `gui/impl/pub/`) expose any lower-level
   way to open a window from a raw path/URL directly, bypassing the
   `R.views` numeric-ID catalog entirely (not yet read in detail — the
   next concrete file to check if pursuing this).

## 7c. Session 1, live test #1 — `file://` in WG's embedded browser: BLOCKED, confirmed live

Built a real test (`camoViewer/utils/browser_test.py`, v0.0.3): F6
writes a small HTML page to the OS temp dir, calls the existing
`showBrowserOverlayView(url)` (§7a/§7b background) with a `file://`
URL pointing at it.

**Result, from live `python.log`**: the browser widget itself
initialized fine (`[WebBrowser] INIT`/`CREATE`/`READY success: True`
all fired), but the actual page load then failed:
```
ERROR: [WebBrowser] FAILED Url: file:///Z:/.../camoViewerBrowserTest.html, Http code: 418, Browser error: None
```
**Conclusion: WG's embedded browser (CEF-based, confirmed by the
`WebBrowser`/`BrowserController` Python glue read in §7b) rejects
`file://` URLs outright**, most likely a deliberate security
restriction baked into however WG initializes their CEF instance (this
game runs under Wine/CrossOver on this machine — note the path got
translated to a `Z:\...` Windows-style path, expected and not the
cause of the failure; the browser log shows it received and attempted
that URL specifically, then rejected it at load time, not at
translation time).

## 7d. Session 1, live test #2 — local HTTP server instead of `file://` (in progress)

Before abandoning "reuse WG's existing browser overlay" entirely,
checked for real precedent of a local HTTP server running inside
WoT's own embedded Python: **found one**,
`sources/res/scripts/client/standalone/login/HttpServer.py` — WG's own
social-login flow runs a `BaseHTTPServer.HTTPServer` on
`127.0.0.1`, port pool `(50010..50014)`, via `threading.Thread(target=self.serve_forever)`,
started/stopped explicitly. Confirms `BaseHTTPServer`/`socket`/
`threading` are real, working, unstripped stdlib modules in this
client's embedded Python 2.7 — not something to worry about being
sandboxed away.

**Applied**: rewrote `browser_test.py` (v0.0.4) to run the same
pattern — a tiny `BaseHTTPServer.HTTPServer` on `127.0.0.1`, port pool
`(50100..50104)`, background daemon thread, serving the same test HTML
on any `GET`. F6 now points `showBrowserOverlayView` at
`http://127.0.0.1:<port>/` instead of a `file://` path.

**Result, from live `python.log`: also blocked, same synthetic error.**
Browser widget init succeeded (`INIT`/`CREATE`/`READY success: True`
all fired again), but load still failed identically:
```
ERROR: [WebBrowser] FAILED Url: http://127.0.0.1:50100/, Http code: 418, Browser error: None
```
**Crucially, our own local HTTP server's request handler never logged
anything** (`_Handler.log_message` overrides to `[CAMO-VIEWER] [http]
...` — absent from the log). That means the client **never actually
opened a TCP connection to our server at all** — this rules out a
Wine/network-routing problem or anything wrong with our server code;
the rejection happens before any real network I/O, for both `file://`
and `http://127.0.0.1` alike. Strong evidence this is a deliberate,
client-side URL policy check inside the native `WebBrowser` module
(not visible in decompiled Python — it's a compiled/native BigWorld
module, not something `wot-src`'s Python decompile can show us),
most plausibly an allow-list restricting this browser to WG's own
CDN/known domains. HTTP 418 here is a synthetic/internal status code
from WG's own wrapper, not a real HTTP response — nothing responded.

**Conclusion: mechanism B (reusing WG's embedded-browser overlay for
custom local content) is a dead end**, at least via any URL scheme
tried so far. Launched a background web-search task to check whether
other WoT modders have documented this restriction or a workaround
before fully abandoning it; not back yet as of this writing.

**Pivoting to test the other remaining candidate**: whether the mod
overlay (`mods/<gameVersion>/`, already confirmed working for
`.py`/`.pyc`) also reaches arbitrary plain resource files under
`res/gui/...` — a much lower-risk, purely additive test (no existing
WG file touched) that's a prerequisite for the §7b `res_map.json`/
`coui://` idea regardless of whether that idea itself pans out. Added
`camoViewer/utils/resmgr_test.py` (v0.0.5): F7 calls
`ResMgr.openSection('gui/camoViewer/test_resource.xml')` (a trivial
file shipped in this mod's own `res/gui/camoViewer/`) and logs
success/failure. Also had to extend `build.sh` to actually zip up
`.xml`/`.html`/`.css`/`.js` resource files into the `.wotmod` — the
original script (inherited from `wotstat-vegetation`) only ever
packaged `.pyc` and `.dds`, since that mod never shipped other
resource types. Not yet tested live.

## 7e. Session 1 — F7 live test result, and the browser route is now conclusively closed

**F7 confirmed positive**, live: `ResMgr.openSection('gui/camoViewer/test_resource.xml')`
found our mod-shipped file and read it correctly
(`marker=camoViewerResMgrTest`). **Confirmed: the mod overlay
(`mods/<gameVersion>/`) reaches arbitrary resource files, not just
`.py`/`.pyc`.** This is genuinely useful groundwork regardless of which
UI path gets picked — any future asset (icons, our own `.xml` configs,
etc.) can ship the same way.

**F6/browser-overlay route: conclusively closed, not just "failed
twice."** Background research (web search + re-reading
`WebBrowser.py` directly, which — unlike `ResMgr`/`BigWorld` — turned
out to actually have real Python source in `wot-src`, not just a
native stub) found the exact mechanism:
- `WebBrowser.py`'s `onWhitelistMiss(...)` is what fires our observed
  `Http code: 418` — it's a synthetic code for "the client-side
  whitelist rejected this URL before navigating."
- The whitelist itself (`igbWhitelist`) is parsed from
  **server-sent** settings in native code (confirmed via strings in
  the client's own `.exe`: `BW::WebWhiteList`,
  `PyWebBrowserProvider::onWhitelistMiss`) — **not present anywhere in
  Python or shipped XML**, i.e. genuinely server-authoritative, not a
  client-side config a mod could point somewhere else.
- One narrow hatch exists (`_WOT_RESOURCE_CUSTOM_SCHEME = 'wotdata'`,
  `WebBrowser.py` lines ~16, ~501-505) but it only serves *sub-resources*
  of an already-whitelisted page, not top-level navigation — doesn't
  help us open our own page.
- **No community documentation found of anyone working around this**
  — searched WoT modding forums/Discord archives/GitHub/wgmods.dev,
  zero hits.
- **Explicit judgment call, and a boundary I'm holding regardless of
  further requests**: bypassing a server-authoritative whitelist would
  mean patching the client executable or intercepting/spoofing server
  settings — squarely Fair Play Policy violation territory, not a
  gray area. **Not pursuing this, full stop**, independent of how the
  rest of this project's technical fork gets decided.

## 7f. Session 1 — reversing the earlier DevilsUI recommendation: Scaleform's view registry is live and Python-scriptable, Gameface's isn't

While confirming there's no Python-level way to influence
`res_map.json`/`UiResourceManager` (grepped the full `wot-src` tree for
both names — **zero matches**, confirming §7b/§7d's suspicion that
Gameface's resource catalog is entirely native/boot-time, not
reachable from Python at all), cross-checked our own captured
`python.log` timestamps from every session so far: `[WULF]
UiResourceManager: parse resources from gui/unbound/res_map.json`
consistently logs at ~08:19:51 in this session's boot sequence, while
`Mod package '...' loaded` consistently logs ~2 seconds *later*
(~08:19:53). **The Gameface resource catalog is parsed before the mods
folder is even scanned.** Even setting aside "is it safe/legitimate to
ship a replacement `res_map.json`" (very risky either way — it's a
single ~1000-entry manifest every screen in the game depends on), it
would likely be **too late** by the time a mod's files are visible,
independent of that risk. This closes mechanism A (§7b) — not just
"risky," actually not workable via any legitimate mod-loading path
found so far.

**But while checking the equivalent question for Scaleform** (how does
a *new* Scaleform view/movie alias get registered — the "unresearched"
item from §7a's original three-way fork), found the opposite answer:
`gui/Scaleform/framework/factories.py`, class `EntitiesFactories`:
```python
class EntitiesFactories(object):
    def __init__(self, factories):
        self.__settings = {}   # plain Python dict, not a native/compiled catalog
        ...
    def addSettings(self, settings):
        ...
        self.__settings[alias] = settings   # live registration, callable at runtime
        return alias
```
`ViewFactory.validate()` (same file) requires `settings.url` (a
resource path to a `.swf`, resolved the same `ResMgr`-backed way §7e's
F7 test just confirmed works for mod-shipped files) and `settings.clazz`
(a Python `View` subclass) and `settings.alias`. **This is an ordinary,
mutable, Python-side registry — not a boot-time-cached native
manifest.** A mod's own init code calling `g_entitiesFactories.addSettings(...)`
with our own alias + our own `.swf` path + our own Python view class
is, as far as the registration mechanism goes, the same shape as
anything else in this codebase — no different in kind from registering
a key handler.

**This reverses the §7b recommendation.** The actual remaining
requirement for "new Scaleform content" was never the registration
step (now confirmed straightforward) — it's authoring the `.swf`
itself (Flex SDK/`mxmlc` + AS3, real but bounded, learnable tooling,
unlike Gameface's dead ends which are hard blockers no amount of
effort gets past). Between the two original candidates: DevilsUI is
now conclusively ruled out (native, boot-time, and its one dynamic
escape hatch is server-authoritative and off-limits); Scaleform's
registration mechanism is confirmed live and scriptable, leaving only
a real-but-solvable tooling gap (Flex SDK setup, AS3 authoring) as the
open item. See chat for the updated recommendation to the user.

## 7g. Session 1 — Flex/AS3 toolchain setup, in progress

User confirmed: commit to the Scaleform/Flex path (§7f). Starting
environment setup.

- **Apache Flex SDK 4.16.1** downloaded and extracted to
  `../flex-sdk/sdk/` (sibling to this project, shared workspace tool —
  not project content, not committed anywhere). `mxmlc -version` runs
  successfully (`Version 4.16.1 build 20171115`) against this
  machine's Java 26 — no compatibility issue hit yet.
- **WG's own compiled component-library `.swc` files extracted
  directly from the installed client** to `../flex-sdk/wg-swc/`:
  `gui_base-1.0-SNAPSHOT.swc`, `gui_lobby-1.0-SNAPSHOT.swc`,
  `common-1.0-SNAPSHOT.swc`, `common_i18n_library-1.0-SNAPSHOT.swc`,
  `base_app-1.0-SNAPSHOT.swc`, `gui_battle-1.0-SNAPSHOT.swc`,
  `lobby.swc`, `battle.swc` (from `gui-part1..4.pkg`, same zip-read
  technique as §7b/§7d). These are almost certainly the compiled form
  of the `sources-as3/{base_app,gui_base,gui_lobby,common,lobby,...}`
  directory names already seen in `wot-src` — i.e. WG's real UI
  framework/component classes, usable as `mxmlc -library-path` inputs
  so new code can extend their actual base classes instead of
  reimplementing everything from scratch. Not yet actually tried in a
  real compile.
- **Open item: `playerglobal.swc` is missing.** Apache Flex SDK
  doesn't bundle it (historically an Adobe-licensed separate download,
  and Adobe Flash Player itself has been discontinued since 2020 —
  unclear yet where a working copy is still obtainable in 2026).
  Checked one real WG `.swf` directly (`gui/flash/lobby.swf` from
  `gui-part4.pkg`): SWF header signature `CWS` (zlib-compressed),
  **SWF file-format version byte = 11**, which historically corresponds
  to roughly the Flash Player 10.1 API level — WoT's Scaleform GFx
  runtime (Autodesk's own AS3-compatible VM, not real Adobe Flash
  Player) is known to only support a frozen, somewhat old AS3/SWF
  feature subset, consistent with this being an intentional old
  target rather than a stale asset. Need the right `playerglobal.swc`
  version and matching `-target-player`/`-swf-version` mxmlc flags to
  produce GFx-compatible bytecode — launched background research into
  what the existing WoT Scaleform-modding community (mods like
  XVM have shipped custom Scaleform UI for years) actually uses, since
  guessing this wrong risks silent failures or crashes rather than a
  clean compiler error. Not back yet as of this writing.

## 7h. Session 1 — toolchain fully solved via a real public example, Phase 2 prototype built

Found the missing pieces by locating a real, complete, currently-shipping
WoT mod's public source: `github.com/wotstat/wotstat-positions`
(`as3/` subfolder). This closed every remaining open item from §7g in
one pass:

- **`playerglobal.swc` and `flash.swc`**: not obtainable from Adobe
  (discontinued), but `wotstat-positions` ships working copies
  directly in their repo (`as3/libs/`). Copied into
  `../flex-sdk/wg-swc/` equivalents / this project's own `as3/libs/`.
- **Correct compiler config**: their `build-config.xml` — externalize
  all 8 WG `.swc` files (§7g) plus `playerglobal.swc`/`flash.swc` via
  `<external-library-path>` (never `<library-path>` — the game already
  has these classes at runtime; linking them in causes conflicts),
  `<target-player>17.0</target-player>`, `<swf-version>17</swf-version>`.
  One gotcha found empirically: their file uses `<royale-config>` as
  the root element, but our own **plain Apache Flex 4.16.1** `mxmlc`
  (not Apache Royale) rejects that — needs `<flex-config>` instead,
  and rejects their `<compiler><targets><target>SWF</target></targets></compiler>`
  block entirely (a Royale-only, multi-target concept; plain Flex only
  ever outputs SWF, no such config knob exists). Both fixed in this
  project's own `as3/build-config.xml`; **the externalized SWC list
  and target-player/swf-version values are otherwise copied verbatim from
  their working config, not re-derived**, per the research's own advice
  not to trust older Scaleform-era version assumptions (SWF version 11
  seen on WG's own shipped `.swf`, §7g, turned out to be a red herring
  — 17 is correct and works, presumably because the actual bytecode
  emitted only uses old-enough opcodes regardless of the nominal target
  version, since everything class-level is externally linked anyway).
- **Real minimal AS3 view class pattern**, copied structurally from
  their `EnterLicenseWindow.as`: extend
  `net.wg.infrastructure.base.AbstractWindowView`, override
  `onPopulate()`, set `width`/`height`/`window.title`, `addChild(...)`
  for content. `py_*`-prefixed public `Function` properties are how
  AS3 calls back into Python — confirms the `py_*`/`as_*` naming
  convention seen throughout decompiled Python (§7a-§7f) is the real,
  actual bidirectional binding convention, not just an internal WG
  naming quirk.
- **Real Python-side registration pattern**, copied structurally from
  their `EnterLicenseWindow.py`: a `setup()` function builds a
  `ViewSettings(alias, PyViewClass, "<swfFilename>", WindowLayer.TOP_WINDOW,
  None, ScopeTemplates.VIEW_SCOPE)` and calls
  `g_entitiesFactories.addSettings(settings)` — this is the exact
  `EntitiesFactories.addSettings` mechanism identified from decompiled
  source in §7f, now with the *correct* real-world calling convention
  (constructor arg order, `ScopeTemplates`, `WindowLayer`) instead of
  guessed. A separate `show()` function does
  `dependency.instance(IAppLoader).getApp().loadView(SFViewLoadParams(alias))`
  to actually trigger opening it.
- **Real build/packaging integration**, from their repo-root
  `build.sh` (not `as3/build.sh`): AS3 gets compiled as a separate
  step, output `.swf` copied into `res/gui/flash/` before the main
  packaging zip runs, and the zip step explicitly includes `*.swf`.
  Structurally almost identical to this project's own `build.sh`
  (same `MOD_NAME`/version/debug-mode perl-templating pattern) —
  applied the same shape here rather than reinventing it.

### Applied: real Phase 2 prototype built and compiled

- `as3/build-config.xml`, `as3/libs/*.swc` (8 WG libs from this
  machine's own client, §7g, plus `playerglobal.swc`/`flash.swc` from
  `wotstat-positions`), `as3/src/camoViewer/CamoViewerTestWindow.as` —
  a minimal `AbstractWindowView` subclass (dark background box + a
  text label, no interactivity yet).
- Compiled successfully:
  `mxmlc -load-config+=build-config.xml --output=bin/silhouette.camoViewer.CamoViewerTestWindow.swf ...`
  → real 1409-byte SWF, header confirms `CWS` (zlib-compressed),
  version byte 17 (matches config).
- `camoViewer/CamoViewerTestWindow.py` — Python-side view class +
  `setup()`/`show()`, structurally copied from the wotstat example.
- `CamoViewer.py`: calls `CamoViewerTestWindow.setup()` at mod init
  (registers the alias unconditionally, matching the reference
  pattern), F8 calls `CamoViewerTestWindow.show()`.
- `build.sh`: added an AS3 compile step (invokes this machine's
  `../flex-sdk/sdk/bin/mxmlc` by absolute path — not portable to
  another machine without adjusting this, acceptable for now since the
  whole script is already this-machine-specific) before the existing
  Python/packaging steps, copies compiled `.swf` into
  `build/res/gui/flash/`, and the zip step now includes `*.swf`.
- Full pipeline verified end-to-end at build time: `./build.sh -v
  0.0.6 -d` → AS3 compiles → Python compiles → final `.wotmod`
  contains all 11 expected files including the real `.swf`. **Not yet
  confirmed live in-game** — that's the next test (F8), which is also
  the first real test of whether `AbstractWindowView`/`ViewSettings`/
  `g_entitiesFactories` actually work end-to-end in this exact client
  build, since everything so far in this section is "should work per a
  real reference example," not yet "confirmed working here."

## 7i. Session 1 — F8 CONFIRMED LIVE: Phase 2 feasibility fully proven

**Success, first try, no errors.** `python.log` shows the full expected
chain firing cleanly (`loadView` → `Loading window: SFWindow(...
viewKey=ViewKey[alias=CAMO_VIEWER_TEST_WINDOW...` →
`gui.impl.pub.main_window.MainWindow` auto-attached as parent), and the
user's screenshot confirms it rendered correctly over the Garage
screen: a real window with **native WG chrome** (title bar reading
"camo-viewer Phase 2 test", a working close/X button) that we never
had to build ourselves — `AbstractWindowView` provided it automatically,
matching the base game's own window styling for free, as hoped.

**This fully closes out the core Phase 1/2 feasibility question this
entire session has been chasing.** Confirmed end-to-end in this exact
client build (`2.3.1.1505`), not just "should work per a reference
elsewhere":
- Flex SDK 4.16.1 (plain Apache Flex, not Royale) + WG's own extracted
  `.swc` component libraries compile real, loadable Scaleform content.
- `EntitiesFactories.addSettings()` + `ViewSettings` really is a live,
  runtime-scriptable registration point, not native/boot-time like
  Gameface's catalog turned out to be.
- The mod-overlay system delivers the compiled `.swf` correctly
  (`res/gui/flash/...`, same as any other WG-shipped movie).
- `AbstractWindowView` gives real native-looking chrome for free —
  directly relevant to `CONCEPT.md`'s "should look similar to the
  vehicle carousel" goal.

**What's proven vs. what's still ahead**: this confirms the
*mechanism* end-to-end (compile → register → load → render), using
throwaway placeholder content (a static text label). Phase 3 is now
about building the *real* content — an actual multi-row item grid, wired
to the real Camo/2D Styles item data (`CustomizationCarouselDataProvider`,
§7a), styled to resemble the vehicle carousel's expanded grid, with
real click-to-select behavior — not about re-proving the mechanism
works, which is now a settled question.

## 7j. Session 1 — Phase 3 first increment: real gating + real grid, built (not yet live-tested)

User direction: proceed to Phase 3, and **the mod must only react to
Space while the Customization screen's Camo/2D Styles tabs are open**
— Space is already used by the vehicle carousel in normal Garage view
(the reference behavior this whole project is based on), so this mod
must not interfere with that anywhere else.

**Screen/tab detection approach**: rather than guessing at global
state, hook the real `CustomizationBottomPanel` class's lifecycle
directly, using the same monkey-patch technique a real shipping mod
already uses for exactly this kind of problem (`OverrideLib.py`,
vendored from `wotstat-positions`, §7h's source — a decorator-based
`registerEvent(cls, methodName)` that wraps an existing method to also
fire our own handler, without replacing the original behavior).

- `CustomizationHook.py` (new): hooks
  `CustomizationBottomPanel._populate`/`_dispose` (screen
  open/close) and the private `_CustomizationBottomPanel__onTabChanged`
  (fires with the new `tabIndex` as an argument — directly gives us
  current-tab tracking with no need to reach into the panel's private
  `__ctx` state). `isActive()` is `True` only when the panel exists
  *and* the current tab is `CAMOUFLAGES` or `STYLES_2D`
  (`CustomizationTabs`, from `gui.Scaleform.daapi.view.lobby.customization.shared`,
  confirmed real in Phase 1 §7a). `getCurrentItems()` reads
  `panel.carouselItems` (public property, confirmed in Phase 1 —
  `self._carouselDP.collection`, already-loaded intCD list for the
  current tab) and resolves each to a display name via
  `panel.service.getItemByCD(intCD).userName` — **`.userName` is a
  guess** based on common convention elsewhere in this codebase, not
  yet confirmed against the real `GUIItem`/`Customization` class for
  this build; wrapped in `try/except` with an intCD-string fallback so
  a wrong guess degrades to ugly-but-functional rather than crashing.
- **Real grid window**: `CamoGridWindow.py`/`.as` (new) — a second
  compiled Scaleform view alongside the Phase 2 test window, following
  the exact same `AbstractWindowView` + `ViewSettings`/
  `g_entitiesFactories.addSettings` pattern (§7h), but now actually
  accepts data: Python passes `items` via `ctx` into the view's
  `__init__` (same convention as the reference `EnterLicenseWindow`),
  then pushes it to AS3 in `_populate` via
  `self.flashObject.as_setItems(items)` — this specific push-after-populate
  convention (`self.flashObject.as_X(...)`) is copied from
  `MinimapOverlay.py`, the other real reference example, since it's
  the one that actually demonstrates ongoing Python→AS3 data pushes
  (the simpler `EnterLicenseWindow` example only ever went AS3→Python).
  AS3 side lays out a plain manual grid (fixed column count, computed
  row/col per index) of dark boxes with a name label each — no icons
  yet, text-only, to prove real data end-to-end before adding art.
- `CamoViewer.py`: **F9** manually triggers the grid with fake
  placeholder data (18 fake items) regardless of screen/tab — a
  standalone debug entry point for iterating on the AS3 layout without
  needing to navigate to the real screen each time. **Space** is now
  wired for real, but gated: only calls
  `CamoGridWindow.show(CustomizationHook.getCurrentItems())` when
  `CustomizationHook.isActive()` is true; does nothing otherwise (in
  particular, does nothing in normal Garage view, where Space should
  keep doing only its existing vehicle-carousel-expand job, entirely
  unaffected — our `InputHandler.g_instance.onKeyUp` hook is
  non-exclusive/additive, per `AGENTS.md`'s `+=` pattern, so it was
  never capable of *blocking* the game's own Space handling in the
  first place; the gating is purely about *us* staying silent, not
  about preventing interference the mechanism couldn't have caused
  anyway).

**Build verified, not yet live-tested.** `./build.sh -v 0.0.7 -d`
compiled both `.as` files cleanly and packaged both `.swf`s correctly.
Untested unknowns going into the next live check: whether
`_CustomizationBottomPanel__onTabChanged`'s name-mangled name is
exactly right (Python name-mangling is mechanical and should be
reliable, but this is the first time this project has hooked a
double-underscore private method), whether `.userName` is the correct
attribute, and whether the whole hook fires at all the first time the
Customization screen is actually opened.

## 7k. Session 1 — Phase 3 first increment CONFIRMED LIVE: real data, real gating, working first try

`python.log` + user screenshot confirm everything worked, no crashes,
no fallback paths hit:
- `CustomizationHook: panel populated` fired on opening Customization.
- `CustomizationHook: tab changed to 7, active=True` — tab index `7`
  is whichever of `CAMOUFLAGES`/`STYLES_2D` the user opened first;
  gating logic correctly recognized it as active.
- `CamoGridWindow: loading view with 174 items` /
  `populated with 174 items` — **`panel.service.getItemByCD(intCD).userName`
  guess from §7j was correct**, no exceptions, no intCD-string
  fallbacks visible in the rendered grid (screenshot shows real names:
  "German Assault", "Black Widow", "Ranger", "Made in Germany", etc.).
- Space did nothing when not on the right tab/screen (implied by no
  errors and no unwanted window — not explicitly re-tested this round
  but the gating logic itself hasn't changed since being written).

**Real, immediate usability problem visible in the screenshot, not a
mechanism failure**: 174 items at 6 columns × 96px cells produces a
grid far taller than the screen (~29 rows) with **no scrolling** — the
window is simply cut off at the bottom, most items unreachable. This
is the clear next fix, ahead of icons/styling/click-select, since it's
the difference between "functional" and "cannot actually browse most
of the tab's items" — arguably worse than the strip it's meant to
replace, in current form.

## 7l. Session 1 — scrolling added via WG's real `ScrollPane` component

Found `net.wg.gui.components.controls.ScrollPane` (`gui_base`, real
decompiled AS3 in `sources-as3`) — a genuine, reusable clipped-viewport
component: set `.width`/`.height` for the fixed visible area, assign
any `DisplayObject` to `.target` as the scrollable content, mouse-wheel
scrolling wired in automatically (`onTargetMouseWheelHandler` on both
`background` and `target`). `getContentHeight()` just reads
`target.height`, which Flash computes automatically from a plain
`Sprite`'s children bounds — no extra bookkeeping needed on our side.

**Applied, first attempt FAILED live**: used
`App.utils.classFactory.getComponent('ScrollPane', ScrollPane, {...})`,
same call shape as the reference's `TextInput`/`SoundButton`. Live
error:
```
[Scaleform] object with "ScrollPane" linkage is not a component from library!
[Scaleform] object with "ScrollPane" linkage can't cast to [class ScrollPane]
TypeError: Error #2007: Parameter child must be non-null.
```
**Root cause, understood not just patched**: `classFactory.getComponent`
resolves its string name against Flash Library **symbol linkage** —
real for `TextInput`/`SoundButton`/`ButtonNormal` because those are
skinned visual components with actual exported MovieClip symbols in
WG's compiled library. `ScrollPane` (per the real `.as` source read
before writing this) is pure logic — no embedded skin/graphics, just
draws a plain background/mask in code — so it was never registered
under a library symbol at all; nothing for `classFactory` to find.
**Fix**: instantiate directly (`new ScrollPane()`), set
`x`/`y`/`width`/`height` as plain property assignments,
`addChild(scrollPane)` — bypassing the symbol-lookup factory entirely,
which is fine since `ScrollPane extends UIComponentEx` and its CLIK
component lifecycle (`configUI()`/`draw()`) should initialize
normally off `ADDED_TO_STAGE`, independent of how the instance was
created. Recompiled clean (2117 bytes). **General lesson for future
AS3 work in this project**: `classFactory.getComponent(name, ...)` is
for skinned/visual widgets with real library symbols; plain
logic/behavior classes (no skin) should just be `new`'d directly —
don't assume every WG framework class goes through the factory just
because one example (`EnterLicenseWindow`) used it for its own
(visual) components. Not yet re-confirmed live.

## 7m. Session 1 — ScrollPane abandoned, native `scrollRect` used instead

Live retest of §7l's `new ScrollPane()` fix: the `classFactory`
linkage error was gone, and **clipping actually worked correctly**
(screenshot showed exactly 5 rows visible, cleanly cut off at the
window edge, confirming the mask/viewport sizing was right) — but a
new error appeared every draw:
```
TypeError: Error #1009: Cannot access a property or method of a null object reference.
	at net.wg.gui.components.controls::ScrollPane/applyScrollBarUpdating()
```
**Root cause**: re-reading `applyScrollBarUpdating()` (§7l's own
quoted source) shows it unconditionally calls
`this.scrollBar.setScrollProperties(...)` with no null guard —
`ScrollPane` requires a real `IScrollBar` object assigned via its
`.scrollBar` setter to function at all, it's not designed to work
scrollbar-less even though mouse-wheel nudging exists independently of
that. Getting a real, properly-skinned scrollbar working would mean
chasing the same kind of classFactory-linkage question all over again
for a *different* component, unverified.

**Decision: dropped `ScrollPane` entirely**, switched to plain native
Flash `DisplayObject.scrollRect` (a standard, non-Scaleform-specific
API — clips a display object to a `Rectangle`, no external component
or linkage dependency at all) plus a manual
`MouseEvent.MOUSE_WHEEL` listener adjusting the rect's `y` and
reassigning `content.scrollRect` (required — the `scrollRect` getter
returns a copy, not a live reference, so mutating a fetched rect
in-place does nothing without reassigning it back). Fully removes the
dependency on any WG framework component for this specific piece —
more code we own directly, less unverified surface area. Recompiled
clean (2345 bytes). Not yet re-confirmed live.

## 7n. Session 1 — scrolling bug found via debug logging: `scrollRect` changes what `.height` reports

The wheel listener placement fix (§7m follow-up: attach directly to
`bg`/`content` instead of the outer window, matching `ScrollPane`'s
own pattern) **worked** — added a `py_log` AS3→Python debug callback
and confirmed live: wheel events fire correctly, `event.delta` values
look sane (±3/±6/±9 per notch, standard mouse wheel granularity).
**But scrolling still didn't move anything**, and the debug log
explained exactly why:
```
wheel event, delta=9, scrollY=0, maxScroll=0, contentHeight=480
```
`content.height` was reporting **480 — exactly `VIEWPORT_HEIGHT`**,
not the true ~2784px (29 rows × 96px) of actual content. **Root
cause**: this is a known, documented Flash gotcha, not a GFx quirk —
once a `scrollRect` is applied to a `DisplayObject`, its `.width`/
`.height` getters report the **scrollRect's** dimensions, not the
unclipped content bounds. §7m's fix used `content.height` to compute
`maxScroll`, which was silently always `0` from the moment
`scrollRect` was first applied in `onPopulate()`. Lesson for this
project: don't rely on `.height`/`.width` on any `DisplayObject` that
has `scrollRect` applied — track real content extent explicitly.

**Fix**: added a `contentHeight:Number` instance var, computed
directly from known layout math in `as_setItems`
(`Math.ceil(items.length / COLUMNS) * CELL_SIZE`) instead of ever
reading `content.height`. Recompiled clean (2495 bytes). Not yet
re-confirmed live — third attempt at this specific bug, each one
narrowed by a concrete piece of new evidence (linkage error → null
scrollbar error → this debug-logged height value) rather than
guessing blind each time.

**CONFIRMED LIVE (v0.0.12): scrolling works.** User confirmed after
this fix. The real-data grid with working scroll is now a genuinely
usable (if still unstyled, text-only, no click-to-select) feature.

## 7o. Session 1 — click-to-select added (not yet live-tested)

- AS3: cells switched from `Shape` to `Sprite` (`Shape` can't receive
  mouse events at all — not an `InteractiveObject` — this would have
  silently eaten any click-handling attempt). Each cell stores its
  `intCD` as a dynamic property (`cell['intCD'] = ...`), a shared
  `onCellClick` handler reads it back via `event.currentTarget` —
  avoids the classic AS3/loop-closure bug of one shared handler
  capturing the wrong loop-iteration's item. Added hover
  color-swap (`MOUSE_OVER`/`MOUSE_OUT`) as a cheap, directly-related
  usability addition (visual affordance that cells are clickable) —
  not scope creep, just finishing the interaction this increment adds.
  `label.mouseEnabled = false` so the text doesn't steal the click
  from its parent cell.
- Python: `CustomizationHook.getPanel()` added (small public accessor
  for the module's already-tracked `_panel`, keeping the module
  boundary clean rather than reaching into a private var from
  `CamoGridWindow.py`). `CamoGridWindow.py`'s new `py_selectItem(intCD)`
  calls the real, confirmed-real (Phase 1, `customization_bottom_panel.py`)
  `panel.onSelectItem(index, intCD, progressionLevel)` — `index` is
  read from the method's own source but never actually used in its
  body, so any value is fine; `progressionLevel=-1` is a guess based
  on the `-1`-as-"no value" sentinel convention used elsewhere in this
  codebase (e.g. `SelectedItem`'s defaults) for non-progressive items,
  not yet confirmed correct for this build. Grid window closes itself
  after a successful selection (matches expected UX: pick something,
  see it applied, don't have to manually close).

**Live test #1 failed**: `ReferenceError: Error #1056: Cannot create
property intCD on flash.display::Sprite` — wrong assumption that
`Sprite` is a dynamic class (true in ActionScript 2, **not** true for
`flash.display.Sprite` under strict AS3/Flex compilation — it's
sealed). **Fix**: added `GridCell.as`, a tiny subclass
(`class GridCell extends Sprite { public var intCD:Number; }`) with a
real typed field instead of a bolted-on dynamic property — cleaner
than the alternative (a `Dictionary` mapping cell→intCD) and avoids
the whole dynamic-vs-sealed question entirely. Recompiled clean (2944
bytes, mxmlc auto-discovered the new file from the existing
`source-path`).

**Live test #2 (v0.0.14) failed differently**: cell click fired
correctly, `py_selectItem` got called with the right `intCD` value —
but a deep exception inside WG's own
`getTypeOfCompactDescr`/`ItemsRequester.getItemByCD`:
`TypeError: 'float' object has no attribute '__getitem__'`. Root
cause: AS3's `Number` type (used for `GridCell.intCD`) crosses the
Python↔AS3 bridge as a Python `float` (`78924.0`, not `78924`), and
WG's internal compact-descriptor code assumes a real Python `int`.
**Fix applied on the Python side** (`CamoGridWindow.py`,
`py_selectItem`): `intCD = int(intCD)` before use — simpler and safer
than trying to force a different AS3-side numeric type across the
bridge.

**CONFIRMED LIVE (v0.0.15): click-to-select works** —
`item selected, intCD=124748` logged clean, no exception, user
confirmed the selection actually applied. Click-to-select is done.

**Follow-up user request, applied in v0.0.16**: don't auto-close the
grid after a selection — removed the `self.onWindowClose()` call in
`py_selectItem` so users can click through several camos/styles in a
row to compare, closing manually (X button) when done. **Confirmed
live** — user tested and reported it working, with a screenshot
showing multi-select-compare in action (2D style visibly applied to
the tank, grid still open).

## 7p. Session 1 — window repositioning (v0.0.17) + Esc-to-close discovered for free

Second follow-up from the same screenshot: user asked to move the
window to the side since the default centered position obstructs the
tank view. Found the real mechanism while reading
`AbstractWindowView.as` (`gui_base`, real decompiled source) for
something else: `as_setGeometry(x, y, width, height)` is a public AS3
method already provided by the base class specifically for overriding
the default centering behavior (`DefaultWindowGeometry` →
`StoredWindowGeometry(x,y,w,h)` once called). Applied: `onPopulate()`
now calls `as_setGeometry(20, 100, width, height)` right after sizing
— pins the window to the left edge, clear of the vehicle (which sits
center/right in the Customization camera). Compiled clean (3019
bytes).

**Live test: still wrong** — user's screenshot showed the left-pinned
window overlapping the season selector panel (Summer Map/Winter/
Desert), which also lives on the left edge. Left-anchoring was the
wrong instinct — the left edge isn't actually empty in this screen.
**Fix**: right-anchored instead, computed dynamically from
`App.appWidth` (a real global, confirmed used the same way inside
`AbstractWindowView.as` itself, e.g. `App.appWidth -
_loc1_.horizontalOffset` in `checkAppBounds()` — package-less/global
class, no import needed, confirmed by a clean compile) rather than a
hardcoded pixel guess tied to one screen resolution:
`as_setGeometry(App.appWidth - width - WINDOW_MARGIN_RIGHT, WINDOW_Y, ...)`.
The right side of this screen is empty hangar background in every
screenshot seen so far, no competing UI panel there. Compiled clean
(3061 bytes). **CONFIRMED LIVE** — user reported everything working
with the right-anchored position.

**Bonus finding, no code change needed**: `AbstractWindowView`'s
`handleInput`/`canCloseFromInputDetails` already wires `Esc` to close
the window natively — confirms `TASKS.md`'s open "toggle collapse"
question at least partly resolved for free: Esc already works as a
close affordance alongside the X button, no code required. Space-to-
toggle-close specifically (re-pressing the same key that opened it) is
still unimplemented, but Esc covers the more universal "get me out of
here" case already.

## 7q. Session 1 — real icons added (not yet live-tested)

Found the real icon-resolution logic WG's own vanilla strip uses,
`customization_item_vo.py`'s `__getIcon(item, progressionLevel)`:
```python
useIcon = item.itemTypeID in (GUI_ITEM_TYPE.CAMOUFLAGE, GUI_ITEM_TYPE.PROJECTION_DECAL)
icon = item.icon if useIcon else item.iconUrl
```
So the two tabs this project targets use **different** icon sources:
Camouflage → `item.icon` (a local resource path), 2D Styles →
`item.iconUrl` (a different property, `Url`-suffixed — likely a full
URL, possibly CDN-hosted, unconfirmed). Applied the same branch in
`CustomizationHook.getCurrentItems()`.

**Rendering side**: found `net.wg.gui.components.controls.Image`
(`gui_base`, real decompiled source) — a self-contained image widget
(`App.imageMgr`-backed loading, own internal `Bitmap`, no external
skin/scrollbar-style dependency the way `ScrollPane` needed). Simple
API: `new Image()`, set `.source = <path or url>`. Added one per cell,
above the name label (icon top ~56px, name below). **This is a
different loading mechanism from the CEF `WebBrowser` component
§7e/§7f found blocked by a server-authoritative whitelist** — `Image`/
`App.imageMgr` is Scaleform-native asset loading, not the embedded
browser, so that specific restriction shouldn't apply here, but this
is not yet confirmed either way for the `iconUrl` (2D Styles) case
specifically if it turns out to be a genuine external URL.

Compiled clean (3214 bytes). **Not yet live-tested — and this one
specifically needs checking on *both* target tabs separately**, since
they exercise two different, independently-unverified code paths
(`item.icon` for Camouflage vs. `item.iconUrl` for 2D Styles).

## 7r. Session 1 — icons: data confirmed real, first render attempt was invisible

Debug log confirmed `item.icon` values are real, well-formed resource
paths, e.g. `img://gui/maps/vehicles/styles/generic_custom_look_2_germany.png`
— the `icon`/`iconUrl` branch logic (§7q) is correct, this isn't a
data problem. **But live test showed the grid rendering with no
images at all**, text-only, same as before — no exceptions in
`python.log` either, a silent rendering failure, not a crash.

**Hypothesis, not yet independently confirmed but consistent with
`Image.as`'s own source**: `Image` loads asynchronously (`App.imageMgr`
→ `IImageData`, `Event.COMPLETE` internally) — the code was setting
`icon.width`/`icon.height` **immediately** after construction, before
`.source` had any chance to load real bitmap data. Setting
`width`/`height` on a `Sprite` computes `scaleX`/`scaleY` from its
*current* bounds — on an empty, zero-content `Image` those bounds are
0, so the resulting scale is degenerate (likely 0 or `Infinity`),
silently breaking the later-loaded bitmap's visibility even though
loading itself may have succeeded.

**Fix**: `Image` dispatches its own `Event.CHANGE` when image data
updates (declared right on the class: `[Event(name="change",
type="flash.events.Event")]`) — moved the `width`/`height` assignment
into a `Event.CHANGE` listener instead of doing it eagerly, so sizing
only happens once real content exists to scale from. Compiled clean
(3308 bytes). Not yet re-tested live.

## 7s. Session 1 — icons CONFIRMED LIVE; applied-item highlight added

User confirmed icons render correctly after the `Event.CHANGE`-deferred
resize fix (§7r). Icons are done. Removed the temporary per-item debug
log (`CustomizationHook.getCurrentItems()`) now that it's served its
purpose.

**New increment**: highlight the currently-applied item, matching
vanilla strip behavior (a real usability gap, not just cosmetic — v1
had no way to tell what was already equipped while browsing).
`CustomizationHook.getCurrentItems()` now also returns `applied` per
item, computed from `panel._carouselDP.getAppliedItems()` (confirmed
real method from Phase 1 reading of `customization_carousel.py`,
`CustomizationCarouselDataProvider.getAppliedItems()`). AS3:
`GridCell` gained an `applied:Boolean` field; `drawCellBackground` now
draws a thicker gold border (`0xd9a441`, matching the orange/gold
accent color WG's own UI uses for selection state, e.g. the diamond
marker seen on the applied item in earlier screenshots) instead of the
default thin grey one when `cell.applied` is true — persists correctly
through hover state changes since both `onCellOver`/`onCellOut` now
read `cell.applied` each time rather than hardcoding the border.
Compiled clean (3459 bytes). Not yet tested live.

## 7t. Session 1 — stale-grid safety bug found live, auto-refresh-on-tab-change implemented

User's live test surfaced a real, meaningful bug, not just a UX gap:
switching Customization tabs while the grid window stayed open left
it showing the **previous** tab's items — user then clicked a stale
Camouflage item while the underlying context had already switched to
2D Styles mode, and `panel.onSelectItem(-1, intCD, -1)` blew up for
real inside WG's own code:
```
AttributeError: 'Camouflage' object has no attribute 'applyType'
AttributeError: 'Camouflage' object has no attribute 'isProgressionRequiredCanBeEdited'
WARNING: Wrong itemType: 30. Only styles could be installed in styled customization mode.
```
i.e. passing a camouflage `intCD` into style-mode selection logic.
This directly matches a request the user made in the same message
(auto-switch grid contents between tabs instead of close/reopen) —
implementing that also closes this safety hole, since the grid will
never hold stale-tab data long enough to click through it.

**Implemented**: `CustomizationHook.py` gained a small
listener-registry (`addTabChangeListener`/`removeTabChangeListener`),
fired from the existing `_populate`/`_dispose`/`__onTabChanged` hooks
(§7j) — decoupled on purpose, `CustomizationHook` has no dependency on
`CamoGridWindow`, only the reverse, avoiding a circular import.
`CamoGridWindow.py` subscribes in `_populate`, unsubscribes in
`_dispose` (guessed lifecycle method name, matching the confirmed-real
`CustomizationBottomPanel._dispose` convention rather than the
alternate `_destroy` convention seen in the `MinimapOverlay` reference
example — not yet independently confirmed for `AbstractWindowView`
specifically). On tab change: if the new tab is still one of ours
(Camo/2D Styles), refresh in place via the already-proven
`as_setItems()` push; otherwise auto-close the window. Iterating over
`list(_tabChangeListeners)` (a copy) in the fire loop deliberately
guards against the close-triggered unsubscribe mutating the list
mid-iteration.

**Also added**: a debug log of `getAppliedItems()`'s raw return value,
to diagnose the user's other report — the gold "currently applied"
border isn't visibly appearing. Not yet root-caused; the AS3-side
logic read back correctly on inspection, so the next data point needed
is whether `appliedItems` is actually non-empty and contains the
expected intCDs.

Compiled/verified locally, not yet live-tested.

## 7u. Session 1 — tab-switch auto-refresh CONFIRMED LIVE; applied-border mystery resolved (not a bug)

**Auto-refresh/auto-close on tab change: confirmed working correctly**
from the user's live log — switching to a non-grid tab (9) closed the
window; switching between Camo (7) and Styles (2) repeatedly refreshed
the same window in place with the right item count each time (174 vs
28), no errors. §7t's fix works as designed.

**Gold border mystery resolved — not a code bug.** Deeper diagnostic
logging showed `getAppliedItems()` returning exactly one real,
resolvable item: `intCD=3968572 name=Emblem of the Wehrmacht
itemTypeID=35`, **not any Camouflage or Style** — and the screenshot's
own right-side panel (`TOTAL / Total (0) / From the Depot (1) /
Cancel`) shows the user has been clicking through many grid items as
**staged/previewed selections that were never confirmed** (no "Apply
and Exit" click during testing). Conclusion:
`_carouselDP.getAppliedItems()` reflects the **committed/equipped**
outfit, not in-progress previews — for this test vehicle, in this
session, nothing in the Camo/2D-Style categories was ever actually
committed, only an Emblem from some earlier point. The gold-border
logic (§7s) is very likely correct as written; there was simply
nothing in-scope to highlight during this specific test. Removed the
now-answered diagnostic logging. **Not re-verified with a genuinely
committed item yet** (would need the user to click "Apply and Exit"
on a camo/style, then reopen the grid on that tab) — noted as the
concrete next check if this is worth confirming further, rather than
assumed fixed outright.

## 7v. Session 1 — Phase 5 started: favorites (not yet live-tested)

Moving into the explicitly-post-v1 backlog from `CONCEPT.md` — user's
original request from the start of this project. Persistence needed a
safe local mechanism, not WG's own `AccountSettings` (server-synced,
shared namespace with real game data — inappropriate for a mod to
write into). Found the right real precedent instead:
`wotstat-positions`' own `common/PlayerPrefs.py` — uses
`BigWorld.wg_getPreferencesFilePath()` (falling back to the older
`BigWorld.getPreferencesFilePath()` name) to find the real local
preferences directory, then creates a mod-namespaced subfolder
(`mods/<modid>/`) and stores each key as its own flat file. Purely
local, no server sync, no shared-namespace collision risk. Vendored
the same pattern as `utils/PlayerPrefs.py`, namespaced to
`mods/silhouette.camoViewer/`.

**Implemented**:
- `Favorites.py`: `isFavorite(intCD)`/`toggle(intCD)`, backed by one
  `PlayerPrefs` key (`favorites.json`) holding a JSON-encoded list,
  loaded lazily into an in-memory `set` and re-saved on every toggle.
  Untested assumption: the embedded Python 2.7 has a working `json`
  module (standard since 2.6, no reason to expect it's missing, but
  nothing in this project has used it yet either).
- `CustomizationHook.getCurrentItems()` now also returns `favorite`
  per item.
- AS3: a small star glyph (`★`/`☆`, plain Unicode text characters —
  no new asset needed) top-right of each cell, gold when favorited,
  muted grey outline when not. Click toggles instantly client-side
  (optimistic update from `py_toggleFavorite`'s return value) without
  waiting for a full grid refresh. Its own `MouseEvent.CLICK` listener
  calls `event.stopPropagation()` so starring an item doesn't also
  trigger the cell's main select action — required removing the
  cell-wide `mouseChildren = false` from §7o (that flag would have
  blocked the star from ever receiving its own clicks at all), and
  explicitly setting `icon.mouseEnabled = false` so the now-clickable
  icon area still passes clicks through to the cell's select handler
  rather than swallowing them itself.

Compiled clean both sides (AS3: 3890 bytes). Not yet live-tested —
first real test of `PlayerPrefs`/local file persistence in this
project, and of the star's independent-click-region interaction
working correctly alongside the existing whole-cell click handler.

## 7w. Session 1 — live test: applied-border confirmed working; stars invisible, switched to vector graphics

**Bonus confirmation, unprompted**: the same screenshot that showed
missing stars also showed the "Germany" cell with a real gold
`APPLIED_BORDER_COLOR` border — §7u's hypothesis was right, the
applied-highlight logic (§7s) works correctly once there's a genuinely
committed item; it just had nothing to highlight in the earlier test
session. No longer an open question.

**Stars: invisible, no errors logged.** Consistent with a font/glyph
problem rather than a crash: `★`/`☆` (Unicode `U+2605`/`U+2606`) are
unusual symbol-range characters, and Scaleform/GFx text rendering is
known to depend on embedded font glyph coverage rather than falling
back to arbitrary OS "device fonts" the way real Flash Player can —
plain ASCII item names render fine in the very same `TextField` class,
which narrows it specifically to font/glyph coverage, not some
`TextField`-wide breakage. **Fix**: replaced the glyph-based star with
a hand-drawn vector star (`Sprite.graphics`, 5-point star via
`Math.cos`/`sin` polygon math, `beginFill` when favorited vs.
`lineStyle`-only outline when not) — no font dependency at all, same
technique already proven reliable for the cell backgrounds themselves.
Also added an invisible larger hit-area rect under the star shape
(`beginFill(0x000000, 0)`, 18×18) since a thin 5-point outline alone
would be an unreliably small/oddly-shaped click target. Compiled clean
(4105 bytes). Not yet re-tested live.

## 7x. Session 1 — favorites CONFIRMED LIVE; contrast tweak

Vector star fix worked — user confirmed seeing stars, and the log
shows clean toggling: `Favorites: toggled intCD=70476 -> True` /
`-> False` alternating correctly across repeated clicks, matching
click-for-click. **Favorites star toggle + persistence: done and
working.** (Restart-survival specifically not yet independently
re-confirmed by the user, but the underlying mechanism — flat file
write per `PlayerPrefs.set`, same pattern as `wotstat-positions` — has
no reason to behave differently from any other file write.)

**Follow-up**: user asked for more contrast — the muted grey
unfavorited-outline color was likely too close to the dark cell
background. Brightened both colors
(`FAVORITE_ON_COLOR` gold → `0xffd23f`, `FAVORITE_OFF_COLOR` grey →
near-white `0xe5e9f0`), thickened the outline stroke (1.3 → 1.6), and
added a semi-transparent dark circular backing behind the star
(`0x000000` at 0.4 alpha) so it stays legible over bright icon
thumbnails too, not just the dark cell background — icons vary a lot
in brightness (screenshots show everything from near-white "Moon
Viewing" to very dark "Fan of Clan Tournaments"), so a single flat
outline color risked being invisible against a same-toned icon
regardless of which color was picked. Compiled clean (4134 bytes).
Not yet re-tested live.

## 7y. Session 1 — filters: Favorites + Season (not yet live-tested)

User asked for filtering "by favorites, colors, etc." Checked what
real, well-grounded categorical metadata is actually available on
`Camouflage`/`Customization` items (`c11n_items.py`,
`sources/res/scripts/client/gui/shared/gui_items/customization/`):
`item.season` is a real bitmask attribute
(`SeasonType.WINTER=1, SUMMER=2, DESERT=4, EVENT=8`, confirmed from
`common/items/components/c11n_constants.py`) — matches the exact
Summer/Winter/Desert categorization the base game's own Customization
screen already uses (visible in every screenshot this session, the
left-side panel). `item.palettes` also exists (real per-camo RGBA
color data) but using it for a true "color" filter needs real design
decisions not yet made (representative-color extraction, a swatch-
picker UI, color-distance matching) — deferred as a follow-up rather
than guessed at; season is the closest available *categorical* filter
that needed no new design decisions, so implemented that first.

**Implemented**:
- `CustomizationHook.getCurrentItems()` now also returns `season` per
  item (the raw bitmask).
- AS3: new `FilterButton.as` (small reusable toggle-look button,
  active/inactive styling) — a filter bar row above the grid:
  "Favorites" toggle + "All"/"Summer"/"Winter"/"Desert" season buttons
  (mutually exclusive, "All" clears the season filter). Filtering
  happens **entirely client-side in AS3** (`allItems` holds the full
  unfiltered set from Python, `applyFilters()` recomputes a `visible`
  subset and rebuilds the grid) — no Python round-trip needed per
  filter click, and toggling a star while "Favorites only" is active
  immediately re-filters so a just-unfavorited item disappears without
  needing to reopen the grid.
- Layout: added a 30px filter bar row, shrank the scrollable viewport
  by the same amount so total window height is unchanged (504px, same
  as before).

Compiled clean both sides (AS3: 5792 bytes). Not yet live-tested —
first real UI beyond the grid itself (buttons, mutually-exclusive
selection state, client-side re-filtering).

## 7z. Session 1 — season filter bugs reported live, diagnostics + tab-gating added

User's live test of the filter bar surfaced real problems, not just
polish:
- Filtering by Summer/Winter/Desert made some real camos disappear
  entirely (didn't show under any season button, only under "All") —
  matches a plausible `item.season` resolution bug: if it silently
  fails/returns 0 for some items (same shape as the earlier `.icon`
  resolution try/except), they'd never match `(season & filterBit) != 0`
  for any real season.
- **More serious**: clicking a filtered "Winter"/"Summer" item could
  trigger the game's own `Error: Unable to customize` toast — no
  Python traceback logged for it (unlike every other error this
  session, which showed full tracebacks), meaning this is likely a
  legitimate server/business-logic rejection, not a local exception —
  consistent with our season bucketing letting through items that
  aren't actually valid for the vehicle's current season context, if
  the underlying `item.season` data is unreliable.
- User also asked to hide the season filter entirely on the 2D Styles
  tab — it's a Camouflage-only concept, confusing/meaningless there
  (matches `CONCEPT.md`'s general v1 framing that Camo and Styles are
  two distinct categories, not asking to unify their filter surface).

**Applied**:
- `CustomizationHook.getCurrentItems()`: added debug logging of the
  first 10 items' resolved `season` values, to actually see what's
  coming back rather than guess further — same discipline as every
  other data-shaped bug this session (§7q/§7t/§7u).
- `CustomizationHook.isCamouflageTab()` (new) +
  `CamoGridWindow.as_showSeasonFilter(Boolean)` (new AS3 method) —
  called on initial populate and on every tab-change refresh, hides
  the season buttons (Favorites stays visible on both tabs) and resets
  to "All" if the filter was active when hidden, so it can't stay
  silently applied while invisible.

**Deliberately not yet touching the season-bucketing/validation logic
itself** — need the diagnostic log's real data first rather than
guessing a second fix blind, consistent with how every other bug this
session got solved (icon resolution, scroll height, applied-items,
etc. — each fixed from a concrete log line, never from a guess alone).

## 7aa. Session 1 — season data confirmed correct, not the bug

Diagnostic log came back clean: most camos are `season=15`
(`SeasonType.ALL` = WINTER|SUMMER|DESERT|EVENT, i.e. universal —
correctly show under every season filter, since
`15 & anyBit != 0`), a handful are genuinely single-season
(`Ambush summer`/`Large spots summer` → `season=2`, confirmed against
a real in-game tooltip too: "Camouflage Large spots winter" showed
`Element Characteristics: For winter map` matching our `season=1`
bucketing). **Season resolution and filter logic are correct, not
buggy** — the "some camo are absent" report was very likely just
filtering correctly narrowing the list (a Summer-only camo not
appearing under Winter is the intended behavior, not a bug). Removed
the now-answered diagnostic logging.

**"Unable to customize" still unexplained** — no traceback was ever
logged for it (unlike every other real bug this session), and the
user's own log showed several rapid repeated clicks on the same two
items within a couple seconds each time, which is a plausible
alternate explanation (a request race/duplicate, unrelated to season
data) now that season data itself is confirmed sound. Asked the user
to try a single deliberate click on a season-filtered item to see if
it reproduces cleanly before chasing this further — not assuming a
second bug exists without a repro, consistent with this session's
concrete-evidence-before-fix discipline.

## 7ab. Session 1 — generalized to all customization tabs (not yet live-tested)

User confirmed the earlier "Unable to customize" error doesn't
reproduce on a single deliberate click — closes out §7z/§7aa, was
very likely a rapid-repeat-click race, not a season-data bug. Then
asked to generalize Space-grid support to every Customization tab.

**Surgical change**: the whole pipeline
(`getCurrentItems()`/icon resolution/`onSelectItem`) was already
written generically off `panel.carouselItems`/`panel.service`, nothing
Camo/Style-specific baked in except the already-scoped season filter
(`isCamouflageTab()`, untouched, still Camo-only per the user's own
earlier request). Only change needed: `GRID_TABS` widened from the
2-tuple to the real WG constant `CustomizationTabs.ALL` — `(STYLES_3D,
STYLES_2D, ATTACHMENTS, PAINTS, CAMOUFLAGES, PROJECTION_DECALS,
EMBLEMS, INSCRIPTIONS, MODIFICATIONS)`, deliberately excludes
`STAT_TRACKERS` (not part of WG's own "ALL" grouping, and not visible
in the tab bar in any screenshot this session) — reusing WG's own
canonical tab-set rather than hand-enumerating matches exactly what
the visible tab bar shows (3D Styles/2D Styles/3D Attachments/Paints/
Camouflage/Decals/Emblems/Inscriptions/Effects).

**One real known-unknown flagged, not solved preemptively**: the
`ATTACHMENTS` (3D Attachments) tab has its own slot-selection concept
(`self.__ctx.mode.selectedSlot`) in vanilla's own carousel logic — our
`onSelectItem(-1, intCD, -1)` call has always ignored slot state
entirely (works fine for every tab tested so far, which don't need
one). Genuinely unknown whether attachment selection needs a slot
chosen first or behaves differently without our grid doing anything
special — not solved speculatively, flagged as the one tab worth
specifically checking once this is live.

Compiled/verified locally, not yet live-tested.

## 7ac. Session 1 — "used up elsewhere" items: investigated the confirm-dialog request, found the real fix is a filter default (not yet live-tested)

User's original ask ("remove style from another tank with approving
popup") led to real research rather than building a redundant dialog:
- Found the exact vanilla confirmation flow
  (`customization_cart_view.py`'s `__onBuy`): `containsVehicleBound(...)`
  triggers a real dialog (`DialogPresets.CUSTOMIZATION_INSTALL_BOUND`,
  `R.strings.dialogs.customization.buy_install_bound`) — but only at
  the **"Apply and Exit"/purchase-confirm step**, not at
  carousel-item-selection time. Since our grid only replaces
  *browsing*, still calling the exact same `panel.onSelectItem` vanilla
  itself uses, and never touches "Apply and Exit" at all, this
  confirmation should already fire automatically without any new code
  — didn't build a duplicate dialog system.
- User's follow-up revealed the REAL gap: vehicle-bound items
  currently installed elsewhere don't show in our grid **at all**.
  Root cause: `FilterTypes.USED_UP` (`customization_carousel.py`,
  Phase 1 finding) is a real, always-shared filter on the underlying
  `CustomizationCarouselDataProvider` — both our grid and the vanilla
  strip read the exact same `panel.carouselItems`, and by default
  (`applied=False`, `inverse=True` → `isEnabled()=True`) it hides
  anything `isItemUsedUp()` flags, unless the user manually opts in
  via a filter-popover checkbox we never exposed. Confirmed via the
  filter's own inverse-XOR logic (`isEnabled() = isApplied() ^
  isInverse`) — counterintuitively, `updateCarouselFilter(USED_UP,
  True)` is what *disables* the hiding criteria and reveals them.

**Applied**: `CustomizationHook.py` now forces this filter open
(`_revealUsedUpItems()`, remembering the original state) when the
Customization panel populates, and restores it
(`_restoreUsedUpFilter()`) when the panel disposes — matching vanilla's
own `__rebuildCarousel()` pattern (`invalidateFilteredItems()` +
`buildList()` + `refresh()`) so the change actually takes effect, not
just the internal flag. **This also affects the vanilla strip while
our mod is active** — a deliberate tradeoff (both views share the same
data provider, no way to show it in only one), and it's fully restored
on leaving the screen, so no lasting side effect.

**Also added, matching the user's second ask**: `getCurrentItems()`
now returns a real `usedUp` flag per item (`isItemUsedUp(item,
panel.service)`, the same real helper vanilla's own VO-building code
uses) — items already installed on THIS vehicle/outfit are correctly
excluded (only genuinely-elsewhere items are flagged). AS3: a small
"On another vehicle" caption in a warning-orange tone, shown only when
flagged — required growing `CELL_SIZE` (96→110) to fit the extra line
without cramming.

**Genuinely unverified going into the next test**: whether calling
`buildList()`/`invalidateFilteredItems()`/`refresh()` from
`onPanelPopulate` (which fires right after `CustomizationBottomPanel._populate()`
returns, but *before* vanilla's own deferred
`BigWorld.callback(0.0, ...)`-scheduled initial `__onTabChanged` call
that normally does the first build) works correctly this early in the
lifecycle, or races/conflicts with that deferred call. Wrapped in
try/except so a failure degrades to "used-up items stay hidden,
logged" rather than crashing, but not yet confirmed live either way.

## 7ad. Session 1 — used-up reveal: confirmed real regression, timing fix applied; selection itself still rejected (separate, legitimate finding)

Live test of v0.0.33 confirmed both halves:
- **Reveal worked**: item count went 174→276, and the screenshot even
  showed WG's own real "On other vehicles" tag on an unrelated rental
  item in the vanilla strip — independent confirmation this is a real
  game concept we're now correctly surfacing more of, not something
  invented.
- **Real regression, exactly the risk flagged going in**: ~250+
  `failed to resolve item/icon` log lines — never happened in any
  prior test. Item names/icons in the actual rendered grid still
  looked correct though, which narrows it: the exception is most
  likely happening at the *last* line inside the try block
  (`isItemUsedUp(...)`, the one genuinely new call this session),
  *after* `name`/`icon`/`season` had already been successfully
  assigned — Python doesn't roll back prior assignments when a later
  line in the same `try` throws, so the item still renders with mostly
  correct data despite the exception firing. Not fully confirmed
  (the log message was generic), so added `repr(sys.exc_info()[1])`
  to the log line for next time instead of re-guessing blind.
- **Fix applied**: `_revealUsedUpItems()` was being called
  synchronously inside `onPanelPopulate`, immediately after
  `_populate()` returns — but vanilla's *own* first carousel build is
  itself deferred via `BigWorld.callback(0.0, ...)` (confirmed, Phase
  1). Calling our rebuild synchronously meant we ran *before* that
  deferred initial build, almost certainly racing/interfering with
  whatever state it sets up. Changed to
  `BigWorld.callback(0.1, _revealUsedUpItems)` — deliberately
  `0.1`s, not `0.0`s, to land safely after vanilla's same-tick `0.0`
  callback rather than risk same-tick ordering ambiguity. Not yet
  re-tested live.

**Separate, legitimate finding — not a bug, a real business rule**:
clicking a revealed "used up elsewhere" item showed a clean, real game
error, `Unable to apply: Tenacious Grip is not in the inventory` — no
Python exception, no crash, just a proper rejection toast. This means
simply revealing these items isn't enough to let them be *selected*
via the simple `onSelectItem` path — they likely need a different
flow (an explicit "reassign from other vehicle" action) that vanilla's
own UI must expose somewhere we haven't found yet. **This also revises
§7ac's hypothesis**: the "Apply and Exit" confirmation dialog
(`containsVehicleBound`/`CUSTOMIZATION_INSTALL_BOUND`) can only ever
fire for items that make it into the purchase cart in the first
place — if `onSelectItem`/`_selectCommonItem` rejects a used-up item
immediately, that later confirmation step is never reached at all via
our simple grid-click path. Not yet investigated further — flagged as
the next open question if the user wants to pursue actually being able
to *select* these items, not just see them.

## 7ae. Session 1 — root cause confirmed exactly: dependency-injection decorator collision, fixed; grayed-out treatment added

The improved `repr(sys.exc_info()[1])` logging (§7ad) paid off
immediately — every failure was the exact same, precise error:
```
TypeError("isItemUsedUp() got multiple values for keyword argument 'service'",)
```
Re-checked the real source: `isItemUsedUp` carries
`@dependency.replace_none_kwargs(service=ICustomizationService)`
(`shared.py`) — a decorator that auto-injects a real service instance
as the `service` **keyword** when the caller doesn't supply one.
Calling it as `isItemUsedUp(item, _panel.service)` passed
`_panel.service` *positionally*, and the decorator's own injection
still tried to supply `service=` as a keyword on top of that,
colliding. **Fix**: call `isItemUsedUp(item)` with no second
argument at all — trust the decorator to inject the correct default
service (the same real singleton `_panel.service` would have
resolved to anyway). This is the third time this session a
`@dependency.replace_none_kwargs`-style decorator's exact calling
convention mattered — worth remembering as a recurring category of
mistake in this codebase, not a one-off.

Also added, per user request: cells where `usedUp` is true now render
at `alpha = 0.5` (whole cell dimmed — icon, name, badge together) as a
clear "unavailable right now" visual, on top of the existing "On
another vehicle" text label. Compiled clean (6092 bytes). Not yet
re-tested live.

**Still open, deliberately deferred**: showing *which specific
vehicle* has the item — needs iterating the player's whole garage and
checking each vehicle's outfit, a real research question not yet
investigated. Flagged to the user as a bigger follow-up rather than
folded into this fix.

## 7af. Session 1 — availability filter added (All / Available / On Other Vehicles)

Confirmed working (label + dimming), then asked for a third filter
dimension on top of Favorites/Season: item availability. Since
`usedUp` was already computed per item (§7ac), this was purely an AS3
UI addition, no new Python data needed. Added a second filter-bar row
("All Items" / "Available" / "On Other Vehicles", mutually exclusive,
same `FilterButton` component) — unlike the season row, this one is
**not** gated to the Camo tab, since `usedUp` is meaningful on every
tab. `FilterButton` gained an optional `width` constructor param
(defaulting to the existing 76px) since "On Other Vehicles" needed
more room than the original fixed width allowed. Filter bar grew to
two rows (`FILTER_BAR_HEIGHT` 30→60), window height unchanged overall
shape-wise (viewport shrinks to match). Compiled clean (6585 bytes).
Not yet live-tested.

## 7. New source, user-provided: `izeberg/wot-src`

User-supplied: <https://github.com/izeberg/wot-src> — a public
decompiled WoT source repo. Matches the same name already listed as
priority #4 in `_reference/wotstat-spotting-notes/NOTES.md` §4
("faster-updated alternative if [`StranikS-Scan/WorldOfTanks-Decompiled`]
lags a very recent patch") from the unrelated prior project — i.e.
this is independent confirmation it's a live, known-useful resource,
not a dead link. **Not yet checked against this project's exact build
(`2.3.1.1505`)** — first Phase 1 task should confirm which
branch/tag (if any) matches, the same way the other project pinned
`StranikS-Scan/WorldOfTanks-Decompiled` to branch `2.3.1_EU` for its
own client version before trusting it (see that project's §14). This
is the primary candidate source for answering the Scaleform-vs-DevilsUI
question and locating the Customization screen's real view/plugin
class names.

## 8. Known non-findings / things NOT to reuse from the old notes

`_reference/wotstat-spotting-notes/NOTES.md` is about a different
feature domain (3D world-space vehicle geometry/rendering via
`DebugDrawer`, matrix transforms, `BigWorld` entity/appearance APIs)
and none of its camo/spotting-specific conclusions transfer to this
2D screen-space UI project. Its *general* WoT-modding infrastructure
findings (build/packaging pipeline shape, general `BigWorld`
familiarity) are fine background reading, already reflected in §2-§3
above via the cleaner `wotstat-vegetation` source directly rather than
that document's secondhand description of it.
