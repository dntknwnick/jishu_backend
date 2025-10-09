from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.api import bp
from app.models.exam import Subject, QuestionWithOptions
from app.models.user import User
import random

@bp.route('/questions', methods=['GET'])
@jwt_required()
def get_questions():
    """Get questions, optionally filtered by subject"""
    subject_id = request.args.get('subject_id', type=int)

    if subject_id:
        questions = QuestionWithOptions.query.filter_by(subject_id=subject_id).all()
    else:
        questions = QuestionWithOptions.query.all()

    return jsonify([question.to_dict() for question in questions])

@bp.route('/questions/<int:id>', methods=['GET'])
@jwt_required()
def get_question(id):
    """Get a specific question by ID"""
    question = QuestionWithOptions.query.get_or_404(id)
    return jsonify(question.to_dict())

@bp.route('/questions/subject/<int:subject_id>', methods=['GET'])
def get_questions_by_subject(subject_id):
    """Get questions for a specific subject, optionally limited by count"""
    count = request.args.get('count', default=50, type=int)

    # Get questions from the QuestionWithOptions model
    questions = QuestionWithOptions.query.filter_by(subject_id=subject_id).limit(count).all()

    if questions:
        # Return questions from the new model
        return jsonify([{
            'id': q.id,
            'text': q.text,
            'subject_id': q.subject_id,
            'difficulty': q.difficulty,
            'marks': q.marks,
            'negative_marks': q.negative_marks,
            'option_a': q.option_a,
            'option_b': q.option_b,
            'option_c': q.option_c,
            'option_d': q.option_d,
            'correct_option': q.correct_option,
            'explanation': q.explanation
        } for q in questions])

    # If no questions found, generate some mock questions for development
    mock_questions = []
    for i in range(1, min(count, 10) + 1):  # Limit mock questions to 10
        correct_option = random.choice(['A', 'B', 'C', 'D'])
        mock_questions.append({
            'id': i,
            'text': f'Mock question {i} for subject {subject_id}. This is a sample question to test the exam functionality.',
            'subject_id': subject_id,
            'difficulty': 'medium',
            'marks': 4,
            'negative_marks': 1,
            'option_a': f'Option A for question {i} - This could be the correct answer',
            'option_b': f'Option B for question {i} - This is another possible answer',
            'option_c': f'Option C for question {i} - This might be correct too',
            'option_d': f'Option D for question {i} - This is the last option',
            'correct_option': correct_option,
            'explanation': f'This is a mock question for testing purposes. The correct answer is {correct_option}.'
        })

    return jsonify(mock_questions)

@bp.route('/questions', methods=['POST'])
@jwt_required()
def create_question():
    """Create a new question with options (admin only)"""
    # Check if user is admin
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or not user.is_admin():
        return jsonify({'error': 'Admin privileges required'}), 403

    data = request.get_json() or {}

    required_fields = ['text', 'subject_id', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    # Check if subject exists
    subject = Subject.query.get(data['subject_id'])
    if not subject:
        return jsonify({'error': 'Subject not found'}), 404

    # Validate correct_option
    if data['correct_option'] not in ['A', 'B', 'C', 'D']:
        return jsonify({'error': 'correct_option must be A, B, C, or D'}), 400

    # Create question using the new model
    question = QuestionWithOptions(
        text=data['text'],
        subject_id=data['subject_id'],
        difficulty=data.get('difficulty', 'medium'),
        option_a=data['option_a'],
        option_b=data['option_b'],
        option_c=data['option_c'],
        option_d=data['option_d'],
        correct_option=data['correct_option'],
        explanation=data.get('explanation', '')
    )

    db.session.add(question)
    db.session.commit()

    return jsonify(question.to_dict()), 201

@bp.route('/questions/<int:id>', methods=['PUT'])
@jwt_required()
def update_question(id):
    """Update a question (admin only)"""
    # Check if user is admin
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or not user.is_admin():
        return jsonify({'error': 'Admin privileges required'}), 403

    question = QuestionWithOptions.query.get_or_404(id)
    data = request.get_json() or {}

    if 'text' in data:
        question.text = data['text']

    if 'difficulty' in data:
        question.difficulty = data['difficulty']

    if 'subject_id' in data:
        # Check if subject exists
        subject = Subject.query.get(data['subject_id'])
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        question.subject_id = data['subject_id']

    # Update options
    if 'option_a' in data:
        question.option_a = data['option_a']
    if 'option_b' in data:
        question.option_b = data['option_b']
    if 'option_c' in data:
        question.option_c = data['option_c']
    if 'option_d' in data:
        question.option_d = data['option_d']

    if 'correct_option' in data:
        if data['correct_option'] not in ['A', 'B', 'C', 'D']:
            return jsonify({'error': 'correct_option must be A, B, C, or D'}), 400
        question.correct_option = data['correct_option']

    if 'explanation' in data:
        question.explanation = data['explanation']

    db.session.commit()

    return jsonify(question.to_dict())

@bp.route('/questions/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_question(id):
    """Delete a question (admin only)"""
    # Check if user is admin
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or not user.is_admin():
        return jsonify({'error': 'Admin privileges required'}), 403

    question = QuestionWithOptions.query.get_or_404(id)

    db.session.delete(question)
    db.session.commit()

    return jsonify({'message': 'Question deleted successfully'})
