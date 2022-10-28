import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer


def get_df(queryset):
    """Takes in a Model instance such as Course and outputs DF of objects with only title and description columns"""
    df = pd.DataFrame(list(queryset.values('title', 'description'))) # Create DF with columns title and description for this model type
    df.index = df.index + 1 # Set index so it starts at 1
    try:
        df.drop(columns=['Unnamed: 0'], inplace=True) # Drop unnecessary column if it exists
    except:
        pass
    return df


def get_cosine_sim_using_tfidf_matrix(df):
    
    # Initialize. Remove all English stop words such as 'the' and 'a'
    tfidf = TfidfVectorizer(stop_words='english')

    # Replace NaN with an empty string
    df['description'] = df['description'].fillna('')  

    # Construct the required TF-IDF matrix by fitting and transforming the data
    tfidf_matrix = tfidf.fit_transform(df['description'])

    # Compute cosine similarity matrix
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    return cosine_sim


def get_indices_series(df):
    # Construct a reverse map of indices and movie titles
    indices = pd.Series(df.index, index=df['title']).drop_duplicates()
    return indices

# indices = get_indices_series(df)


def prep_for_recs(df, obj_instance):
    """
    Inputs: DF of objects with only title and description columns, and obj_instance from DetailView (ex. the specific category 'Languages')
    Outputs: title of obj_instance (ex. 'Languages'), cosine similarity, indices Pandas series
    """
    title = obj_instance.title
    cosine_sim = get_cosine_sim_using_tfidf_matrix(df)
    indices = get_indices_series(df)
    return title, cosine_sim, indices


def get_recs(df, title, cosine_sim, indices):
    """Function that takes in movie title as input and outputs most similar movies"""
    try:
        # Get index of movie that matches the title
        idx = indices[title]

        # Get pairwise smilarity scores of all movies with that movie
        sim_scores = list(enumerate(cosine_sim[idx - 1]))

        # Sort the movies based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Get scores of 10 most similar movies
        sim_scores = sim_scores[1:3]

        # Get movie indices
        res_indices = [i[0] + 1 for i in sim_scores]

        # Return top 10 most similar movies
        return df['title'].iloc[res_indices]
    except:
        return None


def generate_recommendations_from_queryset(queryset, obj):
    # Create Pandas dataframe for content-based recommendation system. For now, only title and description are needed.
    df = get_df(queryset) # Create Pandas DF of all the instances of the obj but put only the columns title and category
    print(df)
    title = obj.title
    cosine_sim = get_cosine_sim_using_tfidf_matrix(df)
    indices = get_indices_series(df)
    print(title)
    print(indices)
    recs = get_recs(df, title, cosine_sim, indices)
    return recs

