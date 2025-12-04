"""AI assistant service using Google Gemini"""

import google.generativeai as genai
from typing import List, Dict, Optional


class AIAssistant:
    """Wrapper for Gemini API with domain-specific prompts"""
    
    # Domain-specific system prompts
    DOMAIN_PROMPTS = {
        "cybersecurity": """You are a cybersecurity expert for a Multi-Domain Intelligence Platform.
Analyse security incidents, explain attack vectors, and provide NIST/MITRE ATT&CK recommendations.
Use professional terminology. Format: Clear, structured responses with bullet points.""",
        
        "datascience": """You are a data science expert for a Multi-Domain Intelligence Platform.
Analyse datasets, recommend techniques, explain statistical methods, and suggest visualisations.
Use professional tone. Format: Clear explanations with practical examples.""",
        
        "itoperations": """You are an IT operations expert for a Multi-Domain Intelligence Platform.
Troubleshoot issues, recommend best practices, and provide step-by-step resolution guides.
Use solution-oriented tone. Format: Clear, actionable steps with explanations.""",
        
        "general": """You are a helpful assistant for a Multi-Domain Intelligence Platform.
Provide professional, accurate advice across Cybersecurity, Data Science, and IT Operations."""
    }
    
    def __init__(self, api_key: str, default_model: str = "gemini-1.5-flash"):
        """Initialise Gemini AI assistant"""
        genai.configure(api_key=api_key)
        
        # Generation configuration
        self._generation_config = {
            "temperature": 1.0,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        self._model_name = default_model
        self._current_domain = "general"
        self._conversation_history: List[Dict[str, str]] = []
        self._system_prompt = self.DOMAIN_PROMPTS["general"]
        
        # Initialise model
        self._initialize_model()
    
    def _initialize_model(self):
        """Create Gemini model with system instruction"""
        self._model = genai.GenerativeModel(
            model_name=self._model_name,
            generation_config=self._generation_config,
            system_instruction=self._system_prompt
        )
        self._chat = self._model.start_chat(history=[])
    
    def set_domain(self, domain: str) -> None:
        """Set AI domain context for specialised responses"""
        domain_lower = domain.lower()
        if domain_lower in self.DOMAIN_PROMPTS:
            self._current_domain = domain_lower
            self._system_prompt = self.DOMAIN_PROMPTS[domain_lower]
            self._initialize_model()  # Reinitialise with new prompt
        else:
            self._current_domain = "general"
            self._system_prompt = self.DOMAIN_PROMPTS["general"]
            self._initialize_model()
    
    def get_current_domain(self) -> str:
        """Return currently active domain"""
        return self._current_domain
    
    def clear_conversation(self) -> None:
        """Clear conversation history"""
        self._conversation_history = []
        self._chat = self._model.start_chat(history=[])
    
    def send_message(self, user_message: str, context: Optional[str] = None, stream: bool = False):
        """Send message to AI and get response"""
        # Build full message with context
        full_message = user_message
        if context:
            full_message = f"{user_message}\n\nContext:\n{context}"
        
        # Add to history
        self._conversation_history.append({"role": "user", "content": full_message})
        
        try:
            if stream:
                return self._stream_response(full_message)
            else:
                # Get complete response
                response = self._chat.send_message(full_message)
                response_text = response.text
                
                # Add to history
                self._conversation_history.append({"role": "assistant", "content": response_text})
                
                return response_text
        except Exception as e:
            error_message = f"AI Error: {str(e)}"
            return error_message
    
    def _stream_response(self, message: str):
        """Stream response chunks (compatible with Streamlit)"""
        try:
            response = self._chat.send_message(message, stream=True)
            
            full_response = ""
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    # Yield in OpenAI-compatible format for Streamlit
                    yield type('obj', (object,), {
                        'choices': [type('obj', (object,), {
                            'delta': type('obj', (object,), {
                                'content': chunk.text
                            })()
                        })()]
                    })()
            
            # Add complete response to history
            self._conversation_history.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            error_text = f"Streaming error: {str(e)}"
            yield type('obj', (object,), {
                'choices': [type('obj', (object,), {
                    'delta': type('obj', (object,), {'content': error_text})()
                })()]
            })()
    
    def analyse_incident(self, incident_data: str) -> str:
        """Analyse security incident with domain-specific prompt"""
        self.set_domain("cybersecurity")
        prompt = f"""Analyse this security incident and provide:
1. Assessment of threat severity
2. Potential attack vectors
3. Recommended immediate actions
4. Long-term preventive measures

Incident Details:
{incident_data}"""
        return self.send_message(prompt)
    
    def analyse_dataset(self, dataset_data: str) -> str:
        """Analyse dataset with domain-specific prompt"""
        self.set_domain("datascience")
        prompt = f"""Analyse this dataset and provide:
1. Assessment of characteristics
2. Potential use cases
3. Recommended analysis techniques
4. Data quality considerations

Dataset Details:
{dataset_data}"""
        return self.send_message(prompt)
    
    def analyse_ticket(self, ticket_data: str) -> str:
        """Analyse IT ticket with domain-specific prompt"""
        self.set_domain("itoperations")
        prompt = f"""Analyse this IT ticket and provide:
1. Assessment of the issue
2. Likely root causes
3. Step-by-step troubleshooting
4. Preventive recommendations

Ticket Details:
{ticket_data}"""
        return self.send_message(prompt)
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get full conversation history"""
        return self._conversation_history
    
    def __str__(self) -> str:
        return f"AIAssistant(domain={self._current_domain}, model={self._model_name})"