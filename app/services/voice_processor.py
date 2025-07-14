import asyncio
import io
import logging
import tempfile
import os
from typing import Optional, Dict, Any, List
from pydub import AudioSegment
import numpy as np
import soundfile as sf
from openai import OpenAI
import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

class VoiceProcessor:
    """
    Voice processing service for transcription and text-to-speech
    Uses OpenAI Whisper for transcription and TTS for speech synthesis
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.client = None
        self.supported_formats = ['mp3', 'wav', 'flac', 'm4a', 'ogg', 'webm']
        
    async def initialize(self):
        """Initialize the voice processor"""
        try:
            if not self.settings.openai_api_key:
                raise ValueError("OpenAI API key is required for voice processing")
            
            self.client = OpenAI(api_key=self.settings.openai_api_key)
            logger.info("Voice processor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize voice processor: {str(e)}")
            raise
    
    async def transcribe_audio(self, audio_content: bytes, language: str = "en") -> Optional[str]:
        """
        Transcribe audio content using OpenAI Whisper
        
        Args:
            audio_content: Raw audio bytes
            language: Language code (default: "en")
            
        Returns:
            Transcribed text or None if failed
        """
        try:
            # Create temporary file for audio processing
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
                
                # Convert audio to appropriate format
                processed_audio = await self._preprocess_audio(audio_content)
                temp_file.write(processed_audio)
                temp_file.flush()
                
                # Transcribe using OpenAI Whisper
                with open(temp_path, 'rb') as audio_file:
                    transcript = self.client.audio.transcriptions.create(
                        model=self.settings.whisper_model,
                        file=audio_file,
                        language=language,
                        response_format="text"
                    )
                
                # Clean up temporary file
                os.unlink(temp_path)
                
                # Validate transcription
                if isinstance(transcript, str) and transcript.strip():
                    logger.info(f"Transcription successful: {transcript[:100]}...")
                    return transcript.strip()
                else:
                    logger.warning("Empty transcription received")
                    return None
                    
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            return None
    
    async def _preprocess_audio(self, audio_content: bytes) -> bytes:
        """
        Preprocess audio for optimal transcription
        
        Args:
            audio_content: Raw audio bytes
            
        Returns:
            Processed audio bytes
        """
        try:
            # Load audio using pydub
            audio = AudioSegment.from_file(io.BytesIO(audio_content))
            
            # Convert to mono if stereo
            if audio.channels > 1:
                audio = audio.set_channels(1)
            
            # Set sample rate to 16kHz (optimal for Whisper)
            audio = audio.set_frame_rate(self.settings.audio_sample_rate)
            
            # Normalize audio levels
            audio = audio.normalize()
            
            # Apply noise reduction (simple implementation)
            audio = self._reduce_noise(audio)
            
            # Trim silence from beginning and end
            audio = self._trim_silence(audio)
            
            # Limit duration to prevent timeouts
            max_duration_ms = self.settings.max_audio_duration * 1000
            if len(audio) > max_duration_ms:
                audio = audio[:max_duration_ms]
                logger.warning(f"Audio truncated to {self.settings.max_audio_duration} seconds")
            
            # Export as WAV
            output_buffer = io.BytesIO()
            audio.export(output_buffer, format="wav")
            return output_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Audio preprocessing error: {str(e)}")
            return audio_content  # Return original if preprocessing fails
    
    def _reduce_noise(self, audio: AudioSegment) -> AudioSegment:
        """Simple noise reduction"""
        try:
            # Apply high-pass filter to remove low-frequency noise
            return audio.high_pass_filter(300)
        except Exception:
            return audio
    
    def _trim_silence(self, audio: AudioSegment, silence_threshold: int = -50) -> AudioSegment:
        """Trim silence from beginning and end"""
        try:
            # Find start and end of actual audio content
            start_trim = 0
            end_trim = len(audio)
            
            # Find first non-silent chunk
            chunk_size = 100  # 100ms chunks
            for i in range(0, len(audio), chunk_size):
                chunk = audio[i:i+chunk_size]
                if chunk.dBFS > silence_threshold:
                    start_trim = max(0, i - chunk_size)
                    break
            
            # Find last non-silent chunk
            for i in range(len(audio) - chunk_size, 0, -chunk_size):
                chunk = audio[i:i+chunk_size]
                if chunk.dBFS > silence_threshold:
                    end_trim = min(len(audio), i + chunk_size * 2)
                    break
            
            return audio[start_trim:end_trim]
            
        except Exception:
            return audio
    
    async def text_to_speech(self, text: str, voice: str = None) -> Optional[bytes]:
        """
        Convert text to speech using OpenAI TTS
        
        Args:
            text: Text to convert to speech
            voice: Voice to use (default from settings)
            
        Returns:
            Audio bytes or None if failed
        """
        try:
            if not text or not text.strip():
                logger.warning("Empty text provided for TTS")
                return None
            
            # Limit text length to prevent API errors
            max_text_length = 4000
            if len(text) > max_text_length:
                text = text[:max_text_length] + "..."
                logger.warning(f"Text truncated to {max_text_length} characters")
            
            # Use specified voice or default
            tts_voice = voice or self.settings.tts_voice
            
            # Generate speech
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=tts_voice,
                input=text,
                response_format="wav"
            )
            
            # Get audio content
            audio_content = response.content
            
            if audio_content:
                logger.info(f"TTS successful for text: {text[:50]}...")
                return audio_content
            else:
                logger.warning("Empty audio content from TTS")
                return None
                
        except Exception as e:
            logger.error(f"TTS error: {str(e)}")
            return None
    
    async def analyze_audio_properties(self, audio_content: bytes) -> Dict[str, Any]:
        """
        Analyze audio properties like duration, quality, etc.
        
        Args:
            audio_content: Raw audio bytes
            
        Returns:
            Dictionary with audio properties
        """
        try:
            audio = AudioSegment.from_file(io.BytesIO(audio_content))
            
            properties = {
                "duration_seconds": len(audio) / 1000.0,
                "sample_rate": audio.frame_rate,
                "channels": audio.channels,
                "format": audio.sample_width * 8,  # bits per sample
                "dBFS": audio.dBFS,
                "max_dBFS": audio.max_dBFS,
                "rms": audio.rms,
                "file_size_bytes": len(audio_content)
            }
            
            # Determine quality assessment
            quality_score = self._assess_audio_quality(audio)
            properties["quality_score"] = quality_score
            properties["quality_assessment"] = self._get_quality_description(quality_score)
            
            return properties
            
        except Exception as e:
            logger.error(f"Audio analysis error: {str(e)}")
            return {
                "duration_seconds": 0,
                "error": str(e)
            }
    
    def _assess_audio_quality(self, audio: AudioSegment) -> float:
        """Assess audio quality on a scale of 0-1"""
        try:
            score = 0.5  # Base score
            
            # Check sample rate
            if audio.frame_rate >= 16000:
                score += 0.2
            elif audio.frame_rate >= 8000:
                score += 0.1
            
            # Check audio level
            if -30 <= audio.dBFS <= -10:
                score += 0.2
            elif -40 <= audio.dBFS <= -5:
                score += 0.1
            
            # Check for clipping
            if audio.max_dBFS < -1:
                score += 0.1
            
            return min(1.0, max(0.0, score))
            
        except Exception:
            return 0.5
    
    def _get_quality_description(self, score: float) -> str:
        """Get quality description from score"""
        if score >= 0.8:
            return "excellent"
        elif score >= 0.6:
            return "good"
        elif score >= 0.4:
            return "fair"
        else:
            return "poor"
    
    async def create_audio_response(self, text: str, user_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create audio response with user preferences
        
        Args:
            text: Text to convert to speech
            user_preferences: User voice preferences
            
        Returns:
            Dictionary with audio data and metadata
        """
        try:
            # Extract voice preferences
            voice = None
            if user_preferences:
                voice = user_preferences.get("preferred_voice", self.settings.tts_voice)
            
            # Generate audio
            audio_content = await self.text_to_speech(text, voice)
            
            if not audio_content:
                return {
                    "success": False,
                    "error": "Failed to generate audio"
                }
            
            # Analyze audio properties
            properties = await self.analyze_audio_properties(audio_content)
            
            return {
                "success": True,
                "audio_content": audio_content,
                "properties": properties,
                "text": text,
                "voice_used": voice or self.settings.tts_voice
            }
            
        except Exception as e:
            logger.error(f"Audio response creation error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def batch_transcribe(self, audio_files: List[bytes]) -> List[Dict[str, Any]]:
        """
        Batch transcribe multiple audio files
        
        Args:
            audio_files: List of audio file bytes
            
        Returns:
            List of transcription results
        """
        tasks = []
        for i, audio_content in enumerate(audio_files):
            task = asyncio.create_task(
                self._transcribe_with_metadata(audio_content, i)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        transcriptions = []
        for result in results:
            if isinstance(result, Exception):
                transcriptions.append({
                    "success": False,
                    "error": str(result)
                })
            else:
                transcriptions.append(result)
        
        return transcriptions
    
    async def _transcribe_with_metadata(self, audio_content: bytes, index: int) -> Dict[str, Any]:
        """Transcribe audio with metadata"""
        try:
            # Analyze audio properties
            properties = await self.analyze_audio_properties(audio_content)
            
            # Transcribe
            transcription = await self.transcribe_audio(audio_content)
            
            return {
                "success": True,
                "index": index,
                "transcription": transcription,
                "properties": properties
            }
            
        except Exception as e:
            return {
                "success": False,
                "index": index,
                "error": str(e)
            }
    
    async def cleanup(self):
        """Cleanup resources"""
        # Close any open resources
        logger.info("Voice processor cleaned up successfully")
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported audio formats"""
        return self.supported_formats.copy()
    
    async def validate_audio_file(self, audio_content: bytes) -> Dict[str, Any]:
        """
        Validate audio file for processing
        
        Args:
            audio_content: Raw audio bytes
            
        Returns:
            Validation result
        """
        try:
            # Check file size
            if len(audio_content) > self.settings.max_file_size:
                return {
                    "valid": False,
                    "error": f"File size exceeds maximum ({self.settings.max_file_size} bytes)"
                }
            
            # Try to load audio
            audio = AudioSegment.from_file(io.BytesIO(audio_content))
            
            # Check duration
            duration_seconds = len(audio) / 1000.0
            if duration_seconds > self.settings.max_audio_duration:
                return {
                    "valid": False,
                    "error": f"Audio duration exceeds maximum ({self.settings.max_audio_duration} seconds)"
                }
            
            # Check if audio has content
            if duration_seconds < 0.1:
                return {
                    "valid": False,
                    "error": "Audio file is too short"
                }
            
            return {
                "valid": True,
                "duration_seconds": duration_seconds,
                "file_size_bytes": len(audio_content),
                "format_info": {
                    "sample_rate": audio.frame_rate,
                    "channels": audio.channels,
                    "bits_per_sample": audio.sample_width * 8
                }
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Invalid audio file: {str(e)}"
            } 