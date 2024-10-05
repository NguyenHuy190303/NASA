# gpt_utils.py

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client
client = OpenAI(api_key=api_key)

def generate_gpt_analysis(country_name, experiment, country_data, user_question, lang_name, text):
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
        model="gpt-4",  # Thay thế bằng mô hình phù hợp nếu cần
        messages=[
            {"role": "system", "content": "You are a climate data expert."},
            {"role": "user", "content": prompt}
        ]
    )
    # Extract the answer and follow-up questions
    answer = response.choices[0].message.content

    # Split the answer and suggested questions
    if text['suggested_questions'] in answer:
        answer_text, questions_text = answer.split(text['suggested_questions'], 1)
        follow_up_questions = questions_text.strip().split('\n')
        follow_up_questions = [q.strip('- ').strip() for q in follow_up_questions if q.strip()]
    else:
        answer_text = answer
        follow_up_questions = []
    return answer_text, follow_up_questions
