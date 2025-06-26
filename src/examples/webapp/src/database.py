import json
import os
import redis

class Database:
    """
    This class handles all database operations for storing and retrieving data from Redis.
    It provides methods to store and retrieve website scan results, summaries, and answers.
    """
    def __init__(self):
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        self.redis_client = redis.Redis.from_url(redis_url)
        self.result_expiry = 1800  # 30 minutes

    def set_expiry_time(self, seconds):
        """
        Set the expiry time for stored data.
        
        Args:
            seconds (int): The number of seconds until data expires.
        """
        self.result_expiry = seconds

    def store_scan_results(self, results):
        """
        Store scan results in Redis.
        
        Args:
            results (list): The scan results to store.
            
        Returns:
            str: A unique identifier for the stored data.
        """
        key = self.redis_client.incr("scan_results_counter")
        result_id = str(key)
        self.redis_client.setex(
            f"scan_results:{result_id}", 
            self.result_expiry, 
            json.dumps(results)
        )
        return result_id
        
    def get_scan_results(self, result_id):
        """
        Retrieve scan results from Redis.
        
        Args:
            result_id (str): The unique identifier for the stored results.
            
        Returns:
            list: The retrieved scan results.
            
        Raises:
            ValueError: If data is not found or the format is invalid.
        """
        self._validate_id(result_id)
        
        data = self.redis_client.get(f"scan_results:{result_id}")
        if not data:
            raise ValueError("Scan results not found or expired")
            
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            raise ValueError("Invalid data format stored in cache")

    def store_summary_data(self, summary_data):
        """
        Store website summary data in Redis.
        
        Args:
            summary_data (dict): The summary data to store.
            
        Returns:
            str: A unique identifier for the stored data.
        """
        key = self.redis_client.incr("summary_data_counter")
        result_id = str(key)
        self.redis_client.setex(
            f"summary_data:{result_id}", 
            self.result_expiry, 
            json.dumps(summary_data)
        )
        return result_id
    
    def get_summary_data(self, result_id):
        """
        Retrieve summary data from Redis.
        
        Args:
            result_id (str): The unique identifier for the stored data.
            
        Returns:
            dict: The retrieved summary data.
            
        Raises:
            ValueError: If data is not found or the format is invalid.
        """
        self._validate_id(result_id)
        
        data = self.redis_client.get(f"summary_data:{result_id}")
        if not data:
            raise ValueError("Summary data not found or expired")
            
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            raise ValueError("Invalid data format stored in cache")
            
    def store_answer(self, result_id, question, answer):
        """
        Store answer data in Redis.
        
        Args:
            result_id (str): The result ID associated with this answer.
            question (str): The question that was asked.
            answer (str): The answer to the question.
            
        Returns:
            str: A unique identifier for the stored answer.
        """
        key = self.redis_client.incr("answer_counter")
        answer_id = str(key)
        answer_data = {
            'result_id': result_id,
            'question': question,
            'answer': answer,
        }
            
        self.redis_client.setex(
            f"answer:{answer_id}", 
            self.result_expiry, 
            json.dumps(answer_data)
        )
        return answer_id
        
    def get_answer(self, answer_id):
        """
        Retrieve answer data from Redis.
        
        Args:
            answer_id (str): The unique identifier for the stored answer.
            
        Returns:
            dict: The retrieved answer data.
            
        Raises:
            ValueError: If data is not found or the format is invalid.
        """
        self._validate_id(answer_id)
        
        data = self.redis_client.get(f"answer:{answer_id}")
        if not data:
            raise ValueError("Answer not found or expired")
            
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            raise ValueError("Invalid answer data format stored in cache")

    def _validate_id(self, id_value):
        """
        Validate that an ID value is provided.
        
        Args:
            id_value (str): The ID value to validate.
            
        Raises:
            ValueError: If the ID is not provided.
        """
        if not id_value:
            raise ValueError("No identifier provided")