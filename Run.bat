echo off

dir /s /b *.bin > out.txt
set /p x= <out.txt
echo %x%
FINDSTR /R /N "^.*" out.txt | FIND /C ":" > lines.txt
set /p lines= <lines.txt

IF %lines% GTR 1 goto :ERROR
del out.txt
del lines.txt
BL_Master_App_L5_V1.exe %x%
goto :DONE

:ERROR
echo "There are more than 1 .bin file in the directory, please leave the only .bin that will be flashed....."
pause
goto :DONE

:DONE
del out.txt
del lines.txt