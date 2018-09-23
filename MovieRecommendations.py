import json
import pandas
import time


# converts raw movie csv data to json
def jsonify(movie_csv, movie_json_file_name, ratings_csv, ratings_json_file_name):
    # movie_info: first column is movie id, second is movie title, third is genre
    movie_info = pandas.io.parsers.read_csv(movie_csv, delimiter=',', dtype=None, encoding=None).values
    # ratings: first column is user id, second is movie id, third is rating
    ratings = pandas.io.parsers.read_csv(ratings_csv, delimiter=',', dtype=None, encoding=None).values

    movie_dict = {}
    title_to_id = {}
    for i in range(0, len(movie_info)):
        title: str = movie_info[i][1]
        movie_id: int = movie_info[i][0]
        genres = movie_info[i][2]
        movie_dict[movie_id] = {"title": title, "genres": genres}
        title_to_id[title] = movie_id
    movie_dict["key"] = title_to_id
    with open(movie_json_file_name, 'w') as file:
        file.write(json.dumps(movie_dict))

    movie_id_to_critic_ratings = {}
    for i in range(0, len(ratings)):
        critic_id: int = ratings[i][0]
        movie_id: int = ratings[i][1]
        rating: float = ratings[i][2]
        critic_to_rating: dict = movie_id_to_critic_ratings.get(movie_id, {})
        critic_to_rating[int(critic_id)] = rating
        movie_id_to_critic_ratings[int(movie_id)] = critic_to_rating
    with open(ratings_json_file_name, 'w') as file:
        file.write(json.dumps(movie_id_to_critic_ratings))


# converts json data to a dictionary
def djsonify(json_file):
    with open(json_file, 'r') as file:
        json_data = file.read()

    return json.loads(json_data)




# title: (str) name of movie
# movies: (dict) key: movie id, value: (dict) title and genre
# move_to_critic_ratings: (dict) key: movie id, value: (dict) key: critic id, value: rating
def get_recommendations(title, movies, movie_to_critic_rating):
    """
    :type title: str
    :type movies: dict
    :type critic_ratings: dict
    :type movie_to_critic_rating: dict
    """

    min_reviews = 20
    title_to_id: dict = movies["key"]
    movie_id = str(int(title_to_id.get(title, -1)))
    ratings_for_search = movie_to_critic_rating.get(movie_id, -1)
    if movie_id == -1:
        raise Exception(title + " could not be found in library.")
    if movie_id not in movie_to_critic_rating or len(ratings_for_search.items()) < min_reviews:
        raise Exception("Not enough reviews for " + title + " to recommend movies")

    recommendations = []
    # for each corresponding movie
    for movie_compare, ratings_compare in movie_to_critic_rating.items():
        if movie_compare == movie_id or len(ratings_compare.keys()) < min_reviews:
            continue
        distance = 0
        critic_count = 0
        for critic, rating in ratings_for_search.items():
            if critic in ratings_compare:
                critic_count += 1
                distance += ((ratings_for_search[critic] - ratings_compare[critic]) ** 2)
        if critic_count < min_reviews:
            continue
        average_distance = distance ** .5 / critic_count
        recommendations.append((average_distance, movies[movie_compare]["title"],
                                movies[movie_compare]["genres"]))
    recommendations = sorted(recommendations, key=lambda rec: rec[0])
    print("Title, Genre(s), Confidence")
    print()
    for pair in recommendations:
        print(pair[1] + ", ", pair[2] + ", ", pair[0])
    return recommendations


movie_file = "big_movies.json"
ratings_file = "movie_to_big_ratings.json"


def main(convert):
    if convert:
        jsonify("big_movies.csv", "big_movies.json", "big_ratings.csv", "movie_to_big_ratings.json")
    movies = djsonify(movie_file)
    movie_to_critic_rating = djsonify(ratings_file)
    while True:
        title = input("Enter movie title: ")
        t = time.time()
        get_recommendations(title, movies, movie_to_critic_rating)
        print(time.time() - t)


main(False)
