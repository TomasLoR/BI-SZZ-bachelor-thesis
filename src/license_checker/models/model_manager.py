from license_checker.models.mistral import Mistral
from license_checker.models.gemini import Gemini


class ModelManager:
    """    
    This class provides a factory for creating instances of different models.
    """
    
    def __init__(self):
        """
        Initialize the ModelManager with supported models.
        
        The models dictionary maps model identifiers to their respective classes.
        """
        self.models = {
            "huggingface": Mistral,
            "googleai": Gemini
        }
        self.model_instances = {}

    def get_model(self, model_name, api_key=None):
        """
        Get an instance of the specified model.
        
        Args:
            model_name (str): The name/identifier of the model to instantiate.
                             Must be one of the keys in the models dictionary.
            api_key (str, optional): API key for the model. If provided, it will
                                    be stored within the model instance.
        
        Returns:
            object: An instance of the requested model class if the model_name is valid,
                   None otherwise.
        """
        model_class = self.models.get(model_name)
        if not model_class:
            return None
            
        # If the model was previously instantiated and no new API key is provided,
        # return the existing instance
        if model_name in self.model_instances and api_key is None:
            return self.model_instances[model_name]
            
        # Create a new instance with the API key if provided
        model_instance = model_class(api_key)
        
        # Store the instance if an API key was provided
        if api_key is not None:
            self.model_instances[model_name] = model_instance
            
        return model_instance
        
    def set_api_key(self, model_name, api_key):
        """
        Set or update the API key for a specific model.
        
        Args:
            model_name (str): The name/identifier of the model.
            api_key (str): The API key to set.
            
        Returns:
            bool: True if the key was successfully set, False if the model doesn't exist.
        """
        # Get or create model instance
        model = self.get_model(model_name)
        if not model:
            return False
            
        # Set the API key
        model.set_api_key(api_key)
        
        # Store the instance
        self.model_instances[model_name] = model
        
        return True