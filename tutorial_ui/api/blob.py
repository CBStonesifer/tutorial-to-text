import json
import uuid
from datetime import datetime, timedelta
from google.cloud import storage
from google.oauth2 import service_account
from .settings import settings


class BlobStorage:
    def __init__(self):
        if settings.gcp_credentials_json:
            credentials_info = json.loads(settings.gcp_credentials_json)
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info
            )
            self.client = storage.Client(
                credentials=credentials,
                project=settings.gcp_project_id or credentials_info.get("project_id")
            )
        else:
            self.client = storage.Client(project=settings.gcp_project_id)

        self.bucket = self.client.bucket(settings.gcp_bucket_name)

    def upload_video(self, video_data: bytes, filename: str) -> str:
        file_extension = filename.split(".")[-1] if "." in filename else "mp4"
        destination_name = f"videos/{datetime.now().strftime('%Y%m%d')}/{uuid.uuid4()}.{file_extension}"

        content_type_map = {
            "mp4": "video/mp4",
            "mov": "video/quicktime",
            "avi": "video/x-msvideo",
            "webm": "video/webm",
            "mkv": "video/x-matroska"
        }
        content_type = content_type_map.get(file_extension.lower(), "video/mp4")

        blob = self.bucket.blob(destination_name)
        blob.upload_from_string(video_data, content_type=content_type)

        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(hours=1),
            method="GET"
        )

        return signed_url
