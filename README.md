# camo-viewer

A [World of Tanks](https://worldoftanks.eu/) client mod that expands the
Customization screen's camo/style carousel into a full scrollable grid —
the same interaction the Garage's vehicle list already uses when you press
**Space**, brought to the Customization screen so browsing camouflages,
2D styles, decals, and everything else in that carousel doesn't mean
scrubbing left/right through a cramped strip one page at a time.

Mod ID: `silhouette.camoViewer`

## Features

- **Full grid view, one keypress.** Open any Customization tab (Camo, 2D
  Styles, Paints, Decals, Emblems, Inscriptions, Modifications, 3D
  Attachments, 3D Styles) and press **Space** to expand the carousel into
  a multi-row grid. Switching tabs while the grid is open refreshes it in
  place instead of closing it.
- **Click to apply.** Clicking a grid item applies it exactly the way
  clicking the vanilla carousel strip does — no separate selection step.
- **Applied-item highlight.** The item currently equipped is outlined.
- **Favorites.** Star any item to pin it; favorites persist locally
  between sessions.
- **Filters.** Favorites-only, season (Summer/Winter/Desert, shown only
  where it's meaningful — the Camo tab), and availability (all items /
  available only / on other vehicles).
- **Search by name**, filtered live as you type.
- **"On another vehicle" labels.** Items already installed elsewhere in
  your garage are shown (dimmed, with the real vehicle name(s)) instead of
  silently disappearing from the list.
- **Forward-compatibility logging.** The mod depends on a number of the
  client's internal, undocumented APIs. If a WoT update renames or removes
  something this mod hooks into, it logs exactly what broke instead of
  crashing outright, and disables only the affected feature.

## Installation

1. Grab the latest `silhouette.camoViewer_<version>.wotmod` (see
   [Building from source](#building-from-source) below — no prebuilt
   releases are currently published).
2. Copy it into your WoT installation's
   `World_of_Tanks/mods/<game version>/` folder (e.g. `mods/2.3.1.1/`).
   The version folder must match your client's exact game version.
3. Launch the game. Open a vehicle's **Customization** screen and press
   **Space** on any tab.

## Building from source

### Prerequisites

- Python 2 (matching WoT's client scripting environment — the build just
  needs `python2` on your `PATH` for `compileall`).
- [Apache Flex SDK](https://flex.apache.org/) 4.16.1 (plain Apache Flex,
  not Apache Royale) to compile the AS3 sources into `.swf` files.
- The WG-authored Scaleform component `.swc` libraries this project's AS3
  code links against (`as3/libs/*.swc`) — extracted from your own,
  legally-owned WoT client install (`res/packages/gui-part*.pkg`), plus
  Adobe's `playerglobal.swc`/`flash.swc` from the Flex SDK. **These are not
  included in this repository** and shouldn't be redistributed — you need
  to extract them yourself.

### Build

`build.sh` has the Flex SDK's `mxmlc` path hardcoded near the top — point
it at your own SDK location first. Then:

```bash
./build.sh -v 0.0.1 -d
```

- `-v` sets the mod version (must match the version embedded in the
  `.wotmod` filename and `meta.xml`).
- `-d` builds a debug build (verbose logging via the mod's `logger`
  module); omit it for a release build.

This compiles the AS3 views, byte-compiles the Python sources, and
packages everything into `silhouette.camoViewer_<version>.wotmod` (and an
identical `.mtmod` copy) in the project root.

## Project structure

```
as3/                    AS3 (Flex SDK) sources for the grid window's UI
  src/camoViewer/        CamoGridWindow, GridCell, FilterButton, ...
  libs/                  WG component .swc's + Flex playerglobal (not committed)
res/scripts/client/gui/mods/camoViewer/
  CamoViewer.py           mod entry point, key handling
  CustomizationHook.py    hooks into the vanilla Customization screen
  CamoGridWindow.py       Python side of the grid window
  Favorites.py            local favorites persistence
  utils/                  logging, compatibility checks, misc helpers
meta.xml                 .wotmod package metadata
build.sh                 build/package script
```

## Compatibility & limitations

This mod works by monkey-patching private methods on the client's own
Customization screen classes and reading internal, undocumented data
providers — there's no supported modding API for this. It's tested
against a specific client version (logged on load, see `utils/compat.py`)
and may break on future WoT updates; when a hook fails to attach, the mod
logs a clear `COMPATIBILITY BREAK` line rather than crashing.

Known limitation: the mod can show which other vehicle an item is
currently installed on, but it cannot remove/free it from that vehicle
without opening that vehicle's own Customization screen — WoT's client
only supports editing the outfit of whichever vehicle's screen is
currently open; a background removal was investigated and confirmed not
to work.

## Disclaimer

Unofficial, community-made mod. Not affiliated with or endorsed by
Wargaming. Use at your own risk and in line with Wargaming's mod policy
for your realm.
