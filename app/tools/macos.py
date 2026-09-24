from subprocess import SubprocessError
import subprocess 
from langchain.tools import tool 

@tool
def open_app(app_name:str) ->str:
    """Open an installed macOS application
    Args : the exact name of the macos application """

    try:
        subprocess.run(['open','-a', app_name] ,check = True)
        return f"succssfully opened {app_name}"

    except subprocess.CalledProcessError:
        return f"Could not open {app_name}.Please make sure it is installed. "


@tool 
def close_app(app_name:str)-> str:
    """Close a running macOS application by name.
    Args: the exact name of the macOS application to close (e.g. 'System Settings', 'Safari')"""
    try:
        subprocess.run(
            ['osascript', '-e', f'tell application "{app_name}" to quit'],
            check=True
        )
        return f"Successfully closed {app_name}."
    except subprocess.CalledProcessError:
        return f"Could not close {app_name}. Make sure the app is running and the name is correct."