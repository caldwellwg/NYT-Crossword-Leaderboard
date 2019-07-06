import json
import sys

file = open(sys.argv[1])
data = json.load(file)

print([{
        'name': item['name'],
        'time': sum([a*b for a,b in zip([60,1], map(int, item['time'].split(':')))]) if item['time'] != '--' else -1
    } for item in data])
