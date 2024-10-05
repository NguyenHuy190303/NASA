import os
import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import sys
from openai import OpenAI
from dotenv import load_dotenv

# Thêm thư viện cho hỗ trợ đa ngôn ngữ
# Bạn cần cài đặt gói googletrans: pip install googletrans==4.0.0-rc1
# Tuy nhiên, để đơn giản và tránh phụ thuộc vào API bên ngoài, chúng ta sẽ sử dụng từ điển cho các chuỗi văn bản

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client
client = OpenAI(api_key=api_key)

# Set the default encoding to utf-8 for printing (for systems supporting it)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

# Thêm tùy chọn cho người dùng chọn loại tệp dữ liệu
data_file_type = st.sidebar.selectbox('Chọn loại tệp dữ liệu / Select Data File Type', ['CSV', 'JSON'])

# Load and cache the data for faster access
@st.cache_data
def load_data(file_type):
    if file_type == 'CSV':
        url = 'https://ceos.org/gst/files/pilot_topdown_CO2_Budget_countries_v1.csv'
        df_all = pd.read_csv(url, skiprows=52)
    elif file_type == 'JSON':
        # Giả sử bạn có một tệp JSON tương đương với dữ liệu CSV
        # Vì không có URL thực tế cho tệp JSON, bạn cần thay thế bằng đường dẫn hoặc URL của bạn
        url = 'https://example.com/data.json'  # Thay thế bằng URL hoặc đường dẫn tệp JSON của bạn
        df_all = pd.read_json(url)
    return df_all

df_all = load_data(data_file_type)

# Experiment list
experiments = ['IS', 'LNLG', 'LNLGIS', 'LNLGOGIS']

# Thêm hỗ trợ đa ngôn ngữ
languages = {'English': 'en', 'Tiếng Việt': 'vi'}
language = st.sidebar.selectbox('Chọn Ngôn ngữ / Select Language', list(languages.keys()))
lang_code = languages[language]

# Từ điển chứa các chuỗi giao diện cho mỗi ngôn ngữ
text = {
    'en': {
        'select_experiment': 'Select Experiment',
        'select_country': 'Select Country',
        'enhanced_dC_loss': 'Enhanced ΔC_loss Visualization for',
        'no_data': 'No data available for the selected country and experiment.',
        'carbon_budget': 'Enhanced Carbon Budget for',
        'select_year': 'Select Year',
        'gpt_analysis': 'GPT Analysis for',
        'ask_question': 'Ask a question about the data or chart:',
        'processing': 'Processing your question...',
        'analysis_result': 'Analysis Result',
        'error': 'An error occurred:',
        'suggested_questions': 'Suggested Follow-up Questions',
        'year': 'Year',
        'dC_loss_label': 'ΔC_loss (TgCO₂)',
        'co2_emissions': 'CO₂ Emissions (TgCO₂)',
        'component': 'Component',
        'value': 'Value',
        'carbon_budget_title': 'Carbon Budget for {country_name} in {year}',
        'select_language': 'Select Language',
        'select_data_file_type': 'Select Data File Type',
    },
    'vi': {
        'select_experiment': 'Chọn Thí nghiệm',
        'select_country': 'Chọn Quốc gia',
        'enhanced_dC_loss': 'Hình ảnh hóa ΔC_loss nâng cao cho',
        'no_data': 'Không có dữ liệu cho quốc gia và thí nghiệm đã chọn.',
        'carbon_budget': 'Ngân sách Carbon nâng cao cho',
        'select_year': 'Chọn Năm',
        'gpt_analysis': 'Phân tích GPT cho',
        'ask_question': 'Đặt câu hỏi về dữ liệu hoặc biểu đồ:',
        'processing': 'Đang xử lý câu hỏi của bạn...',
        'analysis_result': 'Kết quả Phân tích',
        'error': 'Đã xảy ra lỗi:',
        'suggested_questions': 'Câu hỏi tiếp theo gợi ý',
        'year': 'Năm',
        'dC_loss_label': 'ΔC_loss (TgCO₂)',
        'co2_emissions': 'Lượng phát thải CO₂ (TgCO₂)',
        'component': 'Thành phần',
        'value': 'Giá trị',
        'carbon_budget_title': 'Ngân sách Carbon cho {country_name} năm {year}',
        'select_language': 'Chọn Ngôn ngữ',
        'select_data_file_type': 'Chọn loại tệp dữ liệu',
    }
}

# Sử dụng chuỗi văn bản theo ngôn ngữ đã chọn
experiment = st.sidebar.selectbox(text[lang_code]['select_experiment'], experiments)

# Function to process the data based on selected experiment
def select_experiment(df_all, experiment):
    # Kiểm tra xem các cột cần thiết có trong DataFrame hay không
    required_columns = {
        'IS': [4,5,6,7,8,9,12,13,14,15,16,17,20,21,22,23,24,25,34,35,36],
        'LNLG': [2,3,6,7,8,9,10,11,14,15,16,17,18,19,22,23,24,25,33,35,36],
        'LNLGIS': [2,3,4,5,8,9,10,11,12,13,16,17,18,19,20,21,24,25,33,34,36],
        'LNLGOGIS': [2,3,4,5,6,7,10,11,12,13,14,15,18,19,20,21,22,23,33,34,35]
    }
    # Kiểm tra xem số cột có đủ để loại bỏ không
    max_col_index = df_all.shape[1] - 1
    columns_to_drop = [col for col in required_columns[experiment] if col <= max_col_index]
    df = df_all.drop(df_all.columns[columns_to_drop], axis=1)
    return df

