# Use an official Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container (assuming it's inside the 'app' folder)
COPY app/requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files into the container
COPY app/. .

# Download necessary NLTK data
RUN python -m nltk.downloader wordnet omw-1.4 stopwords punkt punkt_tab

# Expose the port Streamlit uses
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "main.py"]