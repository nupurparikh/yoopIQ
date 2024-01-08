import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
from flask import Flask, render_template

app = Flask(__name__)

# Load CSV data
df = pd.read_csv('archive/sales_data_sample.csv', encoding='Latin-1')

# Function to generate total sales by year and return the image as Base64
def total_sales_by_year():
    sales_by_year = df.groupby('YEAR_ID')['SALES'].sum()
    sales_by_year = sales_by_year.reset_index()

    plt.figure(figsize=(10, 6))
    plt.bar(sales_by_year['YEAR_ID'], sales_by_year['SALES'], color='skyblue')
    plt.xlabel('Year')
    plt.ylabel('Total Sales')
    plt.title('Total Sales by Year')
    plt.xticks(sales_by_year['YEAR_ID'])
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.read()).decode('utf-8')

    return img_str

@app.route('/generate_year_graph', methods=['GET'])
def generate_and_show_year_graph():
    img_data = total_sales_by_year()  
    return img_data  

@app.route('/generate_country_graph', methods=['GET'])
def generate_country_graph():
    img_data = analysis__target_column_to_sales(df, 'COUNTRY', top_n=20)
    return img_data 


def analysis__target_column_to_sales(df, target_col, top_n=None):
    result = df.groupby(target_col)['SALES'].sum()
    result_df = result.reset_index()
    if top_n:
        df_sorted = result_df.sort_values(by='SALES', ascending=False)
        result_df = df_sorted.head(top_n)

    plt.figure(figsize=(10, 6))
    plt.bar(result_df[target_col], result_df['SALES'], color='skyblue')
    plt.xlabel(target_col)
    plt.ylabel('Total Sales')
    plt.title(f'Total Sales by {target_col}')
    plt.xticks(rotation=45)
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.read()).decode('utf-8')

    return img_str


def generate_pie_chart():
    unique_years = df['YEAR_ID'].unique()
    ratio = 0.20
    fig, axes = plt.subplots(1, len(unique_years), figsize=(20, 8))
    all_sum = 0
    top_sum = 0
    for i, year in enumerate(unique_years):
        year_data = df[df['YEAR_ID'] == year]
        year_data = year_data.groupby(['MONTH_ID', 'CUSTOMERNAME'])['SALES'].sum()

        n = int(ratio * len(year_data.index))

        new_data = year_data
        new_data = pd.DataFrame(new_data.reset_index())
        new_data = new_data[new_data['MONTH_ID'] == 11]
        new_data['YEAR_ID'] = year
        revenue = new_data['SALES'].sum()
        new_data = new_data.sort_values(by='SALES', ascending=False)

        new_data = new_data.head(n)
        top_n = new_data['SALES'].sum()
        all_sum += revenue
        top_sum += top_n

        # Use predefined colors from Matplotlib's 'tab10' colormap
        colors = plt.cm.tab10(np.arange(len(new_data)))

        explode = (0, 0.2)  # only "explode" the 2nd slice (i.e. 'Hogs')
        if revenue != 0:
            sizes = [revenue - top_n, top_n]
            labels = ['others', 'top\n' + str(int(ratio * 100)) + '%']
            axes[i].pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                        startangle=90, colors=colors)
            axes[i].set_title(str(year) + '\n November', fontsize=16)

    explode = (0, 0.2)
    sizes = [all_sum - top_sum, top_sum]
    labels = ['others', 'top\n' + str(int(ratio * 100)) + '%']

    axes[2].pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                startangle=90, colors=plt.cm.tab10(np.arange(2)))
    axes[2].set_title('2003, 2004 \n November', fontsize=16)

    # Save the plot as an image in memory
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.read()).decode('utf-8')

    plt.close()  # Close the plot to release memory

    return img_str

@app.route('/generate_pie_chart', methods=['GET'])
def generate_and_show_pie_chart():
    img_data = generate_pie_chart()
    return img_data


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
