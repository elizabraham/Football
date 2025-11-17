from statsbombpy import sb
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# View all available competitions
comps = sb.competitions()
#print(comps[['competition_id', 'season_id', 'competition_name', 'season_name']])

df = comps[comps['competition_id']==53]
#print(df[['competition_name', 'season_id']])

matches = sb.matches(competition_id=53, season_id=315)
#print(matches[['match_id', 'home_team', 'away_team', 'match_date']])

COMPETITION_ID = 53  # UEFA Women's Euro
SEASON_ID = 315      # 2025 Season

# --- Load matches ---
matches = sb.matches(competition_id=COMPETITION_ID, season_id=SEASON_ID)

# --- Filter Spain and England matches ---
spain_matches = matches[matches['home_team'].str.contains("Spain") | matches['away_team'].str.contains("Spain")]
england_matches = matches[matches['home_team'].str.contains("England") | matches['away_team'].str.contains("England")]

# --- Get match IDs for players ---
match_ids = pd.concat([spain_matches, england_matches])['match_id'].unique()

# --- Players to analyze ---
players_of_interest = ["Aitana Bonmatí", "Patri Guijarro", "Chloe Kelly"]

# --- Collect data ---
player_events = []

for match_id in match_ids:
    events = sb.events(match_id=match_id)
    events = events[events['player'].isin(players_of_interest)]
    player_events.append(events)

# Combine all event data
events_df = pd.concat(player_events)
print(events_df.columns)
