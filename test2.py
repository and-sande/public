from pywinauto import Desktop

# List all open windows to check for the Adobe Acrobat window
windows = Desktop(backend="uia").windows()
for window in windows:
    print(f"Title: '{window.window_text()}', Class: '{window.class_name()}'")
