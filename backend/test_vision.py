import logging
import os
import sys

# Ensure backend root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.DEBUG)
from auditor_agent.tax_wizard.pdf_extractor import extract_text_vision_llm

with open('test.pdf', 'rb') as f:
    pdf_bytes = f.read()

print("Executing Vision Extraction...")
res = extract_text_vision_llm(pdf_bytes, 'pdf')
print("Result Characters:", len(res))
print("Result Snippet:", res[:100])
