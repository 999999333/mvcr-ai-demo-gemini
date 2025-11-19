from google import genai
from google.genai import types
import time

client = genai.Client(api_key='***REMOVED***')

# Ask a question about the file
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="""Kdo je aktualni prezident?""",
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=["fileSearchStores/mvcraidocs-h8ynqvk4r9rx"],
                )
            )
        ]
    )
)

print(response.text, response.candidates[0].grounding_metadata)