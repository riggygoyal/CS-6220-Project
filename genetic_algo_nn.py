import json
import random
import requests
import time
from operator import itemgetter
import numpy as np
import pandas as pd
from tensorflow.keras.models import model_from_json

num_iter = 10

# Load neural network
# Load the architecture from the JSON file
with open('my_model_architecture.json', 'r') as json_file:
    loaded_model_json = json_file.read()

# Reconstruct the model from the JSON file
model = model_from_json(loaded_model_json)

# Load the weights into the reconstructed model
model.load_weights('my_model_weights.h5')

def time_to_minutes(str):
    return int(str[0:2]) * 60 + int(str[2:])


def generate_sched(course_requirements, courses_taken, num_courses_nextsem, specialization, cs_courses):
    for requirements in course_requirements[specialization]:
        pick = requirements['Pick']
        requirements_set = set(requirements['Courses'])
        taken_requirements = courses_taken & requirements_set
    specialization_course_pool = []
    if len(taken_requirements) < pick:
        choose = pick - len(taken_requirements)
        requirements_set -= courses_taken
        specialization_course_pool += random.sample(
            list(requirements_set), k=choose)

    specialization_courses = random.sample(specialization_course_pool, k=random.randrange(
        min(len(specialization_course_pool), num_courses_nextsem)))
    specialization_courses = list(
        set(specialization_courses) & set(cs_courses.keys()))

    sections = {}
    # Randomly pick a section for each specialization course
    for specialization_course in specialization_courses:
        sections[specialization_course] = random.choice(
            list(cs_courses[specialization_course][1].items()))

    num_electives = num_courses_nextsem - len(specialization_courses)
    elective_pool = random.sample([k for k in cs_courses.keys(
    ) if k not in specialization_course_pool + list(courses_taken)], k=num_electives)

    # Fill out rest of the schedule with randomly selected electives
    for elective in elective_pool:
        sections[elective] = random.choice(
            list(cs_courses[elective][1].items()))
    return sections, list(set(specialization_course_pool) & set(cs_courses.keys()))


def check_conflict(sections, caches):  # dummy function to be updated for time conflicts
    time_conflicts = False
    times = []
    total_time_gap = 0
    earliest_time = '23:45'
    latest_time = '0'
    for day in ['M', 'T', 'W', 'R', 'F']:
        sections_on_current_day = []
        time_intervals = []
        for data in sections.values():
            if day in data[1][1][0][1]:
                sections_on_current_day.append(data)
                start_time, end_time = caches['periods'][data[1][1][0][0]].split(
                    ' ')[0], caches['periods'][data[1][1][0][0]].split(' ')[2]
                time_intervals.append([start_time, end_time])
        time_intervals = sorted(time_intervals, key=itemgetter(0))

        # Earliest/latest time
        if len(time_intervals) > 0:
            earliest_time = min(time_intervals[0][0], earliest_time)
            latest_time = max(time_intervals[-1][1], latest_time)

        # Calculate average time gap, break if time conflict detected
        for i in range(0, len(time_intervals) - 1):
            time_gap = time_to_minutes(
                time_intervals[i + 1][0]) - time_to_minutes(time_intervals[i][1])
            time_conflicts = time_gap < 0
            if time_conflicts:
                break
            total_time_gap += time_gap
        else:
            times.append(time_intervals)
            average_time_gap = total_time_gap / len(sections)
            continue
        break
    return time_conflicts, total_time_gap, earliest_time, latest_time


def get_gpas(sections):
    schedule_gpa = 0
    count = 0
    for k in sections.keys():
        # print(sections[k])
        if len(sections[k][1][1][0][4]) > 0:
            prof_name = sections[k][1][1][0][4][0].replace(' (P)', '')
        else:
            prof_name = ''
        url = 'https://c4citk6s9k.execute-api.us-east-1.amazonaws.com/test/data/course?courseID=' + k
        try:
            gpa_raw = requests.get(url=url).json()['raw']
        except:
            print(k)
            continue

        course_gpa = []
        course_gpa_for_prof = []
        for entry in gpa_raw:
            prof_name_from_raw = entry['instructor_name'].split(', ')[1].split(
                ' ')[0] + ' ' + entry['instructor_name'].split(', ')[0]
            if prof_name_from_raw == prof_name:
                course_gpa_for_prof.append(entry['GPA'])
            course_gpa.append(entry['GPA'])

        average_gpa = 0.0
        if len(course_gpa_for_prof) > 0:
            average_gpa = np.mean(np.array(course_gpa_for_prof))
        elif len(course_gpa) > 0:
            average_gpa = np.mean(np.array(course_gpa).mean())
        # print(k + ' ' + str(average_gpa))
        if average_gpa > 0:
            schedule_gpa += average_gpa
            count += 1
    if count == 0:
        return 0
    return schedule_gpa / count, len(sections) - count


