cls
echo build exe
python setup_cx.py install
echo copy files
xcopy Z:\source\logos6\img\*.png c:\prism\img\ /E/Y
xcopy Z:\source\logos6\build\exe.win-amd64-3.7\* c:\prism\ /E/Y
copy *.ini c:\logos6

echo O.K.