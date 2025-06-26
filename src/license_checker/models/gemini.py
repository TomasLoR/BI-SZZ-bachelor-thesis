from .base_model import BaseModel
from google import genai
import requests

class Gemini(BaseModel):
    """
    Implementation of the BaseModel interface using Google's Gemini model.
    
    This class handles the communication with Google AI's API to generate
    summaries and answer questions about Terms of Service texts using
    the Gemini model.
    """
    
    def __init__(self, api_key=None):
        """
        Initialize the Gemini model with the specific model identifier.
        
        Args:
            api_key (str, optional): API key for the Google AI API
        """
        super().__init__('gemini-2.5-pro-exp-03-25', api_key)

    def summarize(self, data):
        """
        Summarize Terms of Service text using the Gemini model.
        
        Args:
            data (dict): Dictionary containing website data with content to summarize
            
        Returns:
            dict: Updated data dictionary with added 'summary' field
            
        Raises:
            ValueError: If the data validation fails, the API key is invalid or not set
            Exception: If there's an error in API communication
        """
        # Call parent method to check if API key is set
        super().summarize(data)
        
        self._validate_summary_data(data)
        client = genai.Client(api_key=self.api_key)

        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=self._prepare_prompt(data),
            )
            data['summary'] = response.text.strip()
        except Exception as e:
            raise ValueError(f"Failed to generate summary: {str(e)}")

        return data

    def answer_question(self, data, question):
        """
        Answer a question about Terms of Service summary using the Gemini model.
        
        Args:
            data (dict): Dictionary containing website data with summary
            question (str): Question to answer about the Terms of Service
            
        Returns:
            str: Answer to the question about the Terms of Service
            
        Raises:
            ValueError: If the data validation fails, the API key is invalid or not set
            Exception: If there's an error in API communication
        """
        # Call parent method to check if API key is set
        super().answer_question(data, question)
        
        self._validate_question_data(data, question)
        client = genai.Client(api_key=self.api_key)

        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=self._prepare_prompt(data, question),
            )
            return response.text.strip()
        except Exception as e:
            raise ValueError(f"Failed to answer question: {str(e)}")