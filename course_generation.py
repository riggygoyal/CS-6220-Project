import json
import random

specialization = 'HCC'
courses_taken = set(['CSE 6451', 'CSE 6601'])
semesters_left = 2
num_courses_required = 10

with open('course_requirements.json') as f:
    course_requirements = json.load(f)

with open('cs_courses.json') as f:
    cs_courses = json.load(f)['courses']
    
num_courses_remaining = num_courses_required - len(courses_taken)
num_courses_nextsem = num_courses_remaining // semesters_left

specialization_course_pool = []

time_conflicts = True

while time_conflicts:

    for requirements in course_requirements[specialization]:
        pick = requirements['Pick']
        requirements_set = set(requirements['Courses'])
        taken_requirements = courses_taken & requirements_set
        if len(taken_requirements) < pick:
            choose = pick - len(taken_requirements)
            requirements_set -= courses_taken

            specialization_course_pool += random.sample(list(requirements_set), k=choose)


    specialization_courses = random.sample(specialization_course_pool, k=random.randrange(num_courses_nextsem+1))
    specializations_courses = list(set(specialization_courses) & set(cs_courses.keys()))

    sections = {}
    for specialization_course in specialization_courses:
        sections[specialization_course] = random.choice(list(cs_courses[specialization_course][1].items()))

    num_electives = num_courses_nextsem - len(specialization_courses)
    elective_pool = random.sample([k for k in cs_courses.keys() if k not in specialization_course_pool + list(courses_taken)], k=num_electives)

    for elective in elective_pool:
        sections[elective] = random.choice(list(cs_courses[elective][1].items()))

    time_conflicts = len(set(data[1][1][0][0] for data in sections.values())) != num_courses_nextsem


print(sections)





