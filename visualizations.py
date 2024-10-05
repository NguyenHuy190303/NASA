import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def plot_dC_loss(country_data, experiment, country_name, text, lang_code):
    # Enhanced ΔC_loss visualization
    plt.figure(figsize=(10, 6))
    sns.regplot(data=country_data, x='Year', y=experiment+' dC_loss (TgCO2)', marker='o',
                scatter_kws={"s": 50}, line_kws={"color": "red"})
    plt.axhline(0, color='black', linestyle='--')
    plt.title(f"{text[lang_code]['enhanced_dC_loss']} {country_name}", fontsize=16)
    plt.xlabel(text[lang_code]['year'], fontsize=12)
    plt.ylabel(text[lang_code]['dC_loss_label'], fontsize=12)
    plt.grid(True)
    return plt

def plot_carbon_budget_all_years(country_data, experiment, country_name, text, lang_code):
    # Prepare data for carbon budget visualization over all years
    components = ['FF (TgCO2)', 'Rivers (TgCO2)', 'Wood+Crop (TgCO2)',
                  experiment+' dC_loss (TgCO2)', experiment+' NCE (TgCO2)']
    labels = ['Fossil Fuels', 'Rivers', 'Wood + Crops', 'ΔC_loss', 'NCE']
    
    # Filter available components
    available_components = [comp for comp in components if comp in country_data.columns]
    
    # Plot all components over the years
    plt.figure(figsize=(10, 6))
    
    for comp, label in zip(available_components, labels):
        plt.plot(country_data['Year'], country_data[comp], marker='o', label=label)
    
    plt.title(f"{text[lang_code]['carbon_budget']} {country_name}", fontsize=16)
    plt.xlabel(text[lang_code]['year'], fontsize=12)
    plt.ylabel(text[lang_code]['co2_emissions'], fontsize=12)
    plt.legend(title=text[lang_code]['component'], loc='upper right')
    plt.grid(True)
    return plt
