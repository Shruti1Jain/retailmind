# RetailMind AI

Hackathon demo: Streamlit + FastAPI + Vertex AI Gemini + BigQuery on Cloud Run.

Google Cloud Shell is recommended for the first deployment because the Google Cloud CLI is preinstalled.

## 1) Configure your project

Replace `YOUR_PROJECT_ID` with your real project ID.

```bash
export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
export GOOGLE_CLOUD_LOCATION="global"
export BQ_DATASET="catalogiq"
export REGION="us-central1"

gcloud config set project "$GOOGLE_CLOUD_PROJECT"
```

## 2) Enable required APIs

```bash
gcloud services enable \
  aiplatform.googleapis.com \
  bigquery.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com
```

## 3) Prepare source code

Upload the ZIP to Cloud Shell, then run:

```bash
unzip retailmind-ai.zip
cd retailmind-ai

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

For local development auth:

```bash
gcloud auth application-default login
```

Cloud Run uses its assigned service account at runtime.

## 4) Create and populate BigQuery

Generate the starter data:

```bash
python data/generate_data.py
```

This creates and populates:

- `products`: name, category, price, description
- `inventory`: product stock quantity
- `transactions`: historical purchases, quantity, date

Starter volume is intentionally small (10 products and 400 synthetic transactions) for faster validation.

Validate in BigQuery:

```sql
SELECT
  name,
  category,
  price
FROM `YOUR_PROJECT_ID.retailmind.products`
ORDER BY price;
```

## 5) Vertex AI Gemini integration

This project uses the current Google Gen AI Python SDK (`google-genai`) with Vertex AI routing.

Pattern used in the backend:

```python
from google import genai

client = genai.Client(
    vertexai=True,
    project=PROJECT,
    location=LOCATION
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

print(response.text)
```

Important architecture note: BigQuery provides product facts (price, stock, catalog fields), then Gemini produces a grounded response. This reduces hallucinated product claims.

## 6) Run locally

Open two terminals in the project root.

Terminal 1:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8081
```

Terminal 2:

```bash
export API_URL="http://127.0.0.1:8081"
streamlit run frontend/streamlit_app.py
```

Sample prompts:

- Find running shoes under ₹4,000.
- Show me fitness accessories.
- Recommend affordable wireless earbuds.

Current retrieval is keyword-based, so highly open-ended requests may need query refinement.

## 7) Deploy to Cloud Run

Create a runtime service account:

```bash
export SA="retailmind-runtime@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com"

gcloud iam service-accounts create retailmind-runtime \
  --display-name="RetailMind runtime"
```

Grant runtime permissions:

```bash
for ROLE in \
  roles/aiplatform.user \
  roles/bigquery.jobUser \
  roles/bigquery.dataViewer
do
  gcloud projects add-iam-policy-binding \
    "$GOOGLE_CLOUD_PROJECT" \
    --member="serviceAccount:$SA" \
    --role="$ROLE"
done
```

Deploy from source (uses the included `Dockerfile`):

```bash
gcloud run deploy retailmind-ai \
  --source . \
  --region "$REGION" \
  --service-account "$SA" \
  --allow-unauthenticated \
  --memory 1Gi \
  --timeout 120 \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,BQ_DATASET=$BQ_DATASET,API_URL=http://127.0.0.1:8081"
```

Cloud Run prints the public service URL after successful deployment.

Security note: `--allow-unauthenticated` makes this demo public. For non-demo use, require authentication, avoid real customer data, and set billing alerts/quotas.

## 8) Validation checklist

- [ ] BigQuery tables contain synthetic product, inventory, and transaction data
- [ ] Gemini returns an answer grounded in retrieved catalog data
- [ ] Out-of-stock products are excluded from recommendations
- [ ] Shopping assistant responds via Streamlit UI
- [ ] Retail dashboard shows revenue and low-stock alerts
- [ ] Cloud Run deployment URL opens successfully

## 9) Recommended next milestones

| Priority | Enhancement                                                       | Business impact                   |
| -------- | ----------------------------------------------------------------- | --------------------------------- |
| P0       | Structured Gemini intent extraction (budget/category/preferences) | More accurate recommendations     |
| P0       | Product variants and size-aware inventory                         | More realistic shopping flow      |
| P1       | Demand forecasting with BigQuery ML                               | Proactive stock planning          |
| P1       | Semantic product retrieval                                        | Better natural-language discovery |
| P1       | Personalized ranking using customer preferences                   | More relevant results             |
| P2       | Basket analysis and cross-selling                                 | Higher basket value potential     |

## API summary

- `GET /health`
- `POST /api/chat` with body `{"message":"running shoes"}`
- `GET /api/dashboard`

Backend listens on 8081 inside the container. Streamlit serves the public port (8080) on Cloud Run.
