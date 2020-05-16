from cx_Freeze import setup, Executable
import os, sys

# packages = ["smtplib", "ssl"]
PYTHON_INSTALL_DIR = os.path.dirname(sys.executable)

# include_files = [
#     os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'libcrypto-1_1.dll'),
#     os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'libssl-1_1.dll')]

# targetDir = "./build/"

setup(name="prism",
      version="6.0",
      description="prism",
      options={'build_exe': {"include_files": include_files, "packages": ["queue", "idna"]}},
      executables=[Executable("main.py", base="Win32GUI", targetName="prism.exe", icon='logos.ico')])
#       executables=[Executable("main.py",base=None, targetName="prism.exe", icon='logos.ico')])


buildOptions = dict(
    packages=["queue", "idna"],
    excludes=[],
    # We can list binary includes here if our target environment is missing them.
    bin_includes=[],
    include_files=[os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'libcrypto-1_1.dll'), os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'libssl-1_1.dll')]
    
)

executables = [
    Executable(
        'main.py',
        base="Win32GUI",
        targetName='prism.exe',
        icon='logos.ico',
        copyDependentFiles=True,
        compress=True
    )
]

setup(
    name='Prism',
    version='6.1',
    description='Prism',
    options=dict(build_exe=buildOptions),
    executables=executables
)
