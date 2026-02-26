from google import genai
import sys

print("Checking methods...")
try:
    # apiKey is dummy, we just want to inspect the class
    client = genai.Client(api_key="dummy")
    
    print("Methods in client.models:")
    for m in dir(client.models):
        if "generate" in m:
            print(f" - {m}")
            
except Exception as e:
    print(f"Error: {e}")
