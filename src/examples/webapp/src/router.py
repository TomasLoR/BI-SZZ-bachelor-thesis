from flask import render_template, request, session, redirect, url_for

class Router:
    """    
    This class defines all the routes for the Flask application, processes HTTP requests,
    interacts with the Services class to perform business logic operations, and renders
    appropriate templates with the results.
    
    Attributes:
        app (Flask): The Flask application instance.
        services (Services): An instance of the Services class for business logic operations.
    """
    def __init__(self, app, services):
        """
        Initialize the Router with Flask app and Services instances.
        
        Args:
            app (Flask): The Flask application instance.
            services (Services): An instance of the Services class.
        """
        self.app = app
        self.services = services
        self.register_routes()

    def register_routes(self):
        """
        Register all routes for the Flask application.
        
        This method defines route handlers for the home page, scans page, 
        summary page, and question answering functionality.
        """
        @self.app.route('/', methods=['GET'])
        def home():
            """
            Route handler for the home page.
            
            Returns:
                str: Rendered HTML template for the home page with any saved API keys.
            """
            huggingface_key = session.get('huggingface', '')
            googleai_key = session.get('googleai', '')
            
            return render_template('index.html', 
                                  title="Website License Checker",
                                  huggingface_key=huggingface_key,
                                  googleai_key=googleai_key)

        @self.app.route('/scans', methods=['POST'])
        def create_scan():
            """
            Route handler for processing URL submissions.
            
            Processes the URLs submitted by the user, stores API keys in the session,
            scans the submitted websites, then redirects to the scans view.
            
            Returns:
                Response: Redirects to the scans view page or renders an error message.
                
            Raises:
                ValueError: If URL processing or website scanning fails.
            """
            self._store_api_keys()
            
            urls = [url.strip() for url in request.form['urls'].split('\n') if url.strip()]
            
            try:
                result_id = self.services.scan_websites(urls)
                
                return redirect(url_for('view_scan', scan_id=result_id))
            except ValueError as e:
                return render_template('error.html', title="Error", message=str(e), code=400)

        @self.app.route('/scans/<scan_id>', methods=['GET'])
        def view_scan(scan_id):
            """
            Route handler for displaying scan results.
            
            Retrieves scan results using the provided scan_id and renders the scans page.
            
            Args:
                scan_id (str): Unique identifier for the stored results
                
            Returns:
                str: Rendered HTML template with scanning results or error message.
            """
            try:
                results = self.services.retrieve_scan_results(scan_id)
                return render_template('scans.html', title="Scan Results", results=results, scan_id=scan_id)
            except ValueError as e:
                return render_template('error.html', title="Error", message=str(e), code=404)

        @self.app.route('/scans/<scan_id>/summaries', methods=['POST'])
        def create_summary(scan_id):
            """
            Route handler for processing summary requests.
            
            Retrieves the selected API and its key from the session, processes the raw scan results,
            then redirects to the summary view route.
            
            Args:
                scan_id (str): Unique identifier for the stored scan results
                
            Returns:
                Response: Redirects to the summary view page or renders an error message.
                
            Raises:
                ValueError: If API key is missing or summarization fails.
            """
            selected_api = request.form['api']
            api_key = session.get(selected_api)
            raw_result = request.form.get('result')
            
            try:
                if not api_key:
                    return render_template('error.html', title="Error", 
                                        message=f"No API key provided for {selected_api}.", 
                                        code=400)
                
                summary_id = self.services.summarize_results(raw_result, selected_api, api_key)
                
                return redirect(url_for('view_summary', scan_id=scan_id, summary_id=summary_id, api=selected_api))
            except ValueError as e:
                code = 401 if "API" in str(e) else 400
                return render_template('error.html', title="Error", message=str(e), code=code)

        @self.app.route('/scans/<scan_id>/summaries/<summary_id>', methods=['GET'])
        def view_summary(scan_id, summary_id):
            """
            Route handler for displaying a summary.
            
            Retrieves the summary data using the provided summary_id and renders the summary page.
            
            Args:
                scan_id (str): Unique identifier for the stored scan results
                summary_id (str): Unique identifier for the stored summary data
                
            Returns:
                str: Rendered HTML template with the summary or error message.
            """
            try:
                summary_data = self.services.retrieve_summary_data(summary_id)
                api = request.args.get('api')
                
                return render_template('summary.html', 
                                     title="Summary", 
                                     summary=summary_data.get('summary'),
                                     api=api,
                                     scan_id=scan_id,
                                     summary_id=summary_id)
            except ValueError as e:
                return render_template('error.html', title="Error", message=str(e), code=404)

        @self.app.route('/scans/<scan_id>/summaries/<summary_id>/answers', methods=['POST'])
        def create_answer(scan_id, summary_id):
            """
            Route handler for processing question submissions about website licensing.
            
            Processes a user question related to a previously analyzed website and
            redirects to the answer view route.
            
            Args:
                scan_id (str): Unique identifier for the stored scan results
                summary_id (str): Unique identifier for the stored summary data
                
            Returns:
                Response: Redirects to the answer view page or renders an error message.
                
            Raises:
                ValueError: If API key is missing or question processing fails.
            """
            question = request.form.get('question')
            selected_api = request.form['api']
            api_key = session.get(selected_api)
            
            try:
                answer_id = self.services.answer_question(summary_id, question, selected_api, api_key)
                
                return redirect(url_for('view_answer', scan_id=scan_id, summary_id=summary_id, answer_id=answer_id, api=selected_api))
            except ValueError as e:
                code = 401 if "API" in str(e) else 400
                return render_template('error.html', title="Error", message=str(e), code=code)
                
        @self.app.route('/scans/<scan_id>/summaries/<summary_id>/answers/<answer_id>', methods=['GET'])
        def view_answer(scan_id, summary_id, answer_id):
            """
            Route handler for displaying an answer to a question.
            
            Retrieves the summary data and answer using the provided IDs and renders the page.
            
            Args:
                scan_id (str): Unique identifier for the stored scan results
                summary_id (str): Unique identifier for the stored summary data
                answer_id (str): Unique identifier for the stored answer
                
            Returns:
                str: Rendered HTML template with the answer or error message.
            """
            try:
                summary_data = self.services.retrieve_summary_data(summary_id)
                answer_data = self.services.retrieve_answer(answer_id)
                api = request.args.get('api')
                
                return render_template('summary.html', 
                                     title="Summary", 
                                     summary=summary_data.get('summary'), 
                                     api=api,
                                     question=answer_data.get('question'),
                                     answer=answer_data.get('answer'), 
                                     scan_id=scan_id,
                                     summary_id=summary_id)
            except ValueError as e:
                return render_template('error.html', title="Error", message=str(e), code=404)
    
    def _store_api_keys(self):
        """
        Store API keys from form into session.
        
        Extracts API keys from the request form and stores them in the session
        for later use with the AI models.
        """
        api_keys = ["huggingface", "googleai"]
        for key in api_keys:
            form_value = request.form.get(f"{key}_api_key", "").strip()
            if form_value:
                session[key] = form_value