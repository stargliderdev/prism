import datetime
import glob
import os
import subprocess

def run_silent(command):
    toto = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = toto.stdout.readlines()


batch = '''pyinstaller -n prism.exe --noconfirm --icon=logos.ico --log-level=INFO --clean --onefile -w main.py '''

run_silent(batch)

print('Deleting ver files')
path_to_build = 'z:\\source\\logos6\\dist\\'

fileList = glob.glob(path_to_build + '*.ver')
# Iterate over the list of filepaths & remove each file.
for filePath in fileList:
    try:
        os.remove(filePath)
    except:
        print("Error while deleting file : ", filePath)
file_name_version = datetime.datetime.now().strftime("%d_%m_%Y-%H_%M")
fo = open(path_to_build + file_name_version + '.ver', "w")
fo.write("version " + file_name_version)

# Close opend file
fo.close()

