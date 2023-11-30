import json 

with open('202402.json') as f:
    data = json.load(f)
    courses = data['courses']


# Filters for relevant grad CS/CSE courses and certain non-CS/CSE courses
non_cs_courses = [
    'INTA 6742',
    'ISYE 6644',
    'MATH 6640',
    'MATH 6643',
    'MATH 6644'
    ]

cs_courses_to_remove = [
    'CS 7999',
    'CSE 7999'
]

cs_courses = {k: v for k, v in courses.items() if 
           (k.startswith('CS 6') or
           k.startswith('CS 7') or 
           k == 'CS 8803' or
           k == 'CS 8903' or
           k.startswith('CSE 6') or
           k.startswith('CSE 7') or
           k == 'CSE 8803' or
           k == 'CSE 8903' or
           k in non_cs_courses) and 
           k not in cs_courses_to_remove
           }

# Filters only for GT-Atlanta campus sections (no online, study abroad, etc.)
for course, course_data in cs_courses.items():
    course_data[1] = {section: section_data for section, section_data in course_data[1].items() if section_data[-3] == 0}

# Filters out courses if no GT-Atlanta campus sections don't exist
cs_courses = {k: v for k, v in cs_courses.items() if len(v[1]) > 0}

data['courses'] = cs_courses

with open('cs_courses.json', 'w') as f:
    json.dump(data, f)
