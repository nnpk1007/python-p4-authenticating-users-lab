#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

class IndexArticle(Resource):
    
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:

            article = Article.query.filter(Article.id == id).first()
            article_json = jsonify(article.to_dict())

            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401

class Login(Resource):
# It has one route, post().
# post() gets a username from request's JSON.
# post() retrieves the user by username (we made these unique for you).
# post() sets the session's user_id value to the user's id.
# post() returns the user as JSON with a 200 status code.

    def post(self):
        user = User.query.filter(User.username == request.get_json()["username"]).first()
        print(user)
        session["user_id"] = user.id

        response = make_response(jsonify(user.to_dict()), 200)
        
        return response


class Logout(Resource):
# Logout is located at /logout.
# It has one route, delete().
# delete() removes the user_id value from the session.
# delete() returns no data and a 204 (No Content) status code.
    def delete(self):
        session["user_id"] = None

        return {}, 204


class CheckSession(Resource):
# CheckSession is located at /check_session.
# It has one route, get().
# get() retrieves the user_id value from the session.
# If the session has a user_id, get() returns the user as JSON with a 200 status code.
# If the session does not have a user_id, get() returns no data and a 401 (Unauthorized) status code.
    def get(self):
        user = User.query.filter(User.id == session.get("user_id")).first()

        if user:
            print(user)
            return make_response(jsonify(user.to_dict()), 200) 
        else:
            print("No user")
            return {}, 401


api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(CheckSession, "/check_session")

if __name__ == '__main__':
    app.run(port=5555, debug=True)
