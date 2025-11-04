from flask import Flask, jsonify, request
from database import db
from models.user import User


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Bart@localhost:3306/myflasklogin'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


def validate_user_data(data, partial=False):
    if not data:
        return 'No input in data'

    if not partial:
        required_fields = ['username', 'email', 'password']
        if not all(field in data for field in required_fields):
            return 'Required fields are missing'

    if 'email' in data and '@' not in data['email']:
        return 'Invalid email format'

    if 'password' in data and len(data['password']) < 8:
        return 'Password must be at least 8 characters'

    return None


@app.route('/user/', methods=['GET'])
def get_users():
    users = User.query.all()
    all_users = []
    for u in users:
        all_users.append({
            'id': u.id,
            'username': u.username,
            'email': u.email
        })
    return jsonify(all_users)


@app.route('/user/<int:user_id>/', methods=['GET'])
def get_user(user_id):
    user = db.session.get(User, user_id)

    if user is None:
        return jsonify({'message': 'user not found'}), 404

    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email
    })


@app.route('/user/', methods=['POST'])
def create_user():

    data = request.get_json()

    error = validate_user_data(data)
    if error:
        return jsonify({'message': error}), 400

    new_user = User(
        username=data['username'],
        email=data['email'],
        password=data['password']
    )

    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Database error', 'details': str(e)}), 500

    return jsonify({
        'id': new_user.id,
        'username': new_user.username,
        'email': new_user.email
    }), 201


@app.route('/user/<int:user_id>/', methods=['PUT'])
def put_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({'message': 'user not found'}), 404

    data = request.get_json()

    error = validate_user_data(data)
    if error:
        return jsonify({'message': error}), 400

    user.username = data['username']
    user.email = data['email']
    user.password = data['password']

    db.session.commit()

    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email
    }), 200


@app.route('/user/<int:user_id>/', methods=['PATCH'])
def update_user(user_id):
    user = db.session.get(User, user_id)

    if user is None:
        return jsonify({'message': 'user not found'}), 404

    data = request.get_json()

    error = validate_user_data(data, partial=True)
    if error:
        return jsonify({'message': error}), 400

    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    if 'password' in data:
        user.password = data['password']

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Database error', 'details': str(e)}), 500

    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email
    }), 200


@app.route('/user/<int:user_id>/', methods=['DELETE'])
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({'message': 'user not found'}), 404

    try:
        db.session.delete(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Database error', 'details': str(e)}), 500

    return jsonify({'message': 'user deleted'})


if __name__ == '__main__':
    app.run(debug=True)
