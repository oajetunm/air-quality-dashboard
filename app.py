#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  8 17:19:38 2025

@author: olubisiajetunmobi
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px

import base64
st.set_page_config(
    page_title="Local Air Quality & Weather",
    layout="centered",
    initial_sidebar_state="expanded"  # <-- keeps sidebar open
)



def get_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

bg_image = get_base64("background.jpg")

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bg_image}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """,
    unsafe_allow_html=True
)



st.title("🌤️ Local Weather & Air Quality Dashboard")

st.sidebar.title("🔍 Search")
city = st.sidebar.text_input("Enter a city", "Lagos")
st.sidebar.markdown("Created by **Olubisi Ajetunmobi**")
st.sidebar.markdown("[GitHub](https://github.com/oajetunm)")
#city = st.text_input("Enter a city:", "Lagos")
api_key = st.secrets["weather_api"]  
#st.secrets["weather_api"]  # or hardcode it for now


def get_weather_data(city, api_key):
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    res = requests.get(weather_url).json()
    return res

def get_air_quality(lat, lon, api_key):
    aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
    res = requests.get(aqi_url).json()
    return res

if city:
    weather = get_weather_data(city, api_key)
    if weather.get("cod") == 200:
        lat = weather["coord"]["lat"]
        lon = weather["coord"]["lon"]
        import pydeck as pdk
    
        
        air_quality = get_air_quality(lat, lon, api_key)

        st.subheader(f"Weather in {city.title()}")
        col1, col2, col3,col4 = st.columns(4)
        col1.metric("🌡️ Temp (°C)", weather["main"]["temp"])
        col2.metric("💧 Humidity (%)", weather["main"]["humidity"])
        col3.metric("🌬️ Wind Speed (m/s)", weather["wind"]["speed"])
        aqi = air_quality["list"][0]
        col4.metric("🌫️ AQI (1–5)", aqi["main"]["aqi"])
        aqi = air_quality["list"][0]
        
        aqi_val = aqi["main"]["aqi"]
        aqi_labels = {
            1: ("Good", "🟢"),
            2: ("Fair", "🟡"),
            3: ("Moderate", "🟠"),
            4: ("Poor", "🔴"),
            5: ("Very Poor", "🟣")
        }

        label, emoji = aqi_labels.get(aqi_val, ("Unknown", "❓"))
        st.success(f"{emoji} Air Quality: {label}")
        
        #col4, col5 = st.columns(2)
        
        import plotly.express as px

        pollutants = aqi["components"]

# Create and sort the dataframe
        pollutant_df = pd.DataFrame(pollutants.items(), columns=["Pollutant", "Value"])
        pollutant_df = pollutant_df.sort_values(by="Value", ascending=False)  # 👈 SORT!
        
        # Plot
        fig = px.bar(
        pollutant_df,
        x="Pollutant",
        y="Value",
        title="Pollutant Levels (μg/m³)",
        text="Value"
        )
    
        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        
        # ✅ Add this line to prevent cutoff
        fig.update_layout(
            yaxis_title="μg/m³",
            xaxis_title="Pollutant",
            uniformtext_minsize=8,
            margin=dict(t=80)  # Top margin (t=80 px)
        )
        
        st.plotly_chart(fig)
            
        
        
        
        #fig = px.bar(
       #     pollutant_df,
        #    x="Pollutant",
         #   y="Value",
          #  title="Pollutant Levels (μg/m³)",
           # text="Value"  # Optional: show values on bars
       # )
        
        #fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')  # cleaner bar labels
        #fig.update_layout(yaxis_title="μg/m³", xaxis_title="Pollutant", uniformtext_minsize=8)
        
       # st.plotly_chart(fig)
                #col5.write("Pollutants (μg/m³):")   
        #col5.json(aqi["components"])
       
        # Show city on a map
        st.subheader("🗺️ Location Map")
        
        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/dark-v9",
            initial_view_state=pdk.ViewState(
                latitude=lat,
                longitude=lon,
                zoom=10,
                pitch=0,
            ),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=[{"position": [lon, lat], "color": [255, 0, 0], "radius": 1000}],
                    get_position="position",
                    get_color="color",
                    get_radius="radius",
                ),
            ],
        ))
        #st.metric("🌡️ Temperature (°C)", weather["main"]["temp"])
        #st.metric("💧 Humidity (%)", weather["main"]["humidity"])
        #st.metric("🌬️ Wind Speed (m/s)", weather["wind"]["speed"])

        #st.metric("AQI (1–5)", aqi["main"]["aqi"])
        #st.write("Pollutants (μg/m³):")
        #st.json(aqi["components"])
    else:
        st.error("City not found.")
        
import streamlit as st


