import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Import custom modules
import language
from gpt_utils import generate_gpt_analysis
from visualizations import plot_dC_loss, plot_carbon_budget_all_years

# Load environment variables from .env file
load_dotenv()

# Set the default encoding to utf-8 for printing (for systems supporting it)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

# Language selection
lang_code = st.sidebar.selectbox(
    language.text['en']['select_language'],
    list(language.languages.keys()),
    format_func=lambda x: language.get_language_display_name(x, x)
)
text = language.text
language_names = language.language_names

# Dataset selection
datasets = ['CO2_Budget_countries', 'Dataset 2', 'Dataset 3']
dataset_display_names = [text[lang_code].get(ds, ds) for ds in datasets]
selected_dataset = st.sidebar.selectbox(text[lang_code]['select_dataset'], datasets, format_func=lambda x: text[lang_code].get(x, x))

# For now, since we only have CO2_Budget_countries dataset, we will load that
if selected_dataset == 'CO2_Budget_countries':
    @st.cache_data
    def load_data():
        url = 'https://ceos.org/gst/files/pilot_topdown_CO2_Budget_countries_v1.csv'
        df_all = pd.read_csv(url, skiprows=52)
        return df_all

    df_all = load_data()
else:
    st.error(text[lang_code]['dataset_not_available'])
    st.stop()

# Experiment selection
experiment = st.sidebar.selectbox(text[lang_code]['select_experiment'], ['IS', 'LNLG', 'LNLGIS', 'LNLGOGIS'])

# Function to process the data based on selected experiment
def select_experiment(df_all, experiment):
    required_columns = {
        'IS': [4,5,6,7,8,9,12,13,14,15,16,17,20,21,22,23,24,25,34,35,36],
        'LNLG': [2,3,6,7,8,9,10,11,14,15,16,17,18,19,22,23,24,25,33,35,36],
        'LNLGIS': [2,3,4,5,8,9,10,11,12,13,16,17,18,19,20,21,24,25,33,34,36],
        'LNLGOGIS': [2,3,4,5,6,7,10,11,12,13,14,15,18,19,20,21,22,23,33,34,35]
    }
    max_col_index = df_all.shape[1] - 1
    columns_to_drop = [col for col in required_columns[experiment] if col <= max_col_index]
    df = df_all.drop(df_all.columns[columns_to_drop], axis=1)
    return df

df = select_experiment(df_all, experiment)

# Country selection
countries = df['Alpha 3 Code'].unique()
countries.sort()
country_name = st.sidebar.selectbox(text[lang_code]['select_country'], countries)

# Filter data by selected country
country_data = df[df['Alpha 3 Code'] == country_name]
country_data['Year'] = pd.to_numeric(country_data['Year'], errors='coerce')
country_data = country_data.dropna(subset=['Year'])

# Plot ΔC_loss visualization
st.header(f"{text[lang_code]['enhanced_dC_loss']} {country_name}")
if country_data.empty:
    st.error(text[lang_code]['no_data'])
else:
    plt = plot_dC_loss(country_data, experiment, country_name, text, lang_code)
    st.pyplot(plt)

# Plot Carbon Budget visualization for all years
st.header(f"{text[lang_code]['carbon_budget']} {country_name}")
if country_data.empty:
    st.error(text[lang_code]['no_data'])
else:
    plt = plot_carbon_budget_all_years(country_data, experiment, country_name, text, lang_code)
    st.pyplot(plt)

# GPT Analysis Section
st.header(f"{text[lang_code]['gpt_analysis']} {country_name}")
user_question = st.text_input(text[lang_code]['ask_question'])

lang_name = language_names[lang_code]

if user_question:
    with st.spinner(text[lang_code]['processing']):
        try:
            analysis, follow_up_questions = generate_gpt_analysis(
                country_name, experiment, country_data, user_question, lang_name, text[lang_code]
            )
            st.subheader(text[lang_code]['analysis_result'])
            st.write(analysis)
            if follow_up_questions:
                st.subheader(text[lang_code]['suggested_questions'])
                for q in follow_up_questions:
                    st.write(f"- {q}")
        except Exception as e:
            st.error(f"{text[lang_code]['error']} {e}")
import streamlit as st
import streamlit.components.v1 as components

# JavaScript for fetching and displaying dynamic weather information
js_code = """
<script>
async function fetchClimateData() {
    try {
        const response = await fetch('https://api.example.com/climate');
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        const data = await response.json();
        document.getElementById('weather').innerText = `${data.temperature}°C, ${data.weather_description}`;
    } catch (error) {
        document.getElementById('weather').innerText = 'Unable to load weather data';
    }
}

window.addEventListener('DOMContentLoaded', fetchClimateData);
</script>
"""

# Inject JavaScript into the Streamlit app
components.html(f"{html_content}{js_code}", height=800)
