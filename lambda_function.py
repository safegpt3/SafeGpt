import json
import logging
from Presidio import anonymize_text
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.recognizer_registry import RecognizerRegistryProvider
from presidio_anonymizer import AnonymizerEngine
from transformer_recognizer import TransformersRecognizer
from configuration import BERT_DEID_CONFIGURATION, STANFORD_COFIGURATION

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    analyzer = init_analyzer()
    anonymizer = init_anonymizer()
    
    # Get the length and width parameters from the event object. The 
    # runtime converts the event object to a Python dictionary
    text = event['text']
    
    anonymized_text = anonymize_text(text, analyzer, anonymizer)
    print(f"The anonymized text is: {anonymized_text}")
        
    logger.info(f"CloudWatch logs group: {context.log_group_name}")
    
    # return the calculated area as a JSON string
    data = {"anonymized_text": anonymized_text}
    return json.dumps(data)

def tester(text):
    analyzer = init_analyzer()
    anonymizer = init_anonymizer()
    
    # Get the length and width parameters from the event object. The 
    # runtime converts the event object to a Python dictionary
    
    anonymized_text = anonymize_text(text, analyzer, anonymizer)
    print(f"The anonymized text is: {anonymized_text}")
        
    #logger.info(f"CloudWatch logs group: {context.log_group_name}")
    
    # return the calculated area as a JSON string
    data = {"anonymized_text": anonymized_text}
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
    analyzer = AnalyzerEngine(registry=registry, supported_languages=['en'])
    return analyzer

def init_anonymizer():
    anonymizer = AnonymizerEngine()
    return anonymizer
'''
if __name__ == "__main__":
    text = "My name is M. Litoiu and my phone number is 212-555-5555 and my membership is M3J1L1. I am from California. I love California Pizza. I was born on 12-02-1997. My email address is hamza.hussain97@live.com. You can charge my credit card number 4502310077098265. I work at York University and I am 27 years old."
    data = tester(text)
    print(data)
'''