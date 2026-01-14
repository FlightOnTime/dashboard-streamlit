import streamlit as st
from streamlit import Page, navigation

st.set_page_config(layout="wide")

st.markdown("""
<style>
    .stApp { 
        background-color: #ffffff;
        
        background-image: linear-gradient(rgba(255,255,255,0.8), rgba(255,255,255,0.8)), 
                          url("https://upload.wikimedia.org/wikipedia/commons/8/80/World_map_-_low_resolution.svg");
        
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }
</style>
""", unsafe_allow_html=True)

st.title("Flight Delay")

Nova_Previsão= Page("pages/Nova_Previsão.py")
Dashboard= Page("pages/Dashboard.py")
Storytelling= Page("pages/Storytelling.py")

nav = navigation([Nova_Previsão, Dashboard, Storytelling])
nav.run()
