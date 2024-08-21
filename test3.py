from pywinauto.application import Application
from pywinauto import Desktop
import time
from pywinauto import Application, findwindows
import pyautogui

# Start Adobe Acrobat Reader DC
# app = Application(backend="uia").start(r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE")

# # Wait for the application to fully load
# time.sleep(5)
# Connect to the window using the handle
# app = Application(backend="win32").connect(handle=592626)

# # Access the main window
# main_window = app.window(handle=592626)

# # Print the control identifiers of the main window
# main_window.print_control_identifiers()

# Search for an image of the button or text you want to click
button_location = pyautogui.locateOnScreen('maximize.png')

if button_location:
    pyautogui.click(button_location)
else:
    print("Button not found on the screen.")