import json
import datetime as dt
from scipy.special import gamma, gammaincc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sqlite3
import sys

# Elo constants
n = 400
K = 10


def load_json(handle):
    data = json.load(handle)
    return {
        'data': [{
            'name': item['name'],
            'time': sum([a*b for a, b in zip([60, 1], map(int, item['time'].split(':')))])
        } for item in data['data'] if item['time'] != '--'],
        'date': data['date']
    }


def gamma_dist(x, k, theta):
    return x**(k - 1) * np.exp(-x / theta) / (gamma(k) * theta**k)


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


def process_times():
    c.execute('SELECT DISTINCT date FROM times')
    for date in c.fetchall():
        c.execute('SELECT name, time FROM times WHERE date=?', date)
        data = c.fetchall()
        players, times = map(list, zip(*data))
        avg = np.mean(times)
        avglog = np.mean(np.log(times))
        s = np.log(avg) - avglog
        k = (3 - s + np.sqrt((s - 3)**2 + 24 * s)) / (12 * s)
        theta = avg / k

        player_data = []
        for player in players:
            c.execute('''SELECT name, rating
                         FROM ratings
                         WHERE name=?
                         ORDER BY date DESC
                         LIMIT 1''', (player,))
            res = c.fetchone()
            if res is None:
                name = player
                rating = 1200
            else:
                name, rating = res
            player_data.append((name, rating))
        average_rating = np.mean([rating for _, rating in player_data])
        for name, rating in player_data:
            time = [t for nn, t in data if nn == name][0]
            rating_diff = (rating - average_rating) / n
            expected_score = 1 / (1 + 0.1**rating_diff)
            actual_score = score_gamma(time, k, theta)
            new_rating = rating + K * (actual_score - expected_score)
            c.execute('INSERT INTO ratings VALUES (?, ?, ?)',
                      date + (name, new_rating))


def plot_results(new_json):
    data = new_json['data']
    avg = data['time'].mean()
    avglog = data['time'].apply(np.log).mean()
    s = np.log(avg) - avglog
    k = (3 - s + np.sqrt((s - 3) ** 2 + 24 * s)) / (12 * s)
    theta = avg / k
    x = np.linspace(0, 300)
    plt.plot(x, gamma_dist(x, k, theta), c='blue')
    plt.scatter(data['time'], np.zeros(data['time'].count()), c='red')
    plt.show()


# Setup sqlite
conn = sqlite3.connect(":memory:")
c = conn.cursor()
c.execute('''CREATE TABLE times
             (date text, name text, time int)''')
c.execute('''CREATE TABLE ratings
             (date text, name text, rating int)''')

for filename in sys.argv[1:]:
    with open(filename) as h:
        new_json = load_json(h)
        results = [(new_json['date'], d['name'], d['time'])
                   for d in new_json['data']]
        c.executemany('INSERT INTO times VALUES (?,?,?)', results)

process_times()

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator())

c.execute('SELECT MIN(date), MAX(date) FROM times')
start, stop = map(np.datetime64, c.fetchone())
dates = [date.astype(dt.datetime) for date in np.linspace(
    start.astype('f8'), stop.astype('f8'), dtype='<M8[D]')]

c.execute('SELECT DISTINCT name FROM ratings')
for player in c.fetchall():
    c.execute('SELECT date, rating FROM ratings WHERE name=?', player)
    data = []
    z = dict([(dt.datetime.strptime(date, '%Y-%m-%d').date(), rating)
              for date, rating in c.fetchall()])
    plt.plot(dates, forward_fill([z.get(date)
                                  for date in dates]), label=player[0])

plt.gcf().autofmt_xdate()
plt.legend(loc='upper left', fontsize='x-small')
plt.xlabel('Date')
plt.ylabel('Elo')
plt.title('Ratings over time')
plt.show()

conn.close()
