import os
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from rag.settings import PDF_DIR

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200, chunk_overlap=16
)

def load_and_split_pdfs(specific_files=None):
    """
    Load and split PDFs into text chunks for vector embedding
    
    Args:
        specific_files (list): Optional list of specific PDF filenames to process
    
    Returns:
        list: Text chunks from the PDFs
    """
    pdf_texts = []
    
    # If specific files are provided, use them
    if specific_files:
        for filename in specific_files:
            pdf_path = os.path.join(PDF_DIR, filename)
            if os.path.exists(pdf_path):
                print(f"Processing specific file: {pdf_path}")
                with open(pdf_path, 'rb') as file:
                    reader = PdfReader(file)
                    text = "".join([page.extract_text() or "" for page in reader.pages])
                pdf_texts.append(text)
            else:
                print(f"File not found: {pdf_path}")
        
        if not pdf_texts:
            raise FileNotFoundError("None of the specified PDF files were found.")
    else:
        # Look for PDF files in the directory (case-insensitive)
        found_files = False
        for filename in os.listdir(PDF_DIR):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(PDF_DIR, filename)
                print(f"Processing file: {pdf_path}")
                try:
                    with open(pdf_path, 'rb') as file:
                        reader = PdfReader(file)
                        text = "".join([page.extract_text() or "" for page in reader.pages])
                    pdf_texts.append(text)
                    found_files = True
                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")
        
        if not found_files:
            # Try deeper search (including subdirectories)
            for root, dirs, files in os.walk(PDF_DIR):
                for filename in files:
                    if filename.lower().endswith('.pdf'):
                        pdf_path = os.path.join(root, filename)
                        print(f"Processing file from subdirectory: {pdf_path}")
                        try:
                            with open(pdf_path, 'rb') as file:
                                reader = PdfReader(file)
                                text = "".join([page.extract_text() or "" for page in reader.pages])
                            pdf_texts.append(text)
                            found_files = True
                        except Exception as e:
                            print(f"Error processing {filename}: {str(e)}")
    
    # Check if we found any text
    if not pdf_texts:
        print(f"No valid PDF content found in {PDF_DIR}")
        return []
    
    # Split the text into chunks
    combined_text = " ".join(pdf_texts)
    return text_splitter.split_text(combined_text)