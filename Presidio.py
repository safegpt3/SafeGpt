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

logging.basicConfig(level=logging.INFO, filename="py_log.log",format="%(asctime)s %(levelname)s %(message)s", filemode="w")

def anonymize_text(text, analyzer, anonymizer):
    results = analyzer.analyze(text=text, language='en', return_decision_process=True)
    #print(results)
    for result in results:
        decision_process = result.analysis_explanation
        pp = pprint.PrettyPrinter()
        #print("Decision process output:\n")
        #pp.pprint(decision_process.__dict__)
        logging.info(pp.pformat(decision_process.__dict__))
    # Analyzer results are passed to the AnonymizerEngine for anonymization
    anonymized_text = anonymizer.anonymize(text=text, analyzer_results=results)
    return anonymized_text.text

def anonymize_file(filename):
    reader = PdfReader(filename)
    output_filename = os.path.splitext(filename)[0]
    with open(output_filename+"_anonymized.txt", "w", errors='ignore') as output_file:
        # Step 1: Loop through each page, anonymize the text, and write it to the TXT file
        for i, page in enumerate(reader.pages):
            # Extract text from the page
            original_text = page.extract_text()
            anonymized_text = anonymize_text(original_text)
            # Step 2: Write the anonymized text to the file, maintaining page order
            output_file.write(anonymized_text + "\n\n")  # Add double newlines between pages

