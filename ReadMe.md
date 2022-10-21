# Workload AutoInstaller
This is a fancy yet simple GUI which can be adapted for a variety of tasks. I originally designed this as a workload/program installer. However, because it essentially just points to and runs batch files to kick off each installation, it can easily be modified to install or run practically anything by changing just a few lines of code. Here's an example of what it can look like:

![Demo Image](/imgs/Demo.png)

![Checkmark](/imgs/checkMark.png) indicates that option is already installed or has already been run.

You can also set the GUI to time out after a specified amount of time and automatically install/run a default set of options.


## Installation and Setup
:snake: Along with Python 3, the only requirement you should need is PyQt, which you can install using pip, with `pip install PyQt6`.

To hook this up to your own batch files, go to the init method of the AutoInstallerChooser class, and look for calls to `self.addWorkloadOption` within it. You can change these to point to whatever you like. The arguments for addWorkloadOption are as follows:

- **Workload name**; the name to appear in the GUI
- **Install or Run Time**; how long the option is expected to take to install or run, in seconds.
- **Target script path**; the script to run for this particular option. These are run in series when the user clicks "Install". The path specified here should be relative to the directory where the main AutoInstaller.py script is located.
- **Installation-check path**; a file or folder that the program can check for in order to determine whether the workload is installed or whether the target script has already been run. If the file or folder exists, the program assumes the answer is yes, and the option will appear with a checkmark next to it in the GUI. The path specified here should be relative to the directory where the main AutoInstaller.py script is located.
- **Tooltip (optional)**; text to appear after a moment while the user hovers their mouse over an option.

Once you have your workloads ready with addWorkloadOption() calls, you can configure the 'Minimal'/'Balanced'/'Full' suite radio buttons using the lists near the top of the script (around line 25) called `Minimal_Suite` and `Balanced_Suite`. Simply populate the lists with the names of the options you want to appear in that suite. *(i.e. the same names used for the first argument to addWorkloadOption.)* The 'Full' suite always simply selects all of the options.

## Optional Features
:mechanical_arm: If starting the program from command line or another script, you may optionally pass an auto-start timeout argument (an integer count, in seconds). If this is given, the program will automatically start the default set of options (typically the 'Balanced' suite, unless you change it), after that many seconds. Any user interaction during this time will cancel the auto-start.

e.g. `"C:\Python310\python.exe" AutoInstaller.py 1800` will automatically start the install after 30 minutes of inactivity.

When this is used, the time remaining until timeout will be displayed at the bottom of the program.


:game_die: Having random backgrounds is another optional feature. Simply set `useRandomBackgrounds` near the top of the script to True. You can change which backgrounds may appear by looking for the line after the one that checks that variable, or by searching for `random.choice`.
