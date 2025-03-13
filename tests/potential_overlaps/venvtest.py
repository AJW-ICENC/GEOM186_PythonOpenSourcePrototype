## ADD section to enable the venv - before dual testing begins
import subprocess
import sys
import os

def activate_venv():
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the relative path to the virtual environment
    venv_path = os.path.join(current_dir, '..', '..', 'venv')

    # Command to activate the virtual environment
    activate_command = os.path.join(venv_path, 'Scripts', 'activate')

    # Run the activation command in a subprocess
    subprocess.run(activate_command, shell=True, check=True)

    # List packages in  venv
    venv_packages = subprocess.run(['pip', 'list'], capture_output=True, text=True).stdout

    # List global packages
    global_packages = subprocess.run(['pip', 'list', '--user'], capture_output=True, text=True).stdout
    print(global_packages)

    if venv_packages == global_packages:
        print("Error: Virtual environment is not activated.")
        sys.exit(1)

activate_venv()