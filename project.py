# -*- coding: utf-8 -*-
"""project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/15--jWIw_-uGQaC9Tz_B4m7b_U7uV7CA7
"""

!pip install requests pandas

import requests
import pandas as pd
from google.colab import files

api_key = "AIzaSyCZfDjVuOwsi7cM3rB1TVmFBqsasXCEW88"   # API key

def get_book_data(search_query, max_results=5000):
    """
    Fetches book data from the Google Books API.

    Args:
        search_query: The search term for books.
        max_results: The maximum number of results to retrieve (default is 5000).

    Returns:
        A pandas DataFrame containing book information, or None if an error occurs.
    """

    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": search_query,
        "key": api_key,
        "maxResults": 40
    }

    all_book_data = []
    startIndex = 0
    total_items = 0

    try:
        while startIndex < min(max_results, 5000) and (startIndex < total_items or total_items == 0):
            params["startIndex"] = startIndex
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()

            if 'items' not in data:
                print("No items found in API response.")
                break

            items = data['items']
            total_items = data.get("totalItems", 0)

            for item in items:
                volume_info = item.get('volumeInfo', {})
                sale_info = item.get('saleInfo', {})

                book_info = {
                    'bookid': item.get('id', ''),
                    'searchkey': search_query,
                    'booktitle': volume_info.get('title', ''),
                    'booksubtitle': volume_info.get('subtitle', ''),
                    'bookauthors': ", ".join(volume_info.get('authors', [])),
                    'bookdescription': volume_info.get('description', ''),
                    'publisher': volume_info.get('publisher', ''),
                    'industryIdentifiers': ", ".join([identifier.get('identifier', '') for identifier in volume_info.get('industryIdentifiers', [])]),
                    'textreadingModes': volume_info.get('readingModes', {}).get('text', False),
                    'imagereadingModes': volume_info.get('readingModes', {}).get('image', False),
                    'pageCount': volume_info.get('pageCount', ''),
                    'categories': ", ".join(volume_info.get('categories', [])),
                    'language': volume_info.get('language', ''),
                    'imageLinks': str(volume_info.get('imageLinks', {})),
                    'ratingsCount': volume_info.get('ratingsCount', ''),
                    'averageRating': volume_info.get('averageRating', ''),
                    'country': sale_info.get('country', ''),
                    'saleability': sale_info.get('saleability', ''),
                    'isEbook': sale_info.get('isEbook', False),
                    'amountlistPrice': sale_info.get('listPrice', {}).get('amount', ''),
                    'currencyCode_listPrice': sale_info.get('listPrice', {}).get('currencyCode', ''),
                    'amountretailPrice': sale_info.get('retailPrice', {}).get('amount', ''),
                    'currencyCoderetailPrice': sale_info.get('retailPrice', {}).get('currencyCode', ''),
                    'buyLink': sale_info.get('buyLink', ''),
                    'year': volume_info.get('publishedDate', '').split('-')[0] if volume_info.get('publishedDate', '') else ''

                }
                all_book_data.append(book_info)


            startIndex += 40

        if not all_book_data:
            print("No book data found for the search query.")
            return None
        return pd.DataFrame(all_book_data)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None



search_term = "novel, History" #@param {type:"string"}
df = get_book_data(search_term, max_results=5000)

if df is not None:
    print(df.head())
    print(f"Total books found: {len(df)}")

    file_name = f"books_{search_term.replace(' ', '_')}.csv"
    df.to_csv(file_name, index=False)
    files.download(file_name)

!pip install mysql-connector-python

import mysql.connector

mydb = mysql.connector.connect(
  host = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
  port = 4000,
  user = "3QChstWNTCtATP1.root",
  password = "4otgQ1SBiYWNdkuD",
  )
print(mydb)
mycursor = mydb.cursor(buffered=True)

!pip install streamlit

!pip install pyngrok

!npm install localtunnel

!pip install ngrok

# Install necessary libraries


# Set your ngrok auth token
from pyngrok import ngrok
ngrok.set_auth_token("2qZXTI70wbnYK9o4Ldi7bDiVMwX_6N2MUv8REzFnRsePg6zhh")


# Start ngrok tunnel
public_url = ngrok.connect(8501)
print(f"Streamlit app is live at: {public_url}")

# Run the Streamlit app
!streamlit run book.py &>/dev/null&

import requests
import mysql.connector
import pandas as pd
from google.colab import files
from requests.api import head
from mysql.connector import Error
from tabulate import tabulate
import streamlit as st
from PIL import Image
from pyngrok import ngrok


# Establish database connection (replace with your credentials)
mydb = mysql.connector.connect(
    host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
    port=4000,
    user="3nitUUKsZ9vMwCU.root",
    password="O7Y8CYQA1W7AZBtF",
    database="project",
    autocommit=True
)

