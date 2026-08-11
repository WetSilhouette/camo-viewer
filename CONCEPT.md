# CONCEPT.md — camo-viewer (`silhouette.camoViewer`)

## One-line pitch

Bring the Garage's "press Space to expand the vehicle strip into a full
grid" interaction to the Customization screen's camo/style carousel, so
browsing camouflages and 2D styles doesn't mean scrubbing through a
cramped horizontal strip one page at a time.

## The reference behavior (already in the base game)

Garage → vehicle list at the bottom of the screen is normally a single
horizontal strip. Pressing **Space** expands it into a full-screen grid
("My Vehicles" view) — multiple rows, all vehicles visible at once,
same tiles, same click-to-select semantics, just more of them on screen
at a time. Confirmed from the attached screenshots (`Garage` idle view
vs. `Garage → My Vehicles` expanded view).

## The problem this mod solves

Garage → Customization (the paint roller icon) → tabs across the
bottom: 3D Styles, 2D Styles, 3D Attachments, Paints, Camouflage,
Decals, Emblems, Inscriptions, Effects. Each tab's items render in the
same kind of horizontal strip the vehicle list uses in its *collapsed*
state — but there is no equivalent expand action here. With some tabs
(Camouflage especially) holding many dozens of items, this means a lot
of left/right scrolling to compare options, per screenshot 3.

## v1 feature

- Reuse the **Space** key (confirmed unused/free while the
  Customization screen has focus) to toggle the bottom carousel on the
  **Camouflage** and **2D Styles** tabs between:
  - collapsed: today's existing horizontal strip (unchanged, untouched
    when the mod isn't toggled open)
  - expanded: a full grid view of that tab's items, visually and
    interactively consistent with the vehicle carousel's expanded
    state (multi-row grid, same tile size class, scrollable, same
    click-to-select/apply behavior as the existing strip)
- Space again (or the same close affordance the vehicle grid uses —
  TBD in research, see `TASKS.md` Phase 1) collapses back to the strip.
- No changes to *how* an item is applied once clicked — this mod only
  changes how items are *browsed*, not selection/apply logic.

## Explicitly out of scope for v1 (backlog, see `TASKS.md` Phase 5)

- **Favorites** — starring/pinning camos for quick access. Planned
  next, after v1 ships and the expand mechanic is proven solid.
- **Filters** — nation, vehicle-type compatibility, rarity/season,
  owned-only, search-by-name, etc. Planned after favorites.
- **Other tabs** — 3D Styles, 3D Attachments, Paints, Decals, Emblems,
  Inscriptions, Effects. Same expand mechanic could generalize to all
  of them later; v1 deliberately limits scope to the two most
  image-heavy, most-browsed tabs (Camo + 2D Styles) to prove the
  pattern before generalizing.
- Garage vehicle-carousel behavior itself is not touched at all — it
  already works; this mod only adds the equivalent for Customization.

## Non-goals

- No gameplay/stat changes, no reading of hidden or live combat state
  (unlike this workspace's other mod, `wotstat-spotting`, which reads
  vehicle geometry — this project is UI-only).
- Not a general Customization-screen redesign — only the carousel
  expand/collapse behavior.

## Open questions this concept currently depends on

These are unconfirmed and block real architecture decisions — see
`TASKS.md` Phase 1 and `NOTES.md`'s Open Questions section:

1. Is the Customization screen's carousel built with the old
   Scaleform/Flash UI stack, or the newer DevilsUI/Cohtml (HTML/JS)
   stack? This decides *everything* about how the mod hooks in —
   Python-side view patching vs. needing to ship/inject front-end
   assets. Not yet known for this client build (`2.3.1.1505`).
2. Is the vehicle carousel's expand/collapse view a reusable
   game-provided grid component, or something bespoke to the vehicle
   list that would need to be rebuilt for camo items?
3. Exact data source for "all items in the Camouflage/2D Styles tab
   for the currently selected vehicle" — same provider the strip
   already uses, ideally, rather than a second implementation.
