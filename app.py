#Task 1
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:{your_password}@localhost/fitness_center_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

class MemberSchema(ma.Schema):
    name = fields.String(required = True)
    age = fields.String(required = True)
    id = fields.Integer()
    class meta:
        fields = ("name", "age", "id")

member_schema = MemberSchema()
members_schema = MemberSchema(many=True) 

class WorkoutSchema(ma.Schema):
    session_id = fields.Integer()
    member_id = fields.Integer(required = True)
    session_date = fields.String(required = True)
    session_time = fields.String()
    activity = fields.String()
    class meta:
        fields = ("session_id", "member_id", "session_date", "session_time", "activity")

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True) 

class Member(db.Model):
    __tablename__ = "Members"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable = False)
    age = db.Column(db.Integer)
    #Task 3, part 1
    sessions = db.relationship("WorkoutSession", backref = 'member')

class WorkoutSession(db.Model):
    __tablename__ = "WorkoutSessions"
    session_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey("Members.id"))
    session_date = db.Column(db.Date, nullable=False)
    session_time = db.Column(db.String(50), nullable=False)
    activity = db.Column(db.String(255))

@app.route("/")
def home():
    return "Welcome to the Fitness Center!"

#Task 2
@app.route("/members", methods=['GET'])
def get_members():
    members = Member.query.all()
    return members_schema.jsonify(members)
    
@app.route('/members', methods=['POST'])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_member = Member(name=member_data["name"], age=member_data["age"])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({"message": "New member added successfully"}), 201

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    member = Member.query.get_or_404(id)
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    member.name = member_data['name']
    member.age = member_data['age']
    db.session.commit()
    return jsonify({"message": "Customer details updated successfully"}), 200

@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "Member removed sucessfully"}), 200

#Task 3, part 2
@app.route("/workoutsessions", methods=['GET'])
def get_all_workouts():
    workouts = WorkoutSession.query.all()
    return workouts_schema.jsonify(workouts)

@app.route("/workoutsessions/<int:member_id>", methods=['GET'])
def get_member_workouts(member_id):
    Member.query.get_or_404(member_id)
    workouts = WorkoutSession.query.filter_by(member_id=member_id)
    return workouts_schema.jsonify(workouts)

@app.route("/workoutsessions", methods=['POST'])
def add_workout():
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400    

    new_workout = WorkoutSession(member_id=workout_data['member_id'], session_date=workout_data['session_date'], session_time=workout_data['session_time'])
    db.session.add(new_workout)
    db.session.commit()
    return jsonify({"message": "New workout added successfully"}), 201

@app.route("/workoutsessions/<int:session_id>", methods=['PUT'])
def update_workout(session_id):
    workout = WorkoutSession.query.get_or_404(session_id)
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    workout.member_id = workout_data['member_id']
    workout.session_date = workout_data['session_date']
    workout.session_time = workout_data['session_time']
    workout.activity = workout_data['activity']
    db.session.commit()
    return jsonify({"message": "Customer details updated successfully"}), 200

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debut=True)