# XIVDeck for StreamController 
This project aims to support the [XIVDeck-Api](https://github.com/KazWolfe/XIVDeck) for the [StreamController](https://github.com/StreamController/StreamController).

## What's working
- Changing Volume
  - Muting
  - Setting to value
  - Increasing/Lowering
  - Realtime display of current values
- Execute Macros
- Play Emotes
- Change Gearsets/Glam
- Switch to Classes/Jobs
- Press hotbars
- General Actions
  - McGuffin
  - Emote
  - ExtraCommand
  - GearSet
  - GeneralAction
  - Glasses
  - MainCommand
  - Marker
  - Minion
  - Mount
  - FashionAccessory
  - FieldMarker
- Any /commands
- Download of original ingame icons
- A lot of descriptions

## What's missing
* Localization (data requested from the game will be in your FFXIV client's language)
* `Host` and `port` are hardcoded right now

## Usage
Set up the plugin as any other plugin.
Make sure to enable the icon and text as you desire for the selected actions in StreamController.
You could also just disable or overwrite them if there is too much text for your liking.

## Manual installation

Clone the repository into the `data/plugins/` directory of your StreamController installation.

For the flatpak installation that's probably: `~/.var/app/com.core447.StreamController/data/plugin/`

## Disclaimer
This plugin depends on a lot of external factors:

* Final Fantasy XIV Version
* Dalamud
* XIVDeck
* StreamController

So it might be possible to break at any moment. I will only support this software as long as I'm playing the game myself, since it needs a subscription.

If you happen to find a bug, please open an issue.
Some things are really hacky and didn't want to touch them again after I finally got it working.
Maybe I will clean up the mess someday (I won't lol).