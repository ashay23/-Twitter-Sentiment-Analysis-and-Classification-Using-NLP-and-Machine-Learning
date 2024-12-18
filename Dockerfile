# Use an official lightweight Python image as the base
FROM python:3.11-slim

# Set the working directory inside the container to organize files
WORKDIR /app

# Copy the dependency list (requirements.txt) into the container
# This step is separated to leverage Docker's caching mechanism for dependencies
COPY requirements.txt .

# Install Python dependencies and required NLTK data
# - Upgrade pip for compatibility with newer packages
# - Use --no-cache-dir to avoid caching installation files and reduce image size
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    python -m nltk.downloader wordnet omw-1.4 stopwords punkt punkt_tab

# Copy the remaining application files into the working directory
# This includes the main application code and any supporting resources
COPY . .

# Expose the default port used by Streamlit to enable external access
EXPOSE 8501

# Specify the command to run the Streamlit application
# This launches the app using Streamlit on the default port
CMD ["streamlit", "run", "app.py"]
