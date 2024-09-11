import pandas as pd
import itertools

# synergy is summed up from the winrates of each pair in the team
def synergy(column):
    duo_winrates = ''
    for string in open('data/duo_winrates.txt', 'r').readlines():
        duo_winrates = string
    duo_winrates = eval(duo_winrates)
    column.sort()
    synergy = 0
    for pair in itertools.combinations(column, 2):
        try:
            synergy += (duo_winrates[pair]['win'] / duo_winrates[pair]['total'])
        except:
            synergy += (duo_winrates[pair[1], pair[0]]['win'] / duo_winrates[pair[1], pair[0]]['total'])
    return synergy

# adding a columns with total amount of basic attributes for each team
def add_heroes_attributes(df):
    heroes_stats_df = pd.read_csv('data/heroes_stats.csv')
    heroes_list = heroes_stats_df['localized_name']
    d = {k: v for k, v in zip(heroes_list, heroes_stats_df.index)}

    for ch in ('A', 'B'):
        for col in heroes_stats_df.columns[1:]:
            df[f'{ch}_total_{col}'] = 0.

    for hero in heroes_list:
        df.loc[df[f'{hero}'] == -1, f'A_total_dps':f'A_total_stamina'] += heroes_stats_df.loc[d[hero], 'dps':'stamina'].values.astype(float)
        df.loc[df[f'{hero}'] == 1, f'B_total_dps':f'B_total_stamina'] += heroes_stats_df.loc[d[hero], 'dps':'stamina'].values.astype(float)
    return df

if __name__ == '__main__':
    df = pd.read_csv('data/raw_matches.csv')
    
    # replacing target values by numbers: 0 for The Amber Hand, 1 for The Sapphire Flame
    df['winner'] = df['winner'].apply(lambda x: 0 if x == 'The Amber Hand' else 1)
    for ch in ('A', 'B'):
        for i in range(1, 7):
            df[f'hero_{i}_{ch}'] = df[f'hero_{i}_{ch}'].str.lower()

    # packing heroes into teams columns for further more comfortable calculations
    A_team = ['hero_1_A', 'hero_2_A', 'hero_3_A', 'hero_4_A', 'hero_5_A', 'hero_6_A']
    B_team = ['hero_1_B', 'hero_2_B', 'hero_3_B', 'hero_4_B', 'hero_5_B', 'hero_6_B']

    df['A'] = df[A_team].values.tolist()
    df['B'] = df[B_team].values.tolist()

    for ch in ('A', 'B'):
        for i in range(1, 7):
            df.drop(f'hero_{i}_{ch}', axis=1, inplace=True)

    # creating a dictionary that will contain all pairs of heroes and their winrates
    heroes = pd.read_csv('data/heroes_stats.csv')['localized_name']
    duo_winrates = {}
    for i in itertools.combinations(heroes, 2):
        duo_winrates[i] = {'win': 0, 'total': 0}

    A_win = df[df['winner'] == 0]
    B_win = df[df['winner'] == 1]

    for i in duo_winrates:
        count = 0
        for j in A_win['A']:
            if (i[0] in j and i[1] in j):
                count += 1
        duo_winrates[i]['win'] += count
        duo_winrates[i]['total'] += count

        count = 0
        for j in A_win['B']:
            if (i[0] in j and i[1] in j):
                count += 1
        duo_winrates[i]['total'] += count

    for i in duo_winrates:
        count = 0
        for j in B_win['A']:
            if (i[0] in j and i[1] in j):
                count += 1
        duo_winrates[i]['total'] += count

        count = 0
        for j in B_win['B']:
            if (i[0] in j and i[1] in j):
                count += 1
        duo_winrates[i]['win'] += count
        duo_winrates[i]['total'] += count

    open('data/duo_winrates.txt', 'w').write(str(duo_winrates))

    df['A_synergy'] = df['A'].apply(synergy)
    df['B_synergy'] = df['B'].apply(synergy)

    # unpacking heroes for separate slots 
    df[A_team] = df['A'].tolist()
    df[B_team] = df['B'].tolist()
    df.drop(['A', 'B'], axis=1, inplace=True)

    # replacing columns by particular column for every hero
    # -1 - The Amber Hand (A_team)
    # +1 - The Sapphire Flame (B_team)
    for hero in heroes:
        df[hero] = 0
        df[hero] -= (df[A_team] == hero).any(axis=1)
        df[hero] += (df[B_team] == hero).any(axis=1)

    for ch in ('A', 'B'):
        for i in range(1, 7):
            df.drop(f'hero_{i}_{ch}', axis=1, inplace=True)

    add_heroes_attributes(df)

    df.drop('matchid', axis=1, inplace=True)

    df.to_csv('data/preproc_matches.csv', index=False)