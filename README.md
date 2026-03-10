# 2048 for Streamlit

A keyboard-only 2048 game built in Python for Streamlit.

## Local setup

### Windows PowerShell

1. Create the virtual environment:
   `py -m venv .venv`
2. Activate it:
   `.\.venv\Scripts\Activate.ps1`
3. Install the dependencies:
   `pip install -r requirements.txt`
4. Run the app:
   `streamlit run app.py`

## Controls

- Arrow keys: move tiles
- `W`, `A`, `S`, `D`: move tiles
- `N`: start a new game

Keep the browser tab focused while playing.

## Publish to Streamlit Community Cloud

1. Push this project to GitHub.
2. Create a new app in Streamlit Community Cloud.
3. Point the app to [app.py](app.py).
4. Streamlit will install [requirements.txt](requirements.txt) automatically.
