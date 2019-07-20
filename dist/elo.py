import json
from scipy.special import gamma, gammaincc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys

# Elo constants
n = 400
K = 30


def load_json(handle):
    data = json.load(handle)
    return {
        'data': pd.DataFrame([{
            'name': item['name'],
            'time': sum([a*b for a, b in zip([60, 1], map(int, item['time'].split(':')))])
        } for item in data['data'] if item['time'] != '--']),
        'date': data['date']
    }


def gamma_dist(x, k, theta):
    return x**(k-1)*np.exp(-x/theta)/(gamma(k)*theta**k)


def score_gamma(x, k, theta):
    return gammaincc(k, x/theta)


def update_ratings(new_json, players=pd.DataFrame(columns=['name', 'rating'])):
    # Fit to gamma distribution
    data = new_json['data']
    avg = data['time'].mean()
    avglog = data['time'].apply(np.log).mean()
    s = np.log(avg) - avglog
    k = (3 - s + np.sqrt((s - 3) ** 2 + 24 * s)) / (12 * s)
    theta = avg / k

    for _, result in data.iterrows():
        if not (players['name'] == result['name']).any():
            players = players.append({
                'name': result['name'],
                'rating': 1200
            }, ignore_index=True)

    average_rating = players[players['name'].isin(
        data['name'])]['rating'].mean()
    for _, result in data.iterrows():
        rating = players[players['name'] == result['name']]['rating']
        rating_diff = (rating - average_rating) / n
        expected_score = 1 / (1 + 0.1**rating_diff)
        actual_score = score_gamma(result['time'], k, theta)
        new_rating = rating + K * (actual_score - expected_score)
        players.update({'name': result['name'], 'rating': new_rating})
    return players


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


players = pd.DataFrame(columns=['name', 'rating'])
for filename in sys.argv[1:]:
    with open(filename) as file:
        new_json = load_json(file)
        players = update_ratings(new_json, players)
        plot_results(new_json)
        print(players.sort_values(by=['rating']))
