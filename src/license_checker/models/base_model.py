from abc import ABC, abstractmethod

class BaseModel(ABC):
    """    
    This class defines the interface that all model implementations must follow,
    including methods for summarizing Terms of Service text and answering questions
    about them.
    """
    
    def __init__(self, model_name, api_key=None):
        """
        Initialize a BaseModel instance.
        
        Args:
            model_name (str): The name of the model being instantiated
            api_key (str, optional): The API key for accessing the model service
        """
        self.model_name = model_name
        self.api_key = api_key

    def set_api_key(self, api_key):
        """
        Set or update the API key for the model.
        
        Args:
            api_key (str): The API key for accessing the model service
        """
        self.api_key = api_key

    def _prepare_prompt(self, data, question=None):
        """
        Prepare the prompt to be sent to the language model.
        
        Args:
            data (dict): Dictionary containing website data including content and/or summary
            question (str, optional): Question to be asked about the ToS. Defaults to None.
            
        Returns:
            str: Formatted prompt ready to be sent to the language model
        """
        if question:
            return (
                f"Summary of the Terms of Service text:\n{data['summary']}\n\n"
                f"Answer the following question about the ToS summary:\n{question}"
            )
        return f"Summarize the following Terms of Service text from {data['website']}:\n{data['content']}"

    def _validate_summary_data(self, data):
        """
        Validate the data needed for summarization.
        
        Args:
            data (dict): Dictionary containing website data
            
        Raises:
            ValueError: If required fields are missing from the data
        """
        if 'content' not in data or not data['content']:
            raise ValueError("Missing required content in website data")
        if 'website' not in data or not data['website']:
            raise ValueError("Missing website identifier")
    
    def _validate_question_data(self, data, question):
        """
        Validate the data needed for answering questions.
        
        Args:
            data (dict): Dictionary containing website data
            question (str): The question to be answered
            
        Raises:
            ValueError: If required fields are missing from the data or question is empty
        """
        if 'summary' not in data or not data['summary']:
            raise ValueError("Missing summary in website data")
        if not question:
            raise ValueError("Missing question data")

    @abstractmethod
    def summarize(self, data):
        """
        Summarize Terms of Service text.
        
        Args:
            data (dict): Dictionary containing website data with content to summarize
            
        Returns:
            str: Summarized Terms of Service text
            
        Raises:
            ValueError: If the API key is not set
            NotImplementedError: If the implementing class does not override this method
        """
        if not self.api_key:
            raise ValueError("API key is not set")

    @abstractmethod
    def answer_question(self, data, question):
        """
        Answer a question about Terms of Service summary.
        
        Args:
            data (dict): Dictionary containing website data with summary
            question (str): Question to answer about the Terms of Service
            
        Returns:
            str: Answer to the question about the Terms of Service
            
        Raises:
            ValueError: If the API key is not set
            NotImplementedError: If the implementing class does not override this method
        """
        if not self.api_key:
            raise ValueError("API key is not set")