#!/bin/bash
set -e

# CONFIGURATION - UPDATE DB_PASSWORD BEFORE DEPLOYING!
PROJECT_ID="test-b9457"
REGION="asia-south1"  # Mumbai region (closest to Bangladesh)
SERVICE_NAME="health-assistant"
DB_PASSWORD="Prince2025!"
GEMINI_API_KEY="AIzaSyC5nSNnFQ2u68omDXlbGvhquwg3eXSmUsk"

echo "=== FutureBuilders 2025 - Health Assistant Deployment ==="
echo "Team: NSU_Zazabores"
echo ""

echo "=== Building Frontend ==="
cd frontend
npm install
npm run build:web
cd ..

echo "=== Copying Frontend to Backend Static ==="
rm -rf backend/static
mkdir -p backend/static
cp -r frontend/dist/* backend/static/

echo "=== Deploying to Cloud Run ==="
gcloud run deploy $SERVICE_NAME \
  --source backend/ \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --add-cloudsql-instances $PROJECT_ID:$REGION:health-assistant-db \
  --set-env-vars "DATABASE_URL=postgresql+psycopg2://healthuser:$DB_PASSWORD@/healthdb?host=/cloudsql/$PROJECT_ID:$REGION:health-assistant-db" \
  --set-env-vars "GOOGLE_AI_API_KEY=$GEMINI_API_KEY" \
  --memory 512Mi \
  --cpu 1 \
  --port 8080 \
  --timeout 300 \
  --project $PROJECT_ID

echo ""
echo "=== Deployment Complete ==="
echo "Your application is available at:"
gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)" --project $PROJECT_ID
