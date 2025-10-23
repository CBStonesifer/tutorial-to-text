# Tutorial Helper

AI-powered video analysis tool that generates timestamped descriptions of tutorial videos using vision-language models.

## Overview

Tutorial Helper processes video files and provides:
- **Timestamped mode**: Frame-by-frame descriptions with timestamps
- **Summary mode**: Overall video description

The system uses:
- **Frontend**: Next.js 15 with drag-and-drop video upload
- **Backend**: FastAPI for video processing and orchestration
- **Storage**: Google Cloud Storage for video hosting
- **Model**: HuggingFace SmolVLM2-500M-Video-Instruct deployed on Baseten

---

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Node.js 18+ and Bun
- Google Cloud Platform account
- Baseten account

---

## Part 1: Deploy the Model to Baseten

The model deployment uses Baseten's Truss framework to package and deploy the SmolVLM2 video model.

### Step 1: Install Truss CLI

```bash
pip install --upgrade truss
```

### Step 2: Login to Baseten

```bash
truss login
```

This will open a browser window to authenticate with your Baseten account.

### Step 3: Initialize and Push Model

From the project root:

```bash
cd model_deployment

# Push the model to Baseten
truss push --trusted tutorial_helper
```

The `--trusted` flag is required because the model downloads the HuggingFace model at runtime.

### Step 4: Get Your Model Details

After deployment completes:

