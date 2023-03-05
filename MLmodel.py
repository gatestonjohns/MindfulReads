import pandas as pd
import numpy as np
from sklearn import preprocessing
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from functools import lru_cache


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# original df with unencoded values
global ogdf 

@lru_cache()
def readDataIn():
    global ogdf
    ogdf = pd.read_csv("books_dataset.csv").loc[:, ['bookID', 'userID', 'rating']]

    return ogdf

class BookDataset:
    def __init__(self, users, books, ratings):
        self.users = users
        self.books = books
        self.ratings = ratings

    def __len__(self):
        return len(self.users)

    def __getitem__(self, item):

        users = self.users[item] 
        books = self.books[item]
        ratings = self.ratings[item]
        
        return {
            "users": torch.tensor(users, dtype=torch.long),
            "books": torch.tensor(books, dtype=torch.long),
            "ratings": torch.tensor(ratings, dtype=torch.long),
        }
    
class RecSysModel(nn.Module):
    def __init__(self, n_users, n_books):
        super().__init__()
        # trainable lookup matrix for shallow embedding vectors
        
        self.user_embed = nn.Embedding(n_users, 32)
        self.book_embed = nn.Embedding(n_books, 32)
        self.out = nn.Linear(64, 1)

    
    def forward(self, users, books, ratings=None):
        user_embeds = self.user_embed(users)
        book_embeds = self.book_embed(books)
        output = torch.cat([user_embeds, book_embeds], dim=1)
        
        output = self.out(output)
        
        return output

def addNewUserReview(ogdf, isbn, starVal):
  ogdf.loc[len(ogdf)] = {'bookID': isbn, 'userID': "NEW_USER", 'rating': starVal}

# define a function to get book recommendations for a user after retraining the model (should be done after every ~10 book reviews)
def retrain_and_getRecommendations(user_id, ogdf, n=100):
  # copy dataframe that will become encoded
  df = ogdf.copy()

  # encode the user and book id to start from 0 so we don't run into index out of bound with Embedding
  lbl_user = preprocessing.LabelEncoder()
  lbl_book = preprocessing.LabelEncoder()
  df.userID = lbl_user.fit_transform(df.userID.values)
  df.bookID = lbl_book.fit_transform(df.bookID.values)

  train_dataset = BookDataset(
      users=df.userID.values,
      books=df.bookID.values,
      ratings=df.rating.values
  )

  train_loader = DataLoader(dataset=train_dataset,
                            batch_size=4,
                            shuffle=True,
                            num_workers=2) 

  dataiter = iter(train_loader)
  dataloader_data = next(dataiter)

  model = RecSysModel(
      n_users=len(lbl_user.classes_),
      n_books=len(lbl_book.classes_),
  ).to(device)

  optimizer = torch.optim.Adam(model.parameters())  
  sch = torch.optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.7)

  loss_func = nn.MSELoss()

  epochs = 1
  total_loss = 0
  plot_steps, print_steps = 5000, 5000
  step_cnt = 0
  all_losses_list = [] 

  model.train() 
  for epoch_i in range(epochs):
      for i, train_data in enumerate(train_loader):
          output = model(train_data["users"], 
                        train_data["books"]
                        ) 
          
          rating = train_data["ratings"].unsqueeze(-1).to(torch.float32)

          loss = loss_func(output, rating)
          total_loss = total_loss + loss.sum().item()
          optimizer.zero_grad()
          loss.backward()
          optimizer.step()

          step_cnt = step_cnt + len(train_data["users"])
          

          if(step_cnt % plot_steps == 0):
              avg_loss = total_loss/(len(train_data["users"]) * plot_steps)
              print(f"epoch {epoch_i} loss at step: {step_cnt} is {avg_loss}")
              all_losses_list.append(avg_loss)
              total_loss = 0 # reset total_loss

  # get all the books in the dataset
  all_books = ogdf['bookID'].unique()

  # get the books that the user has already reviewed
  reviewed_books = ogdf[ogdf['userID'] == user_id]['bookID'].unique()

  # get the books that the user has not reviewed yet
  new_books = np.setdiff1d(all_books, reviewed_books)

  # create a new dataset with the new_books and the user_id
  new_df = pd.DataFrame({'userID': [user_id] * len(new_books), 'bookID': new_books})

  # encode the user_id and book_id
  new_df['userID'] = lbl_user.transform(new_df['userID'].values)
  new_df['bookID'] = lbl_book.transform(new_df['bookID'].values)

  # create a dataloader for the new dataset
  new_dataset = BookDataset(new_df['userID'].values, new_df['bookID'].values, np.zeros(len(new_df)))
  new_loader = DataLoader(dataset=new_dataset, batch_size=4, shuffle=False)

  # make predictions for the new dataset using the model
  model.eval()
  predictions = []
  with torch.no_grad():
      for i, data in enumerate(new_loader):
          users = data['users'].to(device)
          books = data['books'].to(device)
          output = model(users, books)
          predictions.extend(output.cpu().numpy())

  # add predictions column to new_df
  new_df['predictions'] = predictions

  # sort the predictions in descending order and return the top-N books
  top_books = new_df.sort_values(by=['predictions'], ascending=False)[:n]

  # decode the book_id to get the book title and author
  top_books['bookID'] = lbl_book.inverse_transform(top_books['bookID'].values)

  # return the top-N book recommendations
  return top_books['bookID']

