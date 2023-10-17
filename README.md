# PressReview
A small and fast library for searching queries on online scientific portals (so far, PubMed supported).
## Installation
1. Run in terminal:
```
git clone https://github.com/Leox42/PressReview.git
cd PressReview
mkdir press_review_output_csv
mkdir press_review_output_html
```
2. Modify `config.yaml`. Set:
* Your list of queries
* Maximum number of results
* Your email address
* Your Pubmed API

3. In a designated folder for virtual environments, create a virtual environment, activate it and install requierements. Example in the project's root directory:
```
pip install virtualenv
python3.9 -m venv <venv-name>
source <venv-name>/bin/activate
pip3 install -r requirements.txt
```
4. Run:
```
python3 main.py
```
