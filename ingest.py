import os
import sys
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from langchain_community.document_loaders import PDFPlumberLoader
from src.parsers import ConstituitionParser, BaseLegalParser, IncomeParser
from src.database import document_dtype, get_vectorstore

def main():
    print("=== Starting Database Ingestion ===")
    
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    if not os.path.exists(data_dir):
        print(f"Error: Data directory '{data_dir}' not found.")
        sys.exit(1)
        
    all_documents = []
    
    # 1. Constitution of India
    const_path = os.path.join(data_dir, "constituition.pdf")
    if os.path.exists(const_path):
        print("Parsing Constitution of India...")
        try:
            con_loader = PDFPlumberLoader(const_path)
            con_raw = con_loader.load()
            constitution_chunks = ConstituitionParser(con_raw).parser()
            all_documents.extend(document_dtype(constitution_chunks))
            print(f"Successfully parsed Constitution. Chunks: {len(constitution_chunks)}")
        except Exception as e:
            print(f"Error parsing Constitution: {e}")
    else:
        print("Warning: constituition.pdf not found in data/ folder. Skipping.")
        
    # 2. Standard Acts
    acts = [
        ("bns.pdf", "bns"),
        ("bnss.pdf", "bnss"),
        ("bsa.pdf", "bsa"),
        ("motor.pdf", "motor"),
        ("info_tech.pdf", "info_tech"),
        ("posh.pdf", "posh"),
    ]
    
    for filename, title in acts:
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            print(f"Parsing {title.upper()} Act...")
            try:
                parser_obj = BaseLegalParser(filepath, title)
                chunks = parser_obj.parser()
                all_documents.extend(document_dtype(chunks))
                print(f"Successfully parsed {title.upper()}. Chunks: {len(chunks)}")
            except Exception as e:
                print(f"Error parsing {title.upper()}: {e}")
        else:
            print(f"Warning: {filename} not found in data/ folder. Skipping.")
            
    # 3. Income Tax Act (using special parser)
    income_path = os.path.join(data_dir, "income.pdf")
    if os.path.exists(income_path):
        print("Parsing Income Tax Act...")
        try:
            income_chunks = IncomeParser(income_path).parser()
            all_documents.extend(document_dtype(income_chunks))
            print(f"Successfully parsed Income Tax Act. Chunks: {len(income_chunks)}")
        except Exception as e:
            print(f"Error parsing Income Tax Act: {e}")
    else:
        print("Warning: income.pdf not found in data/ folder. Skipping.")
            
    if not all_documents:
        print("Error: No documents parsed. Ingestion aborted.")
        sys.exit(1)
        
    print(f"Total documents prepared for indexing: {len(all_documents)}")
    print("Uploading to Qdrant and indexing (force_recreate=True)...")
    
    try:
        vectorstore = get_vectorstore(documents=all_documents, force_recreate=True)
        print("=== Database Ingestion Completed Successfully ===")
    except Exception as e:
        print(f"Error during Qdrant ingestion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
