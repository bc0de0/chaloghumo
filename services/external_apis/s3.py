import asyncio
import json
from typing import Any

import boto3

from core.config import settings


class S3Service:
    """
    Service for dumping raw analytical signals and session logs into the
    S3 Landing Zone (Bronze Layer) for Snowflake ingestion.
    """

    def __init__(self):
        self.enabled = all(
            [
                settings.AWS_ACCESS_KEY_ID,
                settings.AWS_SECRET_ACCESS_KEY,
                settings.S3_BUCKET_NAME,
            ]
        )
        if self.enabled:
            self.s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )

    async def upload_session_log(self, session_id: str, payload: dict[str, Any]):
        """
        Uploads a JSON session log to S3.
        This triggers Snowpipe auto-ingestion into RAW_BRONZE.
        """
        if not self.enabled:
            print(f"S3 Upload Skipped (Disabled): {session_id}")
            return False

        try:
            # Execute in thread to avoid blocking event loop
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._execute_upload,
                f"sessions/{session_id}.json",
                json.dumps(payload, indent=2),
            )
            return True
        except Exception as e:
            print(f"S3 Upload Error: {e}")
            return False

    def _execute_upload(self, key: str, data: str):
        self.s3.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=key,
            Body=data,
            ContentType="application/json",
        )


s3_service = S3Service()
