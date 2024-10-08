import sys
from cx_Freeze import setup, Executable

base = None
if (sys.platform == "win32"):
    base = "Win32GUI"

setup(
    name="Andhjan Mandal Data Analysis",
    version="1.0",
    author="Sneh Soni and Dhrumil Sheth",
    executables=[
        Executable(r"D:\NGO\Final\final.py",
                   base=base,
                   icon=r"D:\NGO\Final\icon.ico",
                   shortcut_name="Andhjan Mandal Daya Analysis",
                   shortcut_dir="DesktopFolder")
    ]
)