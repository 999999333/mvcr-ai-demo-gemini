from google import genai
from google.genai import types
import time
import os
import csv
from pathlib import Path

# Initialize the Gemini API client
client = genai.Client(api_key='***REMOVED***')

# File to store the file search store name
STORE_NAME_FILE = 'file_search_store_name.txt'

# Check if file search store already exists
if os.path.exists(STORE_NAME_FILE):
    with open(STORE_NAME_FILE, 'r') as f:
        store_name = f.read().strip()
    
    try:
        # Try to get the existing store
        file_search_store = client.file_search_stores.get(name=store_name)
        print(f"Using existing File Search store: {file_search_store.name}")
        print(f"Display Name: {file_search_store.display_name}")
    except Exception as e:
        print(f"Could not find existing store '{store_name}', creating new one...")
        file_search_store = client.file_search_stores.create(
            config={'display_name': 'mvcr-ai-docs'}
        )
        print(f"File Search store created: {file_search_store.name}")
        # Save the store name
        with open(STORE_NAME_FILE, 'w') as f:
            f.write(file_search_store.name)
else:
    # Create new File Search store
    print("Creating File Search store 'mvcr-ai-docs'...")
    file_search_store = client.file_search_stores.create(
        config={'display_name': 'mvcr-ai-docs'}
    )
    print(f"File Search store created: {file_search_store.name}")
    # Save the store name for future runs
    with open(STORE_NAME_FILE, 'w') as f:
        f.write(file_search_store.name)

# Load metadata from CSV
print("\nLoading metadata from files_metadata.csv...")
metadata_by_filename = {}
try:
    # Use utf-8-sig to handle BOM if present
    with open('files_metadata.csv', 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            filename = row.get('article_filename', '').strip()
            if filename and filename != 'NULL':
                # Store metadata with both the base filename and common extensions
                metadata = {
                    'article_name': row.get('article_name', '').strip(),
                    'is_archived': row.get('is_archived', '').strip(),
                    'is_news': row.get('is_news', '').strip(),
                    'article_year': row.get('article_year', '').strip()
                }
                # Store with base filename and common extensions
                metadata_by_filename[filename] = metadata
                metadata_by_filename[f"{filename}.md"] = metadata
                metadata_by_filename[f"{filename}.txt"] = metadata
                metadata_by_filename[f"{filename}.pdf"] = metadata
    
    # Count unique base filenames (divide by number of extensions we add)
    unique_count = len([k for k in metadata_by_filename.keys() if not any(k.endswith(ext) for ext in ['.md', '.txt', '.pdf'])])
    print(f"Loaded metadata for {unique_count} files")
except Exception as e:
    print(f"Warning: Could not load metadata CSV: {e}")
    print("Continuing without metadata...")

# Get list of already uploaded documents
print("\nFetching existing documents from file search store...")
existing_documents = {}
try:
    for document in client.file_search_stores.documents.list(
        parent=file_search_store.name
    ):
        existing_documents[document.display_name] = document.name
    print(f"Found {len(existing_documents)} existing documents")
except Exception as e:
    print(f"Note: Could not fetch existing documents: {e}")

# Define the source files directory
source_dir = Path('source_files')

# Get all files recursively from source_files directory
all_files = []
for ext in ['*.md', '*.txt', '*.pdf', '*.doc', '*.docx']:
    all_files.extend(source_dir.rglob(ext))

# Filter out files that are already uploaded
files_to_upload = []
skipped_files = []
for file_path in all_files:
    if file_path.name in existing_documents:
        skipped_files.append(file_path.name)
    else:
        files_to_upload.append(file_path)

print(f"\nFound {len(all_files)} total files")
print(f"Already uploaded: {len(skipped_files)}")
print(f"New files to upload: {len(files_to_upload)}")

if skipped_files:
    print("\nSkipping already uploaded files:")
    for name in skipped_files:
        print(f"  - {name}")

# Upload and import each file to the File Search store
operations = []
for file_path in files_to_upload:
    try:
        print(f"\nUploading: {file_path}")
        
        # Prepare custom metadata
        custom_metadata = []
        file_metadata = metadata_by_filename.get(file_path.name, {})
        
        if file_metadata:
            # Add article_name
            if file_metadata.get('article_name'):
                custom_metadata.append(
                    types.CustomMetadata(
                        key='article_name',
                        string_value=file_metadata['article_name']
                    )
                )
            
            # Add is_archived
            if file_metadata.get('is_archived'):
                custom_metadata.append(
                    types.CustomMetadata(
                        key='is_archived',
                        numeric_value=int(file_metadata['is_archived']) if file_metadata['is_archived'].isdigit() else 0
                    )
                )
            
            # Add is_news
            if file_metadata.get('is_news'):
                custom_metadata.append(
                    types.CustomMetadata(
                        key='is_news',
                        numeric_value=int(file_metadata['is_news']) if file_metadata['is_news'].isdigit() else 0
                    )
                )
            
            # Add article_year
            if file_metadata.get('article_year') and file_metadata['article_year'] != 'NULL':
                custom_metadata.append(
                    types.CustomMetadata(
                        key='article_year',
                        numeric_value=int(file_metadata['article_year'])
                    )
                )
            
            print(f"  Metadata: {len(custom_metadata)} fields added")
        else:
            print(f"  Warning: No metadata found for {file_path.name}")
        
        # Upload and import the file into the File Search store
        config = {
            'display_name': file_path.name,
        }
        if custom_metadata:
            config['custom_metadata'] = custom_metadata
        
        operation = client.file_search_stores.upload_to_file_search_store(
            file=str(file_path),
            file_search_store_name=file_search_store.name,
            config=config
        )
        
        operations.append((file_path.name, operation))
        print(f"Upload initiated for: {file_path.name}")
        
    except Exception as e:
        print(f"Error uploading {file_path}: {e}")

# Wait for all operations to complete
print("\n" + "="*60)
print("Waiting for all uploads to complete...")
print("="*60)

for file_name, operation in operations:
    try:
        
        operation = client.operations.get(operation)
        
        # Wait until import is complete
        while not operation.done:
            time.sleep(1)
            operation = client.operations.get(operation)
        
        if operation.error:
            print(f"❌ {file_name}: Error - {operation.error}")
        else:
            print(f"✓ {file_name}: Successfully imported")
            
    except Exception as e:
        print(f"❌ {file_name}: Exception - {e}")

print("\n" + "="*60)
print("All uploads completed!")
print("="*60)
print(f"\nFile Search Store Name: {file_search_store.name}")
print(f"Display Name: {file_search_store.display_name}")
print(f"New files uploaded: {len(operations)}")
print(f"Total documents in store: {len(existing_documents) + len(operations)}")
print(f"\nStore name saved to: {STORE_NAME_FILE}")

# Example of how to use the file search store in a query
print("\n" + "="*60)
print("Example usage:")
print("="*60)
print("""
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Your question here",
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=['{file_search_store.name}']
                )
            )
        ]
    )
)
print(response.text)
""")
