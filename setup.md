# Robot Arm Controller

Adapted for the 2026 NRCC XLR8 Academy.

Original tutorial: https://projecthub.arduino.cc/ryan6534/recordable-cardboard-robot-arm-4b6783

Windows setup commands for this project.

## PowerShell

Open PowerShell in the project folder:

```powershell
cd C:\python_apps\robot_arm
```

Activate the virtual environment:

```powershell
. .\.venv\Scripts\Activate.ps1
```

Install the required Python packages:

```powershell
python.exe -m pip install -r requirements.txt
```

Run the app:

```powershell
python.exe robot_gui.py
```

When you are finished, deactivate the virtual environment:

```powershell
deactivate
```

## If Activation Is Blocked

If PowerShell says script execution is disabled, run this once:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate the virtual environment again:

```powershell
. .\.venv\Scripts\Activate.ps1
```

## Command Prompt Alternative

If you prefer Command Prompt instead of PowerShell:

```bat
cd C:\python_apps\robot_arm
.\.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python robot_gui.py
deactivate
```

## Notes

This project uses `pyserial` to communicate with the robot arm over a COM port.

If `python` opens the wrong Python on your computer, use the explicit virtual environment Python instead:

```powershell
.\.venv\Scripts\python.exe robot_gui.py
```
