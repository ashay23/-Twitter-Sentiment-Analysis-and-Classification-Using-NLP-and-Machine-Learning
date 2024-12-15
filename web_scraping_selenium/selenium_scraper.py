# Import necessary libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
import os, time, csv

# Load environment variables from the .env file
load_dotenv()

# Retrieve the environment variables for Twitter login credentials
username = os.getenv('TWITTER_USERNAME')
password = os.getenv('TWITTER_PASSWORD')

# Set up Chrome WebDriver options (customizing browser behavior if needed)
options = webdriver.ChromeOptions()
# Initialize the WebDriver with the specified options
driver = webdriver.Chrome(options=options)

# Open the Twitter login page in the browser
driver.get('https://twitter.com/login')
# Wait for the page to load before interacting with it
time.sleep(5)

# Find the username input field and enter the username
username_field = driver.find_element(By.NAME, 'text')
username_field.send_keys(username) # Type in the username
username_field.send_keys(Keys.RETURN) # Press 'Enter' to submit the username
time.sleep(3) # Wait for the password field to load

# Find the password input field and enter the password
password_field = driver.find_element(By.NAME, 'password')
password_field.send_keys(password) # Type in the password
password_field.send_keys(Keys.RETURN) # Press 'Enter' to submit the password
time.sleep(5) # Wait for the login to complete

# Navigate to a specific user's Twitter timeline (e.g., Times of India)
driver.get('https://twitter.com/timesofindia')
# Wait for the timeline to load and display the user's tweets
time.sleep(10) # Adjust this time if needed based on the page load speed

from selenium.common.exceptions import StaleElementReferenceException

def extract_tweets(driver, num_tweets):
    tweets_list = []
    last_height = driver.execute_script("return document.body.scrollHeight")

    while len(tweets_list) < num_tweets:
        # Scroll down to load more tweets
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)  # Wait for new tweets to load

        # Re-locate tweet elements after scrolling
        try:
            tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]//div[@lang]')
            for tweet in tweets:
                tweet_text = tweet.text
                if tweet_text and tweet_text not in tweets_list:  # Avoid duplicates
                    tweets_list.append(tweet_text)
                if len(tweets_list) >= num_tweets:
                    break
        except StaleElementReferenceException:
            continue  # Skip and re-fetch elements in the next iteration

        # Check if the page is scrolled to the bottom
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # No new tweets loaded, exit the loop

        last_height = new_height

    return tweets_list

from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

def extract_tweets_parallel(driver, num_tweets, num_threads):
    # Thread-local storage to store tweets for each thread
    thread_local = threading.local()
    
    def task():
        # Initialize a local list for each thread
        thread_local.tweets_list = []
        new_tweets = extract_tweets(driver, num_tweets // num_threads)
        thread_local.tweets_list.extend(new_tweets)
        return thread_local.tweets_list
    
    tweets_list = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(task) for _ in range(num_threads)]
        for future in as_completed(futures):
            tweets_list.extend(future.result())  # Merge each thread's result

    return tweets_list

# Extract 100 tweets using 5 threads
tweets_list_100_parallel = extract_tweets_parallel(driver, 100, 5)

# Save tweets to a CSV file
csv_file = 'tweets_list_100_parallel.csv'
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['extracted tweets'])  # Header
    for tweet in tweets_list_100_parallel:
        writer.writerow([tweet])

# Close the WebDriver
driver.quit()