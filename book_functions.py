import streamlit as st
import pandas as pd
import requests
import time
import pymysql
from sqlalchemy import create_engine

def validate_books_data(query):
     with st.spinner("Fetching Data..."):
          time.sleep(2)

     book_datas = get_books_data(query)
     if book_datas is None:
          st.error("No books found")
     else:
        st.success("**Data fetched and saved to database successfully..!**")

        st.write(book_datas)

import requests
import pandas as pd
import pymysql
from sqlalchemy import create_engine

def get_books_data(query):
    # Google API Key (Replace with your key)
    api_key = "AIzaSyCZ5tCVT43gCcI2tt-M4aHbuntLtyE4F6o"
    # URL for Google Books API
    url = "https://www.googleapis.com/books/v1/volumes"

    max_results = 40  # Maximum number of books to fetch
    all_books_data = []
    start_index = 0  # Start index for paginated API requests

    while len(all_books_data) < max_results:
        # Make the API request
        response = requests.get(url, params={"key": api_key, "q": query, "maxResults": 40, "startIndex": start_index})
        if response.status_code != 200:
            print(f"Error fetching data: {response.status_code}")
            break

        # Parse the response data to JSON
        books = response.json()

        # Check if the 'items' key is in the response
        if 'items' not in books:
            print("No more books found!")
            break

        # Extract information for each book
        for book in books['items']:
            volume_info = book.get('volumeInfo', {})
            sale_info = book.get('saleInfo', {})
            book_info = {
                'book_id': book.get('id'),
                'search_key': query,
                'book_title': volume_info.get('title', 'N/A'),
                'book_subtitle': volume_info.get('subtitle', 'N/A'),
                'book_authors': ",".join(volume_info.get('authors', ['N/A'])),
                'book_description': volume_info.get('description', 'N/A'),
                'industryIdentifiers': volume_info.get('industryIdentifiers', [{}])[0].get('type'),
                'text_readingModes': volume_info.get('readingModes', {}).get('text', False),
                'image_readingModes': volume_info.get('readingModes', {}).get('image', False),
                'pageCount': volume_info.get('pageCount', 0),
                'categories': ",".join(volume_info.get('categories', 'N/A')),
                'language': volume_info.get('language', 'N/A'),
                'imageLinks': volume_info.get('imageLinks', {}).get('thumbnail', 'N/A'),
                'ratingsCount': volume_info.get('ratingsCount', 0),
                'averageRating': volume_info.get('averageRating', 0),
                'country': sale_info.get('country', 'N/A'),
                'saleability': sale_info.get('saleability', 'N/A'),
                'isEbook': sale_info.get('isEbook', False),
                'amount_listPrice': sale_info.get('listPrice', {}).get('amount', 0),
                'currencyCode_listPrice': sale_info.get('listPrice', {}).get('currencyCode', 'N/A'),
                'amount_retailPrice': sale_info.get('retailPrice', {}).get('amount', 0),
                'currencyCode_retailPrice': sale_info.get('retailPrice', {}).get('currencyCode', 'N/A'),
                'buyLink': sale_info.get('buyLink', 'N/A'),
                'year': volume_info.get('publishedDate', 'N/A'),
                'publisher': book.get('volumeInfo', {}).get('publisher', 'N/A'),
            }

            # Add the book info to the list
            all_books_data.append(book_info)

            # Stop if we have reached the required number of results
            if len(all_books_data) >= max_results:
                break

        # Update the start index for the next API request
        start_index += 40

    # Convert the list of book data to a DataFrame
    df = pd.DataFrame(all_books_data)

    # Save the DataFrame to the database
    connection_string = "mysql+pymysql://root:pass123@localhost:3306/books"
    engine = create_engine(connection_string)

    df.to_sql(
        name="extract",        # Name of the table in the database
        con=engine,            # SQLAlchemy engine connection
        index=False,           # Do not include DataFrame index as a column
        if_exists="append",   # Replace the table if it already exists
        chunksize=40           # Number of rows to insert in each chunk (for performance)
    )

    #st.success("Data saved to the database successfully!")
    return df  # Optionally return the DataFrame for further use

