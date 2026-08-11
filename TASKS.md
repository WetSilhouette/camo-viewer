# TASKS.md — camo-viewer

Phased plan. Don't start Phase 0 until the user explicitly says to
write code — everything before that is research/confirmation, which
can start immediately.

---

## Phase 0 — Scaffolding — DONE

- [x] Create mod skeleton modeled on `../wotstat-vegetation` (see
      `AGENTS.md`): `res/scripts/client/gui/mods/mod_camoViewer.py` +
      `res/scripts/client/gui/mods/camoViewer/CamoViewer.py` package.
- [x] `meta.xml` with `<id>silhouette.camoViewer</id>`,
      `<version>{{VERSION}}</version>`, name/description.
- [x] `build.sh` adapted from `wotstat-vegetation`'s (kept the
      `DEBUG_MODE` templating too, same shape as the reference —
      useful for Phase 1/2 verbose logging).
- [x] Confirm `./build.sh -v <n> -d` produces a loadable `.wotmod`,
      install to the local client's `mods/2.3.1.1/`, confirm it loads
      with no errors in `python.log`. Hit and fixed a real bug along
      the way (`DEBUG_MODE` string-concat crash on init — see
      `NOTES.md` §6); confirmed clean load at v0.0.2:
      `[CAMO-VIEWER] loaded, version 0.0.2, debug=True`, no traceback.

## Phase 1 — Research: how the Customization carousel actually works

This is the real unknown blocking any real design decision — see
`CONCEPT.md`'s open questions. Session 1 used a local clone of
`izeberg/wot-src` (branch `EU`) at `_reference/wot-src-eu/` — see
`NOTES.md` §7a for full findings and sources.

- [x] Determine whether the Customization screen (Camouflage/2D Styles
      tabs) is Scaleform or DevilsUI. **Answered: Scaleform/DAAPI**,
      confirmed directly from source
      (`CustomizationBottomPanel(CustomizationBottomPanelMeta)`,
      `CustomizationCarouselDataProvider(SortableDAAPIDataProvider)`).
      Also answered for the vehicle carousel (also Scaleform,
      `TankCarousel(TankCarouselMeta)`) — corrects an earlier wrong
      guess that it might be DevilsUI. See `NOTES.md` §7a.
- [x] Find the Python-side view/data-provider for the Camo/2D Styles
      carousels. **Answered**:
      `gui/Scaleform/daapi/view/lobby/customization/customization_bottom_panel.py`
      (view) +
      `gui/Scaleform/daapi/view/lobby/customization/customization_carousel.py`
      (data provider/cache). All items for the current tab are already
      loaded in memory (`itemCount`/`totalItemCount` already tracked);
      rich existing filter system (historic/inventory/applied/rarity/
      group/etc.) — see `NOTES.md` §7a for the full breakdown, directly
      useful for the Phase 5 filters backlog item.
- [x] Find how the vehicle carousel's Space expand/collapse works, to
      use as a template. **Answered, but not reusable as a template**:
      checked `TankCarouselMeta.py` (has `as_rowCountS`/
      `as_useExtendedCarouselS` — genuine multi-row capability baked
      into that *different* compiled `.swf`) and the equivalent
      `CustomizationBottomPanelMeta.py` (has **no** such method at
      all), plus the AS3 layout files for the Camo carousel
      specifically (no row/grid concept anywhere). **The Customization
      carousel's shipped Flash asset has zero latent grid/expand
      support to unlock** — this is not a "find the hidden flag"
      problem, it's a "this UI doesn't exist yet" problem. See
      `NOTES.md` §7a for the full chain of evidence.
- [x] Confirm Space is free — user confirmed from experience; also,
      Space's routing to the vehicle carousel's own expand doesn't
      appear to go through `command_mapping.xml` (battle-only commands
      there) or a literal `Keyboard.SPACE` in any carousel AS3 file —
      most likely just CLIK's generic "activate focused component"
      behavior, not a hangar-specific binding. Practical upshot: we
      don't need to replicate WG's exact routing, our own
      `InputHandler.g_instance.onKeyUp` hook (§3) is independent of it.
