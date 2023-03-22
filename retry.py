import streamlit as st
import pandas as pd
import MLmodel

page_title = "MindfulReads"
layout = "wide"

st.set_page_config(page_title=page_title, layout=layout)

@st.cache_data
def ogdf(filename, headers):
    return pd.read_csv(filename)[headers].drop_duplicates()

def getRandomBooks(ogdf, n=100):
    toAdd = []
    for i, row in ogdf.sample(n).iterrows():
        toAdd.append({'bookID': row['bookID'], 'title': row['title'], 'description': row['description'], 'image': row['image']})
    return toAdd

if 'ratingLog' not in st.session_state:
    st.session_state.ratingLog = pd.DataFrame(columns=['bookID', 'rating'])

if 'bookStk' not in st.session_state:
    st.session_state.bookStk = getRandomBooks(ogdf("sample_reviews_all_categories.csv", ['bookID', 'image', 'title', 'description']), 200)

if 'ratingList_SMA5' not in st.session_state:
    st.session_state.ratingList_SMA5 = []

def noRating():
    # user does not want to be associated with the book at all
    # remove the book that was just skipped AND fill in with random books if the stack has run out
    st.session_state.bookStk.pop(0)
    if len(st.session_state.bookStk) == 0:
        st.session_state.bookStk = getRandomBooks(ogdf("sample_reviews_all_categories.csv", ['bookID', 'image', 'title', 'description']), 200)

    # add '0' rating to moving average
    # code for updating simple moving average graph
    if len(st.session_state.ratingList_SMA5) == 0:
        newVal = 0
    elif len(st.session_state.ratingList_SMA5) < 9:
        newVal = (((st.session_state.ratingList_SMA5[-1]*len(st.session_state.ratingList_SMA5))+0) / (len(st.session_state.ratingList_SMA5) + 1))
    else:
        newVal = ((st.session_state.ratingList_SMA5[-1]*9) + 0) / 10
    st.session_state.ratingList_SMA5.append(newVal)

def negRating():
    # add rating to the log
    st.session_state.ratingLog = st.session_state.ratingLog.append({'userID': "NEW_USER", 'bookID': currBook['bookID'], 'rating': -5}, ignore_index=True)

    if len(st.session_state.ratingLog) % 31 == 30:
        modelDF = ogdf("sample_reviews_all_categories.csv", ['bookID', 'userID', 'rating'])
        bookDF = ogdf("sample_reviews_all_categories.csv", ['bookID', 'image', 'title', 'description'])
        newISBNs = MLmodel.retrain_and_getRecommendations("NEW_USER", pd.concat([modelDF, st.session_state.ratingLog], axis=0), n=100).tolist()
        for isbn in reversed(newISBNs):
            st.session_state.bookStk.insert(0, bookDF[bookDF['bookID'] == isbn].iloc[0])
        

    # code for updating simple moving average graph
    if len(st.session_state.ratingList_SMA5) == 0:
        newVal = 0
    elif len(st.session_state.ratingList_SMA5) < 9:
        newVal = (((st.session_state.ratingList_SMA5[-1]*len(st.session_state.ratingList_SMA5))-0) / (len(st.session_state.ratingList_SMA5) + 1))
    else:
        newVal = ((st.session_state.ratingList_SMA5[-1]*9) - 0) / 10
    st.session_state.ratingList_SMA5.append(newVal)
    
    # remove the book that was just rated AND fill in with random books if the stack has run out
    st.session_state.bookStk.pop(0)
    if len(st.session_state.bookStk) == 0:
        st.session_state.bookStk = getRandomBooks(ogdf("sample_reviews_all_categories.csv", ['bookID', 'image', 'title', 'description']), 20)
    



def radioClicked():
    # add rating to the log
    st.session_state.ratingLog = st.session_state.ratingLog.append({'userID': "NEW_USER", 'bookID': currBook['bookID'], 'rating': 5}, ignore_index=True)

    if len(st.session_state.ratingLog) % 16 == 15:
        modelDF = ogdf("sample_reviews_all_categories.csv", ['bookID', 'userID', 'rating'])
        bookDF = ogdf("sample_reviews_all_categories.csv", ['bookID', 'image', 'title', 'description'])
        newISBNs = MLmodel.retrain_and_getRecommendations("NEW_USER", pd.concat([modelDF, st.session_state.ratingLog], axis=0), n=100).tolist()
        for isbn in reversed(newISBNs):
            st.session_state.bookStk.insert(0, bookDF[bookDF['bookID'] == isbn].iloc[0])
        

    # code for updating simple moving average graph
    if len(st.session_state.ratingList_SMA5) == 0:
        newVal = 5
    elif len(st.session_state.ratingList_SMA5) < 9:
        newVal = (((st.session_state.ratingList_SMA5[-1]*len(st.session_state.ratingList_SMA5))+5) / (len(st.session_state.ratingList_SMA5) + 1))
    else:
        newVal = ((st.session_state.ratingList_SMA5[-1]*9) + 5) / 10
    st.session_state.ratingList_SMA5.append(newVal)
    
    # remove the book that was just rated AND fill in with random books if the stack has run out
    st.session_state.bookStk.pop(0)
    if len(st.session_state.bookStk) == 0:
        st.session_state.bookStk = getRandomBooks(ogdf("sample_reviews_all_categories.csv", ['bookID', 'image', 'title', 'description']), 20)

if __name__ == '__main__':

    currBook = st.session_state.bookStk[0]

    col1, col2, col3 = st.columns(3)

    with col1:
        try:
            st.image(currBook['image'], use_column_width=True)
        except:
            st.write("Bad data. No valid URL for book cover to be displayed.")
    with col2:
        st.title(currBook['title'])
        st.write(currBook['description'])
    with col3:
        ohyesBtn = st.button("I would definitely read that!", on_click= radioClicked)
        siBtn = st.button("Somewhere inbetween love and hate...", on_click= noRating)
        wnrBtn = st.button("No chance I read that...", on_click= noRating)
        st.line_chart(data=st.session_state.ratingList_SMA5, width=0, height=0, use_container_width=True)


        


    


