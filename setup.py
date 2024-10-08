# Run [python setup.py build] in your command prompt to build the software
import sys
from cx_Freeze import setup, Executable

base = None
if (sys.platform == "win32"):
    base = "Win32GUI"

setup(
    name="Andhjan Mandal Data Analysis",
    version="1.0",
    author="SnHr1707",
    executables=[
        Executable(r"main.py location",
                   base=base,
                   icon=r"icon location",
                   shortcut_name="Andhjan Mandal Daya Analysis",
                   shortcut_dir="DesktopFolder")
    ]
)