- [x] ~~Decision point: going with new DevilsUI (Gameface) content~~ —
      **superseded, see below.** This was the right call given what was
      known at the time, but two live tests + follow-up research
      changed the picture.
- [x] Live test #1 (v0.0.3): `showBrowserOverlayView` + `file://` URL
      → **blocked**, synthetic `Http code: 418`.
- [x] Live test #2 (v0.0.4): same, via local `127.0.0.1` HTTP server
      instead of `file://`, to rule out a `file://`-specific
      restriction → **also blocked**, identical error, and our own
      server never even logged receiving a request. Background
      research then traced this conclusively: WG's embedded browser
      enforces a **server-authoritative** URL whitelist
      (`igbWhitelist`, parsed from server-sent settings in native
      code, not present in Python or shipped XML anywhere). **Dead
      end, not being pursued further** — bypassing it would mean
      patching the client exe or spoofing server settings, which is
      Fair Play Policy territory, not a technical inconvenience. Full
      writeup: `NOTES.md` §7e.
- [x] Live test #3 (v0.0.5, F7): does the mod overlay reach arbitrary
      resource files (not just `.py`), a prerequisite for the
      DevilsUI/`res_map.json` idea regardless of the above → **yes,
      confirmed working** (`ResMgr.openSection` found our mod-shipped
      `.xml` file). Useful groundwork either way, but turned out not
      to save the DevilsUI path: cross-checking our own `python.log`
      timestamps across every session shows `UiResourceManager` parses
      `res_map.json` *before* the mods folder is even scanned — even
      if shipping a replacement manifest were safe (it isn't — one
      file, ~1000 entries, every screen depends on it), it would
      likely be read too late to matter. **DevilsUI path fully closed
      now, both candidate mechanisms from the original fork ruled
      out.** `NOTES.md` §7e/§7f.
- [x] **Recommendation reversed — Scaleform, not DevilsUI.** While
      confirming Gameface's registry has no Python hook, found the
      opposite is true for Scaleform:
      `gui/Scaleform/framework/factories.py`'s `EntitiesFactories` is a
      plain, mutable Python dict-backed registry
      (`addSettings(settings)`), not a boot-time native catalog — a mod
      can register a brand-new view alias + `.swf` path + Python view
      class at runtime, the same way this project already registers a
      key handler. The blocker was never the registration mechanism
      (now confirmed straightforward); it's authoring the `.swf` itself
      (Flex SDK/`mxmlc` + AS3) — real tooling this project doesn't have
      set up, but bounded/learnable, unlike DevilsUI's hard native
      walls. `NOTES.md` §7f has the full trace.
- [x] **User confirmed: commit to Flex/AS3.** Toolchain fully solved
      by finding a real, complete, currently-shipping mod's public
      source (`wotstat-positions`) — supplied the missing
      `playerglobal.swc`/`flash.swc` and the correct compiler config
      end-to-end. Full trace: `NOTES.md` §7h.
- [x] **Real `.swf` compiled successfully** (`as3/build-config.xml` +
      `as3/src/camoViewer/CamoViewerTestWindow.as`, a minimal
      `AbstractWindowView` subclass) — confirmed valid SWF output
      (header `CWS`, version 17). `build.sh` updated to compile AS3 as
      part of the normal build and package the `.swf` into the
      `.wotmod` alongside the `.pyc` files, same shape as the
      reference mod's own build script.
- [x] Python-side registration (`CamoViewerTestWindow.py`:
      `setup()`/`show()` via `ViewSettings`/`g_entitiesFactories.addSettings`/
      `SFViewLoadParams`, structurally copied from the working
      reference) wired to **F8** in `CamoViewer.py`. Built as v0.0.6,
      installed.
- [x] **CONFIRMED LIVE, first try, no errors.** `python.log` shows the
      full expected chain (`loadView` → `SFWindow` → auto-attached to
      `MainWindow`), and a real window rendered over the Garage screen
      with native WG chrome (title bar + working close button, for
      free from `AbstractWindowView`) — screenshot confirmed by user.
      **This is the core feasibility question this whole phase was
      chasing, and it's now settled**: compile → register → load →
      render all work end-to-end in this exact client. `NOTES.md` §7i.

