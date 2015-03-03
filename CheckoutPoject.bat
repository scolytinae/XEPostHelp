@echo off

set SVN_CMD="C:\Program Files\TortoiseSVN\bin\svn.exe"

set DEFAULT_PROJ_DIR=ProjectDir

set PROJ_DIR=%1
if not exist "%PROJ_DIR%" (
  set PROJ_DIR=%DEFAULT_PROJ_DIR%
)
set PROJ_BRANCHES=%PROJ_DIR%\branches
set PROJ_TRUNK=%PROJ_DIR%\trunk
set PROJ_PROJMAKER=%PROJ_DIR%\ProjectMaker


set SVN_MAIN=http://svn.path/to/project
set SVN_BRANCHES=%SVN_MAIN%/branches/my-branches
set SVN_TRUNK=%SVN_MAIN%/trunk
set SVN_PROJMAKER=%SVN_MAIN%/ProjectMaker

rem Checkout base empty folder
%SVN_CMD% checkout %SVN_MAIN% %PROJ_DIR% --depth empty

rem Checkout branches
%SVN_CMD% checkout %SVN_BRANCHES% %PROJ_BRANCHES%

rem Checout trunk
%SVN_CMD% checkout %SVN_TRUNK% %PROJ_TRUNK%

rem Checkout ProjectMaker
%SVN_CMD% checkout %SVN_PROJMAKER% %PROJ_PROJMAKER%