# Google Cloud Deployment Guide - Phase 5
## NSU_Zazabores - FutureBuilders 2025

This guide walks you through setting up the Cloud SQL database and deploying your health assistant app.

---

## Prerequisites ✅

Before starting, make sure you have:
- [ ] Google Cloud account (already created)
- [ ] Project ID: `test-b9457` (already configured)
- [ ] Billing enabled on your Google Cloud project
- [ ] gcloud CLI installed ([Download here](https://cloud.google.com/sdk/docs/install))

---

## Step 1: Install gcloud CLI (If Not Installed)

**Windows:**
1. Download: https://cloud.google.com/sdk/docs/install#windows
2. Run the installer
3. Open a new Command Prompt or PowerShell
4. Verify: `gcloud --version`

---

## Step 2: Authenticate with Google Cloud

```cmd
REM Login to your Google account
gcloud auth login

REM Set your project
gcloud config set project test-b9457

REM Verify it's set correctly
gcloud config get-value project
```

---

## Step 3: Enable Required APIs

```cmd
REM Enable Cloud SQL Admin API
gcloud services enable sqladmin.googleapis.com

REM Enable Cloud Run API
gcloud services enable run.googleapis.com

REM Enable Cloud Build API
gcloud services enable cloudbuild.googleapis.com

REM This may take 1-2 minutes
```

---

## Step 4: Create Cloud SQL Database

**Choose a secure password** (suggestion: `Prince2025!` or `NSU_Zazabores2025`)

```cmd
REM Create PostgreSQL instance (takes ~5-10 minutes)
gcloud sql instances create health-assistant-db ^
  --database-version=POSTGRES_15 ^
  --tier=db-f1-micro ^
  --region=asia-south1 ^
  --root-password="Prince2025!" ^
  --storage-type=SSD ^
  --storage-size=10GB ^
  --backup

REM Create the database
gcloud sql databases create healthdb --instance=health-assistant-db

REM Create the user
gcloud sql users create healthuser ^
  --instance=health-assistant-db ^
  --password="Prince2025!"
```

**⏰ Wait Time:** This will take about 5-10 minutes. You'll see progress updates.

---

## Step 5: Update Deployment Scripts

**Update `deploy.bat` with your chosen password:**

Open `deploy.bat` and change line 13:
```cmd
set DB_PASSWORD=Prince2025!
```

**Or use this command to update it automatically:**
```cmd
REM Replace "your-secure-db-password" with your actual password
```

---

## Step 6: Deploy the Application

**Now run the deployment script:**

```cmd
REM Make sure you're in the project root directory
cd D:\AI_Hackathon

REM Run the deployment
deploy.bat
```

**What happens:**
1. ✅ Builds the frontend (npm install + expo export)
2. ✅ Copies frontend to backend/static
3. ✅ Builds Docker container using Cloud Build
4. ✅ Deploys to Cloud Run
5. ✅ Connects to Cloud SQL database
6. ✅ Sets environment variables (Gemini API key, database URL)

**⏰ Deployment Time:** 5-10 minutes

---

## Step 7: Verify Deployment

After deployment completes, you'll see a URL like:
```
https://health-assistant-abc123xyz.run.app
```

**Test it:**
```cmd
REM Health check
curl https://health-assistant-abc123xyz.run.app/api/health

REM Open in browser
start https://health-assistant-abc123xyz.run.app
```

---

## Troubleshooting 🔧

### Error: "Permission denied"
```cmd
REM Re-authenticate
gcloud auth login
gcloud config set project test-b9457
```

### Error: "Billing not enabled"
1. Go to: https://console.cloud.google.com/billing
2. Link your project to a billing account
3. Retry deployment

### Error: "API not enabled"
```cmd
REM Enable all required APIs
gcloud services enable sqladmin.googleapis.com run.googleapis.com cloudbuild.googleapis.com
```

### Error: "Cloud SQL instance already exists"
```cmd
REM Delete the existing instance first
gcloud sql instances delete health-assistant-db

REM Then recreate it with the commands in Step 4
```

### Frontend not loading
```cmd
REM Check Cloud Run logs
gcloud run services logs read health-assistant --region=asia-south1 --limit=50
```

---

## Cost Estimation 💰

**Monthly costs (estimated):**
- Cloud Run: $0-15 (2M requests/month free)
- Cloud SQL db-f1-micro: $7-10
- Cloud Build: Free (120 min/day)
- **Total: ~$8-27/month**

**Free Tier Benefits:**
- Cloud Run: 2 million requests/month FREE
- Cloud Build: 120 build-minutes/day FREE
- Google AI Studio: 15 requests/minute FREE

---

## Important Notes ⚠️

1. **Database Password Security:**
   - Don't commit `deploy.bat` with the real password to Git
   - The password is already in `.gitignore` via environment variables

2. **Gemini API Key:**
   - Already configured: `AIzaSyC5nSNnFQ2u68omDXlbGvhquwg3eXSmUsk`
   - This is visible in your scripts, consider regenerating after hackathon

3. **Project ID:**
   - Already set to `test-b9457`
   - Don't change this unless you create a new project

4. **Region:**
   - `asia-south1` (Mumbai) - closest to Bangladesh
   - Lowest latency for your target users

---

## Quick Reference Commands

```cmd
REM Check deployment status
gcloud run services describe health-assistant --region=asia-south1

REM View logs
gcloud run services logs read health-assistant --region=asia-south1

REM Get service URL
gcloud run services describe health-assistant --region=asia-south1 --format="value(status.url)"

REM Check Cloud SQL instances
gcloud sql instances list

REM Connect to database (for testing)
gcloud sql connect health-assistant-db --user=healthuser --database=healthdb
```

---

## Need Help?

- Google Cloud Console: https://console.cloud.google.com
- Project Dashboard: https://console.cloud.google.com/home/dashboard?project=test-b9457
- Cloud Run Services: https://console.cloud.google.com/run?project=test-b9457
- Cloud SQL Instances: https://console.cloud.google.com/sql/instances?project=test-b9457

---

**Team:** NSU_Zazabores
**Hackathon:** FutureBuilders 2025
**Good luck! 🚀**
