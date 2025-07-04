try:
    import google.generativeai as genai  # type: ignore
    import vertexai                     # type: ignore
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "google-cloud-aiplatform", "google-generativeai"])
    import google.generativeai as genai  # type: ignore
    import vertexai                     # type: ignore

import os

project  = os.getenv("VERTEX_PROJECT")
location = os.getenv("VERTEX_LOCATION", "us-central1")
vertexai.init(project=project, location=location)

api_key = os.getenv("GOOGLE_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")
resp = model.generate_content("Write a haiku about Patrianna, the product company, in English.")
print(resp.text)
