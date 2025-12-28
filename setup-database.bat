@echo off
REM Phase 5: Cloud SQL Database Setup
REM Team: NSU_Zazabores - FutureBuilders 2025

echo ========================================
echo   Phase 5: Cloud SQL Database Setup
echo   Team: NSU_Zazabores
echo ========================================
echo.

REM Configuration
set PROJECT_ID=test-b9457
set REGION=asia-south1
set DB_PASSWORD=Prince2025!

echo Step 1: Authenticating with Google Cloud...
echo.
gcloud auth login

echo.
echo Step 2: Setting project to %PROJECT_ID%...
gcloud config set project %PROJECT_ID%

echo.
echo Step 3: Enabling required APIs...
echo (This may take 1-2 minutes)
gcloud services enable sqladmin.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

echo.
echo Step 4: Creating Cloud SQL PostgreSQL instance...
echo (This will take 5-10 minutes - please wait)
echo.
gcloud sql instances create health-assistant-db ^
  --database-version=POSTGRES_15 ^
  --tier=db-f1-micro ^
  --region=%REGION% ^
  --root-password="%DB_PASSWORD%" ^
  --storage-type=SSD ^
  --storage-size=10GB ^
  --backup

echo.
echo Step 5: Creating database 'healthdb'...
gcloud sql databases create healthdb --instance=health-assistant-db

echo.
echo Step 6: Creating database user 'healthuser'...
gcloud sql users create healthuser ^
  --instance=health-assistant-db ^
  --password="%DB_PASSWORD%"

echo.
echo ========================================
echo   Database Setup Complete!
echo ========================================
echo.
echo Database Instance: health-assistant-db
echo Database Name: healthdb
echo Database User: healthuser
echo Database Password: %DB_PASSWORD%
echo Region: %REGION%
echo.
echo You can now run deploy.bat to deploy your application!
echo.

pause
