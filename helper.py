from wordcloud import WordCloud
from collections import Counter
import matplotlib.pyplot as plt
from urlextract import URLExtract
import pandas as pd
import emoji


# def fetch_format(choice,device, time_format):
#     if choice == 'Android_12hour':
#         device = 'Android'
#         time_format = '12 hour'
#     elif choice == 'Android_24hour':
#         device = 'Android'
#         time_format = '24 hour'
#     elif choice == 'iOS_12hour':
#         device = 'iOS'
#         time_format = '12 hour'
#     elif choice == 'iOS_24hour':
#         device = 'iOS'
#         time_format = '24 hour'
#     else:



def fetch_stats(df, selected_user):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    num_messages = df.shape[0]
    num_words = df['message'].str.split().apply(len).sum()
    num_media = df[df['message'] == '<Media omitted>'].shape[0]

    ex = URLExtract()
    urls = []
    for message in df['message']:
        urls.extend(ex.find_urls(message))
    num_links = len(urls)

    return num_messages, num_words, num_media, num_links, urls





def fetch_most_active_users(df):
    x = df['user'].value_counts().head()
    df = round(df['user'].value_counts() / df.shape[0] * 100, 2)
    df = df.reset_index().rename(columns={'index': 'user', 'user': 'percentage'})
    return x, df






def create_wordcloud(df, selected_users):

    if selected_users != 'Overall':
        df = df[df['user'] == selected_users]
    
        # Remove group notifications
    temp = df[df['user'] != 'Group_Notification']
    # remove <Media omitted> messages
    temp = temp[temp['message'] != '<Media omitted>']
    # remove empty messages
    temp = temp[temp['message'].str.strip() != '']

    wc = WordCloud(width=500, height=500, background_color='white')
    wc_image = wc.generate(temp['message'].str.cat(sep=" "))

    return wc_image





def most_common_words(df, selected_users):
    if selected_users != 'Overall':
        df = df[df['user'] == selected_users]

    # Remove group notifications
    temp = df[df['user'] != 'Group_Notification']
    # remove <Media omitted> messages
    temp = temp[temp['message'] != '<Media omitted>']
    # remove empty messages
    temp = temp[temp['message'].str.strip() != '']
    words = []

    # remove stopwords of hinglish
    # f = open('stop_hinglish.txt', 'r')
    # stop_words = f.read()
    # for message in temp['message']:
    #     for word in message.lower().split():
    #         if word not in stop_words:
    #             words.append(word)
    # cw = pd.DataFrame(Counter(words).most_common(20))

    for message in temp['message']:
        for word in message.lower().split():
                words.append(word)
    cw = pd.DataFrame(Counter(words).most_common(20),columns=['Word', 'Count'])

    return cw



def emoji_helper(df, selected_users):
    if selected_users != 'Overall':
        df = df[df['user'] == selected_users]
    emojis = []
    for word in df['message']:
        emojis.extend([c for c in word if emoji.is_emoji(c)])  # Check if the character is an emoji

    return pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))), columns=['Emoji', 'Count'])


def timeline(df, selected_user):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    time = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    time['time'] = time['year'].astype(str) + '-' + time['month'].astype(str) 
    # time['time'] = pd.to_datetime(time['time'])
    return time


def week_activity_map(df, selected_user):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()