# Function to execute queries and display results
def run_query(query):
    try:
        cursor = mydb.cursor(buffered=True)
        cursor.execute(query)
        results = cursor.fetchall()
        if results:
            df = pd.DataFrame(results)
            return df
        else:
            st.write("No results found.")
            return None
    except mysql.connector.Error as err:
        st.error(f"Error executing query: {err}")
        return None

st.title('BookScape Explorer :book:')

# Search box for keyword search
keyword = st.text_input("Search for books by keyword (in title):")

# Options for queries
options = {
    "Check Availability of eBooks vs Physical Books": """SELECT COUNT(*) FROM book WHERE isEbook = 'TRUE'; SELECT COUNT(*) FROM book WHERE isEbook = 'FALSE';""",
    "Find the Publisher with the Most Books Published": """SELECT publisher, COUNT(*) AS book_count FROM book GROUP BY publisher ORDER BY book_count DESC LIMIT 1;""",
    "Identify the Publisher with the Highest Average Rating": """SELECT publisher, AVG(averageRating) AS average_rating FROM book GROUP BY publisher ORDER BY average_rating DESC LIMIT 1;""",
    "Get the Top 5 Most Expensive Books by Retail Price": """SELECT booktitle, amountretailPrice FROM book ORDER BY amountretailPrice DESC LIMIT 5;""",
    "Find Books Published After 2010 with at Least 500 Pages": """SELECT booktitle FROM book WHERE CAST(year AS UNSIGNED) > 2010 AND pageCount >= 500;""",
    "List Books with Discounts Greater than 20%": """SELECT booktitle, (amountretailPrice - amountlistPrice) / amountretailPrice AS discount_percentage FROM book WHERE (amountretailPrice - amountlistPrice) / amountretailPrice > 0.2;""",
    "Find the Average Page Count for eBooks vs Physical Books": """SELECT AVG(pageCount) FROM book WHERE isEbook = 'TRUE'; SELECT AVG(pageCount) FROM book WHERE isEbook = 'FALSE';""",
    "Find the Top 3 Authors with the Most Books": """SELECT bookauthors, COUNT(*) AS book_count FROM book GROUP BY bookauthors ORDER BY book_count DESC LIMIT 3;""",
    "List Publishers with More than 10 Books": """SELECT publisher FROM book GROUP BY publisher HAVING COUNT(*) > 10;""",
    "Find the Average Page Count for Each Category": """SELECT categories, AVG(pageCount) FROM book GROUP BY categories;""",
    "Retrieve Books with More than 3 Authors": """SELECT booktitle FROM book WHERE LENGTH(bookauthors) - LENGTH(REPLACE(bookauthors, ',', '')) + 1 > 3;""",
    "Books with Ratings Count Greater Than the Average": """SELECT booktitle FROM book WHERE ratingsCount > (SELECT AVG(ratingsCount) FROM book);""",
    "Books with the Same Author Published in the Same Year": """SELECT bookauthors, year FROM book GROUP BY bookauthors, year HAVING COUNT(*) > 1;""",
    "Books with a Specific Keyword in the Title": """SELECT booktitle FROM book WHERE booktitle LIKE '%keyword%';""",  # Replace 'keyword' with user input
    "Year with the Highest Average Book Price": """SELECT year, AVG(amountretailPrice) AS avg_price FROM book GROUP BY year ORDER BY avg_price DESC LIMIT 1;""",
    "Count Authors Who Published 3 Consecutive Years": """SELECT bookauthors FROM (SELECT bookauthors, year, ROW_NUMBER() OVER (PARTITION BY bookauthors ORDER BY year) as rn FROM book) t WHERE rn = 3;""",
    "Authors with books published in the same year under different publishers": """SELECT bookauthors, year, COUNT(*) AS book_count FROM book GROUP BY bookauthors, year HAVING COUNT(DISTINCT publisher) > 1;""",
    "Average Retail Price of eBooks and Physical Books": """SELECT AVG(CASE WHEN isEbook = 'TRUE' THEN amountretailPrice ELSE NULL END) AS avg_ebook_price, AVG(CASE WHEN isEbook = 'FALSE' THEN amountretailPrice ELSE NULL END) AS avg_physical_price FROM book;""",
    "Books with Average Rating Outliers": """SELECT booktitle, averageRating, ratingsCount FROM book WHERE averageRating > (SELECT AVG(averageRating) + 2*STDDEV(averageRating) FROM book);""",
    "Publisher with Highest Average Rating (more than 10 books)": """SELECT publisher, AVG(averageRating) AS average_rating, COUNT(*) AS book_count FROM book GROUP BY publisher HAVING COUNT(*) > 10 ORDER BY average_rating DESC LIMIT 1;"""
}

if keyword:
    query = f"""SELECT booktitle FROM book WHERE booktitle LIKE '%{keyword}%';"""  # Keyword search
    df = run_query(query)
    if df is not None:
      st.write(df)
else:
  selected_query = st.selectbox("Select a query:", list(options.keys()))
  if selected_query:
      df = run_query(options[selected_query])
      if df is not None:
          st.write(df)