
from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from django.core.paginator import Paginator

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

api = Api(app)
movie_ns = api.namespace('movies')


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        all_movies_query = Movie.query
        args = request.args

        director_id = args.get('director_id')
        if director_id is not None:
            all_movies_query = all_movies_query.filter(Movie.director_id == director_id)

        genre_id = args.get('genre_id')
        if genre_id is not None:
            all_movies_query = all_movies_query.filter(Movie.genre_id == genre_id)

        all_movies_json = movies_schema.dump(all_movies_query)

        page_number = args.get('page')
        if page_number is not None:
            paginator = Paginator(all_movies_json, 3)
            page_obj = paginator.get_page(page_number)
            page_movies = []
            for movie in page_obj:
                page_movies.append(movie)
            return page_movies, 200

        return all_movies_json, 200






@movie_ns.route('/<int:id>')
class MovieView(Resource):
    def get(self, id):
        movie = Movie.query.get(id)
        if movie is None:
            return {}, 404
        return movie_schema.dump(movie), 200



if __name__ == '__main__':
    app.run(debug=True)
