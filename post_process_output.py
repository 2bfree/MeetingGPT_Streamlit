import numpy as np
import re
import pandas as pd

def extract_data_main_topics(row):
    topics_data = re.findall(r'\d+\.\s*([^:(\n]+)\s*(?:\(\d+(?:\.\d+)?%\))*', row['MainTopics'])
    filtered_topics_data = [item.strip() for item in topics_data if item]
    percentage_data = re.findall(r'\d+\..*?(\d+\%)', row['MainTopics'])
    topics_dict = dict(zip(filtered_topics_data, percentage_data))
    df = pd.DataFrame(list(topics_dict.items()), columns=['Topic', 'Percentage'])
    df['meeting_id'] = row['meeting_id']
    return df

# Function to extract data from each row
def extract_data_participant_contributions(row):
    pattern = r"(\w+):.*?(\d+%).*?(\d+)"
    # Find all matches
    # print(row['ParticipantContributions'])
    matches = re.findall(pattern, row['ParticipantContributions'], flags=re.IGNORECASE)

    # Extracted data
    speakers = [match[0] for match in matches]
    speaking_time = [match[1] for match in matches]
    interactions = [int(match[2]) for match in matches]

    df = pd.DataFrame({
    'Speakers': speakers,
    'Speaking Time': speaking_time,
    'Interactions': interactions
    })
    df['meeting_id'] = row['meeting_id']
    return df

# Function to extract the word with " " around it or return the original word if it's a single word
def extract_sentiment(answer):
    words = answer.split()
    if len(words) == 1:
        return words[0]
    else:
        for word in words:
            if word.startswith('"') and word.endswith('"'):
                return word[1:-1]
        return answer
    
# Function to determine sentiment
def determine_sentiment(text):
    positive_words = ["positive", "productive", "collaborative", "constructive", "efficient", "professional", "innovative"]
    negative_words = ["negative", "unproductive", "chaotic", "argumentative", "tense", "inefficient"]

    words = text.lower().split()

    if any(word in words for word in positive_words):
        return "Positive"
    elif any(word in words for word in negative_words):
        return "Negative"
    else:
        return "Neutral"

def reformat_for_visuals(df):
    df[['Summary', 'MainTopics', 'ParticipantContributions', 'ActionItems', 'Sentiment']] = df['final_response'].str.split('\n\n', 4, expand=True)

    c1 = df['Sentiment'].isna()
    df.loc[c1, 'Sentiment'] = df.loc[c1, 'ActionItems']
    c2 = df['Sentiment'] == df['ActionItems']
    df.loc[c1, 'ActionItems'] = df.loc[c1, 'ParticipantContributions']

    # Main Topics df
    main_topics_df = pd.concat([extract_data_main_topics(row) for _, row in df.iterrows()], ignore_index=True)

    # Engagement df
    engagement_df = pd.concat([extract_data_participant_contributions(row) for _, row in df.iterrows()], ignore_index=True)

    engagement_df['Speaking Time'] = engagement_df['Speaking Time'].str.rstrip('%').astype('float') / 100.0

    grouped_df = engagement_df.groupby('meeting_id')
    engagement_df['Scaled Speaking Time'] = grouped_df['Speaking Time'].transform(lambda x: (x / x.sum()) * 100)
    engagement_df['Speaking_Time'] = engagement_df['Scaled Speaking Time'].round(1).map('{:.1f}%'.format)

    # Sentiment Post-Process
    df['Sentiment'] = df['Sentiment'].fillna('Neutral')
    df['Sentiment_1Word'] = df['Sentiment'].apply(extract_sentiment).str.split('\n').apply(lambda x: x[-1] if x else '')

    # Extracting multi-word categories
    multi_word_categories = ['Productive', 'Collaborative', 'Informational', 'Neutral', 'Professional', 'Standard', 'Technical', 
                             'Tense']

    # Creating a regex pattern to match multi-word categories
    pattern = re.compile('|'.join(rf'\b{re.escape(word)}\b' for word in multi_word_categories), re.IGNORECASE)

    # Applying the regex pattern to the 'sentiment' column and creating a new column 'category'
    df['sentiment_category'] = df['Sentiment_1Word'].apply(lambda x: pattern.search(x).group().capitalize() if pattern.search(x) else 'Neutral')

    # Apply the function to create a new column 'Sentiment'
    df['Sentiment_Color'] = df['sentiment_category'].apply(determine_sentiment)

    main_topics_df['Percentage'] = main_topics_df['Percentage'].str.rstrip('%').astype('int')
    engagement_df['Speaking_Time'] = engagement_df['Speaking_Time'].str.rstrip('%').astype('float')
    engagement_df['Interactions'] = engagement_df['Interactions'].astype(int)

    df['Summary_Clipped'] = df['Summary'].str.split('Abstract Summary\n').str[1]
    df['ActionItems_Clipped'] = df['ActionItems'].str.split('Action Items\n').str[1]

    return df, main_topics_df, engagement_df
