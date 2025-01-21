import json
import time
import logging
import os
from custom_anonymizer import CustomAnonymizerEngine
from presidio import anonymize_text, anonymize_file
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.recognizer_registry import RecognizerRegistryProvider
from presidio_anonymizer import AnonymizerEngine
from transformer_recognizer import TransformersRecognizer
from presidio_analyzer.nlp_engine import NlpEngineProvider
from configuration import BERT_DEID_CONFIGURATION, STANFORD_COFIGURATION
from flask import Flask, flash, request, redirect, url_for, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
app.config['ORIGINAL_FOLDER'] = './Original Files/'
app.config['UPLOAD_FOLDER'] = './Anonymized Files/'
ALLOWED_EXTENSIONS = {'pdf'}

app.analyzer = None
app.anonymizer = None

@app.before_first_request
def initialize_dep():
    l_start_time = time.time()
    app.analyzer = init_analyzer()
    app.anonymizer = init_anonymizer()
    l_end_time = time.time()
    
    print(f"Load time: {l_end_time - l_start_time:.4f} seconds")
    
    return app.analyzer, app.anonymizer

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/anonymize', methods=['POST'])
def anonymize():
    text = request.json['text']
    print(text)
    anonymized_text, private_data = anonymize_text(text, app.analyzer, app.anonymizer)
    print(f"The anonymized text is: {anonymized_text}")
        
    # return the calculated area as a JSON string
    data = {"processed_text": anonymized_text, "private_data": private_data,}
    return jsonify(data)

@app.route('/anonymizeAttachments', methods=['POST'])
def anonymize_attachments():
    # Check if files are present in the request
    if 'files' not in request.files:
        return jsonify({"error": "No files part in the request"}), 400
    conversation_id = request.form.get('conversationId')
    logger.info(conversation_id)
    
    files = request.files.getlist('files')

    if not files:
        return jsonify({"error": "No files selected for upload"}), 400

    processed_files = []

    for file in files:
        # Ensure the file is not empty
        if file.filename == '':
            continue  # Skip empty files

        # Save the file securely to the upload directory
        filename = secure_filename(file.filename)
        print("File received: "+filename)
        filepath = os.path.join(app.config['ORIGINAL_FOLDER'], filename)
        file.save(filepath)
        print("File Saved: "+filename)

        # Anonymize the file
        try:
            path = os.path.join(app.config['UPLOAD_FOLDER'], conversation_id)
            if not os.path.exists(path):
                os.mkdir(path)
            anonymized_filename = anonymize_file(filepath, app.analyzer, app.anonymizer, path)
            print("Anonymized File: "+anonymized_filename)
            processed_files.append({
                "original_filename": file.filename,
                "anonymized_file_url": url_for('download_file', conversationId=conversation_id, name=anonymized_filename)  # Adjust for actual server URL if needed
            })
        except Exception as e:
            processed_files.append({
                "original_filename": file.filename,
                "error": str(e)
            })

    if not processed_files:
        return jsonify({"error": "No valid files processed"}), 400

    return jsonify({
        "message": "Files processed successfully.",
        "files": processed_files
    }), 200

@app.route('/anonymized/attachments/<conversationId>/')
def anonymized_attachments(conversationId):
    path = os.path.join(app.config['UPLOAD_FOLDER'], conversationId)
    files = {}
    for filename in os.listdir(path):
        if filename.endswith(".txt"):
            filepath = os.path.join(path, filename)
            with open(filepath, 'r') as f:
                content = f.read()
            files[filename] = content
    return jsonify(files)

@app.route('/anonymized/attachments/<conversationId>/<name>')
def download_file(conversationId, name):
    path = os.path.join(app.config['UPLOAD_FOLDER'], conversationId)
    return send_from_directory(path, name)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def tester(text):
    analyzer, anonymizer = initialize_dep()
    anonymized_text, private_data = anonymize_text(text, analyzer, anonymizer)
    #print(f"The anonymized text is: {anonymized_text}")
        
    #logger.info(f"CloudWatch logs group: {context.log_group_name}")
    
    # return the calculated area as a JSON string
    data = {"processed_text": anonymized_text, "private_data": private_data,}
    return json.dumps(data)

def init_analyzer():
    yaml_file = "./recognizers.yaml"
    provider = RecognizerRegistryProvider(
                    conf_file=yaml_file
                )
    registry = provider.create_recognizer_registry()
    model_path = "./model"
    supported_entities = STANFORD_COFIGURATION.get(
        "PRESIDIO_SUPPORTED_ENTITIES")
    transformers_recognizer = TransformersRecognizer(model_path=model_path,
                                                    supported_entities=supported_entities)

    # This would download a large (~500Mb) model on the first run
    transformers_recognizer.load_transformer(**STANFORD_COFIGURATION)

    # Add transformers model to the registry
    registry.add_recognizer(transformers_recognizer)

    nlp_configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
    }
    nlp_engine = NlpEngineProvider(nlp_configuration=nlp_configuration).create_engine()
    
    analyzer = AnalyzerEngine(registry=registry, nlp_engine=nlp_engine, supported_languages=['en'])
    return analyzer

def init_anonymizer():
    anonymizer = CustomAnonymizerEngine()
    return anonymizer

if __name__ == "__main__":
    '''
    text = "My name is Litoiu and my phone number is 212-555-5555 and my membership is M3J1L1. My email address is hamza.hussain97@live.com. I am from California. I love California Pizza. I was born on 12-02-1997. You can charge my credit card number 4502310077098265. I work at York University and I am 27 years old."
    start_time = time.time()
    data = tester(text)
    end_time = time.time()
    
    print(data)
    print(f"Execution time: {end_time - start_time:.4f} seconds")
    '''
    app.run(host='0.0.0.0', port=8080)
