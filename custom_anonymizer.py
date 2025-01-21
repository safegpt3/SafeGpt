# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 17:20:26 2024

@author: HamzaHussain
"""

from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import RecognizerResult
from presidio_anonymizer.entities import ConflictResolutionStrategy, OperatorConfig
from presidio_anonymizer.operators import OperatorType

class CustomAnonymizerEngine(AnonymizerEngine):
    def anonymize(self, text: str, analyzer_results: list, operators: dict = None, conflict_resolution: ConflictResolutionStrategy = (
        ConflictResolutionStrategy.MERGE_SIMILAR_OR_CONTAINED
    )) -> tuple:
        """
        Anonymize the input text and return both the anonymized text and resolved PII entities.

        Args:
            text (str): The input text to anonymize.
            analyzer_results (list): A list of `RecognizerResult` objects from Presidio Analyzer.
            operators (dict): A mapping of entity types to anonymization operators.

        Returns:
            tuple: A tuple containing:
                   - The anonymized text (str)
                   - The resolved PII entities (list)
        """
        # Perform merge and conflict resolution
        analyzer_results = self._remove_conflicts_and_get_text_manipulation_data(
            analyzer_results, conflict_resolution
        )

        merged_results = self._merge_entities_with_whitespace_between(
            text, analyzer_results
        )
        default_operator = OperatorConfig("replace")
        operators = {"DEFAULT": default_operator}

        anonymized_text = self._operate(
            text=text,
            pii_entities=merged_results,
            operators_metadata=operators,
            operator_type=OperatorType.Anonymize,
        )
        # Return both anonymized text and resolved entities
        return anonymized_text, merged_results
    
# Usage example:
if __name__ == "__main__":
    from presidio_analyzer import RecognizerResult

    # Example input
    text = (
        "My name is M. Litoiu and my phone number is 212-555-5555 "
        "and my email is example@example.com."
    )
    analyzer_results = [
        RecognizerResult("PERSON", 11, 19, 0.99),
        RecognizerResult("PHONE_NUMBER", 43, 55, 1.0),
        RecognizerResult("EMAIL_ADDRESS", 76, 93, 1.0),
    ]
    operators = {
        "PERSON": {"type": "replace", "new_value": "<PERSON>"},
        "PHONE_NUMBER": {"type": "replace", "new_value": "<PHONE_NUMBER>"},
        "EMAIL_ADDRESS": {"type": "replace", "new_value": "<EMAIL_ADDRESS>"},
    }

    # Instantiate the custom anonymizer
    custom_anonymizer = CustomAnonymizerEngine()

    # Run the anonymization process
    anonymized_text, resolved_pii_entities = custom_anonymizer.anonymize(
        text, analyzer_results, operators
    )

    print("Anonymized Text:", anonymized_text)
    print("Resolved PII Entities:", resolved_pii_entities)
