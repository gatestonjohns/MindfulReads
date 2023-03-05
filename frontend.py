import streamlit as st
import pandas as pd
from streamlit_star_rating import st_star_rating

df = pd.read_csv('reviews.csv')


# Get a random book
def get_random_book(df, exclude):
    book = df.sample(1).iloc[0]
    if book['title'] == exclude:
        return get_random_book(df, exclude)
    else:
        return book


def rate_book(book, rating):
    print(f'Book {book["title"]} rated {rating}!')


# Main function to display app
def main():
    # Initialize state variables
    if 'bookstack' not in st.session_state:
        st.session_state.bookstack = []
        for _ in range(50):
            st.session_state.bookstack.append(get_random_book(df, ''))

    current_book = st.session_state.bookstack.pop()
    col1, col2 = st.columns(2)
    with col1:
        st.image(current_book['image'], use_column_width=True)
    with col2:
        st.title(current_book['title'])
        st.subheader(current_book['authors'][2:-2])
        st.write(current_book['description'])
    st.markdown("---")
    _, middle, _ = st.columns((1, 8, 1))
    with middle:
        rating = st_star_rating('', 5, 0, emoticons=True, size=100)
        if rating != 0:
            print(f'Book {current_book["title"]} rated {rating}!')


if __name__ == '__main__':
    main()
