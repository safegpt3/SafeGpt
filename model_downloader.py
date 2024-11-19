# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 12:58:30 2024

@author: HamzaHussain
"""

from transformers import AutoModelForSequenceClassification, AutoTokenizer

MODEL_NAME = "StanfordAIMI/stanford-deidentifier-base"
# Download and save the pre-trained model
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
model.save_pretrained("./model")
# Download and save the tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
tokenizer.save_pretrained("./model")
print("Model and tokenizer downloaded successfully!")