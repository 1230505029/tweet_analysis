import tweepy
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import asyncio
from textblob import TextBlob

# Twitter API Kimlik Bilgileri
TWITTER_CREDENTIALS = {
    "API_KEY": "YOUR_API_KEY",
    "API_SECRET": "YOUR_API_SECRET",
    "ACCESS_TOKEN": "YOUR_ACCESS_TOKEN",
    "ACCESS_SECRET": "YOUR_ACCESS_SECRET"
}

def authenticate_twitter():
    """ Twitter API'ye kimlik doğrulaması yapar. """
    auth = tweepy.OAuthHandler(TWITTER_CREDENTIALS["API_KEY"], TWITTER_CREDENTIALS["API_SECRET"])
    auth.set_access_token(TWITTER_CREDENTIALS["ACCESS_TOKEN"], TWITTER_CREDENTIALS["ACCESS_SECRET"])
    return tweepy.API(auth, wait_on_rate_limit=True)

async def get_tweets(api, keyword, max_tweets=100):
    """ Belirtilen anahtar kelimeye göre tweetleri asenkron olarak getirir. """
    tweets_data = []
    try:
        for tweet in tweepy.Cursor(api.search_tweets, q=keyword, lang="tr", tweet_mode="extended").items(max_tweets):
            tweets_data.append({
                "text": tweet.full_text,
                "created_at": tweet.created_at,
                "likes": tweet.favorite_count,
                "retweets": tweet.retweet_count
            })
    except tweepy.TweepError as error:
        print(f"Twitter API Hatası: {error}")
    return pd.DataFrame(tweets_data)

def analyze_sentiment(df):
    """ Tweet metinlerini analiz eder ve duygu skorlarını ekler. """
    df["polarity"] = df["text"].apply(lambda text: TextBlob(text).sentiment.polarity)
    df["subjectivity"] = df["text"].apply(lambda text: TextBlob(text).sentiment.subjectivity)

    df["sentiment"] = df["polarity"].apply(lambda score: "Positive" if score > 0 else ("Negative" if score < 0 else "Neutral"))
    return df

def plot_sentiment_distribution(df, keyword):
    """ Tweetlerin duygu dağılımını çizer. """
    plt.figure(figsize=(8, 6))
    sns.countplot(x="sentiment", data=df, order=["Positive", "Neutral", "Negative"], palette="coolwarm")
    plt.title(f"'{keyword}' Konulu Tweetlerin Duygu Dağılımı")
    plt.show()

def plot_engagement_distribution(df):
    """ Retweet ve beğeni sayılarını dağılım grafiğinde gösterir. """
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=df["retweets"], y=df["likes"], hue=df["sentiment"], palette="Set1", alpha=0.7)
    plt.xscale("log")
    plt.yscale("log")
    plt.title("Retweet - Beğeni Dağılımı (Log Ölçek)")
    plt.xlabel("Retweet Sayısı")
    plt.ylabel("Beğeni Sayısı")
    plt.show()

async def main():
    api = authenticate_twitter()
    keyword = "teknoloji"
    tweet_limit = 150

    tweets_df = await get_tweets(api, keyword, tweet_limit)
    if not tweets_df.empty:
        tweets_df = analyze_sentiment(tweets_df)
        plot_sentiment_distribution(tweets_df, keyword)
        plot_engagement_distribution(tweets_df)
    else:
        print("Hiç tweet bulunamadı!")

if __name__ == "__main__":
    asyncio.run(main())
