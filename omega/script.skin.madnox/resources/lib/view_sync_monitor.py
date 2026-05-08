import xbmc
import xbmcgui

def run():
    home_window = xbmcgui.Window(10000)
    
    # SAFEGUARD 1: Prevent multiple loops from running if MyVideoNav reloads
    if home_window.getProperty('madnox_viewsync_running') == 'true':
        return
        
    home_window.setProperty('madnox_viewsync_running', 'true')
    monitor = xbmc.Monitor()
    last_path = ""

    try:
        # Wait a moment for the window to fully load before starting the loop
        if monitor.waitForAbort(1):
            return

        while not monitor.abortRequested():
            current_path = xbmc.getInfoLabel('Container.FolderPath')
            
            # Did the user just change folders/directories?
            if current_path != last_path:
                last_path = current_path
                
                # Check if we are INSIDE a movie set (Path = Sets DB, Content = Movies)
                in_set = xbmc.getCondVisibility('String.StartsWith(Container.FolderPath,videodb://movies/sets/) + Container.Content(movies)')
                
                if in_set:
                    global_view = xbmc.getInfoLabel('Skin.String(GlobalSetView)')
                    current_view = xbmc.getInfoLabel('Container.ViewmodeID')
                    
                    # If a global view is set, and it doesn't match current, force it
                    if global_view and current_view != global_view:
                        
                        # SAFEGUARD 2: Wait 50ms for Kodi's internal DB view to apply first, then overwrite it
                        xbmc.sleep(50)
                        
                        # Double check if view still needs forcing after sleep
                        if xbmc.getInfoLabel('Container.ViewmodeID') != global_view:
                            xbmc.executebuiltin('Container.SetViewMode({})'.format(global_view))
                    
                    # ==========================================
                    # NEW: FIX FOCUS ISSUE (REVISED)
                    # ==========================================
                    # Smart Wait: Give Kodi up to 1 second to fetch the DB and populate the list
                    for _ in range(10):
                        xbmc.sleep(100)
                        if xbmc.getCondVisibility('Container.HasFiles') or xbmc.getCondVisibility('Container.HasFolders'):
                            break
                    
                    # Use getCondVisibility (returns native True/False) instead of string matching
                    if xbmc.getCondVisibility('ListItem.IsParentFolder'):
                        # Try moving Down (Vertical lists)
                        xbmc.executebuiltin('Action(Down)')
                        xbmc.sleep(100)
                        
                        # If we are STILL on the parent folder, it must be a Horizontal list
                        if xbmc.getCondVisibility('ListItem.IsParentFolder'):
                            xbmc.executebuiltin('Action(Right)')
            
            # Check 4 times a second (snappy response without hitting CPU)
            if monitor.waitForAbort(0.25):
                break
    
    finally:
        # Clear the lock when Kodi shuts down
        home_window.clearProperty('madnox_viewsync_running')