df = select_experiment(df_all, experiment)

# Country list
countries = df['Alpha 3 Code'].unique()
countries.sort()

# Allow user to select a country
country_name = st.sidebar.selectbox(text[lang_code]['select_country'], countries)

# Filter data by selected country
country_data = df[df['Alpha 3 Code'] == country_name]

# Ensure the 'Year' column is numeric
country_data['Year'] = pd.to_numeric(country_data['Year'], errors='coerce')

# Drop rows with missing or non-numeric years
country_data = country_data.dropna(subset=['Year'])

# Enhanced ΔC_loss chart using Seaborn
st.header(f"{text[lang_code]['enhanced_dC_loss']} {country_name}")

if country_data.empty:
    st.error(text[lang_code]['no_data'])
else:
    # Enhanced ΔC_loss visualization
    plt.figure(figsize=(10, 6))
    sns.regplot(data=country_data, x='Year', y=experiment+' dC_loss (TgCO2)', marker='o',
                scatter_kws={"s": 50}, line_kws={"color": "red"})
    plt.axhline(0, color='black', linestyle='--')
    plt.title(f"{text[lang_code]['enhanced_dC_loss']} {country_name}", fontsize=16)
    plt.xlabel(text[lang_code]['year'], fontsize=12)
    plt.ylabel(text[lang_code]['dC_loss_label'], fontsize=12)
    plt.grid(True)
    st.pyplot(plt)

# Enhanced Carbon Budget visualization using Seaborn
st.header(f"{text[lang_code]['carbon_budget']} {country_name}")

# Select year
years = country_data['Year'].unique().astype(int)
year_options = np.append('mean', years.astype(str))
year = st.selectbox(text[lang_code]['select_year'], year_options)

if year == 'mean':
    country_data_mean = country_data.mean(numeric_only=True)
else:
    country_data_mean = country_data[country_data['Year'] == int(year)].iloc[0]

# Prepare data for carbon budget visualization
components = ['FF (TgCO2)', 'Rivers (TgCO2)', 'Wood+Crop (TgCO2)',
              experiment+' dC_loss (TgCO2)', experiment+' NCE (TgCO2)']
labels = ['Fossil Fuels', 'Rivers', 'Wood + Crops', 'ΔC_loss', 'NCE']

# Kiểm tra xem các cột có tồn tại không
available_components = [comp for comp in components if comp in country_data_mean.index]
values = [country_data_mean[comp] for comp in available_components]
labels = [labels[components.index(comp)] for comp in available_components]

# Create a DataFrame for visualization
budget_df = pd.DataFrame({text[lang_code]['component']: labels, text[lang_code]['value']: values})

# Enhanced Carbon Budget visualization with different color palette
plt.figure(figsize=(8, 6))
sns.barplot(x=text[lang_code]['component'], y=text[lang_code]['value'], data=budget_df, palette='coolwarm')
plt.title(text[lang_code]['carbon_budget_title'].format(country_name=country_name, year=year), fontsize=16)
plt.ylabel(text[lang_code]['co2_emissions'], fontsize=12)
plt.grid(True)
st.pyplot(plt)

# GPT Analysis Section
st.header(f"{text[lang_code]['gpt_analysis']} {country_name}")

# User inputs a question for GPT analysis
user_question = st.text_input(text[lang_code]['ask_question'])

# Thêm mapping cho tên ngôn ngữ để sử dụng trong prompt
language_names = {'en': 'English', 'vi': 'Vietnamese'}
lang_name = language_names[lang_code]

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

    After answering, please suggest three follow-up questions that the user might be interested in, based on the data.

    Please provide the answer and questions in {lang_name}.
    """
    # Make the API request
    response = client.chat.completions.create(
        model="gpt-4",  # Thay thế bằng "gpt-4o-mini" nếu cần
        messages=[
            {"role": "system", "content": "You are a climate data expert."},
            {"role": "user", "content": prompt}
        ]
    )
    # Extract the answer and follow-up questions
    answer = response.choices[0].message.content

    # Tách phần trả lời và câu hỏi gợi ý
    if text[lang_code]['suggested_questions'] in answer:
        answer_text, questions_text = answer.split(text[lang_code]['suggested_questions'], 1)
        follow_up_questions = questions_text.strip().split('\n')
        follow_up_questions = [q.strip('- ').strip() for q in follow_up_questions if q.strip()]
    else:
        answer_text = answer
        follow_up_questions = []
    return answer_text, follow_up_questions

# Process GPT response if user asks a question
if user_question:
    with st.spinner(text[lang_code]['processing']):
        try:
            analysis, follow_up_questions = generate_gpt_analysis(country_name, experiment, country_data, user_question)
            st.subheader(text[lang_code]['analysis_result'])
            st.write(analysis)
            if follow_up_questions:
                st.subheader(text[lang_code]['suggested_questions'])
                for q in follow_up_questions:
                    st.write(f"- {q}")
        except Exception as e:
            st.error(f"{text[lang_code]['error']} {e}")
