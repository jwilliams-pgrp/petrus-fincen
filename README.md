### petrus-fincen ###

This is the background for the Fincen list process which has been automated via python script.

# Requirements

Install VS Code
-   Install python on VS Code

Install Python 3

Clone repo to local computer

Create virtual environment to run code in
- python -m venv /path/to/new/virtual/environment

Install requirements.txt in virtual environment
- pip install -r /path/to/requirements.txt

# Process

Download the Business and People files from Fincen (314a)
- https://fiportal.fincen.gov/

Save the files to R:\Conversion\Archway\DeptOfBanking
- ex. People_20241001 (for October 1, 2024)
- ex. Business_20241001 (for October 1, 2024)

Pull and update the script AsOfDate to the new file date and run it

Notify Jeremy Fowler that the new file has been processed