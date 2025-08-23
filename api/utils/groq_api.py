import json
import os
from api.config.env_loader import get_groq_api_key

class GroqAPI:
    """Groq API implementation"""
    
    def __init__(self):
        self.api_key = get_groq_api_key()
        self.model = "openai/gpt-oss-120b"  # You can change this to other Groq models
    
    def load_conversation_history(self):
        """Load conversation history from JSON file"""
        try:
            conversation_file = 'data/conversation_data.json'
            if os.path.exists(conversation_file):
                with open(conversation_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"Conversation file not found at: {conversation_file}")
                return []
        except Exception as e:
            print(f"Error loading conversation history: {e}")
            return []
    
    def load_profile_data(self):
        """Load profile data from JSON file"""
        try:
            profile_file = 'data/myprofile.json'
            if os.path.exists(profile_file):
                with open(profile_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"Profile file not found at: {profile_file}")
                return {}
        except Exception as e:
            print(f"Error loading profile data: {e}")
            return {}
    
    def build_messages(self, query, relevant_context, conversation_history):
        """Build messages array for Groq API"""
        messages = []
        
        # System message with profile context
        profile_data = self.load_profile_data()
        profile_summary = self._create_profile_summary(profile_data)
        
        system_message = f"""You are Mushini Gopala Swamy, working as Senior Software Engineer.

You are in the job search process and need to answer recruiters based on your profile.

IMPORTANT: Base your responses primarily on the profile information provided below. If specific details aren't available, you can provide general professional responses or politely indicate that you don't have specific information about certain topics. Be helpful and conversational while staying truthful to your profile.

PROFILE INFORMATION:
{profile_summary}

RELEVANT CONTEXT FOR THIS QUESTION:
{chr(10).join([f"- {ctx}" for ctx in relevant_context])}

Please provide a clear, professional answer as if you are Mushini Gopala Swamy responding to a recruiter. Use the profile information and context above to give accurate and helpful answers about your experience, skills, and preferences.

If the context doesn't contain specific information about something, you can:
- Provide general professional insights related to the topic
- Politely mention that you don't have specific details about that particular aspect
- Redirect the conversation to areas where you do have relevant information

Remember to maintain consistency with your previous responses in the conversation history."""
        
        messages.append({"role": "system", "content": system_message})
        
        # Add conversation history
        for conv in conversation_history:
            messages.append({"role": "user", "content": conv["userQuestion"]})
            messages.append({"role": "assistant", "content": conv["modelAnswer"]})
        
        # Add current query
        messages.append({"role": "user", "content": query})
        
        return messages
    
    def _create_profile_summary(self, profile_data):
        """Create a concise summary of profile data"""
        summary_parts = []
        
        # Basic info
        if profile_data.get('name'):
            summary_parts.append(f"Name: {profile_data['name']}")
        if profile_data.get('current_role'):
            summary_parts.append(f"Current Role: {profile_data['current_role']}")
        if profile_data.get('current_company'):
            summary_parts.append(f"Company: {profile_data['current_company']}")
        if profile_data.get('experience_years'):
            summary_parts.append(f"Experience: {profile_data['experience_years']} years")
        if profile_data.get('current_location'):
            summary_parts.append(f"Location: {profile_data['current_location']}")
        
        # Skills summary
        if profile_data.get('skills'):
            skills = profile_data['skills']
            skill_summary = []
            for category, skill_list in skills.items():
                if isinstance(skill_list, list):
                    skill_summary.append(f"{category}: {', '.join(skill_list[:3])}")
            if skill_summary:
                summary_parts.append(f"Key Skills: {'; '.join(skill_summary)}")
        
        # Job preferences
        if profile_data.get('job_preferences'):
            prefs = profile_data['job_preferences']
            if prefs.get('current_ctc'):
                summary_parts.append(f"Current CTC: {prefs['current_ctc']}")
            if prefs.get('expected_ctc'):
                summary_parts.append(f"Expected CTC: {prefs['expected_ctc']}")
            if prefs.get('negotiable_notice_period'):
                summary_parts.append(f"Notice Period: {prefs['negotiable_notice_period']} days")
        
        return "\n".join(summary_parts)
    
    def generate_response_with_context(self, query, relevant_context):
        """Generate response using Groq API with context and conversation history"""
        try:
            # Import Groq client here to avoid import issues
            from groq import Groq
            
            # Load conversation history
            conversation_history = self.load_conversation_history()
            
            # Build messages for Groq
            messages = self.build_messages(query, relevant_context, conversation_history)
            
            # Create Groq client
            client = Groq(api_key=self.api_key)
            
            print(f"🤖 Sending request to Groq with {len(messages)} messages")
            print(f"📝 Current query: {query}")
            
            # Create completion
            completion = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                top_p=0.95
            )
            
            # Get the response content
            response_content = completion.choices[0].message.content
            
            return response_content
                
        except Exception as e:
            print(f"Error generating response with Groq: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
