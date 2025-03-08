# setup.ps1 - Script to set up the Python environment and run a project

# Step 1: Check for Python installation
Write-Host "Checking for Python installation..."
if (!(Get-Command python3 -ErrorAction SilentlyContinue)) {
    Write-Host "Python is not installed. Installing Python..."
    # Install Python using winget (ensure winget is available)
    winget install -e --id Python.Python.3
} else {
    Write-Host "Python is already installed."
}


# Step 2: Create Virtual Environment
Write-Host "Setting up virtual environment..."
python -m venv venv

# Step 3: Activate Virtual Environment (using temporary execution policy)
Write-Host "Activating virtual environment..."
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force
.\venv\Scripts\Activate.ps1

# Step 4: Upgrade pip
Write-Host "Upgrading pip..."
python.exe -m pip install --upgrade pip

# Step 5: Install Dependencies
Write-Host "Installing required packages..."
pip install -r requirements.txt



Write-Host "Setup complete."