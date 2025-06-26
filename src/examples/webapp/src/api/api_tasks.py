from celery import Celery
from license_checker import ModelManager, LicenseDetector
import os

# Dictionary to cache models
_model_cache = {}

# Configure Celery with Redis as the broker
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
celery_app = Celery('tasks', broker=redis_url, backend=redis_url, broker_connection_retry_on_startup=True)

def _get_cached_model(selected_api, api_key):
    """
    Get or create a model instance for the selected API.
    
    This function implements a caching mechanism for language models to avoid
    recreating model instances for each request, improving performance.
    
    Args:
        selected_api (str): The API model name (e.g., 'gemini', 'mistral').
        api_key (str): API key for the selected API.
        
    Returns:
        object: The model instance configured with the provided API key.
        
    Raises:
        ValueError: If the API model is invalid or not selected.
    """
    if not selected_api:
        raise ValueError("No API selected")
    
    if selected_api in _model_cache:
        model = _model_cache[selected_api]
        model.set_api_key(api_key)
        return model
        
    model_manager = ModelManager()
    model = model_manager.get_model(selected_api, api_key)
    if not model:
        raise ValueError(f"Invalid API selected: {selected_api}")
        
    _model_cache[selected_api] = model
        
    return model

@celery_app.task(bind=True)
def summarize_task(self, website_data):
    """
    Celery task for generating a summary of license document content.
    
    This task processes website data asynchronously, retrieving the
    appropriate language model based on the specified API, and generating
    a summary of the license document.
    
    Args:
        self: Celery task instance (automatically provided by Celery)
        website_data (dict): Dictionary containing:
            - website (str): Website URL
            - content (str): License document content
            - api (str): API model to use (e.g., 'gemini', 'mistral')
            - api_key (str): API key for authentication
    
    Returns:
        dict: Summary of the license document
    
    Raises:
        ValueError: If the API is invalid or not selected
    """
    selected_api = website_data.get('api')
    api_key = website_data.get('api_key')

    # Create a copy of website_data without the API key
    safe_website_data = {k: v for k, v in website_data.items() if k != 'api_key'}
    
    model = _get_cached_model(selected_api, api_key)
    
    summary = model.summarize(safe_website_data)
    
    return summary

@celery_app.task(bind=True)
def question_task(self, question_data):
    """
    Celery task for answering questions about license documents.
    
    This task processes question data asynchronously, retrieving the
    appropriate language model based on the specified API, and generating
    an answer to the question about the license document.
    
    Args:
        self: Celery task instance (automatically provided by Celery)
        question_data (dict): Dictionary containing:
            - summary (dict): Summary of the license document
            - question (str): Question about the license document
            - api (str): API model to use (e.g., 'gemini', 'mistral')
            - api_key (str): API key for authentication
    
    Returns:
        str: Answer to the question about the license document
    
    Raises:
        ValueError: If the API is invalid or not selected
    """
    selected_api = question_data.get('api')
    api_key = question_data.get('api_key')
    
    model = _get_cached_model(selected_api, api_key)
    
    question = question_data['question']
    answer = model.answer_question(question_data, question)

    return answer

@celery_app.task(bind=True)
def scan_task(self, scan_data):
    """
    Celery task for scanning websites for licenses.
    
    This task processes website URLs asynchronously, scanning each URL
    for license information using the LicenseDetector.
    
    Args:
        self: Celery task instance (automatically provided by Celery)
        scan_data (dict): Dictionary containing:
            - urls (list): List of website URLs to scan
    
    Returns:
        dict: Dictionary containing scan results with detected licenses
    """    
    detector = LicenseDetector()
    results = detector.scan_websites(scan_data['urls'])
    
    return results