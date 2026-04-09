import xbmc
import os
from xml.etree import ElementTree

# --- SCRIPT CONFIGURATION ---
SCRIPT_NAME = "[Madnox Template]"
TEMPLATE_FILENAME = 'settings_template.xml'

def run(params=None):
    # --- SCRIPT START ---
    xbmc.log(f"{SCRIPT_NAME} Apply Template Script: INITIALIZING.", level=xbmc.LOGINFO)

    try:
        # Construct the full path to the settings template file
        # Note: settings_template.xml must be in the same folder as this script (resources/lib)
        template_file_path = os.path.join(os.path.dirname(__file__), TEMPLATE_FILENAME)
        
        # --- DIAGNOSTIC 1: Check if the template file exists ---
        if not os.path.exists(template_file_path):
            xbmc.log(f"{SCRIPT_NAME} FATAL ERROR: Template file not found at '{template_file_path}'. Aborting.", level=xbmc.LOGERROR)
            xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
            xbmc.executebuiltin('Notification(Template Error, Could not find settings_template.xml, 5000)')
            xbmc.executebuiltin('Dialog.Ok("Template Error", "Could not find the settings_template.xml file.")')
            return
        
        xbmc.log(f"{SCRIPT_NAME} Found template file: {template_file_path}", level=xbmc.LOGINFO)

        # Open and parse the XML template file
        tree = ElementTree.parse(template_file_path)
        root = tree.getroot()
        settings_list = root.findall('setting')

        # --- DIAGNOSTIC 2: Report how many settings were found ---
        settings_count = len(settings_list)
        if settings_count == 0:
            xbmc.log(f"{SCRIPT_NAME} WARNING: Found 0 settings in the template file. Nothing to apply.", level=xbmc.LOGWARNING)
            xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
            xbmc.executebuiltin('Notification(Template Warning, No settings found in template., 5000)')
            return
        else:
            xbmc.log(f"{SCRIPT_NAME} Found {settings_count} settings to process. Starting loop...", level=xbmc.LOGINFO)

        # Loop through every <setting> tag in the file
        for i, setting in enumerate(settings_list):
            setting_id = setting.get('id')
            setting_type = setting.get('type')
            setting_value = setting.text if setting.text is not None else ''

            if not setting_id or not setting_type:
                xbmc.log(f"{SCRIPT_NAME} SKIPPING setting #{i+1} due to missing id or type.", level=xbmc.LOGWARNING)
                continue

            # Construct the correct Skin.Set... builtin function
            builtin_command = ''
            
            if setting_type == 'bool':
                builtin_command = f'Skin.SetBool({setting_id},{setting_value})'
            elif setting_type == 'string':
                builtin_command = f'Skin.SetString({setting_id},{setting_value})'
            elif setting_type == 'integer':
                builtin_command = f'Skin.SetInteger({setting_id},{setting_value})'
            
            # --- DIAGNOSTIC 3: Log the exact command before executing it ---
            if builtin_command:
                xbmc.log(f"{SCRIPT_NAME}[{(i+1):03d}/{settings_count}] Executing: {builtin_command}", level=xbmc.LOGINFO)
                xbmc.executebuiltin(builtin_command)
            else:
                xbmc.log(f"{SCRIPT_NAME}[{(i+1):03d}/{settings_count}] SKIPPING unsupported setting type '{setting_type}' for id '{setting_id}'.", level=xbmc.LOGWARNING)

        xbmc.log(f"{SCRIPT_NAME} Finished processing all {settings_count} settings.", level=xbmc.LOGINFO)

    except Exception as e:
        xbmc.log(f"{SCRIPT_NAME} SCRIPT CRASH: An unexpected error occurred. Error: {e}", level=xbmc.LOGERROR)
        xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
        xbmc.executebuiltin('Notification(Script Error, Failed to apply template settings., 5000)')
        xbmc.executebuiltin('Dialog.Ok("Script Error", "An error occurred while applying settings. Check the log for details.")')
        return

    # --- FINAL ACTIONS ---
    xbmc.log(f"{SCRIPT_NAME} Applying finalization settings...", level=xbmc.LOGINFO)

    # Set the flag to indicate the first run is complete
    xbmc.executebuiltin('Skin.SetBool(Madnox.Settings.Initialized)')
    xbmc.log(f"{SCRIPT_NAME} 'Madnox.Settings.Initialized' flag has been set.", level=xbmc.LOGINFO)

    # 1. Close the busy dialog that was opened by the button
    xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
    
    # 2. Explicitly close Custom Dialog 1107 so it vanishes immediately
    xbmc.executebuiltin('Dialog.Close(1107)')

    # 3. Trigger the skin reload
    xbmc.log(f"{SCRIPT_NAME} Reloading skin now.", level=xbmc.LOGINFO)
    xbmc.executebuiltin('ReloadSkin')

    # 4. Wait for Kodi to finish rebuilding the interface SAFELY.
    # We use a 3.5 second monitor wait. It pauses the script but yields to Kodi
    # so the UI can rebuild without causing a deadlock or crash.
    monitor = xbmc.Monitor()
    
    # .waitForAbort returns True ONLY if the user is exiting Kodi entirely.
    # So we say: "If Kodi is NOT shutting down, go ahead and show the notification"
    if not monitor.waitForAbort(3.5):
        # 5. NOW fire the success notification so it appears on the freshly loaded admin screen
        xbmc.executebuiltin('Notification(Settings Applied, Factory defaults restored successfully., 7000)')

    xbmc.log(f"{SCRIPT_NAME} Script finished.", level=xbmc.LOGINFO)