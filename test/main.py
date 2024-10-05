from flask import Flask, request, jsonify, send_from_directory
import os
import pandas as pd
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client
client = OpenAI(api_key=api_key)

# Initialize Flask app
app = Flask(__name__, static_folder='climategpt', static_url_path='')

# Load and cache the data for faster access
url = 'https://ceos.org/gst/files/pilot_topdown_CO2_Budget_countries_v1.csv'
df_all = pd.read_csv(url, skiprows=52)

# Endpoint to get available experiments
@app.route("/experiments", methods=["GET"])
def get_experiments():
    experiments = ['IS', 'LNLG', 'LNLGIS', 'LNLGOGIS']
    return jsonify({"experiments": experiments})

# Endpoint to get filtered data for a specific country and experiment
@app.route("/country_data", methods=["GET"])
def get_country_data():
    experiment = request.args.get('experiment')
    country_code = request.args.get('country_code')

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
    country_data = df[df['Alpha 3 Code'] == country_code]

    if country_data.empty:
        return jsonify({"error": "No data available for the selected country and experiment"}), 404

    country_data_dict = country_data.to_dict(orient='records')
    return jsonify({"country_data": country_data_dict})

# Endpoint for GPT analysis
@app.route("/gpt_analysis", methods=["POST"])
def gpt_analysis():
    data = request.get_json()
    country_name = data.get('country_name')
    experiment = data.get('experiment')
    country_data = pd.DataFrame(data.get('country_data'))
    user_question = data.get('user_question')

    data_context = country_data.head(10).to_string(index=False)
    prompt = f"""
    You are a data scientist and climate change expert. The data below shows CO₂ emissions for {country_name}, 
    especially focusing on the following components: Fossil Fuels, Rivers, Wood+Crops, ΔC_loss, and NCE.

    {data_context}

    Based on this data, please answer the following question in detail:
    {user_question}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a climate data expert."},
                {"role": "user", "content": prompt}
            ]
        )
        answer = response.choices[0].message.content
        return jsonify({"analysis": answer})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Serve the frontend files
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)