import pandas as pd
from sklearn.model_selection import train_test_split
from preprocess import synergy, add_heroes_attributes
from joblib import load

df = pd.read_csv('data/preproc_matches.csv')
scaler = load('data/joblib/scaler.joblib')
X, y = df.drop('winner', axis=1), df['winner']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=52)

A_team = ['hero_1_A', 'hero_2_A', 'hero_3_A', 'hero_4_A', 'hero_5_A', 'hero_6_A']
B_team = ['hero_1_B', 'hero_2_B', 'hero_3_B', 'hero_4_B', 'hero_5_B', 'hero_6_B']
heroes_stats_df = pd.read_csv('data/heroes_stats.csv')
heroes = heroes_stats_df['localized_name']

heroes_A = [input('enter amber heroes: ').lower().strip() for _ in range(6)]
heroes_B = [input('enter sapphire heroes: ').lower().strip() for _ in range(6)]

# reading sample for input data and deleting unwanted columns
test_match = pd.read_csv('data/blank_sample.csv')
test_match.drop('matchid', axis=1, inplace=True)
test_match.drop('winner', axis=1, inplace=True)

for i in range(1, 7):
    test_match[f'hero_{i}_A'] = heroes_A[i - 1]
for i in range(1, 7):
    test_match[f'hero_{i}_B'] = heroes_B[i - 1]

# packing heroes for each team
test_match['A'] = test_match[A_team].values.tolist()
test_match['B'] = test_match[B_team].values.tolist()
for ch in ('A', 'B'):
    for i in range(1, 7):
        test_match.drop(f'hero_{i}_{ch}', axis=1, inplace=True)

# adding synergy
test_match['A_synergy'] = test_match['A'].apply(synergy)
test_match['B_synergy'] = test_match['B'].apply(synergy)

# unpackung heroes
test_match[A_team] = test_match['A'].tolist()
test_match[B_team] = test_match['B'].tolist()
test_match.drop(['A', 'B'], axis=1, inplace=True)

# replacing columns with column for each hero
for hero in heroes:
    test_match[hero] = 0
    test_match[hero] -= (test_match[A_team] == hero).any(axis=1)
    test_match[hero] += (test_match[B_team] == hero).any(axis=1)

# deleting previous columns
for ch in ('A', 'B'):
    for i in range(1, 7):
        test_match.drop(f'hero_{i}_{ch}', axis=1, inplace=True)

# adding a columns for total basic attributes
for ch in ('A', 'B'):
    for col in heroes_stats_df.columns[1:]:
        test_match[f'{ch}_total_{col}'] = 0

# filling columns with total amount of attributes
add_heroes_attributes(test_match)

# logistic regression prediction for your pick 
logreg = load('data/joblib/logistic_regression_model.joblib')
test_match_scaled = scaler.transform(test_match)
res = logreg.predict(test_match_scaled)
if res == 1:
    print(f'the sapphire flame: {logreg.predict_proba(test_match_scaled)[0][1]* 100:.1f}%')
else:
    print(f'the amber hand: {logreg.predict_proba(test_match_scaled)[0][0]* 100:.1f}%')