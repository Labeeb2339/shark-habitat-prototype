# NASA Earthdata token setup

Experimental code paths can make authenticated Earthdata requests when you
provide your own token at runtime. The generated-data Streamlit interface does
not require a token.

Supplying a token only authorizes request attempts. It does not guarantee that
the displayed grid contains satellite measurements, make the data current, or
validate the habitat score.

## 1. Create your account and token

1. Create or sign in to a NASA Earthdata Login account: <https://urs.earthdata.nasa.gov/>.
2. Generate a token using the current Earthdata instructions.
3. Keep the token private. Do not paste it into source code, commits, issues, screenshots, or chat messages.

## 2. Set the environment variable

PowerShell:

```powershell
$env:EARTHDATA_TOKEN = "paste-your-token-locally"
streamlit run app.py
```

macOS or Linux:

```bash
export EARTHDATA_TOKEN="paste-your-token-locally"
streamlit run app.py
```

The variable applies only to the current shell session unless you configure your operating system or secret manager differently.

## 3. Confirm safe setup

- The application should report that authentication was configured for Earthdata requests.
- `git status` should not list a local `.env` file; `.env` is ignored by this repository.
- Run `python -m unittest discover -s tests -v` before committing.

## If a token was committed

Removing it from the latest file is not enough. Revoke or rotate it with NASA Earthdata, then decide separately whether to rewrite Git history. History rewriting is disruptive because collaborators must re-clone or carefully reset their copies.

This repository never needs another person's token. Each user should supply their own credential.
