import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  CORS(app, resources={r"/api/*": {"origins": "*"} })

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, OPTIONS')
    return response

  @app.route('/api/categories')
  def retrieve_categories():
    """
    Get all available categories.
    """
    try:
      categories = Category.query.all()
      if not categories:
          abort(404)
      return jsonify({
          'success': True,
          'categories': [category.type for category in categories]
      }), 200
    except Exception as error:
        raise error
    finally:
        db.session.close()

  def paginate_quetions(request, selection):
    """ 
    Get available questions and return a paginated result 
    """
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

  @app.route('/api/questions')
  def get_questions():
    """
    Get all available questions paginated 
    by a maximum number of 10 questions per page.
    """
    try:
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_quetions(request, selection)
      categories = {
          category.id: category.type for category in Category.query.all()
      }

      if len(current_questions) == 0:
        abort(404)

      return jsonify({
          'success': True,
          'questions': current_questions,
          'categories': categories,
          'total_questions': len(selection),
          'current_category': None
      }), 200
    except Exception as error:
      raise error
    finally:
      db.session.close()  

  @app.route("/api/questions/<int:question_id>", methods=['DELETE'])
  def delete_question(question_id):
    """
    Delete the question of a given id specified in the request url
    """
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if not question:
        abort(404)

      question.delete()

      return jsonify({
        'success': True,
        'message': 'Question successfully deleted'
      }), 200
    except Exception as error:
        raise error      
    finally:
      db.session.close()  

  @app.route("/api/questions", methods=['POST'])
  def create_question():
    """
    Create a new question given question body, 
    answer, category_id, and difficult_id.  
    """
    try:
      body = request.get_json()
      
      new_question = Question(
        question = body.get('question', None),
        answer = body.get('answer', None),
        category = body.get('category', None),
        difficulty = body.get('difficulty', None)
      )

      if not (new_question.question and new_question.answer and \
        new_question.category and new_question.difficulty):
        abort(400)

      new_question.insert()

      return jsonify({
        'success': True,
        'message': 'Question successfully added'
      }), 201
    except Exception as error:
        raise error      
    finally:
      db.session.close()  

  @app.route('/api/questions/search', methods=['POST'])
  def search_questions():
    """
    Get all questions based on a search term given it's a substring of the question
    """
    try:
      search_term = request.get_json().get('searchTerm', None)
      all_questions = Question.query.filter(
        Question.question.ilike("%" + search_term + "%")
      ).all()
      current_questions = paginate_quetions(request, all_questions)

      if not current_questions:
        abort(404)

      return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(all_questions),
          'current_category': None
      })
    except Exception as error:
        raise error      
    finally:
      db.session.close()

  @app.route('/api/categories/<int:category_id>/questions')
  def retrieve_questions_by_category(category_id):
    """
    Get all available questions of a given category
    """
    try:
      category = Category.query.get(category_id)
      selection = Question.query.filter_by(category=category_id).all()
      current_questions = paginate_quetions(request, selection)
      if not current_questions:
          abort(404)
      return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(selection),
          'current_category': category_id
      }), 200
    except Exception as error:
        raise error
    finally:
      db.session.close()

  @app.route("/api/quizzes", methods=["POST"])
  def get_quizzes():
    """
    Play a quiz by returning random questions within 
    a given category if provided and that is not one of the
    previous questions.
    """
    try:
      data = request.get_json()
      previous_questions = data.get("previous_questions")
      quiz_category = data.get("quiz_category")
      quiz_category_id = int(quiz_category["id"])

      question = Question.query.filter(
          Question.id.notin_(previous_questions)
      )

      if quiz_category_id:
          question = question.filter_by(category=quiz_category_id)

      question = question.first().format()

      return jsonify({"success": True, "question": question,}), 200
    except Exception as error:
        raise error      
    finally:
      db.session.close()  

  @app.errorhandler(400)
  def custom404(error):
      response = jsonify({
          'success': False,
          'message': 'Bad Request'
      })
      return response, 400
  
  @app.errorhandler(404)
  def custom404(error):
      response = jsonify({
          'success': False,
          'message': 'Resource not found'
      })
      return response, 404

  @app.errorhandler(405)
  def custom404(error):
      response = jsonify({
          'success': False,
          'message': 'Method not allowed'
      })
      return response, 405

  @app.errorhandler(422)
  def custom422(error):
      response = jsonify({
          'message': 'Unable to process request'
      })
      return response, 422

  @app.errorhandler(500)
  def custom422(error):
      response = jsonify({
          'success': False,
          'message': 'Internal server error'
      })
      return response, 500
  
  return app
