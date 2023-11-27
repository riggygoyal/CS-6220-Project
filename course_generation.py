import json
import random
import requests
from operator import itemgetter
import numpy as np
import pandas as pd

def time_to_minutes(str):
    return int(str[0:2]) * 60 + int(str[2:])

def generate_schedule(specialization, courses_taken, semesters_left):

    num_courses_required = 10

    # Pulling course requirement data
    with open('course_requirements.json') as f:
        course_requirements = json.load(f)

    # Pulling course data for next semester
    with open('cs_courses.json') as f:
        data = json.load(f)
        cs_courses = data['courses']
        caches = data['caches']
        
    num_courses_remaining = num_courses_required - len(courses_taken)
    num_courses_nextsem = num_courses_remaining // semesters_left

    specialization_course_pool = []

    time_conflicts = True

    while time_conflicts:
        # Create a pool of specialization courses remaining to choose from
        for requirements in course_requirements[specialization]:
            pick = requirements['Pick']
            requirements_set = set(requirements['Courses'])
            taken_requirements = courses_taken & requirements_set
            if len(taken_requirements) < pick:
                choose = pick - len(taken_requirements)
                requirements_set -= courses_taken

                specialization_course_pool += random.sample(list(requirements_set), k=choose)

        # Pick a random number of courses from the specialization course pool
        specialization_courses = random.sample(specialization_course_pool, k=random.randrange(num_courses_nextsem+1))
        specialization_courses = list(set(specialization_courses) & set(cs_courses.keys()))

        sections = {}
        # Randomly pick a section for each specialization course
        for specialization_course in specialization_courses:
            sections[specialization_course] = random.choice(list(cs_courses[specialization_course][1].items()))

        num_electives = num_courses_nextsem - len(specialization_courses)
        elective_pool = random.sample([k for k in cs_courses.keys() if k not in specialization_course_pool + list(courses_taken)], k=num_electives)

        # Fill out rest of the schedule with randomly selected electives
        for elective in elective_pool:
            sections[elective] = random.choice(list(cs_courses[elective][1].items()))
        
        # Calculate average time gap, earliest time, latest time, and detect time conflicts. Randomly generate another schedule if time conflcit present
        times = []
        total_time_gap = 0
        earliest_time = '23:45'
        latest_time = '0'
        for day in ['M', 'T', 'W', 'R', 'F']:
            time_intervals = []
            for data in sections.values():
                if day in data[1][1][0][1]:
                    start_time, end_time = caches['periods'][data[1][1][0][0]].split(' ')[0], caches['periods'][data[1][1][0][0]].split(' ')[2]
                    time_intervals.append([start_time, end_time])
            time_intervals = sorted(time_intervals, key=itemgetter(0))

            # Earliest/latest time
            if len(time_intervals) > 0:
                earliest_time = min(time_intervals[0][0], earliest_time)
                latest_time = max(time_intervals[-1][1], latest_time)

            # Calculate average time gap, break if time conflict detected
            for i in range(0, len(time_intervals) - 1):
                time_gap = time_to_minutes(time_intervals[i + 1][0]) - time_to_minutes(time_intervals[i][1])
                time_conflicts = time_gap < 0
                if time_conflicts:
                    break
                total_time_gap += time_gap
            else:
                times.append(time_intervals)
                average_time_gap = total_time_gap / len(sections)
                continue
            break
        
    # Calculate average GPA for schedule by calling API
    schedule_gpa = []
    for k in sections.keys():
        prof_name = sections[k][1][1][0][4][0].replace(' (P)', '')
        url = 'https://c4citk6s9k.execute-api.us-east-1.amazonaws.com/test/data/course?courseID=' + k
        gpa_raw = requests.get(url=url).json()['raw']

        course_gpa = []
        course_gpa_for_prof = []
        for entry in gpa_raw:
            prof_name_from_raw = entry['instructor_name'].split(', ')[1].split(' ')[0] + ' ' + entry['instructor_name'].split(', ')[0]
            if prof_name_from_raw == prof_name:
                course_gpa_for_prof.append(entry['GPA'])
            course_gpa.append(entry['GPA'])
        
        average_gpa = 0.0
        if len(course_gpa_for_prof) > 0:
            average_gpa = np.mean(np.array(course_gpa_for_prof))
        else:
            average_gpa = np.mean(np.array(course_gpa))
        if average_gpa > 0:
            schedule_gpa.append(average_gpa)
    
    average_schedule_gpa = np.mean(np.array(schedule_gpa))

    # print("Average GPA: " + str(np.mean(np.array(schedule_gpa))))
    # print(times)
    # print('Earliest time: ' + earliest_time)
    # print('Latest time: ' + latest_time)
    # print('Average time gap: ' + str(average_time_gap))

    # print(sections)

    return sections, average_schedule_gpa, average_time_gap, earliest_time, latest_time

sections = []
average_schedule_gpas = []
average_time_gaps = []
earliest_times_min = []
latest_times_min = []
earliest_times = []
latest_times = []

specialization = 'HCC'
courses_taken = set(['CSE 6451', 'CSE 6601'])
semesters_left = 2

for i in range(10):
    sections_i, average_schedule_gpas_i, average_time_gaps_i, earliest_times_i, latest_times_i = generate_schedule(specialization, courses_taken, semesters_left)
    sections.append(sections_i)
    average_schedule_gpas.append(average_schedule_gpas_i)
    average_time_gaps.append(average_time_gaps_i)
    earliest_times.append(earliest_times_i)
    latest_times.append(latest_times_i)
    earliest_times_min.append(time_to_minutes(earliest_times_i))
    latest_times_min.append(time_to_minutes(latest_times_i))


schedules = {
    'Sections': sections, 
    'Average GPA': average_schedule_gpas, 
    'Average Time Gap': average_time_gaps,
    'Earliest Time': earliest_times,
    'Latest Time': latest_times,
    'Earliest Time (Minutes)': earliest_times_min, 
    'Latest Time (Minutes)': latest_times_min
    }

pd.DataFrame(schedules).to_csv('schedules.csv')