def add_mutation(sections, cs_courses, courses_taken, specialization_course_pool):
    rand = random.randint(0, 2)
    if (rand == 0) and specialization_course_pool != []:
        specialization_course = random.sample(specialization_course_pool,k=1)
        specialization_course = list(set(specialization_course) & set(cs_courses.keys()))
        sections[specialization_course[0]] = random.choice(list(cs_courses[specialization_course[0]][1].items()))
    else:
      elective = random.sample([k for k in cs_courses.keys() if k not in specialization_course_pool + list(courses_taken)], k=1)
      sections[elective[0]] = random.choice(list(cs_courses[elective[0]][1].items()))
    return sections


def fitness_nn(sections, caches):
    data_f = []
    data = []
    gpas = get_gpas(sections)
    data.append(gpas[0])  # Average GPA
    data.append(gpas[1])  # Courses w/ no GPA
    time_conflicts, total_gap, earliest, latest = check_conflict(sections, caches)
    if time_conflicts:
        return 0
    data.append(total_gap)  # Total Time Gap
    data.append(time_to_minutes(earliest))  # Earliest Time (Minutes)
    data.append(time_to_minutes(latest))  # Latest Time (Minutes)
    data_f.append(data)
    dataf = pd.DataFrame(data_f, columns=['Average GPA', 'Courses w/ no GPA',
                         'Total Time Gap', 'Earliest Time (Minutes)', 'Latest Time (Minutes)'])
    dataf = dataf.astype(float)
    return model.predict(dataf)

# genetic algo vanilla

def genetic_algorithm(course_requirements, courses_taken, num_courses_nextsem, specialization, cs_courses, caches, population, mutation_rate):
    subjects = []
    for i in range(population):
        val, specialization_course_pool = generate_sched(course_requirements, courses_taken,
                        num_courses_nextsem, specialization, cs_courses)
        subjects.append(val)
    seconds = time.time()
    maxfitness = 0
    # limiting the running time, adding a threshold fitness for termination
    while ((time.time()-seconds < 44.5) and not (maxfitness >= 10)):
        new_population = []
        fit = []
        for i in subjects:
            temp_maxfitness = fitness_nn(i, caches)
            fit.append(temp_maxfitness)
            if (temp_maxfitness > maxfitness):
                maxfitness = temp_maxfitness
        for i in range(len(subjects)):
            parent1 = random.choices(subjects, weights=fit)[0]
            # selecting 2 parents and performing crossover on them
            parent2 = random.choices(subjects, weights=fit)[0]
            c1 = random.randint(0, num_courses_nextsem)
            child = {}
            count = c1
            for j in parent1.keys():
                child[j] = parent1[j]
                count -= 1
                if (count == 0):
                    break
            count = num_courses_nextsem - c1
            for j in parent2.keys():
                child[j] = parent2[j]
                count -= 1
                if (count == 0):
                    break
            for j in list(child.keys()):
                if (random.randint(1, 100) <= mutation_rate):  # for mutation
                    child.pop(j)
                    child = add_mutation(
                        child, cs_courses, courses_taken, specialization_course_pool)
            # to check fitness of child
            temp_maxfitness = fitness_nn(child, caches)
            if (temp_maxfitness > maxfitness):
                maxfitness = temp_maxfitness
            new_population.append(child)
        subjects = new_population
    fit = []
    for i in subjects:
        temp_maxfitness = fitness_nn(i, caches)
        fit.append(temp_maxfitness)
        if (temp_maxfitness > maxfitness):
            maxfitness = temp_maxfitness
    return maxfitness, subjects

# genetic algo elitism

def genetic_algorithm_elit(course_requirements, courses_taken, num_courses_nextsem, specialization, cs_courses, caches, population, elitism_factor):
    subjects = []
    for i in range(population):
        val, specialization_course_pool = generate_sched(course_requirements, courses_taken,
                        num_courses_nextsem, specialization, cs_courses)
        subjects.append(val)
    seconds = time.time()
    maxfitness = 0
    # limiting the running time, adding a threshold fitness for termination
    while ((time.time()-seconds < 44.5) and not (maxfitness >= .7)):
        new_population = []
        fit = []
        combined = []
        for i in subjects:
            temp_maxfitness = fitness_nn(i, caches)
            fit.append(temp_maxfitness)
            if (temp_maxfitness > maxfitness):
                maxfitness = temp_maxfitness
        for i in range(len(subjects)):
            combined.append([fit[i], subjects[i]])
        combined.sort(key=lambda x: x[0])
        for i in range(len(subjects)-elitism_factor, len(subjects)):
            # to take the most fit section of individuals directly to the next generation
            new_population.append(combined[i][1])
        for i in range(len(subjects)-elitism_factor):
            parent1 = random.choices(subjects, weights=fit)[0]
            # selecting 2 parents and performing crossover on them
            parent2 = random.choices(subjects, weights=fit)[0]
            c1 = random.randint(0, num_courses_nextsem)
            child = {}
            count = c1
            for j in parent1.keys():
                child[j] = parent1[j]
                count -= 1
                if (count == 0):
                    break
            count = num_courses_nextsem - c1
            for j in parent2.keys():
                child[j] = parent2[j]
                count -= 1
                if (count == 0):
                    break
            for j in list(child.keys()):
                if (random.randint(1, 100) == 1):  # for mutation
                    child.pop(j)
                    child = add_mutation(
                        child, cs_courses, courses_taken, specialization_course_pool)
            # to check fitness of child
            temp_maxfitness = fitness_nn(child, caches)
            if (temp_maxfitness > maxfitness):
                maxfitness = temp_maxfitness
            new_population.append(child)
        subjects = new_population
    return maxfitness, subjects

