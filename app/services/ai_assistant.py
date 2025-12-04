"""
AI Assistant Service
Provides domain-specific AI analysis using OpenAI's GPT models
"""

from openai import OpenAI
from typing import List, Dict, Optional


class AIAssistant:
    """
    Wrapper for OpenAI API with domain-specific system prompts.
    
    Provides specialised AI assistance for Cybersecurity, Data Science,
    and Operations domains with context-aware responses.
    """
    
    # Domain-specific system prompts
    DOMAIN_PROMPTS = {
        "cybersecurity": """You are a cybersecurity expert assistant for a Multi-Domain Intelligence Platform.

Your responsibilities:
- Analyse security incidents and provide technical assessments
- Explain attack vectors, vulnerabilities, and threat actors
- Recommend mitigation strategies following industry standards (NIST, ISO 27001, MITRE ATT&CK)
- Provide actionable security recommendations
- Use professional terminology appropriate for security analysts

Tone: Professional, technical, and precise
Format: Clear, structured responses with bullet points for recommendations""",
        
        "datascience": """You are a data science expert assistant for a Multi-Domain Intelligence Platform.

Your responsibilities:
- Analyse dataset characteristics and provide insights
- Recommend appropriate data processing and analysis techniques
- Explain statistical methods and machine learning approaches
- Suggest data visualisation strategies
- Help troubleshoot data quality issues

Tone: Professional and educational
Format: Clear explanations with practical examples""",
        
        "itoperations": """You are an IT operations expert assistant for a Multi-Domain Intelligence Platform.

Your responsibilities:
- Troubleshoot IT issues and provide technical solutions
- Recommend best practices for system administration
- Explain infrastructure concepts and technologies
- Provide step-by-step resolution guides
- Prioritise urgent issues and suggest preventive measures

Tone: Professional and solution-oriented
Format: Clear, actionable steps with explanations""",
        
        "general": """You are a helpful assistant for a Multi-Domain Intelligence Platform covering Cybersecurity, Data Science, and IT Operations.

Provide professional, accurate, and actionable advice across these domains."""
    }
    
    def __init__(self, api_key: str, default_model: str = "gpt-4o-mini"):

        """
        Initialise the AIAssistant with OpenAI credentials.
        
        Args:
            api_key: OpenAI API key
            default_model: GPT model to use (default: 'gpt-4o')
        """
        self._client = OpenAI(api_key=api_key)
        self._model = default_model
        self._current_domain = "general"
        self._conversation_history: List[Dict[str, str]] = []
        self._system_prompt = self.DOMAIN_PROMPTS["general"]
    
    def set_domain(self, domain: str) -> None:
        """
        Set the AI domain context for specialised responses.
        
        Args:
            domain: Domain name ('cybersecurity', 'datascience', 'itoperations', or 'general')
        """
        domain_lower = domain.lower()
        if domain_lower in self.DOMAIN_PROMPTS:
            self._current_domain = domain_lower
            self._system_prompt = self.DOMAIN_PROMPTS[domain_lower]
            print(f"🤖 AI Assistant domain set to: {domain}")
        else:
            print(f"⚠️ Unknown domain '{domain}', using 'general' instead")
            self._current_domain = "general"
            self._system_prompt = self.DOMAIN_PROMPTS["general"]
    
    def get_current_domain(self) -> str:
        """Return the currently active domain."""
        return self._current_domain
    
    def clear_conversation(self) -> None:
        """Clear the conversation history to start fresh."""
        self._conversation_history = []
        print("🧹 Conversation history cleared")
    
    def send_message(
        self, 
        user_message: str,
        context: Optional[str] = None,
        stream: bool = False
    ) -> str:
        """
        Send a message to the AI and get a response.
        
        Args:
            user_message: The user's question or request
            context: Optional additional context (e.g., incident details)
            stream: Whether to stream the response (for Streamlit UI)
            
        Returns:
            The AI's response as a string
            
        Example:
            response = ai.send_message(
                "What is a phishing attack?",
                context="User reported suspicious email with urgent payment request"
            )
        """
        # Build the full message with context if provided
        full_message = user_message
        if context:
            full_message = f"{user_message}\n\nContext:\n{context}"
        
        # Add user message to history
        self._conversation_history.append({
            "role": "user",
            "content": full_message
        })
        
        # Build messages array with system prompt
        messages = [
            {"role": "system", "content": self._system_prompt}
        ] + self._conversation_history
        
        try:
            # Call OpenAI API
            if stream:
                # Return the stream object for Streamlit to handle
                return self._client.chat.completions.create(
                    model=self._model,
                    messages=messages,
                    stream=True
                )
            else:
                # Get complete response
                completion = self._client.chat.completions.create(
                    model=self._model,
                    messages=messages
                )
                
                response = completion.choices[0].message.content
                
                # Add assistant response to history
                self._conversation_history.append({
                    "role": "assistant",
                    "content": response
                })
                
                return response
        
        except Exception as e:
            error_message = f"AI Error: {str(e)}"
            print(f"❌ {error_message}")
            return error_message
    
    def analyse_incident(self, incident_data: str) -> str:
        """
        Analyse a security incident and provide recommendations.
        
        Args:
            incident_data: Formatted incident details
            
        Returns:
            Analysis and recommendations from the AI
        """
        self.set_domain("cybersecurity")
        prompt = f"""Analyse this security incident and provide:
1. Assessment of the threat severity
2. Potential attack vectors or vulnerabilities exploited
3. Recommended immediate actions
4. Long-term preventive measures

Incident Details:
{incident_data}"""
        
        return self.send_message(prompt)
    
    def analyse_dataset(self, dataset_data: str) -> str:
        """
        Analyse a dataset and provide insights.
        
        Args:
            dataset_data: Formatted dataset metadata
            
        Returns:
            Analysis and recommendations from the AI
        """
        self.set_domain("datascience")
        prompt = f"""Analyse this dataset and provide:
1. Assessment of the dataset characteristics
2. Potential use cases and applications
3. Recommended analysis techniques
4. Data quality considerations

Dataset Details:
{dataset_data}"""
        
        return self.send_message(prompt)
    
    def analyse_ticket(self, ticket_data: str) -> str:
        """
        Analyse an IT ticket and suggest solutions.
        
        Args:
            ticket_data: Formatted ticket details
            
        Returns:
            Troubleshooting steps and recommendations from the AI
        """
        self.set_domain("itoperations")
        prompt = f"""Analyse this IT support ticket and provide:
1. Assessment of the issue
2. Likely root causes
3. Step-by-step troubleshooting guide
4. Preventive recommendations

Ticket Details:
{ticket_data}"""
        
        return self.send_message(prompt)
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get the full conversation history.
        
        Returns:
            List of message dictionaries with 'role' and 'content' keys
        """
        return self._conversation_history
    
    def __str__(self) -> str:
        """Return a string representation of the AI assistant."""
        return f"AIAssistant(domain={self._current_domain}, model={self._model})"