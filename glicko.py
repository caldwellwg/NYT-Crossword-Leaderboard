import json
import sys

file = open(sys.argv[1])
data = json.load(file)

print({
        'data': [{
            'name': item['name'],
            'time': sum([a*b for a,b in zip([60,1], map(int, item['time'].split(':')))])
        } for item in data['data'] if item['time'] != '--'],
        'date': data['date']
    })
