# Tutorial Helper - Quick Start

Simple video processing app with drag-and-drop upload, GCP storage, and AI model analysis.

## Workflow

1. Drag and drop a video onto the page
2. Video is uploaded to GCP Cloud Storage
3. Baseten model analyzes the video
4. Description is displayed on the page

## Setup

### 1. Backend API Setup

```bash
cd tutorial_ui/api
cp .env.example .env
```

Edit `.env` with your credentials:
```
GCP_CREDENTIALS_PATH=/path/to/service-account-key.json
GCP_BUCKET_NAME=your-bucket-name
BASETEN_API_KEY=your-baseten-api-key
BASETEN_MODEL_ID=your-model-id
```

Start the API:
```bash
./run.sh
```

API runs at `http://localhost:8000`

### 2. Frontend Setup

```bash
cd tutorial_ui
bun install
bun run dev
```

Frontend runs at `http://localhost:3000`

## GCP Setup (First Time Only)

See detailed instructions in `api/README.md`, but in summary:

1. Create GCP project at console.cloud.google.com
2. Enable Cloud Storage API
3. Create a storage bucket
4. Create service account with "Storage Object Admin" role
5. Download JSON key file
6. Update `.env` with path to key file and bucket name

## Usage

1. Go to `http://localhost:3000`
2. Enter password: `tutorial123`
3. Drag and drop video files
4. Click "Process Videos"
5. Wait for results to appear below

## API Endpoint

**POST** `/api/process-video`

**Parameters:**
- `file` (FormData) - Video file to process
- `prompt` (FormData, optional) - Description prompt for the model

**Response:**
```json
{
  "video_url": "https://storage.googleapis.com/...",
  "description": "Video description from AI model"
}
```

## Architecture

```
User drops video
    ↓
Next.js Frontend (port 3000)
    ↓
FastAPI Backend (port 8000)
    ↓
    ├─→ GCP Cloud Storage (saves video)
    └─→ Baseten API (analyzes video)
```

## Files Structure

```
tutorial_ui/
├── app/
│   ├── page.tsx          # Login page
│   └── upload/
│       └── page.tsx      # Video upload & results page
└── api/
    ├── main.py           # FastAPI app
    ├── routes.py         # API endpoints
    ├── blob.py           # GCP storage integration
    ├── model_functions.py # Baseten API client
    └── requirements.txt  # Python dependencies
```
