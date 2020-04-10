import sys
from tetpyclient import RestClient
import json
import pandas as pd
from tabulate import tabulate
import requests.packages.urllib3

requests.packages.urllib3.disable_warnings()

API_ENDPOINT="https://{Your cluster's ip}"

rc = RestClient(API_ENDPOINT,credentials_file='credentials.json', verify=False)

resp = rc.get('/applications')
app = resp.json()

a_list = []
b_list = []
for i in app:
    app_name = i['name']
    id = i['id']
    a_list.append(app_name)
    b_list.append(id)

app_list = list(enumerate(a_list, start=1))
id_list = list(enumerate(b_list, start=1))

print()
print('-' * 10, 'List of applications', '-' * 10)
print()

a_dict = {}
for a, b in app_list:
    a_dict[a] = b
    print(f'{a:2}', ":", b)

print()

id_dict = {}
for a, b in id_list:
    id_dict[a] = b

while True:
    x = input('Please enter the application you want to check by number： ')
    x = int(x)
    if x in a_dict:
        break

application_id = id_dict[x]

print()

while True:
    print('How long do you want to analyze the data? Please enter the year, month, day, and hour of the start.')
    print()
    SY = input('Year[YYYY]：')
    SY = str(SY)
    SM = input('Month[MM]：')
    SM = str(SM)
    SD = input('Day[DD]：')
    SD = str(SD)
    SH = input('Hour[HH]：')
    SH = str(SH)
    if (len(SY) == 4 and 2000 <= int(SY) <= 3000) and (len(SM) == 2 and 1 <= int(SM) <= 12) and (len(SD) == 2 and 1 <= int(SD) <= 31) and (len(SH) == 2 and 1 <= int(SH) <= 24):
        break
    else:
        print()
        print('Please enter the correct date and time')
        print()

print()

while True:
    print('Please enter the year, month, day, and hour of the end.')
    print()
    EY = input('Year[YYYY]：')
    EY = str(EY)
    EM = input('Month[MM]：')
    EM = str(EM)
    ED = input('Day[DD]：')
    ED = str(ED)
    EH = input('Hour[HH]：')
    EH = str(EH)
    if (len(EY) == 4 and 2000 <= int(EY) <= 3000) and (len(EM) == 2 and 1 <= int(EM) <= 12) and (len(ED) == 2 and 1 <= int(ED) <= 31) and (len(EH) == 2 and 1 <= int(EH) <= 24):
        break

category_dict = {1: "permitted", 2: "escaped", 3: "misdropped", 4: "rejected"}

print()
print('-' * 10, 'List of flow categories', '-' * 10)
print()

for k, v in category_dict.items():
    print(f'{k:2}', ":", v)

print()
while True:
    c = input('Please enter the category you want to check by number.[ 1 ~ 4 ]：')
    c = int(c)
    category = category_dict.get(c)
    if c in category_dict.keys():
        break

print()

req_payload = {
    "t0": "{}-{}-{}T{}:00:00+0000".format(SY, SM, SD, SH),
    "t1": "{}-{}-{}T{}:00:00+0000".format(EY, EM, ED, EH),
    "limit": 10,
    "filter": {
                "type": "eq",
                "field": "category",
                "value": category
            },
    }

resp = rc.post('/live_analysis/%s' % application_id, json_body=json.dumps(req_payload))
ana = resp.json()

pd.set_option('display.max_columns', 1000)
pd.set_option('display.max_rows', 2000)
pd.set_option('display.max_colwidth', 2000)
pd.options.display.width=None

if len(ana) == 0:
    print('There are no flows that match the conditions you entered.')
    print()
    sys.exit()

offset = ana.get('Offset')

Results = ana['Results']

num = len(Results)

esc_list = []
x = 0

while True:
    result = Results[x]
    esc_dict = {}
    esc_dict['timestamp'] = result['timestamp']
    esc_dict['src_address'] = result['src_address']
    esc_dict['src_port'] = result['src_port']
    esc_dict['dst_address'] = result['dst_address']
    esc_dict['dst_port'] = result['dst_port']
    esc_dict['proto'] = result['proto']
    esc_list.append(esc_dict)
    x += 1
    if x == num:
        break

df = pd.read_json(json.dumps(esc_list))
df.index = df.index + 1
print(tabulate(df, headers='keys'))
next_index_num = 11

print()
input("Press any key to continue")

while True:
    if offset == '':
        sys.exit()
    else:
        req_payload = {
            "t0": "{}-{}-{}T{}:00:00+0000".format(SY, SM, SD, SH),
            "t1": "{}-{}-{}T{}:00:00+0000".format(EY, EM, ED, EH),
            "limit": 10,
            "filter": {
                "type": "eq",
                "field": "category",
                "value": category
            },
            "offset": offset
        }
        resp = rc.post('/live_analysis/%s' % application_id, json_body=json.dumps(req_payload))
        ana = resp.json()
        offset = ana.get('Offset')
        Results = ana['Results']
        num = len(Results)
        esc_list = []
        x = 0
        print()
        while True:
            result = Results[x]
            esc_dict = {}
            esc_dict['timestamp'] = result['timestamp']
            esc_dict['src_address'] = result['src_address']
            esc_dict['src_port'] = result['src_port']
            esc_dict['dst_address'] = result['dst_address']
            esc_dict['dst_port'] = result['dst_port']
            esc_dict['proto'] = result['proto']
            esc_list.append(esc_dict)
            x += 1
            if x == num:
                break
        df = pd.read_json(json.dumps(esc_list))
        df.index = df.index + next_index_num
        next_index_num += 10
        print(tabulate(df, headers='keys'))
        print()
        if offset == '':
            sys.exit()
        else:
            input("Press any key to continue")



