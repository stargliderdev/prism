from cx_Freeze import setup, Executable
import os, sys

# os.environ['TCL_LIBRARY'] = "C:\\Python37\\tcl\\tcl8.6"
# os.environ['TK_LIBRARY'] = "C:\\Python37\\tcl\\tk8.6"
packages = ["smtplib", "ssl"]
PYTHON_INSTALL_DIR = os.path.dirname(sys.executable)

include_files = [
    os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'libcrypto-1_1.dll'),
    os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'libssl-1_1.dll')]
# os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'),
# os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll')]
# additional_mods = ['numpy.core._methods', 'numpy.lib.format',"matplotlib.backends.backend_tkagg"]

# build_exe_options = {"packages": ["errno", "os", "re", "stat", "subprocess","collections", "pprint","shutil", "humanize","pycallgraph"]}



targetDir = "./build/"

setup(name="prism",
      version="6.0",
      description="prism",
      options={'build_exe': {"include_files": include_files,"packages": ["queue","idna"]}},
      executables=[Executable("main.py", base="Win32GUI", targetName="prism.exe", icon='logos.ico')])
#       executables=[Executable("main.py",base=None, targetName="prism.exe", icon='logos.ico')])
