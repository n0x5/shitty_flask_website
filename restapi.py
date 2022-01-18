try:
    from __main__ import app
except:
    from app import app
from flask_restful import Resource, Api

######################## REST API ################

class movieindexa(Resource):
    def get(self):
        genrelist = (["romance", "comedy", "animation", "mystery", "documentary", "crime", "family", "sport",
                "biography", "history", "western", "sci-fi", "horror", "adventure", "drama", "fantasy", "thriller", "action"])
        genres = [item.title() for item in genrelist]
        return {'genre': '{}' .format(genres)}

api.add_resource(movieindexa, '/api/moviegenres')

def apisearch(self, search):
    list1 = []
    list2 = []
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'databases', 'movies.db'))
    cursor = connection.cursor()
    cursor.execute("select release, director, imdb, infogenres, substr(title, -1, -4), mainactors, infosummary, dated from \
        movies where (genre like ? or infogenres like ? or release like ? or director like ? \
        or mainactors like ? or inforest like ?) order by substr(title, -1, -4) desc, dated desc", 
        ('%'+search+'%', '%'+search+'%', '%'+search+'%', '%'+search+'%', '%'+search+'%', '%'+search+'%'))
    results = [(item[0], item[1].strip().replace('\\n', '').replace(',', ''), item[2], 
                item[3].replace('[', '').replace(']', '').replace('\'', ''), item[4], 
                item[5], item[6]) for item in cursor.fetchall()]
    for i in range(len(results)): 
        list1.append(results[i])
    for item3 in list1:
        results3 = {"data":{"release": '{}' .format(item3[0].encode('utf-8')), "director": '{}' .format(item3[1].encode('utf-8')), "imdb": '{}' .format(item3[2].encode('utf-8')), 
                    "genres": '{}' .format(item3[3].encode('utf-8')), "year": '{}' .format(item3[4].encode('utf-8')), "main_actors": '{}' .format(item3[5].encode('utf-8')),
                    "plot_summary": '{}' .format(item3[6].encode('utf-8'))}}
        list2.append(results3)

    cursor.close()
    return list2

class moviesearchtitle(Resource):
    def get(self, search):
        rls = apisearch(self, search)
        return {"data":{"children": rls}}

api.add_resource(moviesearchtitle, '/api/moviesearch/<string:search>')