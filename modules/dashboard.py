import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from modules.config import TRACK_KEYWORDS, TRACK_SUBREDDITS, DATA_CSV, ROLLING_WINDOW_MINUTES
from modules.data_utils import load_data, aggregate_sentiment


def run_dashboard():
    st.set_page_config(layout="wide", page_title="Reddit Sentiment Tracker")
    # Add subtle background color for main area
    st.markdown("""
    <style>
    .main .block-container { background-color: #F8FAFC !important; }
    </style>
    """, unsafe_allow_html=True)
    
    # Custom CSS to change multiselect box colors to green
    st.markdown("""
    <style>
    /* Reduce Streamlit's default top padding */
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* Only style selected tags in green */
    span[data-baseweb="tag"] {
        background-color: #90EE90 !important;
        border: 1px solid #7DD87D !important;
    }
    
    /* Change multiselect tag text color to dark for better readability - only for selected items */
    span[data-baseweb="tag"] span {
        color: #2D5016 !important;
    }
    
    /* Change multiselect close button color - only for selected items */
    span[data-baseweb="tag"] svg {
        fill: #2D5016 !important;
    }
    
    /* Reset multiselect container to default styling */
    .stMultiSelect > div > div > div > div {
        background-color: white !important;
        border: 1px solid #d1d5db !important;
    }
    
    /* Keep placeholder text with default styling */
    .stMultiSelect > div > div > div > div > div[data-baseweb="select"] > div {
        background-color: transparent !important;
        color: #6b7280 !important;
    }
    
    /* Keep dropdown menu items with default styling */
    .stMultiSelect div[role="listbox"] {
        background-color: white !important;
    }
    
    .stMultiSelect div[role="option"] {
        background-color: white !important;
        color: black !important;
    }
    
    /* Ensure placeholder text stays default color */
    .stMultiSelect div[data-baseweb="select"] div {
        color: #6b7280 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 style="color: #1E3A8A; font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; margin-top: -60px; margin-bottom: 5px; font-size:2.2rem;">Sentiment Tracker</h1>', unsafe_allow_html=True)

    # Expanded options for dropdowns
    keyword_options = TRACK_KEYWORDS + [
        "Microsoft", "MSFT", "Amazon", "AMZN", "Google", "GOOGL", "Meta", "META", "Bitcoin", "BTC", "Ethereum", "ETH", "Nvidia", "NVDA", "Netflix", "NFLX", "AI", "ChatGPT", "OpenAI", "SpaceX", "Elon Musk", "Dogecoin", "DOGE", "Solana", "SOL", "Cardano", "ADA", "Polkadot", "DOT",
        "Apple", "AAPL", "Tesla", "TSLA", "Facebook", "FB", "crypto", "stocks", "investing", "technology", "news", "worldnews", "politics", "gaming", "sports", "music", "movies", "science", "health", "education", "travel", "food", "memes", "funny", "AskReddit", "data", "AI", "GPT", "LLM", "Reddit"
    ]

    # Load data early to get only available subreddits for dropdown (only subreddits with actual data)
    df_for_options = load_data()
    if not df_for_options.empty:
        # Only include subreddits that actually have data (appear in the dataset)
        data_subreddits = df_for_options['subreddit'].dropna().unique().tolist()
        subreddit_options = sorted(data_subreddits)
    else:
        # If no data, use a much larger default list of popular subreddits
        subreddit_options = TRACK_SUBREDDITS + [
            "technology", "news", "worldnews", "politics", "gaming", "sports", "music", "movies", "science", "health", "education", "travel", "food", "memes", "funny", "AskReddit", "dataisbeautiful", "CryptoCurrency", "investing", "stocks", "MachineLearning", "ArtificialInteligence", "GPT3", "GPT4", "OpenAI", "Python", "learnprogramming", "programming", "Space", "space", "TeslaMotors", "apple", "Google", "Nvidia", "Netflix", "Bitcoin", "Ethereum", "Solana", "Cardano", "Dogecoin", "Meta", "Facebook", "ElonMusk", "AAPL", "TSLA", "MSFT", "AMZN", "NVDA", "NFLX", "GOOGL", "META"
        ]

    # Sidebar controls
    st.sidebar.markdown('<h2 style="color: #1E3A8A; margin-bottom: 0.5rem; margin-top: 0.5rem; font-size:1.3rem;">Settings</h2>', unsafe_allow_html=True)
    # Time window selection
    time_unit = st.sidebar.selectbox(
        "Time Window Unit",
        options=["Minutes", "Hours", "Days"],
        index=0,
        help="Choose the unit for aggregation time window"
    )
    
    if time_unit == "Minutes":
        time_value = st.sidebar.number_input("Rolling window (minutes)", min_value=1, max_value=1440, value=ROLLING_WINDOW_MINUTES)
        rolling_mins = time_value
        time_display = f"{time_value} minute{'s' if time_value != 1 else ''}"
    elif time_unit == "Hours":
        time_value = st.sidebar.number_input("Rolling window (hours)", min_value=1, max_value=24, value=1)
        rolling_mins = time_value * 60
        time_display = f"{time_value} hour{'s' if time_value != 1 else ''}"
    else:  # Days
        time_value = st.sidebar.number_input("Rolling window (days)", min_value=1, max_value=30, value=1)
        rolling_mins = time_value * 60 * 24
        time_display = f"{time_value} day{'s' if time_value != 1 else ''}"
    
    # Custom time window option
    use_custom = st.sidebar.checkbox("Use custom time window")
    if use_custom:
        custom_mins = st.sidebar.number_input("Custom window (minutes)", min_value=1, max_value=43200, value=rolling_mins)
        rolling_mins = custom_mins
        if custom_mins >= 1440:
            days = custom_mins // 1440
            hours = (custom_mins % 1440) // 60
            mins = custom_mins % 60
            time_parts = []
            if days > 0:
                time_parts.append(f"{days} day{'s' if days != 1 else ''}")
            if hours > 0:
                time_parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
            if mins > 0:
                time_parts.append(f"{mins} minute{'s' if mins != 1 else ''}")
            time_display = ", ".join(time_parts)
        elif custom_mins >= 60:
            hours = custom_mins // 60
            mins = custom_mins % 60
            time_parts = []
            if hours > 0:
                time_parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
            if mins > 0:
                time_parts.append(f"{mins} minute{'s' if mins != 1 else ''}")
            time_display = ", ".join(time_parts)
        else:
            time_display = f"{custom_mins} minute{'s' if custom_mins != 1 else ''}"

    # Custom keyword input
    custom_keyword = st.sidebar.text_input("Add custom keyword", placeholder="Enter a keyword...")
    if custom_keyword and custom_keyword not in keyword_options:
        keyword_options.append(custom_keyword)

    selected_keywords = st.sidebar.multiselect(
        "Keywords",
        options=keyword_options,
        default=[],
        help="Choose keywords to track sentiment for"
    )

    # Custom subreddit input
    custom_subreddit = st.sidebar.text_input("Add custom subreddit", placeholder="Enter a subreddit...")
    if custom_subreddit and custom_subreddit not in subreddit_options:
        subreddit_options.append(custom_subreddit)

    selected_subreddits = st.sidebar.multiselect(
        "Subreddits",
        options=subreddit_options,
        default=[],
        help="Choose subreddits to monitor for discussions"
    )

    # Action buttons
    st.sidebar.markdown("---")
    
    start_listening = st.sidebar.button("🎯 Start Live Stream", type="primary", help="Begin collecting real-time Reddit data", width="stretch")
    fetch_data = st.sidebar.button("📊 Fetch Historical Data", help="Load existing data from CSV file", width="stretch")
    save_data = st.sidebar.button("💾 Save Current Data", help="Save the current dataset to CSV file", width="stretch")
    
    live_stream_message = None
    if start_listening:
        from modules.reddit_client import start_background
        from modules.processing import start_processing
        # Update keywords and subreddits for streaming if selected
        keywords_to_use = selected_keywords if selected_keywords else keyword_options[:3]
        subreddits_to_use = selected_subreddits if selected_subreddits else subreddit_options[:3]
        live_stream_message = st.sidebar.container()
        live_stream_message.success(f"🚀 Starting live stream for {len(keywords_to_use)} keywords and {len(subreddits_to_use)} subreddits!")
        live_stream_message.info("Check console for streaming status...")
        # Start background threads
        start_background(listen=True)
        start_processing()
        # Auto-refresh every 30 seconds while waiting for new data
        st.experimental_rerun_interval = 30

    # Load data & aggregate
    df = load_data()

    # Remove live stream message once new data is available
    if start_listening and not df.empty:
        live_stream_message.empty()
        # Stop auto-refresh once data is available
        st.experimental_rerun_interval = None
    
    if fetch_data:
        st.sidebar.success("📁 Loading data from CSV...")
        st.rerun()
    
    
    if save_data:
        # This will be handled after df is loaded
        pass

    # Load data & aggregate
    df = load_data()
    
    # Handle save_data after df is loaded
    if save_data:
        if not df.empty:
            st.sidebar.success(f"✅ Data saved! {len(df)} rows in {DATA_CSV}")
        else:
            st.sidebar.warning("⚠️ No data to save")
    
    # Remove duplicates based on text content and timestamp to show unique messages
    if not df.empty:
        df = df.drop_duplicates(subset=['text', 'created_utc'], keep='first')
    
    # Apply user filters to the data
    filtered_df = df.copy()
    total_records = len(df)
    
    # Filter by selected keywords
    if selected_keywords:
        keyword_filter = filtered_df['text'].str.contains('|'.join(selected_keywords), case=False, na=False)
        filtered_df = filtered_df[keyword_filter]
    
    # Filter by selected subreddits
    if selected_subreddits:
        filtered_df = filtered_df[filtered_df['subreddit'].isin(selected_subreddits)]
    
    filtered_records = len(filtered_df)
    
    # Apply aggregation to filtered data
    agg = aggregate_sentiment(filtered_df, window_minutes=rolling_mins)

    # Create main dashboard layout with three columns for compactness
    col1, col2, col3 = st.columns([2, 2, 2])

    with col1:
        st.markdown('<div style="text-align:center;"><h4 style="color: #1E3A8A; margin-bottom: 0px; font-size:1.2rem;">Sentiment Trends</h4>'
                    f'<p style="color: #4B5563; margin-top: 2px; margin-bottom: 6px; font-size:0.95rem;">Sentiment Analysis Over Time ({time_display} windows)</p></div>', unsafe_allow_html=True)
        if agg.empty:
            st.markdown('<div style="text-align:center;"><p style="color: #4B5563; font-style: italic; font-size:0.95rem;">No data yet. Click \'Start Live Stream\' or \'Fetch Historical Data\' to see analytics.</p></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="display:flex; justify-content:center;">', unsafe_allow_html=True)
            fig_line = px.line(agg, x="created_utc", y="sentiment_mean", 
                              labels={"sentiment_mean": "Sentiment Score", "created_utc": "Time"},
                              color_discrete_sequence=["#90EE90"])
            fig_line.update_layout(
                xaxis_title="Time",
                yaxis_title="Sentiment Score",
                hovermode='x unified',
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=10, b=10, l=10, r=10),
                height=280
            )
            fig_line.add_hline(y=0, line_dash="dash", line_color="orange", 
                              annotation_text="Neutral", annotation_position="bottom right")
            st.plotly_chart(fig_line, width="stretch")
            st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div style="text-align:center; margin-left: 2ch;"><h4 style="color: #1E3A8A; margin-bottom: 0px; font-size:1.2rem;">Sentiment Distribution</h4>'
                    '<p style="color: #4B5563; margin-top: 2px; margin-bottom: 6px; font-size:0.95rem;">Message Sentiment Breakdown</p></div>', unsafe_allow_html=True)
        if not filtered_df.empty:
            st.markdown('<div style="display:flex; justify-content:center; margin-left: 2ch;">', unsafe_allow_html=True)
            df_viz = filtered_df.copy()
            df_viz['sentiment_category'] = df_viz['sentiment_compound'].apply(
                lambda x: 'Positive' if x > 0.1 else ('Negative' if x < -0.1 else 'Neutral')
            )
            sentiment_counts = df_viz['sentiment_category'].value_counts()
            colors = []
            labels = []
            values = []
            for category in sentiment_counts.index:
                labels.append(category)
                values.append(sentiment_counts[category])
                if 'Positive' in category:
                    colors.append('#90EE90')
                elif 'Negative' in category:
                    colors.append('#FFB347')
                else:
                    colors.append('#FFFF99')
            fig_pie = px.pie(values=values, names=labels,
                            color_discrete_sequence=colors)
            fig_pie.update_layout(
                height=280,
                margin=dict(t=10, b=10, l=10, r=0),  # Minimal right margin
                showlegend=True,
                legend=dict(orientation="v", font=dict(size=12), xanchor="left", x=0.8, yanchor="middle", y=0.5)  # Legend even closer
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, width="stretch")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align:center;"><p style="color: #4B5563; font-style: italic; font-size:0.95rem;">Sentiment distribution will appear after data collection</p></div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div style="text-align:center; margin-left: 2ch;"><h4 style="color: #1E3A8A; margin-bottom: 0px; font-size:1.2rem;">Channel Activity</h4>'
                    '<p style="color: #4B5563; margin-top: 2px; margin-bottom: 6px; font-size:0.95rem;">Top Active Subreddits</p></div>', unsafe_allow_html=True)
        if not filtered_df.empty:
            st.markdown('<div style="display:flex; justify-content:center; margin-left: 2ch;">', unsafe_allow_html=True)
            subreddit_counts = filtered_df['subreddit'].value_counts().head(6)
            fig_donut = px.pie(values=subreddit_counts.values, names=subreddit_counts.index,
                                   hole=0.4,
                                   color_discrete_sequence=px.colors.qualitative.Set2)
            fig_donut.update_layout(
                height=280,
                showlegend=True,
                legend=dict(orientation="v", font=dict(size=12), xanchor="left", x=0.8, yanchor="middle", y=0.5),  # Legend even closer
                margin=dict(t=10, b=10, l=10, r=0)  # Minimal right margin
            )
            fig_donut.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_donut, width="stretch")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align:center;"><p style="color: #4B5563; font-style: italic; font-size:0.95rem;">Channel activity will appear after data collection</p></div>', unsafe_allow_html=True)

    # Message Volume Bar Chart below main charts
    st.markdown('<h4 style="color: #1E3A8A; margin-bottom: 0px; font-size:1.2rem;">Message Volume</h4>', unsafe_allow_html=True)
    st.markdown(f'<p style="color: #4B5563; margin-top: 2px; margin-bottom: 6px; font-size:0.95rem;">Messages per {time_display} window</p>', unsafe_allow_html=True)
    if not agg.empty:
        fig_bar = px.bar(agg, x="created_utc", y="message_count", 
                        labels={"message_count": "Number of Messages", "created_utc": "Time"},
                        color="message_count",
                        color_continuous_scale=[[0, '#FFFF99'], [0.5, '#FFB347'], [1, '#90EE90']])
        fig_bar.update_layout(
            xaxis_title="Time",
            yaxis_title="Message Count",
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=10, b=10, l=10, r=10),
            height=220
        )
        st.plotly_chart(fig_bar, width="stretch")
    else:
        st.markdown('<p style="color: #4B5563; font-style: italic; font-size:0.95rem;">Volume chart will appear after data collection</p>', unsafe_allow_html=True)

    # Data Table in Expander for compactness
    with st.expander("Recent Activity (last 20 messages)", expanded=False):
        if filtered_df.empty:
            st.markdown('<p style="color: #4B5563; font-style: italic; font-size:0.95rem;">No items match your filters.</p>', unsafe_allow_html=True)
        else:
            recent_data = (filtered_df
                          .drop_duplicates(subset=['text'], keep='last')
                          .sort_values("created_utc", ascending=False)
                          .head(20)[["created_utc", "subreddit", "text", "sentiment_compound"]])
            display_data = recent_data.copy()
            def format_sentiment(score):
                try:
                    sc = float(score)
                    if sc >= 0.05:
                        return f"🟢 {sc:.3f} (Positive)"
                    elif sc <= -0.05:
                        return f"🟠 {sc:.3f} (Negative)"
                    else:
                        return f"🟡 {sc:.3f} (Neutral)"
                except:
                    return "N/A"
            display_data['text'] = display_data['text'].apply(lambda x: str(x)[:100] + "..." if len(str(x)) > 100 else str(x))
            display_data['sentiment_compound'] = display_data['sentiment_compound'].apply(format_sentiment)
            display_data.columns = ['Timestamp', 'Subreddit', 'Message', 'Sentiment']
            st.dataframe(
                display_data,
                width="stretch",
                hide_index=True,
                column_config={
                    "Timestamp": st.column_config.DatetimeColumn(
                        "Timestamp",
                        width="medium"
                    ),
                    "Subreddit": st.column_config.TextColumn(
                        "Subreddit",
                        width="small"
                    ),
                    "Message": st.column_config.TextColumn(
                        "Message",
                        width="large"
                    ),
                    "Sentiment": st.column_config.TextColumn(
                        "Sentiment",
                        width="medium"
                    )
                }
            )