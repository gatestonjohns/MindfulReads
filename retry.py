import streamlit as st
import pandas as pd
import MLmodel

page_title = "MindfulReads"
layout = "centered"

st.set_page_config(page_title=page_title, layout=layout)

def getRandomBooks(ogdf, n=100):
    toAdd = []
    for i, row in ogdf[['bookID', 'title', 'image', 'description']].sample(n).iterrows():
        toAdd.append({'bookID': row['bookID'], 'title': row['title'], 'description': row['description'], 'image': row['image']})
    return toAdd

def nextClicked():
    print("Number of times next has been hit: ", st.session_state['counter'])
    st.session_state.counter += 1
    st.session_state.bookStk.pop()
    if len(st.session_state.bookStk) == 0:
        st.session_state.bookStk = getRandomBooks(st.session_state.ogdf, 5)
    st.write('stk length:', len(st.session_state.bookStk))

def radioClicked():
    print(currBook['title'], " was rated ", st.session_state.rating, " !! ")
    st.session_state.bookStk.pop()
    if len(st.session_state.bookStk) == 0:
        st.session_state.bookStk = getRandomBooks(st.session_state.ogdf, 5)
    st.write('stk length:', len(st.session_state.bookStk))


if 'counter' not in st.session_state:
    st.session_state.counter = 1

if 'ogdf' not in st.session_state:
    st.session_state.ogdf = pd.read_csv("reviews.csv")[['bookID', 'title', 'description', 'image']]

if 'bookStk' not in st.session_state:
    st.session_state.bookStk = getRandomBooks(st.session_state.ogdf, 5)

currBook = st.session_state.bookStk[-1]

col1, col2 = st.columns(2)

with col1:
    st.image(currBook['image'], use_column_width=True)
with col2:
    st.title(currBook['title'])
    st.write(currBook['description'])


# "session state", st.session_state
bottom= st.columns([1,4,1])[1]
with bottom:
    st.radio("Star Rating: ", options=[1, 2, 3, 4, 5], horizontal=True, key="rating", on_change= radioClicked)
    st.write('stk length:', len(st.session_state.bookStk))
    nextBtn = st.button("Next ->", on_click= nextClicked)


    