# genetic algo 4 parents

def genetic_algorithm_extra_parents(course_requirements, courses_taken, num_courses_nextsem, specialization, cs_courses, caches, population):
    subjects = []
    for i in range(population):
        val, specialization_course_pool = generate_sched(course_requirements, courses_taken,
                        num_courses_nextsem, specialization, cs_courses)
        subjects.append(val)
    seconds = time.time()
    maxfitness = 0
    # limiting the running time, adding a threshold fitness for termination
    while ((time.time()-seconds < 44.5) and not (maxfitness >= 10)):
        new_population = []
        fit = []
        for i in subjects:
            temp_maxfitness = fitness_nn(i, caches)
            fit.append(temp_maxfitness)
            if (temp_maxfitness > maxfitness):
                maxfitness = temp_maxfitness
        for i in range(len(subjects)):
            parent1 = random.choices(subjects, weights=fit)[0]
            parent2 = random.choices(subjects, weights=fit)[0]
            parent3 = random.choices(subjects, weights=fit)[0]
            # selecting 4 parents and performing crossover on them
            parent4 = random.choices(subjects, weights=fit)[0]
            c1 = random.randint(0, num_courses_nextsem)
            c2 = random.randint(0, c1)
            c3 = random.randint(0, c2)
            child = {}
            count = c3
            for j in parent1.keys():
                child[j] = parent1[j]
                count -= 1
                if (count == 0):
                    break
            count = c2 - c3
            for j in parent2.keys():
                child[j] = parent2[j]
                count -= 1
                if (count == 0):
                    break
            count = c1 - c2
            for j in parent3.keys():
                child[j] = parent3[j]
                count -= 1
                if (count == 0):
                    break
            count = num_courses_nextsem - c1
            for j in parent4.keys():
                child[j] = parent4[j]
                count -= 1
                if (count == 0):
                    break
            for j in list(child.keys()):
                if (random.randint(1, 100) == 1):  # for mutation
                    child.pop(j)
                    child = add_mutation(
                        child, cs_courses, courses_taken, specialization_course_pool)
            # to check fitness of child
            temp_maxfitness = fitness_nn(child, caches)
            if (temp_maxfitness > maxfitness):
                maxfitness = temp_maxfitness
            new_population.append(child)
        subjects = new_population
    fit = []
    for i in subjects:
        temp_maxfitness = fitness_nn(i, caches)
        fit.append(temp_maxfitness)
        if (temp_maxfitness > maxfitness):
            maxfitness = temp_maxfitness
    return maxfitness, subjects


def main():
    # TODO Insert inputs as needed
    specialization = 'HCC'
    courses_taken = set(['CSE 6451', 'CSE 6601'])
    semesters_left = 2
    num_courses_required = 10

    with open('course_requirements.json') as f:
        course_requirements = json.load(f)

    with open('cs_courses.json') as f:
        data = json.load(f)
        cs_courses = data['courses']
        caches = data['caches']

    num_courses_remaining = num_courses_required - len(courses_taken)
    num_courses_nextsem = num_courses_remaining // semesters_left

    # Genetic algorithm (vanilla)
    _, schedules = genetic_algorithm(course_requirements, courses_taken,
          num_courses_nextsem, specialization, cs_courses, caches, 30, 3)
    
    # Uncomment to use genetic algorithm with elitism
    # _, schedules = genetic_algorithm_elit(course_requirements, courses_taken,
    #       num_courses_nextsem, specialization, cs_courses, caches, 30, 3)
    
    # Uncomment to use genetic algorithm with extra parents
    # _, schedules = genetic_algorithm_extra_parents(course_requirements, courses_taken,
    #       num_courses_nextsem, specialization, cs_courses, caches, 30)
    
    best_schedule = schedules[0]
    max_fitness = 0
    for schedule in schedules:
        fitness = fitness_nn(schedule, caches)
        if fitness > max_fitness:
            best_schedule = schedule
            max_fitness = fitness
    
    print(best_schedule)


main()
