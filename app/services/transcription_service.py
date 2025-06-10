"""
Transcription service module.

This module contains business logic for transcribing audio files using Whisper.
"""
import os
import tempfile
import logging
import time
from typing import Dict, Any, Optional, BinaryIO, List, Tuple
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)

class AudioTranscriber:
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the audio transcriber with the given configuration.
        
        Args:
            config: Configuration dictionary containing model settings
        """
        self.config = config
        self.model_name = config.get('whisper_model', 'base')
        self.device = config.get('device', 'cpu')
        
        # Load the Whisper model
        logger.info(f"Loading Whisper model: {self.model_name}")
        
        # Set compute type based on device
        if self.device == "cuda":
            compute_type = config.get('compute_type', "float16")
            # For CUDA, we can use float16 or int8_float16 for better performance
            if compute_type not in ["float16", "int8_float16"]:
                compute_type = "float16"
        else:
            compute_type = config.get('compute_type', "int8")
            # For CPU, we can use int8 or float32
            if compute_type not in ["int8", "float32"]:
                compute_type = "int8"
                
        logger.info(f"Using compute type: {compute_type}")
        
        # Initialize the model
        self.model = WhisperModel(
            self.model_name, 
            device=self.device, 
            compute_type=compute_type,
            download_root=config.get('model_dir', None),
            cpu_threads=config.get('cpu_threads', 4)
        )
        
        logger.info(f"Audio transcriber initialized with model: {self.model_name}, device: {self.device}, compute_type: {compute_type}")

    def transcribe_audio(self, audio_file: BinaryIO, language: Optional[str] = None, 
    word_timestamps: bool = False, vad_filter: bool = True) -> Dict[str, Any]:
        """
        Transcribe audio file using Whisper.
        
        Args:
            audio_file: The audio file to transcribe
            language: Optional language code to use for transcription
            word_timestamps: Whether to include word-level timestamps
            vad_filter: Whether to use VAD (Voice Activity Detection) to filter out non-speech
            
        Returns:
            A dictionary containing the transcription results
        """
        try:
            # Create a temporary file to save the uploaded audio
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
                temp_audio.write(audio_file.read())
                temp_audio_path = temp_audio.name
            
            logger.info(f"Transcribing audio file: {temp_audio_path}")
            
            start_time = time.time()
            
            # Set transcription options
            beam_size = self.config.get('beam_size', 5)
            
            # Configure VAD parameters if enabled
            vad_parameters = None
            if vad_filter:
                vad_parameters = {
                    'threshold': 0.5,
                    'min_speech_duration_ms': 250,
                    'min_silence_duration_ms': 2000,
                    'speech_pad_ms': 400
                }
            
            # Perform transcription
            segments, info = self.model.transcribe(
                temp_audio_path,
                beam_size=beam_size,
                language=language if language else None,
                task="transcribe",
                word_timestamps=word_timestamps,
                vad_filter=vad_filter,
                vad_parameters=vad_parameters,
                condition_on_previous_text=self.config.get('condition_on_previous_text', True)
            )
            
            # Process segments and build result
            transcription = ""
            segment_list = []
            word_list = []
            
            # Convert generator to list to ensure complete transcription
            segments_list = list(segments)
            
            for segment in segments_list:
                transcription += segment.text + " "
                
                # Add segment info
                segment_data = {
                    "id": segment.id,
                    "seek": segment.seek,
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text,
                    "tokens": segment.tokens,
                    "temperature": segment.temperature,
                    "avg_logprob": segment.avg_logprob,
                    "compression_ratio": segment.compression_ratio,
                    "no_speech_prob": segment.no_speech_prob
                }
                
                # Add word timestamps if requested
                if word_timestamps and segment.words:
                    segment_data["words"] = [
                        {
                            "start": word.start,
                            "end": word.end,
                            "word": word.word,
                            "probability": word.probability
                        }
                        for word in segment.words
                    ]
                    
                    # Also add to global word list
                    for word in segment.words:
                        word_list.append({
                            "start": word.start,
                            "end": word.end,
                            "word": word.word,
                            "probability": word.probability
                        })
                
                segment_list.append(segment_data)
            
            # Create result dictionary
            result = {
                "text": transcription.strip(),
                "language": info.language,
                "language_probability": info.language_probability,
                "duration": time.time() - start_time,
                "segments": segment_list
            }
            
            # Add word timestamps if requested
            if word_timestamps:
                result["words"] = word_list
            
            # Clean up the temporary file
            os.unlink(temp_audio_path)
            
            logger.info(f"Transcription completed in {result['duration']:.2f} seconds")
            
            return {
                "text": result["text"],
                "language": result.get("language", language),
                "duration": result["duration"],
                "segments": result.get("segments", []),
                "success": True,
                "message": "Audio transcribed successfully"
            }
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return {
                "text": "",
                "language": None,
                "duration": None,
                "segments": [],
                "success": False,
                "message": f"Error transcribing audio: {str(e)}"
            }
