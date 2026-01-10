import streamlit as st
from streamlit import Page, navigation

st.set_page_config(layout="wide")

themes = {
    "Light": {
        "primaryColor": "#ff4b4b",
        "backgroundColor": "#ffffff",
        "secondaryBackgroundColor": "#f0f2f6",
        "textColor": "#31333f"
    },
    "Dark": {
        "primaryColor": "#ff4b4b",
        "backgroundColor": "#0D0D0D",
        "secondaryBackgroundColor": "1A1A1A",
        "textColor": "#fafafa"
    }
}


col1, col2 = st.columns([0.85, 0.15])

with col1:
    st.title("Flight Delay")

with col2:
    chosen_theme = st.selectbox(
        "Selecione o Tema:", 
        list(themes.keys()), 
        label_visibility="collapsed" 
    )

def apply_theme(theme_name):
    theme = themes[theme_name]
    css = f"""
    <style>
        :root {{
            --primary-color: {theme['primaryColor']};
            --background-color: {theme['backgroundColor']};
            --secondary-background-color: {theme['secondaryBackgroundColor']};
            --text-color: {theme['textColor']};
        }}
        .stApp {{
            background-color: {theme['backgroundColor']};
            color: {theme['textColor']};
        }}
        [data-testid="stSidebar"] {{
            background-color: {theme['secondaryBackgroundColor']};
        }}
        .stButton>button {{
            color: {theme['textColor']};
            border-color: {theme['primaryColor']};
            background-color: {theme['secondaryBackgroundColor']};
        }}
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)

apply_theme(chosen_theme)

Dashboard= Page("pages/Dashboard.py")
Storytelling= Page("pages/Storytelling.py")

nav = navigation([Dashboard, Storytelling])
nav.run()
