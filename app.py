import pandas as pd
import re
import streamlit as st
import pickle
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Ensure necessary NLTK data is downloaded
def download_nltk_data():
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet')
    try:
        nltk.data.find('corpora/omw-1.4')
    except LookupError:
        nltk.download('omw-1.4')
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        nltk.download('punkt_tab')

download_nltk_data()  # Call to download necessary NLTK data once at the start

# Define the CleaningPipeline class
class CleaningPipeline:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))

    def remove_non_ascii(self, text):
        """Remove non-ASCII characters from the text"""
        return re.sub(r'[^\x00-\x7F]+', '', text)

    def remove_whitespace_and_special_chars(self, text):
        """Remove extra whitespace and special characters"""
        text = re.sub(r'\s+', ' ', text).lower()  # Replace multiple spaces with a single space
        return re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove non-alphanumeric characters

    def remove_stopwords(self, text):
        """Remove stopwords"""
        return " ".join([word for word in word_tokenize(text) if word.lower() not in self.stop_words])

    def word_lemmatization(self, text):
        """Lemmatize words in the text"""
        lemmatizer = WordNetLemmatizer()
        return " ".join([lemmatizer.lemmatize(word) for word in word_tokenize(text)])

    def transform(self, text):
        if not isinstance(text, str):
            text = str(text)  # Convert to string if not already
        text = self.remove_non_ascii(text)
        text = self.remove_whitespace_and_special_chars(text)
        text = self.remove_stopwords(text)
        text = self.word_lemmatization(text)
        return re.sub(r'\d+', '', text)  # Remove numerics last to avoid messing up other steps

def identify_text_column(df):
    """Automatically identify the text column based on content."""
    text_column = df.select_dtypes(include=['object']).apply(lambda x: x.str.split().str.len().mean(), axis=0).idxmax()
    return text_column

def predict_sentiment(pipeline, text_data):
    """Predict sentiment using the model pipeline."""
    prediction = pipeline.predict([text_data])
    return {0: 'Negative', 4: 'Positive'}.get(prediction[0], 'Unknown')  # Default to 'Unknown' if label is unexpected

def process_text_data(df, text_column, pipeline):
    """Process text data from a CSV and predict sentiment."""
    # Apply cleaning pipeline
    cleaning_pipeline = CleaningPipeline()
    df['cleaned_text'] = df[text_column].fillna('').apply(cleaning_pipeline.transform)

    # Predict sentiment
    df['predictions'] = df['cleaned_text'].apply(lambda x: predict_sentiment(pipeline, x))

    return df[['cleaned_text', 'predictions']]

def validate_csv_file(df):
    """Ensure the CSV file contains data."""
    if df.empty:
        st.error("The uploaded CSV file is empty. Please upload a valid file.")
        return False
    return True

def main():
    st.title("Text Processing and Classification")
    
    # Model loading
    try:
        with open('vectorization_model_pipeline_1.pkl', 'rb') as file:
            pipeline = pickle.load(file)
    except Exception as e:
        st.error(f"Error loading model pipeline: {e}")
        return

    option = st.sidebar.selectbox("Choose the functionality", ("Upload CSV", "Enter Text"))
    
    if option == "Upload CSV":
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except UnicodeDecodeError:
                st.error("Unable to decode the file. Please ensure it is UTF-8 encoded.")
                return
            
            # Validate CSV file
            if not validate_csv_file(df):
                return

            # Start spinner while processing
            with st.spinner('Processing your CSV...'):
                text_column = identify_text_column(df)
                if text_column:
                    st.write(f"Detected text column: {text_column}")
                    st.write(df[text_column])
                    processed_data = process_text_data(df, text_column, pipeline)
                    st.write(processed_data)
                    
                    # Provide download option
                    csv = processed_data.to_csv(index=False).encode('utf-8')
                    st.download_button("Download Processed Data", csv, "processed_data.csv", "text/csv")
    elif option == "Enter Text":
        user_input = st.text_area("Enter your text here:")
        if st.button("Analyze Sentiment"):
            if user_input.strip():
                with st.spinner('Analyzing sentiment...'):
                    cleaned_text = CleaningPipeline().transform(user_input)
                    sentiment = predict_sentiment(pipeline, cleaned_text)
                    st.subheader("Sentiment Analysis Result")
                    st.write(f"The sentiment of the entered text is: {sentiment}")
            else:
                st.warning("Please enter some text for analysis.")

if __name__ == '__main__':
    main()
