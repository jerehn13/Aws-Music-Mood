# Deploying the Mood App to AWS

The app is ready to deploy to **AWS Elastic Beanstalk** (a service that hosts
web apps). These files make it deploy-ready:

- `application.py` — WSGI entry point Elastic Beanstalk runs
- `Procfile` — tells the server to run it with gunicorn
- `requirements.txt` — Python packages AWS installs (scikit-learn, joblib, gunicorn)

The machine-learning model (`ml_model.py`) trains automatically on the first
request after deployment.

## One-time setup

1. **Create a free AWS account:** https://aws.amazon.com
2. **Install the tools** (in PowerShell):
   ```powershell
   pip install awsebcli awscli
   ```
3. **Add your AWS keys** (from the AWS console → IAM → Security credentials):
   ```powershell
   aws configure
   ```
   Paste your Access Key, Secret Key, and a region (e.g. `us-east-1`).

## Deploy

From this project folder:

```powershell
eb init -p python-3.11 mood-app
eb create mood-app-env
eb open
```

- `eb init` sets up the project (pick your region when asked).
- `eb create` builds the cloud environment and deploys (takes a few minutes).
- `eb open` opens the live public URL in your browser.

## Update after changes

```powershell
eb deploy
```

## Take it down (to avoid charges)

```powershell
eb terminate mood-app-env
```

## Notes

- Elastic Beanstalk's free tier covers a small instance, but **leaving it
  running can incur charges** — terminate it when you're done.
- The song previews still come from the iTunes API (client-side), so the
  deployed site needs internet, which it has.
