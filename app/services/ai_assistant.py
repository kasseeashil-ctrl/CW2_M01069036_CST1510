"""AI assistant service using Google Gemini (OpenAI-compatible structure)"""

import google.generativeai as genai
from typing import List, Dict, Optional


class AIAssistant:
    """Gemini API wrapper following OpenAI patterns from Week 10 Lab"""
    
    def __init__(self, api_key: str, default_model: str = "gemini-2.0-flash"):
        genai.configure(api_key=api_key)
        self._model_name = default_model
        self._model = genai.GenerativeModel(model_name=self._model_name)
        self._chat = None
        self._messages: List[Dict[str, str]] = []
    
    def _get_system_prompt(self) -> Optional[str]:
        """Extract system prompt from messages"""
        for msg in self._messages:
            if msg["role"] == "system":
                return msg["content"]
        return None
    
    def _convert_messages_for_gemini(self) -> List[Dict]:
        """Convert OpenAI format to Gemini format"""
        gemini_history = []
        for msg in self._messages:
            if msg["role"] == "system":
                continue
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})
        return gemini_history
    
    def set_messages(self, messages: List[Dict[str, str]]) -> None:
        """Set conversation messages (OpenAI format)"""
        self._messages = messages
        
        system_prompt = self._get_system_prompt()
        if system_prompt:
            self._model = genai.GenerativeModel(
                model_name=self._model_name,
                system_instruction=system_prompt
            )
        
        history = self._convert_messages_for_gemini()
        if len(history) > 1:
            self._chat = self._model.start_chat(history=history[:-1])
        else:
            self._chat = self._model.start_chat(history=[])
    
    def chat_completions_create(self, messages: List[Dict[str, str]], stream: bool = False, temperature: float = 1.0):
        """
        OpenAI-compatible completion method
        Mirrors: client.chat.completions.create()
        """
        self.set_messages(messages)
        
        last_message = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                last_message = msg["content"]
                break
        
        if not last_message:
            return self._create_response("No user message found")
        
        try:
            if stream:
                return self._stream_response(last_message)
            else:
                response = self._chat.send_message(last_message)
                return self._create_response(response.text)
        except Exception as e:
            return self._create_response(f"Error: {str(e)}")
    
    def _create_response(self, content: str):
        """Create OpenAI-compatible response object"""
        return type('ChatCompletion', (), {
            'choices': [
                type('Choice', (), {
                    'message': type('Message', (), {
                        'content': content,
                        'role': 'assistant'
                    })()
                })()
            ]
        })()
    
    def _stream_response(self, message: str):
        """
        Stream response in OpenAI-compatible format
        Yields chunks with: chunk.choices[0].delta.content
        """
        try:
            response = self._chat.send_message(message, stream=True)
            
            for chunk in response:
                if chunk.text:
                    yield type('StreamChunk', (), {
                        'choices': [
                            type('Choice', (), {
                                'delta': type('Delta', (), {
                                    'content': chunk.text
                                })()
                            })()
                        ]
                    })()
        except Exception as e:
            # Yield each chunk in OpenAI-compatible format
            yield type('StreamChunk', (), {
                'choices': [
                    type('Choice', (), {
                        'delta': type('Delta', (), {
                            'content': f"Error: {str(e)}"
                        })()
                    })()
                ]
            })()
    
    def clear_conversation(self) -> None:
        """Clear conversation history"""
        self._messages = []
        self._chat = self._model.start_chat(history=[])
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Get current messages"""
        return self._messages


class GeminiClient:
    """
    OpenAI-compatible client wrapper
    Usage mirrors: client = OpenAI(api_key=...)
    """
    
    def __init__(self, api_key: str):
        self._assistant = AIAssistant(api_key)
        self.chat = self._ChatCompletions(self._assistant)
    
    class _ChatCompletions:
        def __init__(self, assistant: AIAssistant):
            self._assistant = assistant
            self.completions = self # Allow client.chat.completions.create() syntax
        
        def create(self, model: str, messages: List[Dict[str, str]], stream: bool = False, temperature: float = 1.0):
            """
            OpenAI-compatible method
            Usage: client.chat.completions.create(model=..., messages=..., stream=...)
            """
            return self._assistant.chat_completions_create(messages, stream, temperature)