### Phase 1 status: DONE. Phase 2 core mechanism: PROVEN.

Everything above is now resolved with live confirmation, not just
research. Ready to move to real Phase 3 work: actual grid content
wired to real item data, not a placeholder label.

## Phase 2 — Prototype: prove the hook point

The mechanism this phase exists to prove is now confirmed (see F8
above) — the items below were the original, more incremental plan for
getting there. Worth still doing the *tab-context-gating* one
specifically (so the eventual feature only activates on the right
tabs), but treat this section as "mostly superseded," not blocking —
proceed to Phase 3 for the real content.

- [ ] Minimal proof-of-concept: while on the Customization →
      Camouflage tab, pressing Space logs a confirmation line (no
      visual change yet). Confirms the input hook fires in the right
      screen/tab context and doesn't fire elsewhere (e.g. not on other
      tabs, not in Garage's own vehicle-list context).
- [ ] Confirm the mod can read the current tab's full item list (not
      just what's currently rendered in the strip) via whatever data
      provider Phase 1 found.

## Phase 3 — Full grid view (the actual feature)

- [x] **First increment CONFIRMED LIVE** (v0.0.7): real
      `CustomizationBottomPanel` lifecycle hook (`CustomizationHook.py`,
      via vendored `OverrideLib.py`'s `registerEvent` monkey-patch
      technique) correctly gates Space to only the Camo/2D-Styles tabs
      while Customization is open; real grid window
      (`CamoGridWindow.py`/`.as`) populated with the tab's actual live
      item data (174 real camo names rendered, e.g. "German Assault",
      "Black Widow"), no crashes, first try. `NOTES.md` §7j/§7k.
- [x] **Scrolling CONFIRMED LIVE** (v0.0.12). Took three live-tested
      attempts, each narrowed by concrete new evidence rather than
      guessing blind: (1) `ScrollPane` needs a real library-linked
      skin symbol, doesn't exist for that component, switched to
      manual `new ScrollPane()`; (2) `ScrollPane` also unconditionally
      needs a real scrollbar object internally or it crashes on every
      draw — dropped it entirely for plain native `scrollRect` +
      manual wheel handling instead; (3) wheel events weren't moving
      content because `content.height` silently reports the
      `scrollRect`'s size once one is applied, not the true unclipped
      content bounds (a real, documented Flash gotcha) — fixed by
      tracking content height explicitly from known layout math
      instead of trusting `.height`. Full trace: `NOTES.md` §7l-§7n.
      User confirmed working after the third fix.
