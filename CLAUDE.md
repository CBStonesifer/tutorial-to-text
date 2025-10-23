# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Tutorial Helper is a video processing application that uses AI to analyze tutorial videos and generate timestamped descriptions. The system consists of:

1. **NextJS Frontend** (`tutorial_ui/`) - Video upload interface with timeline visualization
2. **FastAPI Backend** (`tutorial_ui/api/`) - Handles uploads, GCP storage, and model orchestration
3. **Model Deployment** (`model_deployment/`) - Baseten deployment using HuggingFace SmolVLM2-500M-Video-Instruct

## Architecture

The application follows a three-tier architecture:

```
NextJS (localhost:3000)
    ↓ HTTP multipart/form-data
FastAPI (localhost:8000)
    ↓ Video storage → GCP Cloud Storage (signed URLs)
    ↓ Inference → Baseten API (SmolVLM2 model)
    ↓ Returns: timestamped frame descriptions
Timeline component displays results
```

**Key architectural decisions:**
- Videos are stored in GCP with 1-hour signed URLs for security
- The FastAPI backend acts as a coordinator between storage and inference
- Model processes videos in two modes: `timestamped` (per-frame descriptions) or `summary` (overall description)
- Frontend uses SWR for data fetching and caching

## Common Commands

### Frontend (tutorial_ui/)
```bash
cd tutorial_ui
bun install           # Install dependencies
bun run dev          # Start dev server (localhost:3000, with Turbopack)
bun run build        # Build for production (with Turbopack)
bun run lint         # Run ESLint
bun run start        # Start production server
```

### Backend API (tutorial_ui/api/)
```bash
cd tutorial_ui/api

# Activate virtual environment
source .venv/bin/activate

# Install dependencies (use uv if available)
uv pip install -r requirements.txt
# or
pip install -r requirements.txt

# Start API server
cd ..  # Back to tutorial_ui/
uvicorn api.main:app --reload --port 8000

# Or use the convenience script
cd api
./run.sh  # Creates venv, installs deps, starts server
```

### Model Deployment (model_deployment/)
```bash
cd model_deployment

# Activate virtual environment
source .venv/bin/activate

# Install dependencies (use uv if available)
uv pip install -r requirements.txt

# Test model locally
python main.py
```

## Environment Setup

### Backend API Environment Variables
Located in `tutorial_ui/api/.env`:

```bash
# GCP credentials as JSON string (not file path)
GCP_CREDENTIALS_JSON='{"type":"service_account",...}'
GCP_BUCKET_NAME=your-bucket-name
GCP_PROJECT_ID=your-gcp-project-id

# Baseten configuration
BASETEN_API_KEY=your-api-key
BASETEN_MODEL_ID=your-model-id
```

**Important:** The API uses `pydantic-settings` with `Settings` class in `api/settings.py`. All configuration must flow through this single settings file.

### Frontend Environment Variables
Located in `tutorial_ui/.env`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Code Structure Details

### Frontend (tutorial_ui/)

**Directory structure:**
```
tutorial_ui/
├── app/
│   ├── page.tsx           # Password-protected login (password: "tutorial123")
│   ├── layout.tsx         # Root layout with fonts
│   └── upload/page.tsx    # Main upload interface with drag-drop
├── components/
│   ├── timeline.tsx       # Timeline visualization for video descriptions
│   └── navigation.tsx     # Navigation component
├── lib/
│   ├── api/
│   │   ├── client.ts      # API client with error handling
│   │   └── types.ts       # TypeScript type definitions
│   └── utils.ts          # Utility functions (cn for classNames)
└── api/                   # FastAPI backend (see below)
```

**Key patterns:**
- All pages are client components (`"use client"`)
- Path aliases: `@/*` maps to root directory
- Tailwind v4 with PostCSS
- Uses `bun` as package manager (not npm)
- Session-based auth using `sessionStorage`

### Backend API (tutorial_ui/api/)

**File structure:**
```
api/
├── main.py              # FastAPI app with CORS middleware
├── routes.py            # API endpoints (/upload-video, /process-video, /test-timeline)
├── settings.py          # Centralized settings using pydantic-settings
├── model_functions.py   # BasetenClient for model inference
├── blob.py              # BlobStorage for GCP integration
└── run.sh               # Startup script
```

**Key patterns:**
- All routes are prefixed with `/api`
- `BlobStorage` class handles GCP Cloud Storage with signed URL generation
- `BasetenClient` uses persistent session for HTTP requests
- Settings loaded from `.env` file via pydantic
- CORS configured to allow `localhost:3000` only

**API endpoints:**
- `POST /api/upload-video` - Upload video, store in GCP, process with model
- `POST /api/process-video` - Alternative processing endpoint
- `GET /api/test-timeline` - Returns mock data for frontend testing
- `GET /health` - Health check endpoint

### Model Deployment (model_deployment/)

**Structure:**
```
model_deployment/
├── main.py                        # Entry point (basic hello world)
└── tutorial_helper/
    ├── model/
    │   ├── __init__.py
    │   └── model.py               # Model class with Baseten interface
    └── requirements.txt           # Model dependencies
```

**Model class interface:**
- `__init__(**kwargs)` - Initialize model configuration
- `load()` - Load HuggingFace model and processor
- `predict(request)` - Process video from URL
  - Downloads video from GCP signed URL
  - Extracts frames using OpenCV
  - Runs inference based on mode (`timestamped` or `summary`)
  - Returns structured frame descriptions with timestamps

**Model details:**
- Uses `HuggingFaceTB/SmolVLM2-500M-Video-Instruct`
- Extracts 8 evenly-spaced frames by default
- Returns timestamps in seconds and frame numbers
- Cleans up temporary files automatically

## Development Workflow

**Typical development session:**
1. Start backend API: `cd tutorial_ui/api && ./run.sh`
2. Start frontend: `cd tutorial_ui && bun run dev`
3. Access at `http://localhost:3000` (password: tutorial123)
4. After changes to frontend: `bun run lint` to check for issues
5. Before committing: `bun run build` to verify production build

**Testing the flow:**
1. Upload a video through the UI
2. Check backend logs for upload confirmation
3. Video stored in GCP with signed URL
4. Baseten model processes video
5. Results displayed in timeline component

## Important Notes

- **Python package management:** Use `uv` rather than direct pip commands where possible
- **Virtual environments:** Backend uses `.venv` in `tutorial_ui/api/` and `model_deployment/`
- **Frontend package manager:** Always use `bun`, never npm or yarn
- **Environment files:** Never commit `.env` files - use `.env.example` as template
- **GCP credentials:** Stored as JSON string in environment variable, not as file path
- **Settings pattern:** All backend config flows through `settings.py` - refactor any hardcoded values into this file
- **CORS:** Backend only allows requests from `localhost:3000`
- **Video storage:** Signed URLs expire after 1 hour
- **Model modes:** `timestamped` returns per-frame descriptions, `summary` returns single description

## Debugging

**Backend issues:**
- Check logs in terminal running uvicorn
- Verify `.env` file exists and has correct values
- Test GCP access: ensure service account has Storage Object Admin role
- Test Baseten API: check API key and model ID

**Frontend issues:**
- Check browser console for API errors
- Verify backend is running on port 8000
- Check network tab for failed requests
- Ensure session storage has `authenticated: "true"`

**Model issues:**
- Check Baseten dashboard for model status
- Verify video URL is accessible (signed URL not expired)
- Check model logs in Baseten console
