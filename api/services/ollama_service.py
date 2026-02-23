"""
Ollama service for connecting to local LLM on Raspberry Pi.
Handles chat completions with educational prompts.
"""
import logging
import requests
from typing import Optional, List, Dict, Generator
from django.conf import settings

logger = logging.getLogger(__name__)


class OllamaService:
    """
    Service class for interacting with Ollama API.
    Designed for Raspberry Pi 4B with 4GB RAM.
    """

    def __init__(self):
        self.host = getattr(settings, 'OLLAMA_HOST', 'http://localhost:11434')
        self.model = getattr(settings, 'OLLAMA_MODEL', 'tinyllama')
        self.timeout = getattr(settings, 'OLLAMA_TIMEOUT', 120)
        self.system_prompt = getattr(settings, 'LOKAL_SYSTEM_PROMPT', '')

    def is_available(self) -> bool:
        """Check if Ollama service is available."""
        try:
            response = requests.get(
                f"{self.host}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except requests.RequestException as e:
            logger.warning(f"Ollama not available: {e}")
            return False

    def get_available_models(self) -> List[str]:
        """Get list of available models from Ollama."""
        try:
            response = requests.get(
                f"{self.host}/api/tags",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except requests.RequestException as e:
            logger.error(f"Failed to get Ollama models: {e}")
            return []

    def chat(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        subject: Optional[str] = None
    ) -> str:
        """
        Send a chat message to Ollama and get a response.
        
        Args:
            message: The user's question/message
            conversation_history: Optional list of previous messages
            subject: Optional subject area for context
            
        Returns:
            The AI assistant's response text
        """
        # Build messages array with system prompt
        messages = []
        
        # Add system prompt with optional subject context
        system_prompt = self.system_prompt
        if subject:
            system_prompt += f"\n\nCurrent subject focus: {subject}"
        
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": message
        })

        try:
            response = requests.post(
                f"{self.host}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        # Optimize for Raspberry Pi 4B (4GB RAM)
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 500,  # Limit response length for Pi
                        "num_ctx": 2048,     # Reduced context window (saves RAM)
                        "num_batch": 256,    # Smaller batch size for 4GB RAM
                        "num_thread": 4,     # Match Pi 4 core count
                    }
                },
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("message", {}).get("content", "I apologize, I couldn't generate a response.")
            else:
                logger.error(f"Ollama error: {response.status_code} - {response.text}")
                return self._fallback_response(message)

        except requests.Timeout:
            logger.error("Ollama request timed out")
            return "I'm sorry, I'm taking too long to think. Could you ask a simpler question?"
        except requests.RequestException as e:
            logger.error(f"Ollama request failed: {e}")
            return self._fallback_response(message)

    def chat_stream(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        subject: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Send a chat message and stream the response.
        Useful for showing progress on slower Pi hardware.
        
        Yields:
            Chunks of the response text as they arrive
        """
        messages = []
        
        system_prompt = self.system_prompt
        if subject:
            system_prompt += f"\n\nCurrent subject focus: {subject}"
        
        messages.append({"role": "system", "content": system_prompt})
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": message})

        try:
            response = requests.post(
                f"{self.host}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": True,
                    "options": {
                        # Optimize for Raspberry Pi 4B (4GB RAM)
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 500,
                        "num_ctx": 2048,     # Reduced context window (saves RAM)
                        "num_batch": 256,    # Smaller batch size for 4GB RAM
                        "num_thread": 4,     # Match Pi 4 core count
                    }
                },
                timeout=self.timeout,
                stream=True
            )

            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            import json
                            data = json.loads(line)
                            content = data.get("message", {}).get("content", "")
                            if content:
                                yield content
                            if data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue
            else:
                yield self._fallback_response(message)

        except requests.RequestException as e:
            logger.error(f"Ollama stream failed: {e}")
            yield self._fallback_response(message)

    def _fallback_response(self, question: str) -> str:
        """
        Provide a fallback response when Ollama is unavailable.
        """
        return (
            "I'm sorry, I'm having trouble connecting to my thinking engine right now. "
            "Please make sure Ollama is running on this device. "
            "You can start it by running 'ollama serve' in a terminal."
        )

    def generate_summary(self, text: str, max_length: int = 50) -> str:
        """
        Generate a short summary of text (for conversation titles).
        
        Args:
            text: The text to summarize
            max_length: Maximum length of summary
            
        Returns:
            A short summary string
        """
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"Summarize this in 5 words or less: {text}",
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 20,
                    }
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                summary = data.get("response", "")[:max_length]
                return summary.strip()
        except requests.RequestException:
            pass
        
        # Fallback: just truncate the text
        return text[:max_length] + ("..." if len(text) > max_length else "")


# Singleton instance for easy import
ollama_service = OllamaService()
