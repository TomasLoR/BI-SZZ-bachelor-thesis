from .base_model import BaseModel
from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError

class Mistral(BaseModel):
    """
    Implementation of the BaseModel interface using Mistral model from Hugging Face.
    
    This class handles the communication with Hugging Face's Inference API
    to generate summaries and answer questions about Terms of Service texts
    using the Mixtral-8x7B-Instruct model.
    """
    
    def __init__(self, api_key=None):
        """
        Initialize the Mistral model with the specific model identifier.
        
        Args:
            api_key (str, optional): API key for the Hugging Face API
        """
        super().__init__('mistralai/Mixtral-8x7B-Instruct-v0.1', api_key)

    def summarize(self, data):
        """
        Summarize Terms of Service text using the Mistral model.
        
        Args:
            data (dict): Dictionary containing website data with content to summarize
            
        Returns:
            dict: Updated data dictionary with added 'summary' field
            
        Raises:
            ValueError: If the data validation fails, the API key is invalid or not set
        """
        # Call parent method to check if API key is set
        super().summarize(data)
        
        self._validate_summary_data(data)
        client = InferenceClient(model=self.model_name, token=self.api_key)

        try:
            response = client.text_generation(
            prompt=self._prepare_prompt(data),
            temperature=0.2,
            max_new_tokens=1000,
            return_full_text=False
        )
        except HfHubHTTPError:
           raise ValueError("Invalid API key: Failed to authenticate with Hugging Face API")

        data['summary'] = response.strip()
        return data

    def answer_question(self, data, question):
        """
        Answer a question about Terms of Service summary using the Mistral model.
        
        Args:
            data (dict): Dictionary containing website data with summary
            question (str): Question to answer about the Terms of Service
            
        Returns:
            str: Answer to the question about the Terms of Service
            
        Raises:
            ValueError: If the data validation fails, the API key is invalid or not set
        """
        # Call parent method to check if API key is set
        super().answer_question(data, question)
        
        self._validate_question_data(data, question)
        client = InferenceClient(model=self.model_name, token=self.api_key)
        try:
            response = client.text_generation(
                prompt=self._prepare_prompt(data, question),
                temperature=0.4,
                max_new_tokens=1000,
                return_full_text=False
            )
        except HfHubHTTPError:
            raise ValueError("Invalid API key: Failed to authenticate with Hugging Face API")

        return response.strip()