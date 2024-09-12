from pywinauto.application import Application
from pywinauto import Desktop
import time

app = Application(backend="uia").start('explorer.exe')

dlg = Desktop().window(title_re=".*Home.*")
dlg_f = dlg.wait('visible')

# Access the Windows Explorer window
dlg = Desktop(backend="uia").window(title_re=".*Home.*")
dlg_f = dlg.wait('visible')

# Simulate Alt + D to focus the address bar
dlg_f.type_keys('%d')  # %d simulates Alt + D
time.sleep(0.5)  # Give a moment for the address bar to focus

# Type the desired path
dlg_f.type_keys("C:\\Users\\", with_spaces=True)
dlg_f.type_keys('{ENTER}')  # Press Enter to navigateasfasf