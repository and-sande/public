import PyAutoIt

autoit = PyAutoIt.autoit()

# Activate Adobe Acrobat Reader window
autoit.win_activate("[CLASS:AcrobatSDIWindow]")

# Wait for the window to be active
autoit.win_wait_active("[CLASS:AcrobatSDIWindow]", 10)

# Click on the "File" menu
autoit.control_click("[CLASS:AcrobatSDIWindow]", "Menu", "File")

# Wait a bit for the menu to open
autoit.sleep(1000)

# Click on the "Open..." menu item
autoit.send("o")  # Assuming 'o' is the shortcut key for "Open"
