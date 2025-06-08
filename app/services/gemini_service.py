import google.generativeai as genai
from app.core.config import settings
from app.schemas.chat import UserInfo
from typing import List, Dict

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def _build_context(self, user_info: UserInfo = None) -> str:
        """Build context from user information"""
        if not user_info:
            return ""
        
        context_parts = []
        
        if user_info.firstName or user_info.lastName:
            name = f"{user_info.firstName or ''} {user_info.lastName or ''}".strip()
            context_parts.append(f"User's name: {name}")
        
        if user_info.weight:
            context_parts.append(f"Current weight: {user_info.weight}kg")
        
        if user_info.weightGoal:
            context_parts.append(f"Weight goal: {user_info.weightGoal}kg")
        
        if user_info.height:
            context_parts.append(f"Height: {user_info.height}cm")
        
        if user_info.job:
            context_parts.append(f"Occupation: {user_info.job}")
        
        if user_info.fitnessLevel:
            context_parts.append(f"Fitness level: {user_info.fitnessLevel}")
        
        if user_info.fitnessGoal:
            context_parts.append(f"Fitness goal: {user_info.fitnessGoal}")
        
        if user_info.healthCondition:
            context_parts.append(f"Health condition: {user_info.healthCondition}")
        
        if user_info.allergy:
            context_parts.append(f"Allergies: {user_info.allergy}")
        
        if context_parts:
            return "User context:\n" + "\n".join(context_parts) + "\n\n"
        
        return ""
    
    async def generate_response(
        self, 
        message: str, 
        conversation_history: List[Dict[str, str]] = None,
        user_info: UserInfo = None
    ) -> str:
        """Generate response using Gemini API"""
        try:
            # Build the prompt with context
            context = self._build_context(user_info)
            
            # Build conversation history
            chat_history = []
            if conversation_history:
                for msg in conversation_history:
                    if msg['role'] == 'user':
                        chat_history.append(f"User: {msg['content']}")
                    else:
                        chat_history.append(f"Assistant: {msg['content']}")
            
            # Construct the full prompt
            full_prompt = context
            if chat_history:
                full_prompt += "Previous conversation:\n" + "\n".join(chat_history[-10:]) + "\n\n"
            full_prompt += f"User: {message}\nAssistant:"
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            return response.text
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again."

gemini_service = GeminiService()