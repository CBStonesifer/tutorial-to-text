from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from .blob import BlobStorage
from .model_functions import BasetenClient
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/test-timeline")
async def test_timeline():
    return {
        "video_url": "https://example.com/test-video.mp4",
        "filename": "test_video.mp4",
        "result": {
            "frames": [
                {
                    "timestamp": 0.0,
                    "frame_number": 0,
                    "description": "A person is standing in front of a whiteboard with a marker in hand, preparing to start the tutorial."
                },
                {
                    "timestamp": 0.3,
                    "frame_number": 9,
                    "description": "The instructor begins writing the title 'Introduction to React' on the whiteboard."
                },
                {
                    "timestamp": 0.6,
                    "frame_number": 18,
                    "description": "A diagram showing the React component lifecycle is being drawn on the board."
                },
                {
                    "timestamp": 0.9,
                    "frame_number": 27,
                    "description": "The instructor points to the 'useState' hook explanation on the whiteboard."
                },
                {
                    "timestamp": 1.2,
                    "frame_number": 36,
                    "description": "A code example demonstrating useState is being written on the board."
                },
                {
                    "timestamp": 1.5,
                    "frame_number": 45,
                    "description": "The instructor gestures to emphasize the importance of component props."
                },
                {
                    "timestamp": 1.8,
                    "frame_number": 54,
                    "description": "A new section titled 'useEffect Hook' is being added to the whiteboard."
                },
                {
                    "timestamp": 2.1,
                    "frame_number": 63,
                    "description": "The instructor demonstrates the cleanup function in useEffect with arrows and annotations."
                },
                {
                    "timestamp": 2.4,
                    "frame_number": 72,
                    "description": "A comparison table between class components and functional components is drawn."
                },
                {
                    "timestamp": 2.7,
                    "frame_number": 81,
                    "description": "The instructor concludes by pointing to the key takeaways section on the whiteboard."
                }
            ]
        }
    }

class VideoProcessResponse(BaseModel):
    video_url: str
    description: str | None = None
    error: str | None = None

@router.post("/upload-video")
async def upload_video(
    file: UploadFile = File(...),
    prompt: str = Form("Describe what is happening in this frame."),
    mode: str = Form("timestamped")
):
    try:
        logger.info(f"=== VIDEO UPLOAD STARTED ===")
        logger.info(f"Filename: {file.filename}")
        logger.info(f"Content type: {file.content_type}")
        logger.info(f"Mode: {mode}")
        logger.info(f"Prompt: {prompt}")

        video_data = await file.read()
        logger.info(f"Video size: {len(video_data) / (1024*1024):.2f} MB")

        blob_storage = BlobStorage()
        logger.info("Uploading to GCS bucket...")
        video_url = blob_storage.upload_video(video_data, file.filename)

        logger.info(f"=== VIDEO STORED SUCCESSFULLY ===")
        logger.info(f"Storage URL: {video_url}")

        logger.info("Calling Baseten model for inference...")
        baseten_client = BasetenClient()
        result = baseten_client.predict(
            data={
                "video_url": video_url,
                "prompt": prompt,
                "mode": mode
            }
        )

        logger.info(f"=== MODEL RESPONSE RECEIVED ===")
        if "frames" in result:
            logger.info(f"Received {len(result['frames'])} frame descriptions")
        elif "description" in result:
            logger.info(f"Received summary description")
        elif "error" in result:
            logger.error(f"Model returned error: {result['error']}")
        else:
            logger.warning(f"Unexpected response format: {result.keys()}")

        return {
            "video_url": video_url,
            "filename": file.filename,
            "result": result
        }
    except Exception as e:
        logger.error(f"Upload and processing failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-video")
async def process_video(
    file: UploadFile = File(...),
    prompt: str = Form("Describe what is happening in this frame."),
    mode: str = Form("timestamped")
):
    try:
        logger.info(f"=== VIDEO PROCESSING STARTED ===")
        logger.info(f"Filename: {file.filename}")
        logger.info(f"Mode: {mode}")
        logger.info(f"Prompt: {prompt}")

        video_data = await file.read()
        logger.info(f"Video size: {len(video_data) / (1024*1024):.2f} MB")

        blob_storage = BlobStorage()
        logger.info("Uploading to GCS bucket...")
        video_url = blob_storage.upload_video(video_data, file.filename)
        logger.info(f"Video stored: {video_url}")

        logger.info("Calling Baseten model...")
        baseten_client = BasetenClient()
        result = baseten_client.predict(
            data={
                "video_url": video_url,
                "prompt": prompt,
                "mode": mode
            }
        )

        logger.info(f"=== MODEL RESPONSE RECEIVED ===")
        if "frames" in result:
            logger.info(f"Received {len(result['frames'])} frame descriptions")
        elif "description" in result:
            logger.info(f"Received summary description")
        else:
            logger.warning(f"Unexpected response format: {result.keys()}")

        return {
            "video_url": video_url,
            "result": result
        }
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
