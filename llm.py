from google import genai
from google.genai import types
import time

client = genai.Client(api_key='***REMOVED***')

# Read the file search store name from the saved file
with open('file_search_store_name.txt', 'r') as f:
    store_name = f.read().strip()

print(f"Using File Search Store: {store_name}\n")

# Ask a question about the file
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="""Kdo je aktualni prezident?""",
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[store_name],
                    # metadata_filter="is_news=1"  # Uncomment to filter by metadata
                )
            )
        ]
    )
)

print(response.text)
print("\n" + "="*60)
print("Grounding Metadata:")
print("="*60)

grounding = response.candidates[0].grounding_metadata
if grounding and grounding.grounding_chunks:
    # Cache document metadata to avoid repeated API calls

    for i, chunk in enumerate(grounding.grounding_chunks, 1):
        print(f"\n{'='*60}")
        print(f"Chunk {i}:")
        print('='*60)
        
        if hasattr(chunk, 'retrieved_context') and chunk.retrieved_context:
            ctx = chunk.retrieved_context
            url = f"https://policie.gov.cz/clanek/{ctx.title[:-3]}.aspx"
            print(f"  Document: {ctx.title}")
            print(f"  Source URI: {url}")
            # Show a snippet of the text
            if hasattr(ctx, 'text') and ctx.text:
                snippet = ctx.text[:200].replace('\n', ' ')
                print(f"  Text snippet: {snippet}...")
else:
    print("No grounding metadata available")

print(response.candidates[0].grounding_metadata)