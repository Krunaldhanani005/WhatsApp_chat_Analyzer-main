import streamlit as st # type: ignore
import pandas as pd # type: ignore
import preprocess, helper
from wordcloud import WordCloud # type: ignore
import matplotlib.pyplot as plt # type: ignore

st.title("WhatsApp Data Analysis and Visualization App")
st.sidebar.title("Upload your data")

# variable declaration
if 'df' not in st.session_state:
    st.session_state.df = None
if 'choice' not in st.session_state:
    st.session_state.choice = None
if 'urls' not in st.session_state:
    st.session_state.urls = []
if 'show_links' not in st.session_state:
    st.session_state.show_links = False
device = None
time_format = None

st.session_state.choice = st.sidebar.radio("select your device and time format",['None','Android_12hour','Android_24hour','iOS_12hour','iOS_24hour'])
uploaded_file = st.sidebar.file_uploader("Upload your WhatsApp chat data", type="txt")
# button = st.sidebar.button("Analyz")

if uploaded_file is not None :
    if st.session_state.choice == 'Android_12hour':
        device = 'Android'
        time_format = '12 hour'
    elif st.session_state.choice == 'Android_24hour':
        device = 'Android'
        time_format = '24 hour'
    elif st.session_state.choice == 'iOS_12hour': 
        device = 'iOS'
        time_format = '12 hour'
    elif st.session_state.choice == 'iOS_24hour':
        device = 'iOS'
        time_format = '24 hour'
    elif st.session_state.choice == 'None':
        st.session_state.choice = None
    
    if st.session_state.choice is not None:

        with st.spinner('Processing chat data...'):
            data = uploaded_file.read().decode("utf-8")
            st.session_state.df = preprocess.preprocess(data,device,time_format)
            st.session_state.uploaded_file = uploaded_file

        df = st.session_state.df

        # Get unique users
        users_list = df['user'].unique().tolist()
        if 'Group_Notification' in users_list:
            users_list.remove('Group_Notification')
        users_list.sort()
        users_list.insert(0, 'Overall')
        selected_users = st.sidebar.selectbox("Select Users to Analyze", users_list)

        # if st.sidebar.button("Analyze"):

        if st.session_state.df is not None :
            # Display filtered dataframe
            if selected_users != 'Overall':
                df_filtered = df[df['user'] == selected_users]
                st.dataframe(df_filtered)
            else:
                st.dataframe(df)
            
            # Get statistics
            msg, words, media, link, urls = helper.fetch_stats(df, selected_users)
            st.session_state.urls = urls  # Store URLs in session state
            

            # Display stats
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.subheader("Total Messages")
                    st.title(msg)
                with c2:
                    st.subheader("Total Words")
                    st.title(words)
                with c3:
                    st.subheader("Total Media")
                    st.title(media)
                with c4:
                    st.subheader("Total Links")
                    st.title(link)
                    
                    # Show Links button
                    if st.button("Show Links"):
                        st.session_state.show_links = not st.session_state.show_links
            
            # Display links if button was clicked
            if st.session_state.show_links:
                if st.session_state.urls:
                    st.write("## Detected Links:")
                    for url in st.session_state.urls:
                        st.write(url)
                else:
                    st.write("No links found in the messages.")

            if selected_users == 'Overall':
                st.title('Most Active Users')
                x, per_df = helper.fetch_most_active_users(df)
                user_names = x.index
                user_counts = x.values
                c1, c2, c3 = st.columns([2, 2, 3])

                # Bar Chart
                with c1:

                    plt.figure(figsize=(10, 10))  # Set figure size
                    plt.barh(user_names, user_counts, color='orange')
                    plt.xlabel("Message Count")
                    plt.ylabel("Users")
                    plt.title("Top 5 Most Active Users")
                    # plt.tight_layout()  # Adjust layout
                    st.pyplot(plt)  # Display the matplotlib chart in Streamlit

                # Pie Chart
                with c2:

                    plt.figure(figsize=(10, 10))  # Set figure size
                    plt.pie(user_counts, labels=user_names, autopct='%1.1f%%', startangle=90)
                    plt.title("User Message Distribution")
                    # plt.tight_layout()  # Adjust layout
                    st.pyplot(plt)

                with c3:
                    st.dataframe(per_df, width=700)
            

            # Word Cloud
            st.title("Word Cloud")
            wc_img = helper.create_wordcloud(df, selected_users)
            # plt.figure(figsize=(10, 10))
            fig, ax = plt.subplots()
            ax.imshow(wc_img)
            st.pyplot(fig)

            # Most Common Words
            st.title('Most Common Words')
            common_words_df = helper.most_common_words(df, selected_users)
            st.dataframe(common_words_df)   

            # Emoji Analysis
            st.title('Emoji Analysis')
            emoji_df = helper.emoji_helper(df, selected_users)
            st.dataframe(emoji_df)

            # Time Analysis
            st.title('Time Analysis')
            time_df = helper.timeline(df, selected_users)

            # Convert columns to NumPy arrays for plotting
            time = time_df['time'].to_numpy()
            message_counts = time_df['message'].to_numpy()

            # Plot the data
            fig, ax = plt.subplots()
            ax.plot(time, message_counts, marker='*', color='orange',)
            plt.xticks(rotation='vertical')
            plt.xlabel("Date")
            plt.ylabel("Messages Count")
            plt.title("Messages over Time")
            st.pyplot(fig)

            # Display the DataFrame
            st.dataframe(time_df)

            # Weekly Activity
            st.title('Weekly Activity')
            user_activity_df = helper.week_activity_map(df, selected_users)
            # sort this df by day_name
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            user_activity_df = user_activity_df.reindex(days_order)
            fig, ax = plt.subplots()
            ax.bar(user_activity_df.index, user_activity_df.values, color='red')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
            
            st.dataframe(user_activity_df)
    else:
        st.sidebar.warning("Please select a device and time format.")
else:
    st.sidebar.warning("Please upload a file to analyze.")



# Add custom CSS for background image
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1563832528262-15e2bca87584?q=80&w=2019&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
        # background-image: url("https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?q=80&w=1974&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        # opacity: 0.5;
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: -1;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# sidebar_bg = ""  # Web URL
sidebar_bg = "https://images.unsplash.com/photo-1736942145358-ff047387450b?q=80&w=1887&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"  # Web URL

st.markdown(
    f"""
    <style>
    [data-testid="stSidebar"] > div:first-child {{
        width: 300px;
        background-image: url("{sidebar_bg}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        color:white; 
        text-shadow: 0.3px 0.3px 0.3px white,0.6px 0.6px 1px black;

        
    }}
    </style>
    """,
    unsafe_allow_html=True
)