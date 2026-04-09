import xbmc
import xbmcgui
import xbmcaddon
import json

ADDON = xbmcaddon.Addon('script.skin.madnox')

# (addon_id, friendly_label)
OPTIONAL_EXTRAS = [
    ('script.cu.lrclyrics',                             'LRC Lyrics'),
    ('script.trakt',                                    'Trakt'),
    ('service.upnext',                                  'Up Next'),
    ('script.artistslideshow',                          'Artist Slideshow'),
    ('script.rss.editor',                               'RSS Editor'),
    ('plugin.library.node.editor',                      'Library Node Editor'),
    ('resource.images.weathericons.3d-coloured',        'Weather Icons (3D)'),
    ('resource.images.weatherfanart.multi',             'Weather Fanart'),
    ('resource.images.studios.white',                   'Studio Icons (White)'),
    ('resource.images.studios.coloured',                'Studio Icons (Colour)'),
    ('resource.images.recordlabels.white',              'Record Labels'),
    ('resource.images.languageflags.rounded',           'Language Flags'),
    ('resource.images.musicgenreicons.text',            'Music Genre Icons'),
    ('resource.images.moviecountryicons.flags',         'Country Icons'),
    ('script.artwork.dump',                             'Artwork Dump'),
    ('service.tvtunes',                                 'TV Tunes'),
    ('script.wikipedia',                                'Wikipedia'),
    ('script.preshowexperience',                        'Preshow Experience'),
    ('resource.images.moviegenreicons.filmstrip-hd.bw',     'Movie Genre Icons (B&W)'),
    ('resource.images.moviegenreicons.filmstrip-hd.colour',  'Movie Genre Icons (Colour)'),
]

def _set_addon_enabled(addon_id, enabled):
    xbmc.executeJSONRPC(json.dumps({
        "jsonrpc": "2.0",
        "method": "Addons.SetAddonEnabled",
        "params": {"addonid": addon_id, "enabled": enabled},
        "id": 1
    }))

def _wait_for_addon(addon_id, timeout_ms=15000):
    """Poll until addon appears in Kodi's addon table, or timeout."""
    elapsed = 0
    while elapsed < timeout_ms:
        result = json.loads(xbmc.executeJSONRPC(json.dumps({
            "jsonrpc": "2.0",
            "method": "Addons.GetAddonDetails",
            "params": {"addonid": addon_id},
            "id": 1
        })))
        if 'result' in result:
            return True
        xbmc.sleep(500)
        elapsed += 500
    return False

def run():
    dialog = xbmcgui.Dialog()

    if not dialog.yesno(
        'Madnox — Optional Extras',
        'Download optional extras in the background?\n\n'
        '[B]Flags, studio icons, genre art, lyrics, TV tunes[/B] and more.\n\n'
        'Everything installs [B]disabled[/B] — enable only what you want\n'
        'in [I]Settings → Addons → My Addons[/I].'
    ):
        # Declined — mark done so this never fires again
        xbmc.executebuiltin('Skin.SetBoolSetting(Madnox.ExtrasInstalled)')
        return

    progress = xbmcgui.DialogProgress()
    progress.create('Madnox Setup', 'Preparing optional extras...')

    total = len(OPTIONAL_EXTRAS)
    for i, (addon_id, label) in enumerate(OPTIONAL_EXTRAS):
        if progress.iscanceled():
            break

        pct = int((i / total) * 100)
        progress.update(pct, f'Installing: [B]{label}[/B]')

        # Skip if already present
        if xbmc.getCondVisibility(f'System.HasAddon({addon_id})'):
            continue

        xbmc.executebuiltin(f'InstallAddon({addon_id})', True)  # True = wait for dialog
        _wait_for_addon(addon_id)

        # Immediately disable — user opts in later
        _set_addon_enabled(addon_id, False)

    progress.update(100, 'Done!')
    xbmc.sleep(800)
    progress.close()

    # Permanent sentinel — Home.xml onload never fires again
    xbmc.executebuiltin('Skin.SetBoolSetting(Madnox.ExtrasInstalled)')

    dialog.ok(
        'Madnox Setup',
        'Optional extras installed and [B]disabled[/B].\n\n'
        'Enable what you want in [I]Settings → Addons → My Addons[/I].'
    )