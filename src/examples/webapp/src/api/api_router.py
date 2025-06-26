from flask import Blueprint, request, jsonify, url_for, make_response

class APIRouter:
    """  
    This class creates a Flask Blueprint for API routes and registers
    endpoints for scanning websites for license information, generating
    summaries, and answering questions about license documents.
    """
    def __init__(self, app, services):
        """
        Initialize the API router.
        
        Args:
            app: Flask application instance
            services: APIServices instance containing business logic
        """
        self.app = app
        self.services = services
        self.api_bp = Blueprint('api', __name__)
        self.register_routes()
        self.app.register_blueprint(self.api_bp, url_prefix='/api')

    def register_routes(self):
        """
        Register all API routes and their handler functions.
        
        Defines endpoints for scanning websites, generating summaries,
        and answering questions about license documents.
        """
        @self.api_bp.route('/scans', methods=['POST'])
        def api_scan_create():
            """
            Process a website scan request.
            
            Expects a JSON payload with a 'urls' key containing a list of website URLs to scan.
            Queues the scanning task asynchronously.
            
            Returns:
                JSON response with task ID and status
            """
            data = request.get_json()
            validation_error = self.services.validate_scan_request(data)
            if validation_error:
                return validation_error
            
            task = self.services.queue_scan_task(data)
            task_url = url_for('api.api_scan_get', task_id=task.id, _external=True)
            
            response = jsonify({
                'status': 'processing',
                'task_id': task.id
            })
            return make_response(response, 202, {'Location': task_url})

        @self.api_bp.route('/scans/<task_id>', methods=['GET'])
        def api_scan_get(task_id):
            """
            Get the status and result of a website scanning task.
            
            Args:
                task_id: ID of the scanning task
                
            Returns:
                JSON response with task status and scan results if available
            """
            result = self.services.get_scan_task_result(task_id)
            http_status = result.pop('http_status')
            return make_response(jsonify(result), http_status)

        @self.api_bp.route('/summaries', methods=['POST'])
        def api_summary_create():
            """
            Process a website summary request.
            
            Expects a JSON payload with 'website', 'content', 'api', and 'api_key' keys.
            Queues the summarization task asynchronously.
            
            Returns:
                JSON response with task ID and status
            """
            data = request.get_json()
            validation_error = self.services.validate_summary_request(data)
            if validation_error:
                return validation_error

            task = self.services.queue_summary_task(data)
            task_url = url_for('api.api_summary_get', task_id=task.id, _external=True)
            
            response = jsonify({
                'status': 'processing',
                'task_id': task.id
            })
            return make_response(response, 202, {'Location': task_url})

        @self.api_bp.route('/summaries/<task_id>', methods=['GET'])
        def api_summary_get(task_id):
            """
            Get the status and result of a summary task.
            
            Args:
                task_id: ID of the summarization task
                
            Returns:
                JSON response with task status and result if available
            """
            result = self.services.get_summary_task_result(task_id)
            http_status = result.pop('http_status')
            return make_response(jsonify(result), http_status)

        @self.api_bp.route('/answers', methods=['POST'])
        def api_answer_create():
            """
            Process a question about a license document.
            
            Expects a JSON payload with 'summary', 'question', 'api', and 'api_key' keys.
            Queues the question answering task asynchronously.
            
            Returns:
                JSON response with task ID and status
            """
            data = request.get_json()
            validation_error = self.services.validate_question_request(data)
            if validation_error:
                return validation_error

            task = self.services.queue_question_task(data)
            task_url = url_for('api.api_answer_get', task_id=task.id, _external=True)
            
            response = jsonify({
                'status': 'processing',
                'task_id': task.id
            })
            return make_response(response, 202, {'Location': task_url})

        @self.api_bp.route('/answers/<task_id>', methods=['GET'])
        def api_answer_get(task_id):
            """
            Get the status and result of a question answering task.
            
            Args:
                task_id: ID of the question answering task
                
            Returns:
                JSON response with task status and answer if available
            """
            result = self.services.get_question_task_result(task_id)
            http_status = result.pop('http_status')
            return make_response(jsonify(result), http_status)