@echo off
echo Building Child Growth Analyzer...

rem Clean previous build
rmdir /s /q build dist

rem Build executable
pyinstaller child_growth_analyzer.spec

rem Sign the executable (using self-signed certificate)
signtool sign /f "ChildGrowthAnalyzer.pfx" /p YourPassword /tr http://timestamp.digicert.com /td sha256 /fd sha256 "dist\ChildGrowthAnalyzer.exe"

echo Build complete!
pause 