"""
Transcriptions endpoints module.

This module contains API routes for audio transcription using Whisper.
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from app.schemas.transcriptions import TranscriptionResponse
from app.services.transcription_service import AudioTranscriber
from app.core.config import load_config

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Load configuration
config = load_config()

# Initialize components
transcriber = AudioTranscriber(config)

@router.post("/", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: Optional[str] = Form(None),
    word_timestamps: bool = Form(False),
    vad_filter: bool = Form(True),
):
    """
    Transcribe an audio file using Whisper.
    
    Args:
        audio: The audio file to transcribe
        language: Optional language code to use for transcription
        
    Returns:
        A response containing the transcription results
    """
    try:
        logger.info(f"Received audio file: {audio.filename}, size: {audio.size}, content_type: {audio.content_type}")
        
        # Check if file is empty
        if not audio.size:
            return TranscriptionResponse(
                text="",
                success=False,
                message="Audio file cannot be empty"
            )
        
        # Check file type
        allowed_content_types = [
            "audio/wav", "audio/x-wav", "audio/mp3", "audio/mpeg", 
            "audio/ogg", "audio/flac", "audio/x-flac"
        ]
        
        if audio.content_type not in allowed_content_types and not audio.filename.endswith(('.wav', '.mp3', '.ogg', '.flac')):
            return TranscriptionResponse(
                text="",
                success=False,
                message=f"Unsupported file type: {audio.content_type}. Supported types: WAV, MP3, OGG, FLAC"
            )
        
        # Process with Whisper
        logger.info(f"Transcribing audio with language: {language or 'auto-detect'}, word_timestamps: {word_timestamps}, vad_filter: {vad_filter}")
        result = transcriber.transcribe_audio(
            audio_file=audio.file, 
            language=language,
            word_timestamps=word_timestamps,
            vad_filter=vad_filter
        )
        
        if result["success"]:
            return TranscriptionResponse(
                text=result["text"],
                language=result["language"],
                duration=result["duration"],
                success=True,
                message="Audio transcribed successfully"
            )
        else:
            return TranscriptionResponse(
                text="",
                success=False,
                message=result["message"]
            )
            
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error transcribing audio: {str(e)}")
