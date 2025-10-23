from transformers import AutoProcessor, AutoModelForImageTextToText
import torch
from PIL import Image
import cv2
import tempfile
import os
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Model:
    def __init__(self, **kwargs):
        self.model_id = "HuggingFaceTB/SmolVLM2-500M-Video-Instruct"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = None
        self.model = None

    def load(self):
        self.processor = AutoProcessor.from_pretrained(self.model_id)
        self.model = AutoModelForImageTextToText.from_pretrained(
            self.model_id,
            dtype=torch.float32,
            device_map="auto" if torch.cuda.is_available() else None,
            low_cpu_mem_usage=True
        ).to(self.device).eval()

    def sample_frames(self, video_path, num_frames=8):
        """Extracts evenly spaced frames from video with timestamps"""
        cap = cv2.VideoCapture(video_path)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        interval = max(1, total // num_frames)
        frames = []
        for i in range(0, total, interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if not ret:
                continue
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            timestamp = i / fps if fps > 0 else 0
            frames.append({"image": img, "timestamp": timestamp, "frame_number": i})
        cap.release()
        return frames

    def predict(self, request):
        video_url = request.get("video_url")
        if not video_url:
            logger.error("Missing video_url in request")
            return {"error": "video_url is required"}

        prompt = request.get("prompt", "Describe what is happening in this frame.")
        mode = request.get("mode", "timestamped")

        logger.info(f"=== MODEL PREDICTION STARTED ===")
        logger.info(f"Video URL: {video_url}")
        logger.info(f"Mode: {mode}")
        logger.info(f"Prompt: {prompt}")

        tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        try:
            logger.info("Downloading video from storage...")
            response = requests.get(video_url, timeout=30, stream=True)
            response.raise_for_status()

            with open(tmpfile.name, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info(f"Video downloaded successfully to {tmpfile.name}")

            logger.info("Extracting frames from video...")
            frame_data = self.sample_frames(tmpfile.name)
            if not frame_data:
                logger.error("Failed to extract frames from video")
                return {"error": "No frames could be extracted from video"}

            logger.info(f"Extracted {len(frame_data)} frames")

            if mode == "timestamped":
                logger.info("Processing frames individually for timestamped descriptions...")
                descriptions = []
                for idx, frame_info in enumerate(frame_data):
                    logger.info(f"Processing frame {idx + 1}/{len(frame_data)} - Timestamp: {frame_info['timestamp']:.2f}s")

                    formatted_prompt = f"<image>{prompt}"

                    inputs = self.processor(
                        text=formatted_prompt,
                        images=[frame_info["image"]],
                        return_tensors="pt",
                        padding=True
                    ).to(self.device)

                    with torch.no_grad():
                        output = self.model.generate(**inputs, max_new_tokens=100)

                    text = self.processor.batch_decode(output, skip_special_tokens=True)[0]
                    logger.info(f"Frame {idx + 1} description: {text[:100]}...")

                    descriptions.append({
                        "timestamp": round(frame_info["timestamp"], 2),
                        "frame_number": frame_info["frame_number"],
                        "description": text
                    })

                logger.info(f"=== MODEL PREDICTION COMPLETE ===")
                logger.info(f"Generated {len(descriptions)} timestamped descriptions")
                return {"frames": descriptions}
            else:
                logger.info("Processing all frames for summary description...")
                images = [f["image"] for f in frame_data]

                formatted_prompt = f"<image>{prompt}"

                inputs = self.processor(text=formatted_prompt, videos=images, return_tensors="pt", padding=True).to(self.device)

                with torch.no_grad():
                    output = self.model.generate(**inputs, max_new_tokens=200)

                text = self.processor.batch_decode(output, skip_special_tokens=True)[0]
                logger.info(f"=== MODEL PREDICTION COMPLETE ===")
                logger.info(f"Summary description: {text[:100]}...")
                return {"description": text}

        except requests.RequestException as e:
            logger.error(f"Failed to download video: {str(e)}")
            return {"error": f"Failed to download video: {str(e)}"}
        except Exception as e:
            logger.error(f"Processing failed: {str(e)}", exc_info=True)
            return {"error": f"Processing failed: {str(e)}"}
        finally:
            if os.path.exists(tmpfile.name):
                os.unlink(tmpfile.name)
                logger.info("Temporary video file cleaned up")
