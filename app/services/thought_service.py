"""
Thought service module.

This module contains business logic for processing thoughts.
"""
import logging
import signal
from typing import Dict, Any, Optional
from ollama import Client
from app.schemas.thoughts import ThoughtAnalysisResult

logger = logging.getLogger(__name__)

class TextAnalyzer:
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the text analyzer with the given configuration.
        
        Args:
            config: Configuration dictionary containing model, URL, and timeout settings
        """
        self.config = config
        self.ollama_model = config['model']
        self.ollama_url = config.get('url', 'http://localhost:11434')
        self.timeout = config.get('timeout', 30)  # Default timeout: 30 seconds
        
        # Initialize Ollama client with configured URL
        self.client = Client(host=self.ollama_url)
        
        logger.info(f"Text analyzer initialized with model: {self.ollama_model}, URL: {self.ollama_url}, timeout: {self.timeout}s")

    def analyze_with_ollama(self, text: str) -> Dict[str, Any]:
        """
        Analyze text to extract insights using Ollama structured output.
        
        Args:
            text: The text to analyze
            
        Returns:
            A dictionary containing the analysis results
        """
        try:
            prompt = f"""
You are an AI assistant designed to help a senior DevOps engineer organize and manage their thoughts.

Your job is to take a raw, unstructured thought and return the following information in JSON format:

- processed: A cleaned-up, structured version of the thought suitable for later reflection.
- categories: List of categories this thought relates to. Example: ["infrastructure", "team", "idea", "bug", "workflow", "infra as code"].
- tags: Relevant tags or keywords related to the thought.
- type: What kind of thought is this? One of: ["idea", "task", "observation", "reminder", "question", "note"].
- priority: Optional. If you detect urgency, label it as "low", "medium", or "high".
- summary: A short summary of the core idea in the thought.

Respond ONLY with a valid JSON matching this schema.

Thought:
{text}
"""
            logger.info(f"Sending request to Ollama at {self.ollama_url} with timeout {self.timeout}s")
            try:
                # Set a timeout for the request
                import signal
                
                # Define timeout handler
                def timeout_handler(signum, frame):
                    raise TimeoutError(f"Ollama request timed out after {self.timeout} seconds")
                
                # Set the timeout
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(self.timeout)
                
                # Make the request
                response = self.client.chat(
                    model=self.ollama_model,
                    messages=[{
                        'role': 'user',
                        'content': prompt,
                    }],
                    format=ThoughtAnalysisResult.model_json_schema(),
                )
                
                # Cancel the timeout if request completes successfully
                signal.alarm(0)
            except TimeoutError as e:
                logger.error(f"Timeout error: {str(e)}")
                raise
            
            logger.info("Received response from Ollama")
            print("\n--- RAW OLLAMA RESPONSE ---\n", response['message']['content'], "\n--- END RAW RESPONSE ---\n")
            result = ThoughtAnalysisResult.model_validate_json(response['message']['content'])
            return result.model_dump()
        except Exception as e:
            logger.error(f"Error analyzing text with Ollama: {str(e)}")
            return {
                'processed': '',
                'categories': [],
                'tags': [],
                'type': 'note',
                'priority': None,
                'summary': ''
            }
