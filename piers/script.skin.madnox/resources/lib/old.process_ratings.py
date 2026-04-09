import xbmc

def calculate_and_set_ratings(params):
    # 1. Get Output Property Names from Params (with defaults for InfoDialog)
    # This was the breaking point - now it respects what the HUD requests
    out_tmdb = params.get("output_tmdb", "InfoDialog.TMDb.Percent")
    out_imdb = params.get("output_imdb", "InfoDialog.IMDb.Percent")
    out_user = params.get("output_user", "InfoDialog.User.Formatted")
    out_pct  = params.get("output_user_percent", "InfoDialog.User.Percent")
    
    # Filename/Star properties
    out_f5   = params.get("output_file_5star", "InfoDialog.User.File5Star")
    out_f10  = params.get("output_file_10star", "InfoDialog.User.File10Star")
    out_prec = params.get("output_file_precision", "InfoDialog.User.FilePrecision")
    out_star = params.get("output_star", "InfoDialog.User.StarValue") # Legacy trigger

    # 2. Bio/Person Protection
    # Explicitly block persons so we don't wipe out Movie memory properties
    if xbmc.getCondVisibility("String.IsEqual(ListItem.DBTYPE,person) | String.IsEqual(ListItem.DBTYPE,actor) | String.IsEqual(ListItem.Property(item.type),person)"):
        return

    # --- 3. Process TMDb Percentage ---
    tmdb = xbmc.getInfoLabel('ListItem.Property(TMDb_Rating)') or \
           xbmc.getInfoLabel('Window(Home).Property(TMDbHelper.ListItem.TMDb_Rating)') or \
           xbmc.getInfoLabel('ListItem.Rating(themoviedb)')
    
    if tmdb:
        try:
            val = int(round(float(tmdb) * 10))
            xbmc.executebuiltin(f"SetProperty({out_tmdb},{val},Home)")
        except: pass

    # --- 4. Process IMDb Percentage ---
    imdb = xbmc.getInfoLabel('Window(Home).Property(TMDbHelper.ListItem.IMDb_Rating)') or \
           xbmc.getInfoLabel('ListItem.Rating(imdb)')
    if imdb:
        try:
            val = int(round(float(imdb) * 10))
            xbmc.executebuiltin(f"SetProperty({out_imdb},{val},Home)")
        except: pass

    # --- 5. Process User/Star Ratings ---
    user = xbmc.getInfoLabel('ListItem.Property(TMDb_Rating)') or \
           xbmc.getInfoLabel('Window(Home).Property(TMDbHelper.ListItem.TMDb_Rating)') or \
           xbmc.getInfoLabel('ListItem.Rating(themoviedb)') or \
           xbmc.getInfoLabel('ListItem.Rating')

    if user:
        try:
            n = float(user)
            # Text (8.5)
            xbmc.executebuiltin(f"SetProperty({out_user},{round(n, 1):.1f},Home)")
            # Percent (85)
            xbmc.executebuiltin(f"SetProperty({out_pct},{int(round(n * 10))},Home)")
            # 5-Star File (rating4)
            xbmc.executebuiltin(f"SetProperty({out_f5},rating{int(round(n / 2.0))},Home)")
            # 10-Star File (9)
            xbmc.executebuiltin(f"SetProperty({out_f10},{int(round(n))},Home)")
            # Precision File (8.5)
            xbmc.executebuiltin(f"SetProperty({out_prec},{round(n, 1):.1f},Home)")
            # Star Value (Legacy/Group Trigger)
            xbmc.executebuiltin(f"SetProperty({out_star},{int(round(n / 2.0))},Home)")
        except: pass

def run(params):
    mode = params.get("mode", "calculate")
    
    if mode == 'monitor':
        # --- HUD MODE (Real-time polling) ---
        window_id = params.get("window_id", "98")
        last_dbid = None
        
        # ADDED: Instantiate Monitor to safely manage the while loop
        monitor = xbmc.Monitor() 
        
        # Loop while the HUD is open AND Kodi is not trying to shut down
        while xbmc.getCondVisibility(f"Window.IsVisible({window_id})") and not monitor.abortRequested():
            curr_dbid = xbmc.getInfoLabel("ListItem.DBID")
            
            # Check for changes and recalculate
            if curr_dbid != last_dbid:
                calculate_and_set_ratings(params)
                last_dbid = curr_dbid
            
            # REPLACED xbmc.sleep(450) with waitForAbort(0.45 seconds)
            # This sleeps for 450ms, but instantly breaks the sleep if Kodi starts closing.
            if monitor.waitForAbort(0.45):
                break 
            
    else:
        # --- ONE-SHOT MODE (Movie Info) ---
        xbmc.sleep(450)
        calculate_and_set_ratings(params)
        
        #xbmc.executebuiltin("SetFocus(50)")
