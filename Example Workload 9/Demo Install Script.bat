:: This file does [almost] nothing!
:: 
:: This is to demonstrate how the App Installer program may be used.
:: The App Installer will present the user with a list of options to
:: run; the options point to these batch scripts, which of course may be 
:: program installers, program/workload runners, or a myriad of other things.
::
:: These scripts each have their own folder so that other executables
:: or program files needed for them may be included together.
::

:: Turn off echoing of the commands themselves in the console
@echo off

set scriptVer=1.0


	:: Main work start

:: Print progress out to the console
echo Running "%~dpf0"

:: Get the pretend name of this workload (the folder name)
for %%I in ("%~dp0\.") do set ParentFolderName=%%~nxI

:: Get the parent folder path (for logging)
for %%I in ("%~dp0.") do for %%J in ("%%~dpI.") do set ParentFolderPath=%%~dpnxJ

:: Simulate doing something that takes 3 seconds
sleep 3


	:: Logging and clean-up (main work finished)

:: Check for errors and log/exit accordingly
if not %ERRORLEVEL%==0 goto :Problem

:: Log output to a log file and to console
echo %ParentFolderName% installed, using installer version %scriptVer%. >> "%ParentFolderPath%\Completion Log.log"
echo %ParentFolderName% installation complete.
echo Done! >> Done.txt

:: Exit with exit code 0 (could add functionality to handle different exit codes)
exit /b 0

:Problem
:: Log output to a log file and to console
echo %ParentFolderName% installation encounted an error sleeping and was not installed ^(script version: %scriptVer%^). >> "%ParentFolderPath%\Completion Log.log"
echo %ParentFolderName% installation failed.

:: Exit with exit code 1 (could add functionality to handle different exit codes)
exit /b 1
