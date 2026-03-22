import PyPDF2

def extract_text_from_pdf(pdf_path):
    try:
        # Open the PDF file in read-binary mode
        with open(pdf_path, 'rb') as file:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract text from all pages
            text = ""
            for page in pdf_reader.pages:
                # Extract text from the current page
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                
            return text
            
    except FileNotFoundError:
        return f"Error: The file '{pdf_path}' was not found."
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    # Example usage with a dummy PDF file
    # Please ensure you have a 'dummy.pdf' in the same directory, 
    # or change the path to point to an existing PDF file.
    dummy_pdf_path = "dummy.pdf"
    
    print(f"Attempting to extract text from {dummy_pdf_path}...\n")
    
    extracted_text = extract_text_from_pdf(dummy_pdf_path)
    print("--- Extracted Text ---")
    print(extracted_text)
    print("----------------------")
