from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

class Student:
    def __init__(self, name, roll_number):
        self.name = name
        self.roll_number = roll_number
        self.grades = {}

    def add_grade(self, subject, grade):
        self.grades[subject] = grade

    def to_dict(self):
        return {
            'name': self.name,
            'roll_number': self.roll_number,
            'grades': self.grades
        }

    @staticmethod
    def from_dict(data):
        student = Student(data['name'], data['roll_number'])
        student.grades = data.get('grades', {})
        return student

class StudentTracker:
    def __init__(self):
        self.students = []
        self.load_data()

    def add_student(self, name, roll_number):
        if not any(s.roll_number == roll_number for s in self.students):
            self.students.append(Student(name, roll_number))
            self.save_data()

    def get_student(self, roll_number):
        return next((s for s in self.students if s.roll_number == roll_number), None)

    def delete_student(self, roll_number):
        self.students = [s for s in self.students if s.roll_number != roll_number]
        self.save_data()

    def save_data(self):
        with open('students.json', 'w') as f:
            json.dump([s.to_dict() for s in self.students], f)

    def load_data(self):
        if os.path.exists('students.json'):
            with open('students.json', 'r') as f:
                data = json.load(f)
                self.students = [Student.from_dict(d) for d in data]

tracker = StudentTracker()

@app.route('/')
def index():
    return render_template('index.html', students=tracker.students)

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        roll_number = request.form['roll_number']
        tracker.add_student(name, roll_number)
        return redirect(url_for('index'))
    return render_template('add_student.html')

@app.route('/add_grade/<roll_number>', methods=['GET', 'POST'])
def add_grade(roll_number):
    student = tracker.get_student(roll_number)
    if not student:
        return "Student not found", 404

    if request.method == 'POST':
        subject = request.form['subject']
        grade = int(request.form['grade'])
        student.add_grade(subject, grade)
        tracker.save_data()
        return redirect(url_for('index'))

    return render_template('add_grade.html', student=student)

@app.route('/view_student/<roll_number>')
def view_student(roll_number):
    student = tracker.get_student(roll_number)
    if not student:
        return "Student not found", 404
    return render_template('view_student.html', student=student)

@app.route('/delete_student/<roll_number>', methods=['POST'])
def delete_student(roll_number):
    tracker.delete_student(roll_number)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