1. Go to your [Baseten dashboard](https://app.baseten.co/)
2. Find your newly deployed model
3. Copy the **Model ID** (you'll need this for the API configuration)
4. Go to **Settings -> API Keys** and copy your **API Key**

**Note**: The first deployment may take 10-15 minutes as Baseten builds the container and downloads the model weights (~1GB).

### Model Configuration

The model deployment in `model_deployment/tutorial_helper/` includes:

- `model/model.py` - Model inference logic with frame extraction
- `requirements.txt` - Python dependencies (transformers, torch, opencv-python, etc.)
- `data/` - Optional: sample data for testing
- `packages/` - Optional: custom Python packages

---

## Part 2: Configure Google Cloud Storage

### Step 1: Create a GCP Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" -> "New Project"
3. Enter project name (e.g., `tutorial-helper`)
4. Click "Create"
5. Note your **Project ID** (you'll need this later)

### Step 2: Enable Cloud Storage API

1. In Cloud Console, navigate to **APIs & Services** -> **Library**
2. Search for "Cloud Storage API"
3. Click on it and press "Enable"

### Step 3: Create a Storage Bucket

1. Navigate to **Cloud Storage** -> **Buckets**
2. Click "Create Bucket"
3. Configure:
   - **Name**: Choose globally unique name (e.g., `tutorial-helper-videos-[your-initials]`)
   - **Location**: Choose region close to your users (e.g., `us-central1`)
   - **Storage class**: Standard
   - **Access control**: Fine-grained
   - **Protection tools**: None (for development)
4. Click "Create"
5. **Save your bucket name** - you'll need it for configuration

### Step 4: Create Service Account

1. Navigate to **IAM & Admin** -> **Service Accounts**
2. Click "Create Service Account"
3. Enter details:
   - **Name**: `tutorial-helper-api`
   - **Description**: `Service account for tutorial helper API`
4. Click "Create and Continue"
5. Grant roles:
   - Add role: **Storage Object Admin**
6. Click "Continue" -> "Done"

### Step 5: Create Service Account Key

1. Click on the service account you just created
2. Go to **Keys** tab
3. Click **Add Key** -> **Create new key**
4. Select **JSON** format
5. Click "Create"
6. Save the JSON file securely

**The downloaded JSON will look like:**
```json
{
  "type": "service_account",
  "project_id": "tutorial-helper-123456",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "tutorial-helper-api@tutorial-helper-123456.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

-> **Important**: Keep this file secure and never commit it to version control!

---

## Part 3: Local Development Setup

### Step 1: Clone and Install Backend Dependencies

```bash
cd tutorial_ui/api

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Backend Environment

Create `.env` file in `tutorial_ui/api/`:

```bash
cd tutorial_ui/api
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# GCP Configuration
# Paste the ENTIRE contents of your service account JSON as a single-line string
GCP_CREDENTIALS_JSON='{"type":"service_account","project_id":"tutorial-helper-123456","private_key_id":"abc123...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"tutorial-helper-api@...","client_id":"123456789","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/..."}'

# Your GCP bucket name from Step 3
GCP_BUCKET_NAME=tutorial-helper-videos-xyz

# Your GCP project ID
GCP_PROJECT_ID=tutorial-helper-123456

# Baseten Configuration (from Part 1, Step 4)
BASETEN_API_KEY=your-baseten-api-key-here
BASETEN_MODEL_ID=your-baseten-model-id-here
```

**Important Notes:**
- `GCP_CREDENTIALS_JSON` must be the entire JSON as a **single-line string** enclosed in single quotes
- Replace `tutorial-helper-videos-xyz` with your actual bucket name
- Replace the Baseten credentials with your actual values from Part 1

### Step 3: Start the Backend API

From `tutorial_ui/api/`:

```bash
# Option 1: Use the convenience script
./run.sh

# Option 2: Manual start
cd tutorial_ui
source api/.venv/bin/activate
uvicorn api.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

Verify it's running:
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

API documentation: `http://localhost:8000/docs`

### Step 4: Install Frontend Dependencies

Open a new terminal:

```bash
cd tutorial_ui

# Install dependencies with bun
bun install
```

### Step 5: Configure Frontend Environment (Optional)

Create `.env` in `tutorial_ui/` (optional - defaults work for local development):

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 6: Start the Frontend

```bash
bun run dev
```

The frontend will be available at `http://localhost:3000`

### Step 7: Access the Application

1. Open `http://localhost:3000` in your browser
2. Enter password: `tutorial123`
3. You'll be redirected to the upload page
4. Drag and drop a video file or click to browse
5. Click "Process Videos" to analyze
6. View timestamped descriptions in the timeline below

---

## Environment Variables Reference

### Backend (`tutorial_ui/api/.env`)

```bash
# GCP Cloud Storage Configuration
GCP_CREDENTIALS_JSON='<your-service-account-json-as-single-line-string>'
GCP_BUCKET_NAME=<your-bucket-name>
GCP_PROJECT_ID=<your-project-id>

# Baseten Model Configuration
BASETEN_API_KEY=<your-baseten-api-key>
BASETEN_MODEL_ID=<your-baseten-model-id>
```

### Frontend (`tutorial_ui/.env`) - Optional

```bash
# API endpoint (defaults to http://localhost:8000 if not set)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Project Structure

```
tutorialHelper/
├── model_deployment/           # Baseten model deployment
│   ├── tutorial_helper/
│   │   ├── model/
│   │   │   ├── __init__.py
│   │   │   └── model.py       # SmolVLM2 model inference
│   │   ├── requirements.txt    # Model dependencies
│   │   ├── data/              # Optional test data
│   │   └── packages/          # Optional custom packages
│   ├── main.py                # Local testing script
│   └── requirements.txt       # Deployment dependencies
│
└── tutorial_ui/                # Full-stack application
    ├── app/                    # Next.js app directory
    │   ├── page.tsx           # Login page
    │   ├── layout.tsx         # Root layout
    │   └── upload/
    │       └── page.tsx       # Video upload & results
    ├── components/             # React components
    │   ├── timeline.tsx       # Timeline visualization
    │   └── navigation.tsx     # Navigation component
    ├── lib/                    # Utilities
    │   ├── api/
    │   │   ├── client.ts      # API client with error handling
    │   │   └── types.ts       # TypeScript types
    │   └── utils.ts           # Utility functions
    ├── api/                    # FastAPI backend
    │   ├── main.py            # FastAPI app
    │   ├── routes.py          # API endpoints
    │   ├── blob.py            # GCP storage client
    │   ├── model_functions.py # Baseten client
    │   ├── settings.py        # Configuration
    │   ├── requirements.txt   # Backend dependencies
    │   ├── .env.example       # Environment template
    │   └── run.sh             # Startup script
    ├── package.json           # Frontend dependencies
    ├── tsconfig.json          # TypeScript config
    └── next.config.ts         # Next.js config
```

---

## API Endpoints

### `GET /health`
Health check endpoint.

**Response:**
```json
{"status": "healthy"}
```

### `POST /api/upload-video`
Upload and process a video file.

**Parameters:**
- `file` (multipart/form-data): Video file
- `prompt` (string, optional): Description prompt for the model. Default: "Describe what is happening in this frame."
- `mode` (string, optional): Processing mode - `timestamped` or `summary`. Default: `timestamped`

**Response (timestamped mode):**
```json
{
  "video_url": "https://storage.googleapis.com/...",
  "filename": "my-video.mp4",
  "result": {
    "frames": [
      {
        "timestamp": 0.0,
        "frame_number": 0,
        "description": "The instructor is standing in front of a whiteboard..."
      },
      {
        "timestamp": 2.5,
        "frame_number": 75,
        "description": "A diagram showing React components is being drawn..."
      }
    ]
  }
}
```

**Response (summary mode):**
```json
{
  "video_url": "https://storage.googleapis.com/...",
  "filename": "my-video.mp4",
  "result": {
    "description": "This tutorial video covers React fundamentals including..."
  }
}
```

### `GET /api/test-timeline`
Returns mock data for testing the timeline component without processing a real video.

---

## Development Commands

### Backend
```bash
cd tutorial_ui/api

# Activate environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
cd .. && uvicorn api.main:app --reload --port 8000

# Or use convenience script
./run.sh
```

### Frontend
```bash
cd tutorial_ui

# Install dependencies
bun install

# Run development server
bun run dev

# Build for production
bun run build

# Lint code
bun run lint

# Start production server
bun run start
```

### Model Deployment
```bash
cd model_deployment

# Test model locally (requires dependencies)
python main.py

# Deploy to Baseten
truss push --trusted tutorial_helper

# Check deployment status
truss logs tutorial_helper
```

---

## Troubleshooting

### Backend Issues

**"Cannot connect to GCP"**
- Verify `GCP_CREDENTIALS_JSON` is properly formatted as a single-line string
- Ensure the service account has "Storage Object Admin" role
- Check that Cloud Storage API is enabled in your GCP project

**"Bucket not found"**
- Verify `GCP_BUCKET_NAME` matches your actual bucket name
- Ensure the bucket exists in GCP Console
- Check bucket permissions allow your service account access

**"Baseten API error"**
- Verify `BASETEN_API_KEY` is correct (from Baseten Settings -> API Keys)
- Ensure `BASETEN_MODEL_ID` matches your deployed model
- Check model status in Baseten dashboard (should be "Active")
- Verify model has finished deploying (can take 10-15 minutes initially)

**"CORS errors"**
- Ensure frontend is running on `localhost:3000`
- Backend CORS is configured for `localhost:3000` only
- Check that both services are running

### Frontend Issues

**"Cannot connect to API"**
- Verify backend is running on port 8000
- Check `curl http://localhost:8000/health` returns success
- Verify no other service is using port 8000

**"Authentication failed"**
- Password is `tutorial123` (case-sensitive)
- Clear browser cache and sessionStorage
- Check browser console for errors

### Model Issues

**"Model deployment failed"**
- Ensure you ran `truss login` first
- Use `--trusted` flag: `truss push --trusted tutorial_helper`
- Check deployment logs: `truss logs tutorial_helper`

**"Model inference timeout"**
- First inference can take 30-60 seconds (model loads into memory)
- Subsequent requests should be faster
- Check video file size (large files take longer)

**"No frames extracted"**
- Ensure video codec is supported (MP4, MOV, AVI, WebM, MKV)
- Check video isn't corrupted
- Try a different video file

---

## Security Notes

-> **Important Security Practices:**

1. **Never commit `.env` files** - They contain sensitive credentials
2. **Keep GCP service account JSON secure** - Treat it like a password
3. **Rotate API keys regularly** - Both GCP and Baseten keys
4. **Use environment-specific buckets** - Separate buckets for dev/staging/production
5. **Review bucket permissions** - Ensure minimal required access
6. **Change default password** - The `tutorial123` password is for demo only

For production deployment:
- Use proper authentication (not hardcoded password)
- Enable HTTPS/TLS
- Set up proper CORS policies
- Use signed URLs with appropriate expiration times
- Enable GCP audit logging
- Implement rate limiting on API endpoints

---

## License

MIT

---

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review logs in terminal running the backend
3. Check browser console for frontend errors
4. Review Baseten dashboard for model status
