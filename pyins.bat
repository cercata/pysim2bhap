cd sim2bhap
pyinstaller Sim2bHap.py --add-data "C:\Program Files\Python310\Lib\site-packages\simconnect\*.json;./simconnect" --add-binary "C:\Program Files\Python310\Lib\site-packages\simconnect\SimConnect.dll;./simconnect" --hidden-import=simconnect -w -F -i ..\mini_plane.ico
copy /y *.tact dist
copy /y Sim2bHap.ini dist
cd ..
copy /y mini_plane.ico dist
copy /y README.md dist

pause