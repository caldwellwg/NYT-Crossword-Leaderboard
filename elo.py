import json
from scipy.special import gamma, gammaincc
import numpy as np
import matplotlib.pyplot as plt
import sys

# Elo constants
n = 400
K = 30


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
    return x**(k-1)*np.exp(-x/theta)/(gamma(k)*theta**k)


def score_gamma(x, k, theta):
    return gammaincc(k, x/theta)


def update_ratings(new_json, players=[]):
    # Fit to gamma distribution
    times = [item['time'] for item in new_json['data']]
    avg = np.average(times)
    std = np.std(times)
    k = (avg/std)**2
    theta = std**2/avg

    for result in new_json['data']:
        if not any(player['name'] == result['name'] for player in players):
            players.append({
                'name': result['name'],
                'rating': 1200
            })

    average_rating = np.average([player['rating'] for player in players if player['name'] in map(
        lambda i: i['name'], new_json['data'])])
    for result in new_json['data']:
        rating = next(player['rating']
                      for player in players if player['name'] == result['name'])
        rating_diff = (rating - average_rating) / n
        expected_score = 1 / (1 + 0.1**rating_diff)
        actual_score = score_gamma(result['time'], k, theta)
        new_rating = rating + K * (actual_score - expected_score)
        for player in players:
            if player['name'] == result['name']:
                player['rating'] = new_rating
    return players


def plot_results(new_json):
    times = [item['time'] for item in new_json['data']]
    avg = np.average(times)
    std = np.std(times)
    k = (avg/std)**2
    theta = std**2/avg
    x = np.linspace(0, 300)
    plt.plot(x, gamma_dist(x, k, theta), c='blue')
    plt.scatter(times, np.zeros(len(times)), c='red')
    plt.show()


players = []
for filename in sys.argv[1:]:
    with open(filename) as file:
        new_json = load_json(file)
        players = update_ratings(new_json, players)
        print(sorted(players, key=lambda i: -i['rating']))
