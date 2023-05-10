import itertools
from collections import deque
import copy
import random
import multiprocessing


def find_min_spacing_no_wrap(_list):
    _l = len(_list)
    min_spacing = _l
    for _i in range(_l):
        for j in range(_l):
            if j >= min_spacing:
                break
            k = (_i + j) % _l
            if k == _i:
                continue
            if _i + j >= _l:
                break
            if _list[_i][0] in _list[k]:
                min_spacing = j
                break
            if _list[_i][1] in _list[k]:
                min_spacing = j
                break
    return min_spacing


def find_min_spacing(_list):
    _l = len(_list)
    min_spacing = _l
    for _i in range(_l):
        for j in range(_l):
            if j >= min_spacing:
                break
            k = (_i + j) % _l
            if k == _i:
                continue
            if _list[_i][0] in _list[k]:
                min_spacing = j
                break
            if _list[_i][1] in _list[k]:
                min_spacing = j
                break
    return min_spacing


class JobData:
    toAdd = deque()
    added = deque()

    def __init__(self, _to_add, _added):
        self.toAdd = copy.deepcopy(_to_add)
        self.added = copy.deepcopy(_added)


def workload(_job_data, _record):
    if len(_job_data.toAdd) == 0:
        min_spacing = find_min_spacing(_job_data.added)
        return "completed", min_spacing, copy.deepcopy(_job_data.added)
    new_jobs = deque()
    _toAdd = copy.deepcopy(_job_data.toAdd)
    while len(_toAdd) > 0:
        new_to_add = copy.deepcopy(_job_data.toAdd)
        _added = copy.deepcopy(_job_data.added)
        _combo = _toAdd.pop()
        new_to_add.remove(_combo)
        _added.append(_combo)
        min_spacing = find_min_spacing_no_wrap(_added)
        if min_spacing > _record[0]:
            new_jobs.append(JobData(new_to_add, _added))
    return "new jobs", new_jobs


def worker(_work_queue, _done_queue, _worker_index):
    while True:
        _job = _work_queue.get(True)
        _result = (_worker_index, workload(_job[0], _job[1]))
        _done_queue.put(_result, False)


if __name__ == "__main__":
    colors = ["White", "Red", "Orange", "Yellow", "Fern Green", "Green", "Sea Green", "Cyan", "Blue", "Violet", "Pink"]
    exclude = [('White', 'Yellow'),
               ('Red', 'Orange'),
               ('Red', 'Yellow'),
               ('Red', 'Fern Green'),
               ('Red', 'Green'),
               ('Red', 'Pink'),
               ('Orange', 'Yellow'),
               ('Fern Green', 'Green'),
               ('Fern Green', 'Sea Green'),
               ('Green', 'Sea Green'),
               ('Green', 'Cyan'),
               ('Sea Green', 'Cyan'),
               ('Cyan', 'Blue'),
               ('Blue', 'Violet'),
               ('Violet', 'Pink')]  # ("Col 1", "Col 2")
    listOfCombinations = list(itertools.combinations(colors, r=2))
    combinations = deque()
    for combo in listOfCombinations:
        combinations.append(combo)
    for combo in exclude:
        if combo in combinations:
            combinations.remove(combo)

    for combo in combinations:
        print(combo)

    assert find_min_spacing([["White", "Red"], ["Orange", "Yellow"], ["Blue", "White"]]) == 1
    assert find_min_spacing_no_wrap([["White", "Red"], ["Orange", "Yellow"], ["Blue", "White"]]) == 2

    multiprocessing.freeze_support()
    record = [1]
    jobStack = deque()
    toAdd = deque()
    added = deque()
    for combo in combinations:
        if combo == combinations[0]:
            continue
        toAdd.append(combo)
    added.append(combinations[0])
    jobStack.append(JobData(toAdd, added))

    workerCount = 128
    doneQueue = multiprocessing.Queue(workerCount)
    workQueue = multiprocessing.Queue(workerCount)
    instances = []
    for i in range(workerCount):
        instance = multiprocessing.Process(target=worker, args=(workQueue, doneQueue, i))
        instance.daemon = True
        instance.start()
        instances.append(instance)

    while True:
        innerEmpty = True
        numberOfActiveJobs = 0
        for i in range(workerCount):
            if len(jobStack) == 0:
                break
            innerEmpty = False
            numberOfActiveJobs += 1
            job = jobStack.pop()
            workQueue.put([job, record])
        if innerEmpty:
            break
        for i in range(numberOfActiveJobs):
            result = doneQueue.get(True)
            if result[1][0] == "completed":
                if result[1][1] > record[0]:
                    record[0] = result[1][1]
                    print("")
                    print("")
                    print("Found Solution with " + str(record[0]) + " min Spacing:")
                    print("")
                    for combo in result[1][2]:
                        if bool(random.getrandbits(1)):
                            print(str(combo[0]) + " - " + str(combo[1]))
                        else:
                            print(str(combo[1]) + " - " + str(combo[0]))
                    print("")
                    print(str(record[0]) + " min Spacing")
            if result[1][0] == "new jobs":
                for newJob in result[1][1]:
                    jobStack.append(JobData(newJob.toAdd, newJob.added))

    print("")
    print("done")
