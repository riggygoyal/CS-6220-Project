# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from genetic_algo_nn import genetic_algorithm

app = Flask(__name__)
CORS(app)


@app.route('/')
def home():
    return "Welcome to the Course Schedule Generator!"


@app.route('/generate_schedule', methods=['POST'])
def generate_schedule():
    data = request.json
    print("Received POST request with data: ", data)

    specialization = data['specialization']
    coursesTaken = data['coursesTaken']
    semestersLeft = data['semestersLeft']
    numCoursesRequired = data['numCoursesRequired']

    with open('course_requirements.json') as f:
        course_requirements = json.load(f)

    with open('cs_courses.json') as f:
        data = json.load(f)
        cs_courses = data['courses']
        caches = data['caches']

    specialization_abbr = {
        "Computational Perception and Robotics": "CPR",
        "Computer Graphics": "CG",
        "Computing Systems": "CS",
        "High Performance Computing": "HPC",
        "Human Centered Computing": "HCC",
        "Human-Computer Interaction": "HCI",
        "Interactive Intelligence": "II",
        "Machine Learning": "ML",
        "Modeling and Simulation": "MS",
        "Scientific Computing": "SC",
        "Social Computing": "SOC",
        "Visual Analytics": "VA",
    }

    specialization_abbreviated = specialization_abbr[specialization]

    num_courses_remaining = int(numCoursesRequired) - len(coursesTaken)
    num_courses_nextsem = num_courses_remaining // int(semestersLeft)

    if (specialization_abbreviated != ""):
        fitness, subjects = genetic_algorithm(course_requirements, set(coursesTaken),
                                              num_courses_nextsem, specialization_abbreviated, cs_courses, caches, 30, 3)

    print(subjects)

    schedule_data = {
        "Best Schedule on given input": [
            {"CSE 6742": ["A", "32416", ["5", "W"],
                          "Cherry Emerson 320", 25, "Mariel Borowitz (P)"]},
            {"CS 6999": ["K13", "32647", ["2", "TBA"], 1, "Neha Kumar (P)"]},
            {"CS 6457": ["A", ["24107"], ["3", "MW"]]},
            {"CS 7455": ["A", ["29357", ["1"]]]}
        ]
    }

    return jsonify(schedule_data)


if __name__ == '__main__':
    app.run(debug=True)
