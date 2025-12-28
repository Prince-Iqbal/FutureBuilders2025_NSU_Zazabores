@echo off
REM Windows Deployment Script for FutureBuilders 2025 - Health Assistant
REM Team: NSU_Zazabores

echo === FutureBuilders 2025 - Health Assistant Deployment ===
echo Team: NSU_Zazabores
echo.

REM CONFIGURATION - UPDATE DB_PASSWORD BEFORE DEPLOYING!
set PROJECT_ID=test-b9457
set REGION=asia-south1
set SERVICE_NAME=health-assistant
set DB_PASSWORD=Prince2025!
set GEMINI_API_KEY=AIzaSyC5nSNnFQ2u68omDXlbGvhquwg3eXSmUsk

echo === Building Frontend ===
cd frontend
call npm install
call npm run build:web
cd ..

echo === Copying Frontend to Backend Static ===
if exist backend\static rmdir /s /q backend\static
mkdir backend\static
xcopy /E /I /Y frontend\dist\* backend\static\

echo === Deploying to Cloud Run ===
gcloud run deploy %SERVICE_NAME% ^
  --source backend/ ^
  --platform managed ^
  --region %REGION% ^
  --allow-unauthenticated ^
  --add-cloudsql-instances %PROJECT_ID%:%REGION%:health-assistant-db ^
  --set-env-vars "DATABASE_URL=postgresql+psycopg2://healthuser:%DB_PASSWORD%@/healthdb?host=/cloudsql/%PROJECT_ID%:%REGION%:health-assistant-db" ^
  --set-env-vars "GOOGLE_AI_API_KEY=%GEMINI_API_KEY%" ^
  --memory 512Mi ^
  --cpu 1 ^
  --port 8080 ^
  --timeout 300 ^
  --project %PROJECT_ID%

echo.
echo === Deployment Complete ===
echo Your application is available at:
gcloud run services describe %SERVICE_NAME% --region %REGION% --format "value(status.url)" --project %PROJECT_ID%

pause
