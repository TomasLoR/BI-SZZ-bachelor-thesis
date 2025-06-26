import json
import ast
import os
from license_checker import LicenseDetector, ModelManager
from .database import Database

class Services:
    """    
    This class provides methods to scan websites for licensing information,
    summarize the results using AI models, and answer questions about the analyzed websites.
    It uses a separate Database class for data storage and retrieval.
    """
    def __init__(self):
        self.detector = LicenseDetector()
        self.model_manager = ModelManager()
        self.db = Database()
        self.models = {}


    def scan_websites(self, urls):
        """
        Scan websites for licensing information and store the results.
        
        Args:
            urls (list): A list of URLs to scan.
            
        Returns:
            str: A unique identifier for the stored scan results.
            
        Raises:
            ValueError: If no valid URLs are provided.
        """
        self._validate_urls(urls)
        results = self.detector.scan_websites(urls)
        return self.db.store_scan_results(results)

    def summarize_results(self, raw_result, selected_api, api_key):
        """
        Summarize scan results using the selected API.
        
        Args:
            raw_result (str): Raw scan results to summarize.
            selected_api (str): The name of the API model to use (e.g., 'huggingface', 'googleai').
            api_key (str): API key for the selected API.
            
        Returns:
            str: A unique identifier for the stored summary data.
                  
        Raises:
            ValueError: If inputs are invalid or processing fails.
        """
        if not raw_result:
            raise ValueError("No scan results provided")
        
        result = self._parse_raw_result(raw_result)
        
        model = self._get_model(selected_api, api_key)
        summary_data = self._generate_summary(model, result)
        
        result_id = self.db.store_summary_data(summary_data)
        
        return result_id

    def retrieve_summary_data(self, result_id):
        """
        Retrieve summary data from database.
        
        Args:
            result_id (str): The unique identifier for the stored data.
            
        Returns:
            dict: The retrieved summary data.
            
        Raises:
            ValueError: If the result_id is not provided or data is not found.
        """
        return self.db.get_summary_data(result_id)

    def answer_question(self, result_id, question, selected_api, api_key):
        """
        Answer a question based on summary data using the selected API.
        
        Args:
            result_id (str): The unique identifier for the stored summary data.
            question (str): The question to answer.
            selected_api (str): The name of the API model to use.
            api_key (str): API key for the selected API.
            
        Returns:
            str: A unique identifier for the stored answer.
            
        Raises:
            ValueError: If inputs are invalid or processing fails.
        """
        if not question:
            raise ValueError("No question provided")
            
        summary_data = self.retrieve_summary_data(result_id)
        
        model = self._get_model(selected_api, api_key)
        answer = self._process_question(summary_data, question, model)
        
        answer_id = self.db.store_answer(result_id, question, answer)
        
        return answer_id

    def retrieve_scan_results(self, result_id):
        """
        Retrieve scan results from database.
        
        Args:
            result_id (str): The unique identifier for the stored results.
            
        Returns:
            list: The retrieved scan results.
            
        Raises:
            ValueError: If the result_id is not provided or data is not found.
        """
        return self.db.get_scan_results(result_id)
            
    def retrieve_answer(self, answer_id):
        """
        Retrieve answer data from database.
        
        Args:
            answer_id (str): The unique identifier for the stored answer.
            
        Returns:
            dict: The retrieved answer data.
            
        Raises:
            ValueError: If the answer_id is not provided or data is not found.
        """
        return self.db.get_answer(answer_id)

    def _validate_urls(self, urls):
        """
        Validate URL inputs.
        
        Args:
            urls (list): A list of URLs to validate.
            
        Raises:
            ValueError: If no valid URLs are provided.
        """
        if not urls or not isinstance(urls, list):
            raise ValueError("No valid URLs provided")

    def _parse_raw_result(self, raw_result):
        """
        Parse raw result string to Python object.
        
        Args:
            raw_result (str): Raw scan results in string format.
            
        Returns:
            dict: Parsed scan results as a Python dictionary.
            
        Raises:
            ValueError: If the raw result format is invalid.
        """
        try:
            return ast.literal_eval(raw_result)
        except (ValueError, SyntaxError) as e:
            raise ValueError(f"Invalid scan result format: {str(e)}")

    def _generate_summary(self, model, result):
        """
        Generate summary using the selected model.
        
        Args:
            model (object): The model instance to use for summarization.
            result (dict): The scan results to summarize.
            
        Returns:
            dict: Summarized results.
            
        Raises:
            ValueError: If summarization fails or API authentication fails.
        """
        try:
            return model.summarize(result)
        except Exception as e:
            if "API" in str(e):
                raise ValueError(f"API authentication failed: {str(e)}")
            else:
                raise ValueError(f"Error generating summary: {str(e)}")

    def _process_question(self, summary_data, question, model):
        """
        Process question and return answer.
        
        Args:
            summary_data (dict): The summary data to analyze.
            question (str): The question to answer.
            model (object): The model instance to use for answering.
            
        Returns:
            str: The answer to the question.
            
        Raises:
            ValueError: If processing fails or API authentication fails.
        """
        try:
            return model.answer_question(summary_data, question)
        except Exception as e:
            if "API" in str(e):
                raise ValueError(f"API authentication failed: {str(e)}")
            else:
                raise ValueError(f"Error generating answer: {str(e)}")

    def _get_model(self, selected_api, api_key):
        """
        Get or create a model instance for the selected API.
        
        Args:
            selected_api (str): The API model name.
            api_key (str): API key for the selected API.
            
        Returns:
            object: The model instance.
            
        Raises:
            ValueError: If the API model is invalid or not selected.
        """
        if not selected_api:
            raise ValueError("No API selected")
            
        if not api_key:
            raise ValueError(f"No API key provided for {selected_api}")
        
        if selected_api in self.models:
            model = self.models[selected_api]
            model.set_api_key(api_key)
            return model
            
        model = self.model_manager.get_model(selected_api, api_key)
        if not model:
            raise ValueError(f"Invalid API selected: {selected_api}")
            
        self.models[selected_api] = model
            
        return model