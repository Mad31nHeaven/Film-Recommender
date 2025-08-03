import pandas as pd
from surprise import accuracy
from surprise import KNNBasic
from surprise import Dataset
from surprise import Reader
from surprise.model_selection import train_test_split
import numpy as np
reader_movies=pd.read_csv('Movie/movies.csv')
reader_ratings = pd.read_csv("Movie/ratings.csv")

def convert_numpy(id):
    binarized_genres = reader_movies[reader_movies['movieId'] == id]['binarized_genres'].iloc[0]
    clean_genre=binarized_genres.strip('[]').split()
    return np.array(clean_genre,dtype=int)
def get_cos_sim(movieId):
    main_genre=convert_numpy(movieId)
    cosine_sims = []
    for i in range(len(reader_movies)):
        current_movieId = reader_movies['movieId'][i]
        current_vector = convert_numpy(current_movieId)
        dot_product = np.dot(main_genre, current_vector)
        magnitude_product = np.linalg.norm(main_genre) * np.linalg.norm(current_vector)
        if magnitude_product!=0:
            cosine_sim = dot_product / magnitude_product
        else:
            cosine_sim=0
        cosine_sims.append(cosine_sim)

    return cosine_sims
def return_collab_filt(new_userIds,new_movieIds,new_ratings):
    #setting up dictionary
    rating = [i for i in reader_ratings['rating']]
    userid = [i for i in reader_ratings['userId']]
    movieid = [i for i in reader_ratings['movieId']]
    ratings_dict = {
        "item": movieid,
        "user": userid,
        "rating": rating,
    }
    ratings_dict['item'].extend(new_movieIds)
    ratings_dict['user'].extend(new_userIds)
    ratings_dict['rating'].extend(new_ratings)
    df = pd.DataFrame(ratings_dict)
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(df[["user", "item", "rating"]], reader)

    train_set, test_set = train_test_split(data, test_size=0.2, random_state=30)
    sim_options = {
        "name": "cosine",
        "user_based": True
    }


    UserId=new_userIds[0]
    model = KNNBasic(sim_options=sim_options)

    model.fit(train_set)
    test = model.test(test_set)
    rmse = accuracy.rmse(test)
    movie_ids_unique=df['item'].unique()

    #code for predictions
    rated_by_user_1 = df[df['user'] == UserId]['item'].unique() #here you change userId
    movies_not_rated_1=[i for i in movie_ids_unique if i not in rated_by_user_1]
    print(rated_by_user_1)
    print(movies_not_rated_1)
    predictions = []
    list_names=[]
    #collaborative filtering


    for i in movies_not_rated_1:
        estimation= model.predict(UserId,i) #here you change userId
        predictions.append(estimation.est)
    top_5_indices = np.argsort(predictions)[-5:][::-1]
    for i in top_5_indices:
        movie_id = movies_not_rated_1[i]
        title = reader_movies[reader_movies['movieId'] == movie_id]['title'].iloc[0]
        print(f'recommended: {title}')
        list_names.append(title)
    #content based



    cosine=0
    for i in rated_by_user_1:
        current=get_cos_sim(i)
        cosine+=np.array(current)
    movie_list=reader_movies['movieId'].tolist()
    valid_indexes=[i for i in range(len(cosine)) if movie_list[i] not in rated_by_user_1]
    cosine_to_predict=[cosine[i] for i in valid_indexes]
    top_5_indices = np.argsort(cosine_to_predict)[-5:][::-1]

    for i in top_5_indices:
        valid_index=valid_indexes[i]
        title = reader_movies.loc[valid_index, 'title']
        print(f'recommended:{title}')
        list_names.append(title)
    for i in rated_by_user_1:

        title = reader_movies[reader_movies['movieId'] == i]['title'].iloc[0]

        print(title)
    return list_names
