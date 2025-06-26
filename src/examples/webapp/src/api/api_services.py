from license_checker.license_detector import LicenseDetector
from .api_tasks import summarize_task, question_task, scan_task
from flask import jsonify, make_response

class APIServices:
    """    
    This class handles validation of API requests, interacts with the license detector,
    and manages the lifecycle of asynchronous tasks for summarization and question-answering.
    """
    def __init__(self):
        """
        Initialize the API services with a LicenseDetector instance.
        """
        self.detector = LicenseDetector()

    def validate_scan_request(self, data):
        """
        Validate scan request data.
        
        Args:
            data (dict): Request data containing URLs to scan
            
        Returns:
            Response or None: Error response if validation fails, None otherwise
        """
        if not data or 'urls' not in data:
            return make_response(jsonify({'error': 'Missing urls key in request.'}), 400)
        return None

    def validate_summary_request(self, data):
        """
        Validate summary request data.
        
        Args:
            data (dict): Request data containing website, content, API model, and API key
            
        Returns:
            Response or None: Error response if validation fails, None otherwise
        """
        if not data or 'website' not in data or 'content' not in data or 'api' not in data or 'api_key' not in data:
            return make_response(jsonify({'error': 'Missing required fields: "website", "content", "api", or "api_key"'}), 400)
        return None

    def validate_question_request(self, data):
        """
        Validate question request data.
        
        Args:
            data (dict): Request data containing summary, question, API model, and API key
            
        Returns:
            Response or None: Error response if validation fails, None otherwise
        """
        if not data or 'summary' not in data or 'question' not in data or 'api' not in data or 'api_key' not in data:
            return make_response(jsonify({'error': 'Missing required fields: "summary", "question", "api", or "api_key"'}), 400)
        return None

    def scan_websites(self, urls):
        """
        Scan websites for licenses.
        
        Args:
            urls (list): List of website URLs to scan
            
        Returns:
            dict: Dictionary containing scan results with detected licenses
        """
        return self.detector.scan_websites(urls)

    def queue_summary_task(self, data):
        """
        Queue a summary generation task with Celery.
        
        Args:
            data (dict): Data containing website information and API keys
            
        Returns:
            AsyncResult: Celery task object representing the queued task
        """
        return summarize_task.delay(data)

    def queue_question_task(self, data):
        """
        Queue a question answering task with Celery.
        
        Args:
            data (dict): Data containing summary, question, and API keys
            
        Returns:
            AsyncResult: Celery task object representing the queued task
        """
        return question_task.delay(data)

    def queue_scan_task(self, data):
        """
        Queue a website scanning task with Celery.
        
        Args:
            data (dict): Data containing URLs to scan
            
        Returns:
            AsyncResult: Celery task object representing the queued task
        """
        return scan_task.delay(data)

    def get_summary_task_result(self, task_id):
        """
        Get the result of a summary generation task.
        
        Args:
            task_id (str): ID of the summary task to retrieve
            
        Returns:
            dict: Task status and result information
        """
        task = summarize_task.AsyncResult(task_id)
        return self._get_task_result(task)

    def get_question_task_result(self, task_id):
        """
        Get the result of a question answering task.
        
        Args:
            task_id (str): ID of the question task to retrieve
            
        Returns:
            dict: Task status and result information
        """
        task = question_task.AsyncResult(task_id)
        return self._get_task_result(task)

    def get_scan_task_result(self, task_id):
        """
        Get the result of a website scanning task.
        
        Args:
            task_id (str): ID of the scan task to retrieve
            
        Returns:
            dict: Task status and result information
        """
        task = scan_task.AsyncResult(task_id)
        return self._get_task_result(task)

    def _get_task_result(self, task):
        """
        Helper method to process task result and determine status.
        
        Args:
            task (AsyncResult): Celery AsyncResult object
            
        Returns:
            dict: Dictionary containing task status, result or error message,
                 and appropriate HTTP status code
        """
        if task.state == 'PENDING':
            if not task.backend.get(task.id):
                return {'status': 'not_found', 'error': 'Task not found', 'http_status': 404}
            return {'status': 'processing', 'http_status': 202}
        elif task.state == 'SUCCESS':
            return {'status': 'completed', 'result': task.result, 'http_status': 200}
        elif task.state == 'FAILURE':
            return {'status': 'failed', 'error': str(task.result), 'http_status': 500}
        elif task.state == 'RETRY':
            return {'status': 'retrying', 'http_status': 202}
        elif task.state == 'REVOKED':
            return {'status': 'cancelled', 'http_status': 200}
        else:
            return {'status': task.state, 'http_status': 200}