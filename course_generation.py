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
        # print(specialization)
        # print(specialization_course_pool)
        specialization_courses = random.sample(specialization_course_pool, k=random.randrange(min(num_courses_nextsem, len(specialization_course_pool)) + 1))
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
                continue
            break
    
    # Calculate average GPA for schedule by calling API
    schedule_gpa = []
    num_courses_no_gpa = 0
    for k in sections.keys():
        # Checks if professor(s) are actually assigned to the selected section
        if len(sections[k][1][1][0][4]) > 0:
            prof_name = sections[k][1][1][0][4][0].replace(' (P)', '')
        else:
            prof_name = ''
        url = 'https://c4citk6s9k.execute-api.us-east-1.amazonaws.com/test/data/course?courseID=' + k
        try:
            gpa_raw = requests.get(url=url).json()['raw']
        except:
            print(k)

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
        elif len(course_gpa) > 0:
            average_gpa = np.mean(np.array(course_gpa))
        else:
            num_courses_no_gpa += 1

        if average_gpa > 0:
            schedule_gpa.append(average_gpa)
    
    average_schedule_gpa = np.mean(np.array(schedule_gpa))

    return sections, average_schedule_gpa, num_courses_no_gpa, total_time_gap, earliest_time, latest_time

# Generate a number of (default=10) random schedules using parameters
def specialization_schedules(specialization, courses_taken, semesters_left):

    sections = []
    average_schedule_gpas = []
    num_courses_no_gpa = []
    total_time_gaps = []
    earliest_times_min = []
    latest_times_min = []
    earliest_times = []
    latest_times = []

    for _ in range(10):
        sections_i, average_schedule_gpas_i, num_courses_no_gpa_i, total_time_gaps_i, earliest_times_i, latest_times_i = generate_schedule(specialization, courses_taken, semesters_left)
        sections.append(sections_i)
        average_schedule_gpas.append(average_schedule_gpas_i)
        num_courses_no_gpa.append(num_courses_no_gpa_i)
        total_time_gaps.append(total_time_gaps_i)
        earliest_times.append(earliest_times_i)
        latest_times.append(latest_times_i)
        earliest_times_min.append(time_to_minutes(earliest_times_i))
        latest_times_min.append(time_to_minutes(latest_times_i))
    
    return sections, average_schedule_gpas, num_courses_no_gpa, total_time_gaps, earliest_times_min, latest_times_min, earliest_times, latest_times

# Generate all schedules and store features
sections = []
average_schedule_gpas = []
num_courses_no_gpa = []
total_time_gaps = []
earliest_times_min = []
latest_times_min = []
earliest_times = []
latest_times = []

specializations = ['CPR', 'CG', 'CS', 'HPC', 'HCC', 'HCI', 'II', 'ML', 'MS', 'SC', 'SOC', 'VA']
courses_taken = [
    set(['CS 6505', 'CS 6475']),
    set(['CS 6476', 'CS 7496']),
    set(['CS 6200', 'CS 6210']),
    set(['CSE 6220', 'CS 6241']),
    set(['CSE 6451', 'CSE 6601']),
    set(['CSE 6456', 'CSE 6601', 'CS 7470', 'CS 6515', 'CS 6220', 'CS 8803']),
    set([]),
    set(['CS 7641', 'CS 6210']),
    set(['CS 6220', 'CS 7641', 'ISYE 6644', 'MATH 6640', 'CSE 6140', 'CS 7632']),
    set([]),
    set([]),
    set(['CS 6220', 'CS 6474'])
]
semesters_left = [
    2,
    2,
    2,
    2,
    2,
    1,
    3,
    2,
    1,
    3,
    3,
    2
]

for i in range(len(specializations)):

    specialization_section, specialization_average_schedule_gpas, specialization_courses_no_gpa, specialization_total_time_gaps, specialization_earliest_times_min, specialization_latest_times_min, specialization_earliest_times, specialization_latest_times = specialization_schedules(specializations[i], courses_taken[i], semesters_left[i])
    sections += specialization_section
    average_schedule_gpas += specialization_average_schedule_gpas
    num_courses_no_gpa += specialization_courses_no_gpa
    total_time_gaps += specialization_total_time_gaps
    earliest_times_min += specialization_earliest_times_min
    latest_times_min += specialization_latest_times_min
    earliest_times += specialization_earliest_times
    latest_times += specialization_latest_times


schedules = {
    'Sections': sections, 
    'Average GPA': average_schedule_gpas,
    'Courses w/ no GPA':  num_courses_no_gpa,
    'Total Time Gap': total_time_gaps,
    'Earliest Time': earliest_times,
    'Latest Time': latest_times,
    'Earliest Time (Minutes)': earliest_times_min, 
    'Latest Time (Minutes)': latest_times_min
    }

pd.DataFrame(schedules).to_csv('schedules.csv')
