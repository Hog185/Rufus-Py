# Rufus-Py Development Agenda
## DEVELOPMENT ENVIRONMENT 
uv is used for this project. Check out PR: https://github.com/Hog185/Rufus-Py/pull/37
## Conventions:
- Proper PR  or Issue link must be provided where relevant.
- Errors and Exceptions which halt the usage of the whole program are added to the immediate attention group only.
- Other bugs are added to the Immediate attention or further attention group according to priority only.
- Suggestions are added to the further attention or Down the line group accordingly.
- These are listed with a priority order from higher priority to lower priority.
-  Editors are requested to strictly follow this priority order to maximize efficiency
## To-Do
### Immediate Attention:
- Fix cluster function command and error handling to avoid crash when executed [backend]
- Troubleshoot all the commands being used using subprocess and pkexec [backend]
- Connect all the existing format functions to the respective gui components [backend + frontend]
## Further attention:
- Start completing the dd flashing and writing functions [backend]
- Work on MBR/GPT and BIOS/UEFI functions probably [backend]
- Troubleshoot those functions and do proper error handling [backend]
- Convert printed errors to gui error messages [frontend]
- Find alternatives to asking for root privilege from user every time a command is to be run [backend]
- Ensure all gui components are connected to their respective functions [frontend + backend]
- Ensure all the data is on the disk before telling the user that the writing is done, if not we must find a way to counter this? [backend]
- Make the cancel button actually work: (no clue how to properly implement yet?) [backend + frontend]
- When cancel button is clicked we must stop the ongoing process
- We must restore the initial data, label and other stuff or not?
- We may possibly remove this feature all together and just warn the user in BIG RED TEXT saying that the changes are irreversible XD (makes the most sense to me)
- Hopefully make the progress bar actually increment like it should. [frontend]

---
At this stage, the program should be ready for first release.
---
## Down the line:
- Executable packages
- Add Support for Windows ISO
- Add Rufus windows iso features possibly
- Add Support for Windows ISO
- Ventoy support
- Executable packages (RPM, DEB,APPIMAGE)
