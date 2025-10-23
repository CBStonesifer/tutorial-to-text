# Tutorial Helper API

FastAPI backend for Tutorial Helper with GCP Cloud Storage and Baseten model integration.

## Setup

### 1. Create Python Virtual Environment

```bash
cd tutorial_ui/api
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```
GCP_CREDENTIALS_PATH=/path/to/your/service-account-key.json
GCP_BUCKET_NAME=your-bucket-name
BASETEN_API_KEY=your-baseten-api-key
BASETEN_MODEL_ID=your-default-model-id
```

## GCP Setup Instructions

### Step 1: Create a GCP Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name (e.g., "tutorial-helper")
4. Click "Create"

### Step 2: Enable Cloud Storage API

1. In the Cloud Console, navigate to "APIs & Services" → "Library"
2. Search for "Cloud Storage API"
3. Click on it and press "Enable"

### Step 3: Create a Storage Bucket

1. Navigate to "Cloud Storage" → "Buckets"
2. Click "Create Bucket"
3. Configure your bucket:
   - Name: Choose a globally unique name (e.g., "tutorial-helper-videos")
   - Location: Choose a region close to your users
   - Storage class: Standard (or Nearline for cost savings)
   - Access control: Fine-grained
4. Click "Create"

### Step 4: Set Bucket Permissions (Optional - for public access)

If you want files to be publicly accessible:

1. Go to your bucket
2. Click "Permissions" tab
3. Click "Grant Access"
4. Add principal: `allUsers`
5. Role: "Storage Object Viewer"
6. Click "Save"

### Step 5: Create a Service Account

1. Navigate to "IAM & Admin" → "Service Accounts"
2. Click "Create Service Account"
3. Enter details:
   - Name: "tutorial-helper-api"
   - Description: "Service account for tutorial helper API"
4. Click "Create and Continue"
5. Grant roles:
   - "Storage Object Admin" (full control over objects)
   - Or "Storage Object Creator" and "Storage Object Viewer" (more restrictive)
6. Click "Continue" then "Done"

### Step 6: Create and Download Service Account Key

1. Click on the service account you just created
2. Go to "Keys" tab
3. Click "Add Key" → "Create new key"
4. Select "JSON" format
5. Click "Create"
6. Save the JSON file securely (e.g., `~/credentials/tutorial-helper-key.json`)
7. Update `GCP_CREDENTIALS_PATH` in your `.env` file with this path

**Important**: Keep this file secure and never commit it to version control!

### Step 7: Update Environment Variables

Update your `.env` file:

```
GCP_CREDENTIALS_PATH=/absolute/path/to/tutorial-helper-key.json
GCP_BUCKET_NAME=tutorial-helper-videos
```

## Baseten Setup Instructions

### Step 1: Get Baseten API Key

1. Go to [Baseten](https://baseten.co/)
2. Sign in or create an account
3. Navigate to Settings → API Keys
4. Create a new API key or copy existing one
5. Update `BASETEN_API_KEY` in your `.env` file

### Step 2: Deploy Your Model (if needed)

If you need to deploy a model:

1. Follow Baseten's model deployment guide
2. Get your model ID from the model dashboard
3. Update `BASETEN_MODEL_ID` in your `.env` file

## Running the API

### Development Mode

```bash
uvicorn api.main:app --reload --port 8000
```

### Production Mode

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## API Endpoints

### Health Check
- `GET /health` - Check API status

### Video Processing
- `POST /api/process-video` - Upload video to GCP bucket and run model prediction

## Example Usage

### Process a Video

```bash
curl -X POST "http://localhost:8000/api/process-video" \
  -F "file=@video.mp4" \
  -F "prompt=Describe this video in detail."
```

Response:
```json
{
  "video_url": "https://storage.googleapis.com/your-bucket/videos/20241022/abc123.mp4",
  "description": "The video shows..."
}
```

## Troubleshooting

### Authentication Error

If you get authentication errors:
- Verify your service account key path is correct
- Ensure the key file has proper read permissions
- Check that the service account has the necessary roles

### Bucket Access Error

If you can't access the bucket:
- Verify the bucket name is correct
- Ensure your service account has proper permissions
- Check that Cloud Storage API is enabled

### Baseten API Error

If Baseten requests fail:
- Verify your API key is correct
- Check that your model ID is valid
- Ensure your account has proper permissions
