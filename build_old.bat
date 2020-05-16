cls
pyinstaller --noconfirm --log-level=WARN ^
    -D -w ^
    --name logos6 ^
    --distpath c:\ ^
    -y ^
    main.py
copy *.png c:\logos6
copy *.ini c:\logos6

echo O.K.