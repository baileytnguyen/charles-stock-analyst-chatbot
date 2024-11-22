import streamlit as st
from datetime import datetime

def display_stock_news(news_list, ticker):
    """
    Displays the stock news in a readable format on the Streamlit webserver.

    Parameters:
    - news_list (list): A list of dictionaries containing news details.
    """
    
    # Add a main title
    st.title(f"{ticker} News")
    
    if not news_list:
        st.write("No news available for this stock.")
        return
    
    # Iterate through each news story and format it
    for article in news_list:
        
        # Format the published date to "YYYY-MM-DD"
        published_date = article['Published Date']
        formatted_date = (
            datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
            if published_date
            else "Unknown"
        )
        
        # Extract publisher logo URL
        logo_url = article.get("Source Logo URL")
        
        # Display the publisher logo if available
        if logo_url:
            st.image(logo_url, use_column_width=False, width=100)
            
        # Add Streamlit emoji shortcodes based on sentiment
        sentiment = article.get("Sentiment")
        sentiment_emoji = ""
        if sentiment == "positive":
            sentiment_emoji = ":smiley:"
        elif sentiment == "neutral":
            sentiment_emoji = ":neutral_face:"
        elif sentiment == "negative":
            sentiment_emoji = ":disappointed:"
            
        st.markdown(f"### {article['Title']}")
        st.markdown(f"**Author**: {article['Author'] or 'Unknown'}")
        st.markdown(f"**Source**: {article['Source Name'] or 'Unknown'}")
        st.markdown(f"**Published on**: {formatted_date}")
        st.markdown(f"**Description**: {article['Description']}")
        if article["Sentiment"]:
            st.markdown(f"**Sentiment**: {article['Sentiment'].capitalize()}\{sentiment_emoji}")
            st.markdown(f"**Reasoning**: {article['Sentiment Reasoning']}")
        st.markdown(f"[Read full article here]({article['Article URL']})")
        st.header("", divider=True)