import requests
import json
import time
from datetime import date

OWNER = 'glass-bead-labs'
REPO = 'sensor-group'


parameters = {'state': 'all', 'per_page': 100}

# request is a list filled with dictionaries that represent each issue
# listed in the order seen on github repo
request = requests.get('https://api.github.com/repos/' + OWNER +
                     '/' + REPO + '/issues', params=parameters).json()



def get_index(title):
    for i in range(len(request)):
        if title == get_title(i):
            return i
    

def get_issue_number(i):
    # Returns the number assigned to the issue when made. 
    return request[i]['number']

def get_state(i):
    # Returns whether the issue is open or closed. 
    return str(request[i]['state'])

def get_creator(i):
    # Returns who created the issue.
    return str(request[i]['user']['login'])

def get_title(i):
    return str(request[i]['title'])

def get_label(i):
    labels = []
    if request[i]['labels'] != []:
        for label in request[i]['labels']:
            labels.append(str(label['name']))
    return labels

def get_date_created(i):
    time = request[i]['created_at']
    if (time != None):
        time_stamp = str(time)
        month = int(time_stamp[5:7])
        day = int(time_stamp[8:10])
        return str(month) + '/' + str(day)

def get_date_closed(i):
    time = request[i]['closed_at']
    if (time != None):
        time_stamp = str(time)
        month = int(time_stamp[5:7])
        day = int(time_stamp[8:10])
        return str(month) + '/' + str(day)

def get_date_updated(i):
    time = request[i]['updated_at']
    if (time != None):
        time_stamp = str(time)
        month = int(time_stamp[5:7])
        day = int(time_stamp[8:10])
        return str(month) + '/' + str(day)


def get_num_comments(i):
    return int(request[i]['comments'])

# Date of the first issue created. 
startDate = get_date_created(len(request) - 1)

# Date of the most recent issue created. 
endDate = get_date_created(0)

def dates_of_issues():
    # Returns a list of all the dates issues were made from oldest to newest date. 
    dates = [get_date_created(0)]
    for i in range(1, len(request) - 1):
        if (get_date_created(i) not in dates):
            dates.append(get_date_created(i))
    return dates[::-1]


def comments_per_day():
    # Returns a list of the total number of per day an issue was made.
    num_comments = []
    comments = 0
    for k in range(len(dates_of_issues())):
        for i in range(len(request) - 1):
            if (get_date_created(i) == dates_of_issues()[k]):
                comments += get_num_comments(i)
        num_comments.append(comments)
        comments = 0
    return num_comments

def get_all_labels():
    labels = []
    for i in range(len(request)):
        for label in get_label(i):
            if label not in labels:
                labels.append(label)
    return labels


def get_issues_with_label(label):
    # Returns the titles of the issues with a specific label
    issues = []
    for i in range(len(request)):
        if label in get_label(i):
            issues.append(get_title(i))
    return issues

def get_issues_without_label():
    issues = []
    for i in range(len(request)):
        if get_label(i) == []:
            issues.append(get_title(i))
    return issues


# Today's date.
year = date.today().year
month = str(date.today().month)
day = str(date.today().day)


# Creates a list of all the data to be stored in a JSON file. 
data = []
for i in range(len(request)):
    data.append({'issue': i, 'creator': get_creator(i), 'title': get_title(i),
                'dateCreated': get_date_created(i), 'dateClosed': get_date_closed(i),
                'dateUpdated': get_date_updated(i), 'comments': get_num_comments(i),
                'labels': get_label(i)})


# Creates the JSON file. 
with open ('github_issues_' + month + '-' + day + '.json', 'w') as outfile:
    json.dump(data, outfile, indent=4)


# Another set of data to potentially analyze based on number of comments. 
data = []
data.append({'dates_of_issues': dates_of_issues() , 'num_comments': comments_per_day()})
for i in range(len(dates_of_issues())):
    data.append({dates_of_issues()[i]: comments_per_day()[i]})

# Creates another JSON file. 
with open ('mydata.json', 'w') as outfile:
    json.dump(data, outfile, indent=4)


# Another set of data to potentially analyze based on number of comments. 
data = {}
dataset = []

for label in get_all_labels():
    issues = []
    for issue in get_issues_with_label(label):
        index = get_index(issue)
        size = get_num_comments(index) + 1
        issues.append({"name": issue, "size": size})
    dataset.append({"name": label, "children": issues})

issues = []
for issue in get_issues_without_label():
    index = get_index(issue)
    size = get_num_comments(index) + 1
    issues.append({"name": issue, "size": size})

dataset.append({"name": "no label", "children": issues})
data["name"] = "issues"
data["children"] = dataset

# Creates another JSON file. 
with open ('mydata2.json', 'w') as outfile:
    json.dump(data, outfile, indent=4)
   
