# testing-online-coding

A small Flask web app that adds two numbers. It now requires a Google login so
only an authorized Gmail account can use the calculator.

## Setup

```bash
pip install -r requirements.txt
```

## Run the app

```bash
python app.py
```
Set the following environment variables with your Google OAuth credentials and
the email allowed to use the app:

```bash
export GOOGLE_CLIENT_ID="your-client-id"
export GOOGLE_CLIENT_SECRET="your-client-secret"
export AUTHORIZED_EMAIL="user@example.com"
export SECRET_KEY="choose-a-secret"
```

Then open `http://localhost:5000/` in your browser.
