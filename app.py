import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Load and cache the data for faster access
@st.cache_data
def load_data():
    url ='https://ceos.org/gst/files/pilot_topdown_CO2_Budget_countries_v1.csv'
    df_all = pd.read_csv(url, skiprows=52)
    return df_all

df_all = load_data()

# Experiment list
experiments = ['IS', 'LNLG', 'LNLGIS', 'LNLGOGIS']

# Allow user to select an experiment
experiment = st.sidebar.selectbox('Select Experiment', experiments)

# Function to process the data based on selected experiment
def select_experiment(df_all, experiment):
    if experiment == 'IS':
        df = df_all.drop(df_all.columns[[4,5,6,7,8,9,12,13,14,15,16,17,20,21,22,23,24,25,34,35,36]], axis=1)
    elif experiment == 'LNLG':
        df = df_all.drop(df_all.columns[[2,3,6,7,8,9,10,11,14,15,16,17,18,19,22,23,24,25,33,35,36]], axis=1)
    elif experiment == 'LNLGIS':
        df = df_all.drop(df_all.columns[[2,3,4,5,8,9,10,11,12,13,16,17,18,19,20,21,24,25,33,34,36]], axis=1)
    elif experiment == 'LNLGOGIS':
        df = df_all.drop(df_all.columns[[2,3,4,5,6,7,10,11,12,13,14,15,18,19,20,21,22,23,33,34,35]], axis=1)
    return df

df = select_experiment(df_all, experiment)

# Country list
countries = df['Alpha 3 Code'].unique()
countries.sort()

# Allow user to select a country
country_name = st.sidebar.selectbox('Select Country', countries)

# Filter data by selected country
country_data = df[df['Alpha 3 Code'] == country_name]

# Ensure the 'Year' column is numeric
country_data['Year'] = pd.to_numeric(country_data['Year'], errors='coerce')

# Drop rows with missing or non-numeric years
country_data = country_data.dropna(subset=['Year'])

# Enhanced ΔC_loss chart using Seaborn
st.header(f'Enhanced $\Delta C_{{loss}}$ Visualization for {country_name}')

if country_data.empty:
    st.error('No data available for the selected country and experiment.')
else:
    # Enhanced ΔC_loss visualization
    plt.figure(figsize=(10, 6))
    sns.regplot(data=country_data, x='Year', y=experiment+' dC_loss (TgCO2)', marker='o', scatter_kws={"s": 50}, line_kws={"color": "red"})
    plt.axhline(0, color='black', linestyle='--')
    plt.title(f'$\Delta C_{{loss}}$ over the years for {country_name}', fontsize=16)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel(f'$\Delta C_{{loss}}$ (TgCO₂)', fontsize=12)
    plt.grid(True)
    st.pyplot(plt)

# Enhanced Carbon Budget visualization using Seaborn
st.header(f'Enhanced Carbon Budget for {country_name}')

# Select year
years = country_data['Year'].unique().astype(int)  # Convert years to integers
year_options = np.append('mean', years.astype(str))  # Fix mixed type error
year = st.selectbox('Select Year', year_options)

if year == 'mean':
    country_data_mean = country_data.mean(numeric_only=True)
else:
    country_data_mean = country_data[country_data['Year'] == int(year)].iloc[0]

# Prepare data for carbon budget visualization
components = ['FF (TgCO2)', 'Rivers (TgCO2)', 'Wood+Crop (TgCO2)', experiment+' dC_loss (TgCO2)', experiment+' NCE (TgCO2)']
labels = ['Fossil Fuels', 'Rivers', 'Wood + Crops', 'ΔC_loss', 'NCE']
values = [country_data_mean[comp] for comp in components]

# Create a DataFrame for visualization
budget_df = pd.DataFrame({'Component': labels, 'Value': values})

# Enhanced Carbon Budget visualization with different color palette
plt.figure(figsize=(8, 6))
sns.barplot(x='Component', y='Value', data=budget_df, palette='coolwarm')
plt.title(f'Carbon Budget for {country_name} in {year}', fontsize=16)
plt.ylabel('CO₂ Emissions (TgCO₂)', fontsize=12)
plt.grid(True)
st.pyplot(plt)

# GPT Analysis Section
st.header(f'GPT Analysis for {country_name}')

# User inputs a question for GPT analysis
user_question = st.text_input('Ask a question about the data or chart:')

import os
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_gpt_analysis(country_name, experiment, country_data, user_question):
    # Prepare the data context
    data_context = country_data.head(10).to_string(index=False)
    
    # Create the prompt
    prompt = f"""
    You are a data scientist and climate change expert. The data below shows CO₂ emissions for {country_name}, 
    especially focusing on the following components: Fossil Fuels, Rivers, Wood+Crops, ΔC_loss, and NCE.

    {data_context}

    Based on this data, please answer the following question in detail:
    {user_question}
    """

    # Make the API request using the latest OpenAI API client
    response = client.chat.completions.create(
        model="gpt-4o",  # You can replace this with "gpt-3.5-turbo" if needed
        messages=[
            {"role": "system", "content": "You are a climate data expert."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content



if user_question:
    with st.spinner('Processing your question...'):
        analysis = generate_gpt_analysis(country_name, experiment, country_data, user_question)
        st.subheader('Analysis Result')
        st.write(analysis)
