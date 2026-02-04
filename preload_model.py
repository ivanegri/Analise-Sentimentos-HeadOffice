from pysentimiento import create_analyzer

print("Pre-loading model for Docker build...")
# This triggers the download and caching of the model
create_analyzer(task="sentiment", lang="pt")
print("Model downloaded successfully.")
