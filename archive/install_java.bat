@echo off
echo Installing Java for PDF table extraction...
echo.

REM Install OpenJDK 17 using winget
winget install Microsoft.OpenJDK.17 --accept-package-agreements --accept-source-agreements

echo.
echo Java installation complete!
echo.

REM Verify installation
echo Verifying Java installation...
java -version

echo.
echo If you see a Java version above, installation was successful!
echo You may need to restart your terminal for the PATH to update.
pause