# CogniBrew Cloud Edge Gateway

Receives daily batch face-embedding vectors from Edge devices, validates payload schemas, and stores raw data to S3-compatible storage (RustFS).

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/gateway/batch` | Receive daily batch of face-embedding vectors |
| `POST` | `/api/v1/gateway/enroll` | Enroll a new customer's baseline face vector |
| `GET` | `/api/v1/utils/health-check/` | Health check |

### Batch Upload

```bash
curl -X POST http://localhost:8000/api/v1/gateway/batch \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "edge-001",
    "date": "2026-03-23",
    "vectors": [
      {
        "username": "alice",
        "embedding": [0.1, 0.1, ...],  # 512-dim vector
        "is_correct": true
      }
    ]
  }'
```

### Enrollment

```bash
curl -X POST http://localhost:8000/api/v1/gateway/enroll \
  -H "Content-Type: application/json" \
  -d '{
    "username": "bob",
    "embedding": [0.2, 0.2, ...],  # 512-dim vector
    "device_id": "edge-001"
  }'
```

## Project Structure

```
.github/workflows/
└── ci.yml          # Lint + Docker build & push
app/
├── api/            # Route handlers
├── core/           # Config & logging
├── crud/           # S3 operations
├── models/         # Pydantic schemas
├── main.py         # FastAPI application
└── pre_start.py    # Pre-startup script
scripts/
├── init_rustfs.sh  # Start RustFS for local development
└── prestart.sh     # Docker container pre-start hook
```

## Development Setup

### Prerequisites

- Docker
- Python 3.10+

### 1. Start RustFS

```bash
./scripts/init_rustfs.sh
```

This starts a RustFS container on port `9000` (API) and `9001` (console).

### 2. Run the API

**With Docker:**

```bash
docker build -t cognibrew-gateway .
docker run --name cognibrew-gateway \
  --link rustfs:rustfs \
  -e S3_ENDPOINT_URL=http://rustfs:9000 \
  -e ENVIRONMENT=local \
  -p 8000:8000 \
  cognibrew-gateway
```

**Without Docker:**

```bash
pip install -r requirements.txt
export S3_ENDPOINT_URL=http://localhost:9000
uvicorn app.main:app --reload --port 8000
```

### 3. Open API Docs

Visit [http://localhost:8000/docs](http://localhost:8000/docs) for interactive Swagger documentation.

## CI/CD

GitHub Actions pipeline (`.github/workflows/ci.yml`):

| Job | Trigger | Description |
|-----|---------|-------------|
| **Lint** | PR to `main`, push to `main`, tags | Runs [Ruff](https://docs.astral.sh/ruff/) linter |
| **Build & Push** | Tags matching `v*` | Builds Docker image and pushes to Docker Hub |

### Image Tags

```
<DOCKERHUB_USERNAME>/actions:cognibrew-cloud-edge-gateway-v1.0.0-abc1234
<DOCKERHUB_USERNAME>/actions:cognibrew-cloud-edge-gateway-latest
```

### Required Secrets

| Secret | Description |
|--------|-------------|
| `DOCKERHUB_USERNAME` | Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token |

## Environment Variables

See [`.env.example`](.env.example) for all available configuration options.

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `ENVIRONMENT` | `production` | `local`, `staging`, or `production` |
| `API_PREFIX_STR` | `/api/v1` | API route prefix |
| `PROJECT_NAME` | `CogniBrew Edge Gateway` | Application display name |
| `S3_ENDPOINT_URL` | `http://rustfs:9000` | S3-compatible storage endpoint |
| `S3_ACCESS_KEY` | `rustfsadmin` | S3 access key |
| `S3_SECRET_KEY` | `rustfsadmin` | S3 secret key |
| `S3_BUCKET_NAME` | `cognibrew-raw` | Bucket name for raw data |
