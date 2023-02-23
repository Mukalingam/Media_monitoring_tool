import streamlit as st
import feedparser
import nltk
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from textblob import TextBlob
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
import pandas as pd
import streamlit.components.v1 as components
import datetime
import base64

def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img = get_img_as_base64("menu.jpg") 
img2 = get_img_as_base64("cover.jpg") 


# Function to collect RSS feed URLs
def collect_rss_feeds():
    st.sidebar.title("RSS Feed Reader")
    rss_feeds = st.sidebar.text_input("Enter RSS feed URLs (separated by commas):")
    if rss_feeds:
        return rss_feeds.split(",")
    else:
        return []

# Function to collect keywords
def collect_keywords():
    keywords = st.sidebar.text_input("Enter keywords (separated by commas):")
    if keywords:
        return keywords.split(",")
    else:
        return []

# Function to generate word cloud
def generate_wordcloud(text):
    wordcloud = WordCloud().generate(text)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    st.pyplot()

# Function to perform sentiment analysis
def sentiment_analysis(text):
    sentiments = []
    nltk.download('vader_lexicon')
    from nltk.sentiment import SentimentIntensityAnalyzer
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(text)
    sentiments.append(sentiment)
    for sentiment in sentiments:
        return sentiment

def summarize_text(text):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, 4)
    summary_str = " ".join([str(sentence) for sentence in summary])
    return summary_str

import requests

def get_social_posting_count(url):
    response = requests.get(f"https://graph.facebook.com/?id={url}")
    data = response.json()
    return data.get("share", {}).get("share_count", 0)


# Main function
def main():
    st.set_page_config(page_title="RSS Feed Reader", page_icon=":newspaper:", layout="wide")
    page_bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"] > .main {{
    background-image: url("data:image/png;base64,{img2}");
    background-size: 140%;
    background-position: top left;
    background-repeat: no-repeat;
    background-attachment: local;
    }}
    [data-testid="stSidebar"] > div:first-child {{
    background-image: url("data:image/png;base64,{img}");
    background-position: center; 
    background-repeat: no-repeat;
    background-attachment: fixed;
    }}
    [data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
    }}
    [data-testid="stToolbar"] {{
    right: 2rem;
    }}
    </style>
    """  
    st.markdown(page_bg_img, unsafe_allow_html=True)
    hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
    st.markdown(hide_st_style, unsafe_allow_html=True)
    st.title("Welcome to Media Marketing Tool!!")
    st.markdown("This application allows you to fetch articles from multiple RSS feed URLs, search for keywords in the articles and then view the sentiment analysis, word clouds and summarization of the articles containing the keywords.")
    article_choice=None

    # Collect RSS feed URLs and keywords using the menu bar
    rss_feeds = collect_rss_feeds()
    keywords = collect_keywords()
    if st.button("Fetch Articles"):
        # Parse RSS feeds and extract articles
        articles = []
        for rss_feed in rss_feeds:
            parsed_feed = feedparser.parse(rss_feed)
            for entry in parsed_feed.entries:
                articles.append(entry.summary)

        # Search for keywords in articles
        keyword_articles = []
        for keyword in keywords:
            for article in articles:
                if keyword in article:
                    keyword_articles.append(article)
        st.success("Fetched {} articles".format(len(articles)))
        print(keyword_articles)
        # Display articles that contain keywords
        st.write("Articles containing keywords are shown below")
        #df = pd.DataFrame(articles,columns="Article_Name")
        st.table(keyword_articles)
        article_choice = st.selectbox("Select an article:", keyword_articles)

        # Generate word cloud, sentiment analysis and summarization
    if not article_choice is None :
        
        summarization_tab,sentiment_tab,wordcloud_tab= st.tabs(["Summarization", "Sentiment Analysis", "Word Cloud"])
        with wordcloud_tab:
            st.subheader("Word Cloud")
            generate_wordcloud(article_choice)
            st.write("Social Media Posting count: ", get_social_posting_count(article_choice))
            #st.write("View count: ", get_view_count(article_choice))

        with sentiment_tab:
            st.subheader("Sentiment Analysis")
            sentiment = sentiment_analysis(article_choice)
            st.write(sentiment)

        with summarization_tab:
            st.subheader("Summarization")
            summary = summarize_text(article_choice)
            st.write(summary)


if __name__== "__main__":
    main()
