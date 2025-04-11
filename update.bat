@echo off && title Install All Tweaker && mode con: cols=100 lines=25 && color a
chcp 65001
cls

REM Проверяем, установлен ли Python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Python уже установлен.
) else (
    echo Python не установлен. Загрузка и установка...
    
    REM Загружаем Python
    Utils\busybox wget https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe
    
    echo Устанавливаем Python без графического интерфейса
    python-3.12.3-amd64.exe /quiet InstallAllUsers=1 PrependPath=1
    
    REM Удаляем загруженный установочный файл
    del python-3.12.3-amd64.exe
    
    echo Python успешно установлен.
)

REM Загружаем All Tweaker с GitHub
REM del install.bat
Utils\aria2c https://github.com/scode18/All-Tweaker/raw/main/LICENSE
Utils\aria2c https://github.com/scode18/All-Tweaker/raw/main/tweaks.7z
Utils\aria2c https://github.com/scode18/All-Tweaker/raw/main/icon.ico
REM Utils\aria2c https://github.com/scode18/All-Tweaker/raw/main/install.bat
Utils\aria2c https://github.com/MotyaDev/MTweaker/raw/main/All.Tweaker.py
Utils\aria2c https://github.com/scode18/All-Tweaker/raw/main/cleaning.py
Utils\aria2c https://github.com/scode18/All-Tweaker/raw/main/settings.ini

REM Utils\\aria2c https://github.com/scode18/All-Tweaker/raw/main/All.Tweaker.Start.bat
cd Utils
aria2c https://github.com/scode18/All-Tweaker/raw/main/Utils/elevator.exe
aria2c https://github.com/scode18/All-Tweaker/raw/main/Utils/launcher.exe
cd ..

REM Распаковываем архив с помощью 7zip
Utils\7za x tweaks.7z

REM Удаляем загруженный архив
del tweaks.7z

REM Запускаем скрипт install.bat
install.bat

REM Создаем ярлык на рабочем столе с иконкой icon.ico
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = oWS.ExpandEnvironmentStrings("%USERPROFILE%\Desktop\All Tweaker.lnk") >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%CD%\All.Tweaker.Start.bat" >> CreateShortcut.vbs
echo oLink.IconLocation = "%CD%\icon.ico" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%CD%" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript CreateShortcut.vbs

REM Удаляем временный файл CreateShortcut.vbs
del CreateShortcut.vbs
