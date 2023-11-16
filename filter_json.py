import json 

with open('202402.json') as f:
    data = json.load(f)
    courses = data['courses']

# Filters for grad CS/CSE courses
cs_courses = {k: v for k, v in courses.items() if 
           k.startswith('CS 6') or
           k.startswith('CS 7') or 
           k.startswith('CS 8') or
           k.startswith('CSE 6') or
           k.startswith('CSE 7') or
           k.startswith('CSE 8')
           }

# Filters only for GT-Atlanta campus sections (no online, study abroad, etc.)
for course, course_data in cs_courses.items():
    course_data[1] = {section: section_data for section, section_data in course_data[1].items() if section_data[-3] == 0}

# Filters out courses if no GT-Atlanta campus sections don't exist
cs_courses = {k: v for k, v in cs_courses.items() if len(v[1]) > 0}

data['courses'] = cs_courses

with open('cs_courses.json', 'w') as f:
    json.dump(data, f)
