import json
import datetime as dt
from scipy.special import gammaincc, gamma
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sqlite3
import sys

# Elo constants
n = 400
K = 10

wblist = json.load(open('whiteblacklist.json'))
whitelist = wblist['whitelist']
blacklist = wblist['blacklist']


def load_json(handle):
    data = json.load(handle)
    return {
        'data': [{
            'name': item['name'],
            'time': sum([a*b for a, b in zip([60, 1], map(int, item['time'].split(':')))])
        } for item in data['data'] if item['time'] != '--'],
        'date': data['date']
    }


def score_gamma(x, k, theta):
    return gammaincc(k, x / theta)


def forward_fill(arr):
    ret = arr[:1]
    prev = arr[0]
    for val in arr[1:]:
        if val is None:
            ret.append(prev)
        else:
            ret.append(val)
            prev = val
    return ret


def process_times(cur):
    cur.execute('SELECT DISTINCT date FROM times ORDER BY date ASC')
    for date in cur.fetchall():
        cur.execute('SELECT name, time FROM times WHERE date=?', date)
        today_data = dict(cur.fetchall())
        players = list(today_data.keys())
        times = list(today_data.values())
        avg = np.mean(times)
        avglog = np.mean(np.log(times))
        s = np.log(avg) - avglog
        k = (3 - s + np.sqrt((s - 3)**2 + 24 * s)) / (12 * s)
        theta = avg / k

        cur.execute('''SELECT name, rating
                       FROM ratings
                       WHERE name IN ({0})
                       AND name NOT IN ({1})
                       GROUP BY name
                       ORDER BY date DESC'''.format(', '.join('?' for _ in players),
                                                    ', '.join('?' for _ in blacklist)),
                    players + blacklist)
        player_data = dict(cur.fetchall())
        for player in players:
            if player not in player_data.keys():
                player_data.update({player: 1200})

        average_rating = np.mean(list(player_data.values()))
        for name, rating in player_data.items():
            time = today_data[name]
            rating_diff = (average_rating - rating) / n
            expected_score = 1 / (1 + 10 ** rating_diff)
            actual_score = score_gamma(time, k, theta)
            new_rating = rating + K * (actual_score - expected_score)
            cur.execute('INSERT INTO ratings VALUES (?, ?, ?)',
                        date + (name, new_rating))
            print(date[0], " - ", name, ": ", new_rating)


# Setup sqlite
conn = sqlite3.connect(":memory:")
c = conn.cursor()
c.execute('''CREATE TABLE times
             (date text, name text, time int)''')
c.execute('''CREATE TABLE ratings
             (date text, name text, rating real)''')

for filename in sys.argv[1:]:
    with open(filename) as h:
        new_json = load_json(h)
        results = [(new_json['date'], d['name'], d['time'])
                   for d in new_json['data']]
        c.executemany('INSERT INTO times VALUES (?,?,?)', results)

process_times(c)

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator())

c.execute('SELECT MIN(date), MAX(date) FROM times')
start, stop = map(np.datetime64, c.fetchone())
dates = [date.astype(dt.datetime) for date in np.linspace(
    start.astype('f8'), stop.astype('f8'), dtype='<M8[D]')]

c.execute('''SELECT DISTINCT name FROM ratings
             WHERE name IN ({0})'''.format(', '.join('?' for _ in whitelist)), whitelist)
for player in c.fetchall():
    c.execute('SELECT date, rating FROM ratings WHERE name=?', player)
    z = {dt.datetime.strptime(date, '%Y-%m-%d').date(): rating
         for date, rating in c.fetchall()}
    plt.plot(dates, forward_fill([z.get(date)
                                  for date in dates]), label=player[0])

plt.gcf().autofmt_xdate()
plt.legend(loc='upper left', fontsize='x-small')
plt.xlabel('Date')
plt.ylabel('Elo')
plt.title('Ratings over time')
plt.show()

conn.close()
