"""
S3 Service Module for ChaloGhumo.

This module provides the analytical bridge, dumping raw session logs and 
cognitive signals into the AWS S3 Landing Zone (Bronze Layer). These files 
serve as the source for Snowpipe automated ingestion into Snowflake.
"""

import asyncio
import json
from typing import Any, Dict

import boto3

from core.config import settings


class S3Service:
    """
    Data Ingestion Layer (AWS S3).
    
    Responsible for persisting raw reasoning outputs to cloud storage for 
    downstream analytical processing.
    """

    def __init__(self):
        """
        Initializes the S3 client.
        
        Checks for required AWS credentials and bucket configuration before 
        activating the client.
        """
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

    async def upload_session_log(self, session_id: str, payload: Dict[str, Any]) -> bool:
        """
        Uploads a structured JSON session log to the Bronze landing zone.
        
        Args:
            session_id: Unique identifier for the reasoning session.
            payload: The full cognitive snapshot to be persisted.
            
        Returns:
            True if upload was successful, False otherwise.
        """
        if not self.enabled:
            # We fail silently to avoid disrupting the primary reasoning flow.
            print(f"S3 Upload Skipped (Disabled): {session_id}")
            return False

        try:
            # boto3 is a synchronous SDK; we use an executor to keep the 
            # FastAPI event loop responsive during I/O.
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
        """Synchronous wrapper for the boto3 put_object operation."""
        self.s3.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=key,
            Body=data,
            ContentType="application/json",
        )


# Singleton service instance
s3_service = S3Service()
