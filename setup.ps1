python -m venv ./.venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip wheel setuptools
pip install -r requirements.txt
python -m ipykernel install --user --name glue --display-name "Python (glue)"