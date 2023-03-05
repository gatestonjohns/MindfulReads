import streamlit as st
import MLmodel
from streamlit_star_rating import st_star_rating

ogdf = MLmodel.readDataIn()
print(ogdf)

if "title" not in st.session_state:
    st.session_state.title = "How to be Fine"
if "author" not in st.session_state:
    st.session_state.author = "Jolenta Greenberg & Kristen Meinzer"
if "description" not in st.session_state:
    st.session_state.description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
if "image" not in st.session_state:
    st.session_state.image = "https://books.google.com/books/publisher/content?id=rbadDwAAQBAJ&printsec=frontcover&img=1&zoom=5&edge=curl&imgtk=AFLRE70s-adKehseO6TjSN6bQzhH31D-nUXSZMPMDvjCbAE21_h9s7TuPcUMJqQL-CuJJXpd8zPcWjpyy0ZNG5lu-OeVJpxFxcvgUwRp7UjFtdr5-2wAMMIAAJJLT4YnG8Y8U-flNwVk"
if "smileys" not in st.session_state:
    st.session_state.smileys = -1


# This function is executed when a user clicks a smiley
def update_book_on_display(t, a, d, i):
    st.session_state.title = t
    st.session_state.author = a
    st.session_state.description = d
    st.session_state.image = i
    st.session_state.smileys = -1


# This function is executed when a user clicks a smiley
def smiley_callback():
    # NOTE: You have access to smileys, which is the user's selection 1-5
    update_book_on_display(
        "New title3", "new author", "desc", "https://docs.streamlit.io/"
    )


# This function is executed when a user clicks the "Add to Reading List" button
def add_button_callback():
    # NOTE: You have access to smileys, which is the user's selection 1-5
    # Do what you need with that, get a new book to display, and update the display
    update_book_on_display(
        "New title", "new author", "desc", "https://docs.streamlit.io/"
    )


col1, col2 = st.columns(2)
col1.image(st.session_state.image, use_column_width=True)
col2.title(st.session_state.title)
col2.subheader(st.session_state.author)
col2.write(st.session_state.description)
st.markdown("---")

update_book_on_display(
    "New title 2", "new author", "desc", "https://docs.streamlit.io/"
)

_, col2, _ = st.columns((1, 8, 1))
with col2:
    smileys = st_star_rating("", 5, 0, emoticons=True, size=100)
if smileys >= 0:
    st.write(f"{smileys} bruddah")
    smiley_callback()
if st.button("**Add to Reading List!**", use_container_width=True, type="primary"):
    add_button_callback()
