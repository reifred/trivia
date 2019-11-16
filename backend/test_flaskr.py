import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'incorrect6363','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
            self.category = Category(type='Math')
            self.db.session.add(self.category)
            self.db.session.flush()
            self.question = Question(
                question='What is four by four?',
                answer='Sixteen',
                category=self.category.id, 
                difficulty=2
            )
            self.db.session.add(self.question)
            self.db.session.commit()

    
    def tearDown(self):
        """Executed after reach test"""
        with self.app.app_context():
            self.db.session.query(Question).delete()
            self.db.session.query(Category).delete()
            self.db.session.commit()
            self.db.session.close()

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories_with_success_response(self):
    """
        Test getting all categories with a success response
    """
        response = self.client().get("/api/categories")
        data = json.loads(response.data)
        self.assertTrue(response.status_code, 200)
        self.assertTrue(data['success'], True)

    def test_get_questions_with_success_response(self):
    """
        Test getting all questions with a success response
    """
        response = self.client().get('/api/questions')
        data = json.loads(response.data)
        self.assertTrue(response.status_code, 200)
        self.assertTrue(data['success'], True)

    def test_get_questions_with_failure_response(self):
    """
        Test getting unavailable questions from the database
    """
        question = Question.query.first()
        question.delete()
        response = self.client().get('/api/questions')
        data = json.loads(response.data)
        self.assertTrue(response.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_delete_a_questions_with_success_response(self):
    """
        Test deleting an existing question from the database
    """
        question_id = Question.query.first().id
        response = self.client().delete(f"/api/questions/{question_id}")
        data = json.loads(response.data)
        self.assertTrue(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Question successfully deleted')

    def test_delete_a_questions_with_failure_response(self):
    """
        Test deleting an unexisting question from the database
    """
        question_id = Question.query.first().id
        response = self.client().delete(f"/api/questions/{question_id + 1}")
        data = json.loads(response.data)
        self.assertTrue(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_get_questions_of_given_category_with_success_response(self):
    """
        Test getting all questions of a given category id
    """
        category_id = Category.query.first().id
        response = self.client().get(f"/api/categories/{category_id}/questions")
        data = json.loads(response.data)
        self.assertTrue(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 1)

    def test_get_questions_of_given_category_with_failure_response(self):
    """
        Test getting all questions of an unexisting category
    """
        category_id = Category.query.first().id
        response = self.client().get(f"/api/categories/{category_id + 1}/questions")
        data = json.loads(response.data)
        self.assertTrue(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_create_a_question_with_success_response(self):
    """
        Test creating a question with all required fields and required request method
    """
        response = self.client().post('/api/questions',
            content_type='application/json',
            data=json.dumps(
            {
                'question': 'Test question',
                'answer': 'Test answer',
                'difficulty': 2,
                'category': 2
            }
            )
        )
        data = json.loads(response.data)
        self.assertTrue(response.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Question successfully added')

    def test_create_a_question_with_failure_response(self):
    """
        Test creating a question with a wrong request url
    """
        response = self.client().post('/api/questions/2',
            content_type='application/json',
            data=json.dumps(
            {
                'question': 'Test question',
                'answer': 'Test answer',
                'difficulty': 2,
                'category': 2
            }
            )
        )
        data = json.loads(response.data)
        self.assertTrue(response.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method not allowed')

    def test_search_a_question_with_success_response(self):
    """
        Test searching a question using a correct search term.
    """
        search_term = 'four'
        response = self.client().post('/api/questions/search',
            content_type='application/json',
            data=json.dumps({'searchTerm': search_term})
        )
        data = json.loads(response.data)
        self.assertTrue(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 1)

    def test_search_a_question_with_failure_response(self):
    """
        Test searching a question using a wrong search term.
    """
        search_term = 'fred'
        response = self.client().post('/api/questions/search',
            content_type='application/json',
            data=json.dumps({'searchTerm': search_term})
        )
        data = json.loads(response.data)
        self.assertTrue(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_get_quiz_question_with_success_response(self):
    """
        Test playing a quiz category and previous question parameters.
    """
        response = self.client().post('/api/quizzes',
            content_type='application/json',
            data=json.dumps({'previous_questions': [], 'quiz_category': {'id': 0, 'type': 'all'}}
            )
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_get_quiz_question_with_failure_response(self):
    """
        Test playing a quiz category a wrong request method.
    """
        response = self.client().get('/api/quizzes')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method not allowed')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