- [x] **Icons CONFIRMED LIVE** (v0.0.21). Found the real WG icon-source
      logic (`customization_item_vo.py`'s `__getIcon`) — Camouflage
      uses `item.icon`, 2D Styles uses `item.iconUrl` (different
      properties), applied the same branch. Rendering via
      `net.wg.gui.components.controls.Image` (self-contained,
      `App.imageMgr`-backed, no scrollbar-style external dependency).
      One live-tested fix: `Image` loads asynchronously, resizing it
      immediately after construction (before real bitmap data existed)
      silently broke visibility — fixed by deferring resize to the
      component's own `Event.CHANGE`. `NOTES.md` §7q/§7r/§7s.
- [x] **Applied-item highlight added** (v0.0.25). Debugged a
      not-highlighting report down to root cause: `getAppliedItems()`
      correctly returned data, just not for the Camo/Style categories
      in that specific test session (only a committed Emblem, no
      committed camo/style yet — everything else clicked during
      testing was staged/previewed, never confirmed via "Apply and
      Exit"). Logic itself looks correct; genuinely untested against a
      real committed camo/style. `NOTES.md` §7s/§7u.
- [x] **Auto-refresh/auto-close on tab change CONFIRMED LIVE** (v0.0.23,
      user-requested): switching between Camo/2D-Styles tabs refreshes
      the open grid in place instead of requiring close/reopen;
      switching to any other tab auto-closes it. This also fixed a
      real bug the user's testing surfaced — a stale grid let a
      wrong-type item get clicked after the tab had already changed,
      crashing WG's own selection code (`'Camouflage' object has no
      attribute 'applyType'` etc.). `NOTES.md` §7t/§7u.
- [x] **Click-to-select CONFIRMED LIVE** (v0.0.15). Two live-tested
      fixes along the way: `Sprite` isn't dynamic in strict AS3 (added
      a tiny typed `GridCell` subclass instead of a bolted-on
      property), and AS3 `Number` crosses the bridge as Python `float`
      but WG's compact-descriptor code needs a real `int` (cast on the
      Python side in `py_selectItem`). Calls the real
      `panel.onSelectItem(-1, intCD, -1)` — confirmed working, user
      verified the selection actually applies. `NOTES.md` §7o.
      **User-requested follow-up (v0.0.16)**: don't auto-close the
      window after selecting, so multiple camos/styles can be clicked
      through in a row to compare — done, one-line change (removed the
      auto-close call).
- [ ] Implement collapse (Space again, or Esc, or click-outside — not
      yet decided) back to the normal strip. Currently only the
      window's native close (X) button works.
- [x] Scope check done at the gating level: `CustomizationHook.isActive()`
      only returns true for `CAMOUFLAGES`/`STYLES_2D` — confirmed
      live, tab 7 recognized correctly as active. Still needs the
      *negative* check (confirm Space does nothing, and no visual
      regression, on every other tab) — not yet explicitly re-tested
      since this logic was written.

## Phase 4 — Polish & regression check

- [ ] Verify vanilla horizontal-strip behavior is untouched when the
      mod is toggled closed (no visual/layout regressions on any tab,
      including the ones the mod doesn't touch).
- [ ] Verify across a few different vehicles (different nations, since
      Camouflage item counts/eligibility vary by vehicle) that the
      grid populates correctly.
- [ ] Verify switching tabs while the grid is expanded behaves
      sensibly (collapses automatically vs. carries the expanded state
      to the new tab — needs a decision, not yet made).

## Phase 5 — Backlog (explicitly post-v1, per `CONCEPT.md`)

- [x] **Favorites — star toggle + persistence CONFIRMED LIVE** (v0.0.28).
      Persistence: local per-mod preferences file via
      `BigWorld.wg_getPreferencesFilePath()`, same real pattern
      `wotstat-positions` uses — not WG's own `AccountSettings`
      (server-synced, wrong namespace for mod data). UI: originally a
      `★`/`☆` glyph, invisible in practice (Scaleform/GFx font glyph
      coverage doesn't include those Unicode symbols here) — switched
      to a hand-drawn vector star (no font dependency), then brightened
      colors + added a dark backing circle for contrast against both
      dark cell backgrounds and bright icon thumbnails per user
      feedback. Toggle click doesn't trigger the cell's own select
      action. `NOTES.md` §7v-§7x.
- [x] **Filters: Favorites-only + Season built** (v0.0.29, not yet
      live-tested). New filter bar above the grid (`FilterButton.as`):
      Favorites toggle + All/Summer/Winter/Desert (real `item.season`
      bitmask, matches the game's own categorization). Filtering is
      client-side in AS3, no Python round-trip per click; toggling a
      star while "Favorites only" is active re-filters immediately.
      `NOTES.md` §7y.
      **Still open**: a real "color" filter — deferred, needs design
      decisions (representative-color extraction from `item.palettes`,
      swatch UI, color-distance matching) not yet made. Also: rarity,
      owned-only, name search, nation, vehicle-type compatibility —
      research into what filter metadata is actually available per
      item from the existing data provider before any UI is designed.
- [x] **Generalized to all tabs** (v0.0.32, not yet live-tested):
      `GRID_TABS` widened to `CustomizationTabs.ALL` (WG's own
      constant — 3D/2D Styles, 3D Attachments, Paints, Camouflage,
      Decals, Emblems, Inscriptions, Effects; deliberately excludes
      Stat Trackers). Rest of the pipeline was already generic, no
      other code changes needed. Season filter stays Camo-only.
      **Flagged, not solved**: 3D Attachments has its own slot-
      selection concept in vanilla that our simple
      `onSelectItem(-1, intCD, -1)` call has never had to account for
      — genuinely unknown whether it behaves correctly there, worth
      specifically checking. `NOTES.md` §7ab.
