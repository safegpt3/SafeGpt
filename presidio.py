# -*- coding: utf-8 -*-

import logging
import pprint
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.recognizer_registry import RecognizerRegistryProvider
from presidio_anonymizer import AnonymizerEngine
from pypdf import PdfReader
from transformer_recognizer import TransformersRecognizer
import os
from configuration import BERT_DEID_CONFIGURATION, STANFORD_COFIGURATION
from presidio_anonymizer import DeanonymizeEngine


logging.basicConfig(level=logging.INFO, handlers=[
        logging.StreamHandler()  # Log to the console (stdout)
    ],format="%(asctime)s %(levelname)s %(message)s")

def anonymize_text(text, analyzer, anonymizer, prepare_dict=True):
    results = analyzer.analyze(text=text, language='en', return_decision_process=True)
    #print(results)
    for result in results:
        decision_process = result.analysis_explanation
        pp = pprint.PrettyPrinter()
        #print("Decision process output:\n")
        #pp.pprint(decision_process.__dict__)
        logging.info(pp.pformat(decision_process.__dict__))
        
    # Analyzer results are passed to the AnonymizerEngine for anonymization
    anonymized_text, resolved_entities = anonymizer.anonymize(text=text, analyzer_results=results)
    if prepare_dict:
        anonymized_text, private_data = generate_private_data_dictionary(text, anonymized_text.text, resolved_entities)
    else:
        anonymized_text = anonymized_text.text
        private_data = []
    return anonymized_text, private_data

def anonymize_file(filename, analyzer, anonymizer, outputpath):
    reader = PdfReader(filename)
    output_filename = os.path.split(os.path.splitext(filename)[0])[1]+".txt"
    with open(outputpath+ '/' +output_filename, "w", errors='ignore') as output_file:
        # Step 1: Loop through each page, anonymize the text, and write it to the TXT file
        for i, page in enumerate(reader.pages):
            # Extract text from the page
            original_text = page.extract_text()
            anonymized_text, private_data = anonymize_text(original_text, analyzer, anonymizer, prepare_dict=False)
            # Step 2: Write the anonymized text to the file, maintaining page order
            output_file.write(anonymized_text + "\n\n")  # Add double newlines between pages
    return output_filename
            

def generate_private_data_dictionary(original_string, anonymized_string, results):
    private_data = {}
    entity_count = {}
    new_anonymized_string = original_string

    for item in results:
        entity_type = item.entity_type
        start = item.start
        end = item.end
        
        placeholder = f"<{entity_type}>"
        
        if placeholder in anonymized_string:
            # Extract the corresponding value from the original string
            original_value = original_string[start:end]
    
            # Handle repeated entity types
            if entity_type in entity_count:
                entity_count[entity_type] += 1
                unique_key = f"{entity_type}{entity_count[entity_type]}"
            else:
                entity_count[entity_type] = 0
                unique_key = entity_type
    
            # Store the value in the private_data dictionary
            private_data[unique_key] = original_value
    
            # Replace the placeholder in the anonymized string
            new_placeholder = f"<{unique_key}>"
            new_anonymized_string = new_anonymized_string.replace(original_value, new_placeholder, 1)

    return new_anonymized_string, private_data
