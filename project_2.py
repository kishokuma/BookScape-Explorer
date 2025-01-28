import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
import book_functions as bf


# SQL connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="pass123",
    database='books',
    autocommit=True)
mycursor = mydb.cursor()

# Helper function to fetch data
def run_query(query):
    return pd.read_sql(query, mydb)

# Custom CSS for background and styling
st.markdown(
    """
    <style>
    body {
        background-image: url("https://via.placeholder.com/1920x1080.png"); /* Use a hosted image */
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        font-family: 'Roboto', sans-serif;
        color: #ffffff;
    }
    .header-title {
        color: #FF0000; /* Changed color to red */
        text-align: center;
        font-size: 56px; /* Increased font size */
        font-weight: bold;
        margin-bottom: 40px; /* Added more spacing */
        text-shadow: 3px 3px 6px rgba(255, 255, 255, 0.5); /* Enhanced shadow for visibility */
    }
    
    </style>
    """,
    unsafe_allow_html=True
)




# Sidebar Navigation
with st.sidebar:
    selected = option_menu("Main Menu", ["Home", 'Institutional Queries','Data Extraction'], 
        icons=['house', 'list-task','gear'], menu_icon="cast", default_index=1)

if selected == 'Home':
    # Add background image for music books
    st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://as2.ftcdn.net/v2/jpg/03/10/83/33/1000_F_310833371_wUOvc3sOpfIdJz8FkkkxHNtOFVrDw5Cj.jpg"); /* Replace with actual image URL */
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    </style>
    """,
    unsafe_allow_html=True
    )

    st.markdown('<div class="header-title">Music Books Explorer</div>', unsafe_allow_html=True)
    # Search Filters
    st.sidebar.header("Search Filters")
    title_filter = st.sidebar.text_input("Book Title")
    author_filter = st.sidebar.text_input("Author")
    publisher_filter = st.sidebar.text_input("Publisher")
    rating_range = st.sidebar.slider("Select Rating Range", 0.0, 10.0, (0.0, 10.0))

    # Build SQL Query
    query = "SELECT book_title,book_authors,book_publisher,ratingsCount,isEbook,year,buyLink FROM data_books WHERE 1=1"
    if title_filter:
        query += f" AND book_title LIKE '%{title_filter}%'"
    if author_filter:
        query += f" AND book_authors LIKE '%{author_filter}%'"
    if publisher_filter:
        query += f" AND book_publisher LIKE '%{publisher_filter}%'"
    query += f" AND ratingsCount BETWEEN {rating_range[0]} AND {rating_range[1]}"

    # Run Query and Display Results
    st.subheader("Search Results")
    try:
        results = run_query(query)
        if results.empty:
            st.write("No books found.")
        else:
            st.dataframe(results)

            # Add Visualization
            fig1 = px.bar(results, 
              x='book_title', 
              y='ratingsCount', 
              title='Ratings Count by Book Title',
              color='ratingsCount',  # Adds color based on the ratings count
              color_continuous_scale=px.colors.sequential.Rainbow)  
            st.plotly_chart(fig1)

            # Download Button
            csv = results.to_csv(index=False).encode('utf-8')
            st.download_button("Download Results", data=csv, file_name="books_data.csv", mime="text/csv")

    except Exception as e:
        st.error(f"An error occurred: {e}")

if selected == 'Institutional Queries':

    

    st.markdown('<div class="header-title">Institutional Queries</div>', unsafe_allow_html=True)

    # Define query options
    query_options = {
        "1.Check Availability of eBooks vs Physical Books": "select sum(if(isEbook = 'yes',1,0)) as Ebook_count,sum(if(isEbook = 'no',0,1)) as physical_book_count from data_books",
        "2.Find the Publisher with the Most Books Published": "select book_publisher,count(book_id) as number_of_books from data_books where book_publisher != '' and book_publisher is not null and book_publisher not in ('unknown') group by book_publisher order by number_of_books desc limit 1",
        "3.Identify the Publisher with the Highest Average Rating": "select book_publisher,max(averageRating) as max_avg_rating from data_books where book_publisher != '' and book_publisher is not null and book_publisher not in ('unknown') group by book_publisher order by max_avg_rating desc limit 1",
        "4.Get the Top 5 Most Expensive Books by Retail Price": "select book_title, amount_retailPrice , currencyCode_retailPrice from data_books order by amount_retailPrice desc limit 5",
        "5.Find Books Published After 2010 with at Least 500 Pages": "select book_title,pageCount,year from data_books where year>2010 and pageCount>=500",
        "6.List Books with Discounts Greater than 20%": "select book_title,amount_listPrice,amount_retailPrice,((amount_listPrice - amount_retailPrice)/amount_listPrice)*100 as disc_percent from data_books where ((amount_listPrice - amount_retailPrice)/amount_listPrice)*100 >20",
        "7.Find the Average Page Count for eBooks vs Physical Books":"select avg(if(isEbook = '1',pageCount,null)) as avg_Ebook_page_count,avg(if(isEbook = '0',pageCount,null)) as avg_phybook_page_count from data_books;",
        "8.Find the Top 3 Authors with the Most Books":"select book_authors,count(book_id) as number_of_books from data_books where book_authors != '' and book_authors is not null and book_authors not in ('unknown') group by book_authors order by number_of_books desc limit 3;",
        "9.List Publishers with More than 10 Books":"select book_publisher,count(book_id) as number_of_books from data_books group by book_publisher having count(book_id)>10;",
        "10.Find the Average Page Count for Each Category":"select categories, avg(pageCount) as avg_page_count from data_books group by categories order by avg_page_count desc;",
        "11.Retrieve Books with More than 3 Authors":"select book_title,book_authors from data_books where length(book_authors)- length(replace(book_authors,',',''))>2;",
        "12.Books with Ratings Count Greater Than the Average":"select book_title,ratingsCount from data_books where ratingsCount > (select avg(ratingsCount) from data_books);",
        "13.Books with the Same Author Published in the Same Year":"SELECT DISTINCT b1.book_authors,LEAST(b1.book_title, b2.book_title) AS book_1,GREATEST(b1.book_title, b2.book_title) AS book_2,b1.yearFROM data_books b1JOIN data_books b2 ON b1.book_authors = b2.book_authors AND b1.year = b2.year AND b1.book_title <> b2.book_titlewhere b1.book_authors != '' and b1.book_authors is not null and b1.book_authors not in ('unknown')ORDER BY b1.book_authors, b1.year;",
        "14.Books with 'classical' in the Title":"SELECT book_title, book_authors FROM data_books WHERE book_title LIKE '%classical%';",
        "15.Year with the Highest Average Book Price":"SELECT year, AVG(amount_retailPrice) AS avg_price FROM data_books GROUP BY year ORDER BY avg_price DESC LIMIT 1;",
        "16.Count Authors Who Published 3 Consecutive Years":"SELECT book_authors, COUNT(DISTINCT year) AS consecutive_years FROM data_books GROUP BY book_authors HAVING MAX(year) - MIN(year) >= 2;",
        "17.Write a SQL query to find authors who have published books in the same year but under different publishers. Return the authors, year, and the COUNT of books they published in that year":"SELECT book_authors, year, COUNT(DISTINCT book_publisher) AS publisher_count  FROM data_books  GROUP BY book_authors, year HAVING publisher_count > 1;",
        "18.Create a query to find the average amount_retailPrice of eBooks and physical books. Return a single result set with columns for avg_ebook_price and avg_physical_price. Ensure to handle cases where either category may have no entries":"SELECT AVG(CASE WHEN isEbook = TRUE THEN amount_retailPrice END) AS avg_ebook_price,AVG(CASE WHEN isEbook = FALSE THEN amount_retailPrice END) AS avg_physical_price FROM data_books;",
        "19.Write a SQL query to identify books that have an averageRating that is more than two standard deviations away from the average rating of all books. Return the title, averageRating, and ratingsCount for these outliers":"WITH stats AS (SELECT AVG(averageRating) AS avg_rating, STDDEV(averageRating) AS stddev_rating FROM data_books)SELECT book_title, averageRating, ratingsCount FROM data_books, stats WHERE averageRating > avg_rating + 2 * stddev_rating OR averageRating < avg_rating - 2 * stddev_rating;",
        "20.Create a SQL query that determines which publisher has the highest average rating among its books, but only for publishers that have published more than 10 books. Return the publisher, average_rating, and the number of books published":"SELECT book_publisher, AVG(averageRating) AS avg_rating, COUNT(*) AS book_count FROM data_books GROUP BY book_publisher HAVING COUNT(*) > 10 ORDER BY avg_rating DESC LIMIT 1;"
    }

    # Select query
    selected_query = st.selectbox("Select a query", list(query_options.keys()))
    query = query_options[selected_query]

    try:
        results = run_query(query)
        st.dataframe(results)

        # Optional visualization
        if 'ratingsCount' in results.columns:
            st.bar_chart(results['ratingsCount'])

    except Exception as e:
        st.error(f"An error occurred: {e}")



if selected == "Data Extraction":



    

    st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://img.freepik.com/premium-photo/stack-books-against-background-library_1270664-33518.jpg"); /* Replace with actual image URL */
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    </style>
    """,
    unsafe_allow_html=True
    )


    st.markdown('<div class="header-title">Data Extraction</div>', unsafe_allow_html=True)
    search_key = st.text_input("Enter the Search Key",placeholder="Type your search key here",autocomplete="off")
    if st.button("Fetch Data") and search_key == "":
        @st.dialog(" ")
        def isSearchKeyPresent():
            st.write("Please enter the search key")
            if st.button("ok"):
                st.rerun()
        if "isSearchKeyPresent" not in st.session_state:
            isSearchKeyPresent()
    elif search_key !="":
        bf.validate_books_data(search_key)




