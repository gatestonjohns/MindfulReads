import streamlit as st
import pandas as pd

# Load CSV into DataFrame
df = pd.read_csv('reviews.csv')

# Function to display a single book
def display_book(book):
    st.write(book['title'])
    st.write(book['description'])

# Get a random book
def get_random_book(df, exclude):
    book = df.sample(1).iloc[0]
    if book['title'] == exclude:
        return get_random_book(df, exclude)
    else:
        return book

# Main function to display app
def main():
    # Initialize state variables
    current_book = get_random_book(df, '')
    ratings = {}

    # Create UI
    col1, col2 = st.columns([2, 1])
    with col1:
        display_book(current_book)
    with col2:
        rating = st.radio('Rate this book:', options=[1, 2, 3, 4, 5])
        if st.button('Next book'):
            ratings[current_book['title']] = rating
            current_book = get_random_book(df, current_book['title'])

    # Show current ratings
    st.write('Current ratings:')
    for title, rating in ratings.items():
        st.write(f'{title}: {rating}')

if __name__ == '__main__':
    main()
