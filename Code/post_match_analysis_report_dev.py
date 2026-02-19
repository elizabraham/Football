# -*- coding: utf-8 -*-
 # TAL Prakrida vs SBFC M1


import pandas as pd
import numpy as np
from mplsoccer import Pitch
from streamlit.components.v1 import html
import matplotlib.pyplot as plt




# Commented out IPython magic to ensure Python compatibility.
#writefile app.py
import streamlit as st


# Page setup
st.set_page_config(page_title="Post-Match Analysis", layout="wide")



# Custom CSS for styling cards
st.markdown("""
    <style>
        .card {
            padding: 20px;
            border-radius: 15px;
            background-color: #f4f4f4;
            text-align: center;
            box-shadow: 0px 0px 10px #ccc;
            margin-bottom: 20px;
        }
        .card h3 {
            margin: 0;
            font-size: 24px;
            color: #333;
        }
        .card p {
            margin: 5px 0;
            font-size: 16px;
            color: #666;
        }
        .header {
            text-align: center;
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 30px;
        }
        .filters {
            text-align: center;
            margin-bottom: 40px;
        }
    </style>
""", unsafe_allow_html=True)


uploaded_file = st.sidebar.file_uploader("Upload your match CSV file:", type=["csv"])
if uploaded_file is None:
    st.warning("⚠️ Please upload a CSV file to proceed with the analysis.")
    st.stop()

else:
    # Header
     st.markdown('<div class="header"><h2 style="font-size:40px;">Post-Match Analysis Dashboard</h2></div>', unsafe_allow_html=True)
    #Load data into a DataFrame
     df = pd.read_csv(uploaded_file)
     # Display the raw data
     #st.subheader("Match Event Data")
     #st.dataframe(df)

     # Ensure columns exist
     required_columns = [ "Team", "Player","Event","Mins", "Secs", "X", "Y" ]
     if not all(col in df.columns for col in required_columns):
         st.error(f"Data must include columns: {', '.join(required_columns)}")
     else:
        #Sort data by time
         df = df.sort_values(by=["Mins", "Secs"]).reset_index(drop=True)

         # Correct Y-axis
         df["Y"] = 100 - df["Y"]

         #Lagging team names (to understand which team event it was before the current event)
         df["Nxt_Event"] = df["Event"].shift(-1)
         df["Nxt_Team"] = df["Team"].shift(-1)
         df["Key_Pass_Event"] = np.where((df["Nxt_Event"] == 'Shot On Target') | (df["Nxt_Event"] == 'Shot Off Target'), df["Nxt_Event"],'null')
         df["Key_Pass_Event"] = np.where(((df["Nxt_Event"] == 'Unsuccessful DA') | (df["Nxt_Event"] == 'Tackle')) & (df["Nxt_Team"] != df["Team"]),
                                df["Event"].shift(-2), df["Key_Pass_Event"])
         df["Key_Pass"] = np.where(((df["Key_Pass_Event"] == 'Shot On Target') | (df["Key_Pass_Event"] == 'Shot Off Target')) & (df["Event"] == 'Successful Pass'),1,0)

         #st.dataframe(df)

         # Filters
         analysis_type = st.selectbox("Type of Analysis", ["Match Performance", "Team Performance", "Player Performance"])
         player_filter = []
         # Sidebar filters
         if analysis_type in ("Team Performance", "Match Performance"):
            st.sidebar.header("Filters")
            team_filter = st.sidebar.selectbox("Select Team", options=["All"] + df["Team"].unique().tolist())
         elif analysis_type == "Player Performance":
             st.sidebar.header("Filters")
             team_filter = st.sidebar.selectbox("Select Team", options=["All"] + df["Team"].unique().tolist())
             player_filter = st.sidebar.selectbox("Select Player", options=["All"] + df["Player"].unique().tolist())


         filtered_df = df.copy()

         # Filters
         if team_filter != "All":
            filtered_df = filtered_df[filtered_df["Team"] == team_filter]

         if player_filter is None:
             if player_filter != "All":
                filtered_df = filtered_df[filtered_df["Player"] == player_filter]

         #st.subheader(analysis_type)
         st.markdown("---")
         st.markdown(f"<h2 style='font-size:30px;text-align: center; '>{analysis_type}</h2>", unsafe_allow_html=True)
         st.markdown("---")
         teams = df["Team"].unique().tolist()
         team_a = teams[1]
         team_b = teams[0]
         st.markdown(f"""
                        <div style='
                        display: flex;
                        justify-content: space-between;
                        max-width: 900px;
                        margin: auto;
                    '>
                    <h3 style='color:#1f77b4; margin: 0;'>{team_a}</h3>
                    <h3 style='color:#d62728; margin: 0;'>{team_b}</h3>
                    </div>
                    """, unsafe_allow_html=True)
         st.markdown("")
         #Goal Data
         goals_team_a = len(filtered_df[(filtered_df["Event"] == "Goal") & (filtered_df["Team"] == team_a)])
         goals_team_b = len(filtered_df[(filtered_df["Event"] == "Goal") & (filtered_df["Team"] == team_b)])

         goal_data_team_a = filtered_df[(filtered_df["Event"] == "Goal") & (filtered_df["Team"] == team_a)]
         goal_data_team_b = filtered_df[(filtered_df["Event"] == "Goal") & (filtered_df["Team"] == team_b)]

         # Generate HTML for player lists
         def generate_goal_list_html(goal_data_team):
            html_parts = []
            for idx, row in goal_data_team.iterrows():
                player = row["Player"]
                minute = row["Mins"]
                penalty_note = " [P]" if row["Event"] == "Penalty" else ""
                html_parts.append(
                    f"<div style='display: flex;justify-content: space-between;align-items: center;width: 40%;margin: 5px auto;font-size: 15px;'>"
                    f"<div style='text-align: left;'>⚽ <b>{player}</b></div>"
                    f"<div style='text-align: right;'>{minute}'{penalty_note}</div>"
                    f"</div>"
                )
            # If no goals, display a placeholder for consistent card height
            if not html_parts:
                html_parts.append(f"<div style='display: flex;justify-content: center;align-items: center;width: 30%;margin: 5px auto;font-size: 15px;'>"
                                  f"<div style='color:gray;font-size:30px;text-align:center; '>----</div>"
                                  f"</div>")
            return "".join(html_parts), len(html_parts)


         goal_player_list_team_a, count_a = generate_goal_list_html(goal_data_team_a)
         goal_player_list_team_b, count_b = generate_goal_list_html(goal_data_team_b)

         # Dynamic min-height based on number of players (adjust factor as needed)
         base_height = 200  # minimum height even if no goals
         height_per_goal = 40  # additional height per goal scorer line

         calculated_height_a = base_height + int(count_a) * height_per_goal
         calculated_height_b = base_height + int(count_b) * height_per_goal

         # To ensure both cards have the same height
         final_min_height = max(calculated_height_a, calculated_height_b)

         # Create two columns with same card height and clean styling
         col1, col2 = st.columns(2)

         card_style = f"""
             border: 0.5px  #ddd;
             border-radius: 60px;
             padding: 30px 20px;
             margin: 6px;
             min-height: {final_min_height}px;
             display: flex;
             flex-direction: column;
             justify-content: flex-start;
             align-items: center;
             box-shadow: 0 4px 10px rgba(0, 123, 255, 0.3)
             """

         with col1:
            st.markdown(f"""
             <div class="card" style="{card_style}">
                <h2 style='font-size:80px;text-align: center;  '>{goals_team_a}</h2>
                 {goal_player_list_team_a}
             </div>
             """, unsafe_allow_html=True)

         with col2:
            st.markdown(f"""
             <div class="card" style="{card_style}">
                 <h2 style='font-size:80px;text-align: center;  '>{goals_team_b}</h2>
                 {goal_player_list_team_b}
             </div>
             """, unsafe_allow_html=True)


         first_half = filtered_df[(filtered_df["Mins"] < 10) | (filtered_df["Mins"] == 10) & (filtered_df["Secs"] <= 39)]
         second_half = filtered_df[(filtered_df["Mins"] > 10) | (filtered_df["Mins"] == 10) & (filtered_df["Secs"] > 39)]
         st.markdown("")

        # Ball Possession Calculation
        # First Half
         bp_fh = first_half[((first_half['Event'] == 'Successful Pass') | (first_half['Event'] == 'Unsuccessful Pass') | (
                first_half['Event'] == 'Shot On Target') | (first_half['Event'] == 'Shot Off Target') | (
                                    first_half['Event'] == 'Goal Throw'))]
         p_teama_fh = bp_fh[bp_fh['Team'] == team_a]
         bp_teamb_fh = bp_fh[bp_fh['Team'] == team_b]

         total_event_counts_fh = bp_fh["Event"].value_counts()
         total_teama_events_fh = p_teama_fh["Event"].value_counts()
         total_teamb_events_fh = bp_teamb_fh["Event"].value_counts()

         bposs_pr_fh = round(((total_teama_events_fh.sum() / total_event_counts_fh.sum()) * 100), 2)
         bposs_sbfc_fh = round(((total_teamb_events_fh.sum() / total_event_counts_fh.sum()) * 100), 2)

         # Second Half
         bp_sh = second_half[((second_half['Event'] == 'Successful Pass') | (second_half['Event'] == 'Unsuccessful Pass') | (
                    second_half['Event'] == 'Shot On Target') | (second_half['Event'] == 'Shot Off Target') | (
                                         second_half['Event'] == 'Goal Throw'))]
         bp_teama_sh = bp_sh[bp_sh['Team'] == 'Prakrida FC']
         bp_teamb_sh = bp_sh[bp_sh['Team'] == 'SBFC']

         total_event_counts_sh = bp_sh["Event"].value_counts()
         total_teama_events_sh = bp_teama_sh["Event"].value_counts()
         total_teamb_events_sh = bp_teamb_sh["Event"].value_counts()

         bposs_teama_sh = round(((total_teama_events_sh.sum() / total_event_counts_sh.sum()) * 100), 0)
         bposs_teamb_sh = round(((total_teamb_events_sh.sum() / total_event_counts_sh.sum()) * 100), 0)

         # Full Time
         total_event_counts = total_event_counts_sh.sum() + total_event_counts_fh.sum()
         total_teama_events = total_teama_events_sh.sum() + total_teama_events_fh.sum()
         total_teamb_events = total_teamb_events_sh.sum() + total_teamb_events_fh.sum()

         bposs_teama = round(((total_teama_events / total_event_counts) * 100), 2)
         bposs_teamb = round(((total_teamb_events / total_event_counts) * 100), 2)

         #Shots On Target
         shot_data = filtered_df[(filtered_df["Event"] == "Shot On Target") | (filtered_df["Event"] == "Shot Off Target")]
         shot_data_teama = len(shot_data[shot_data['Team'] == team_a].reset_index(drop=True))
         shot_data_teamb = len(shot_data[shot_data['Team'] == team_b].reset_index(drop=True))

         sot_teama = len(filtered_df[((filtered_df["Event"] == "Shot On Target") & (filtered_df["Team"] == team_a))])
         sot_teamb = len(filtered_df[((filtered_df["Event"] == "Shot On Target") & (filtered_df["Team"] == team_b))])

         shot_acc_teama = round((sot_teama / shot_data_teama), 2) * 100
         shot_acc_teamb = round((sot_teamb / shot_data_teamb), 2) * 100

         # Pass Accuracy
         pass_data = filtered_df[(filtered_df["Event"] == "Successful Pass") | (filtered_df["Event"] == "Unsuccessful Pass")]
         pass_data_teama = len(pass_data[pass_data['Team'] == team_a].reset_index(drop=True))
         pass_data_teamb = len(pass_data[pass_data['Team'] == team_b].reset_index(drop=True))

         succ_pass = pass_data[(pass_data["Event"] == "Successful Pass")]
         succ_pass_teama = len(succ_pass[succ_pass['Team'] == team_a].reset_index(drop=True))
         succ_pass_teamb = len(succ_pass[succ_pass['Team'] == team_b].reset_index(drop=True))

         pass_acc_teama = round((succ_pass_teama / pass_data_teama), 2) * 100
         pass_acc_teamb = round((succ_pass_teamb / pass_data_teamb), 2) * 100

         # Tackles
         tackle_data = filtered_df[(filtered_df["Event"] == "Tackle")]
         tackle_data_teama = len(shot_data[shot_data['Team'] == team_a].reset_index(drop=True))
         tackle_data_teamb = len(shot_data[shot_data['Team'] == team_b].reset_index(drop=True))

         # Shot Accuracy
         sot_teama = len(filtered_df[((filtered_df["Event"] == "Shot On Target") & (filtered_df["Team"] == team_a))])
         sot_teamb = len(filtered_df[((filtered_df["Event"] == "Shot On Target") & (filtered_df["Team"] == team_b))])

         shot_acc_teama = round((sot_teama / shot_data_teama), 2) * 100
         shot_acc_teamb = round((sot_teamb / shot_data_teamb), 2) * 100


         stats = [
                    ("Ball Possession", bposs_teama, bposs_teamb),
    ("Shots Accuracy", shot_acc_teama, shot_acc_teamb),
    ("Pass Accuracy", pass_acc_teama, pass_acc_teamb),
    ("Tackles", tackle_data_teama, tackle_data_teamb),
    ("Shot Accuracy", 20, 80),
         ]

         # Container with Card Styling
         st.markdown("""
    <style>
    .stat-card {
        background-color: white;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.1);
        width: 100%;
        max-width: 1000px;
        margin: auto;
    }
    .stat-block {
        margin-bottom: 30px;
    }
    .stat-labels {
        display: flex;
        justify-content: space-between;
        margin-bottom: 6px;
        font-weight: 500;
    }
    .stat-name {
        text-align: center;
        margin-bottom: 6px;
        font-weight: 600;
    }
    .bar-row {
    display: flex;
    align-items: center;
    gap: 8px;
    }
    .stat-left,
    .stat-right {
    font-size: 13px;
    font-weight: 600;
    min-width: 35px;
    text-align: center;
    }

    .progress-bar {
        height: 12px;
        width: 50%;
        margin: 0 auto;
        background-color: #f1f1f1;
        border-radius: 20px;
        display: flex;
        overflow: hidden;
    }
    .bar-left {
        background-color: #2f80ed;
        height: 100%;
    }
    .bar-right {
        background-color: #eb4d4b;
        height: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Start HTML card container

# Loop through each stat and render
         for stat_name, team1_val, team2_val in stats:

            if stat_name in ["Tackles"]:
                st.markdown(f"""
                        <div class="stat-block">
                            <div class="stat-labels">
                                <div> ({team1_val}%)</div>
                                <div> ({team2_val}%)</div>
                            </div>
                            <div class="stat-name">{stat_name}</div>
                            <div class="progress-bar">
                                <div class="bar-left" style="width: {team1_val}%"></div>
                                <div class="bar-right" style="width: {team2_val}%"></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)


            else:
                st.markdown(f"""
        <div class="stat-block">
            <div class="stat-labels">
                <div> ({team1_val}%)</div>
                <div> ({team2_val}%)</div>
            </div>
            <div class="stat-name">{stat_name}</div>
            <div class="progress-bar">
                <div class="bar-left" style="width: {team1_val}%"></div>
                <div class="bar-right" style="width: {team2_val}%"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# End HTML card container
         st.markdown('</div>', unsafe_allow_html=True)




# Match Performance
         #if analysis_type == "Match Performance":





# Display cards


#file_path = "D:/fooball/projecs/Prakrida/Match files/TAL/M1.csv"
# Read the CSV file into a DataFrame
#df = pd.read_csv(file_path)



#st.markdown("### Upload your match event CSV file below:")
#uploaded_file = st.sidebar.file_uploader("Upload your match CSV file:", type=["csv"])
if uploaded_file:




         # Ball Possession Calculation
         #First Half
         bp_fh = first_half[((first_half['Event'] == 'Successful Pass') |(first_half['Event'] == 'Unsuccessful Pass')| (first_half['Event'] =='Shot On Target') | (first_half['Event'] =='Shot Off Target') | (first_half['Event'] =='Goal Throw'))]
         bp_pr_fh = bp_fh[bp_fh['Team'] == 'Prakrida FC']
         bp_sbfc_fh = bp_fh[bp_fh['Team'] == 'SBFC']

         total_event_counts_fh = bp_fh["Event"].value_counts()
         total_pr_events_fh = bp_pr_fh["Event"].value_counts()
         total_sbfc_events_fh = bp_sbfc_fh["Event"].value_counts()

         bposs_pr_fh = round(((total_pr_events_fh.sum()/total_event_counts_fh.sum()) *100),2)
         bposs_sbfc_fh = round(((total_sbfc_events_fh.sum()/total_event_counts_fh.sum()) *100),2)


         #Second Half
         bp_sh = second_half[((second_half['Event'] == 'Successful Pass') |(second_half['Event'] == 'Unsuccessful Pass')| (second_half['Event'] =='Shot On Target') | (second_half['Event'] =='Shot Off Target') | (second_half['Event'] =='Goal Throw'))]
         bp_pr_sh = bp_sh[bp_sh['Team'] == 'Prakrida FC']
         bp_sbfc_sh = bp_sh[bp_sh['Team'] == 'SBFC']

         total_event_counts_sh = bp_sh["Event"].value_counts()
         total_pr_events_sh = bp_pr_sh["Event"].value_counts()
         total_sbfc_events_sh = bp_sbfc_sh["Event"].value_counts()

         bposs_pr_sh = round(((total_pr_events_sh.sum()/total_event_counts_sh.sum()) *100),2)
         bposs_sbfc_sh = round(((total_sbfc_events_sh.sum()/total_event_counts_sh.sum()) *100),2)

         #Full Time
         total_event_counts = total_event_counts_sh.sum() + total_event_counts_fh.sum()
         total_pr_events = total_pr_events_sh.sum() + total_pr_events_fh.sum()
         total_sbfc_events = total_sbfc_events_sh.sum() + total_sbfc_events_fh.sum()

         bposs_pr = round(((total_pr_events/total_event_counts)*100),2)
         bposs_sbfc = round(((total_sbfc_events/total_event_counts)*100),2)

         st.markdown("---")
         st.subheader("Ball Possession")
         st.markdown("---")
         st.markdown(

                       "<h2 style='text-align: center; color: gray;'>First Half</h2>", unsafe_allow_html=True

         )
         bp_fh =  f"""

                        <div style="text-align: center; font-size: 24px; font-family: Arial, sans-serif; color: 1E90FF;">

                        <p><strong>{team_a}</strong>: {bposs_pr_fh}%</p>

                        <p><strong>{team_b}</strong>: {bposs_sbfc_fh}%</p>

                        </div>

                        """
         st.markdown(bp_fh, unsafe_allow_html=True)
         st.markdown("<h2 style='text-align: center; color: gray;'>Second Half</h2>", unsafe_allow_html=True)
         bp_sh = f"""
                        <div style="text-align: center; font-size: 24px; font-family: Arial, sans-serif; color: 1E90FF;">

                        <p><strong>{team_a}</strong>: {bposs_pr_sh}%</p>

                        <p><strong>{team_b}</strong>: {bposs_sbfc_sh}%</p>

                        </div>

                        """

         st.markdown(bp_sh,unsafe_allow_html=True)
         st.markdown(

                       "<h2 style='text-align: center; color: gray;'>Full Time</h2>", unsafe_allow_html=True

         )
         bp_full = f"""

                        <div style="text-align: center; font-size: 24px; font-family: Arial, sans-serif; color: 1E90FF;">

                        <p><strong>{team_a}</strong>: {bposs_pr}%</p>

                        <p><strong>{team_b}</strong>: {bposs_sbfc}%</p>

                        </div>

                        """
         st.markdown(bp_full,unsafe_allow_html=True)
         st.markdown("------------------------------------------------")

         col1, col2, col3 = st.columns(3)

         col1.metric("Goals", 3, "+1")
         col2.metric("Pass Accuracy", "85%", "-2%")
         col3.metric("Possession", "61%", "+5%")

      #Shot Data

         st.subheader("Shot Data")
         st.markdown("------------------------------------------------")
         total_shots=f"""

                        <div style="text-align: center; font-size: 24px; font-family: Arial, sans-serif; color: 1E90FF;">

                        <p><strong>Total Shots</strong>: {len(filtered_df[(filtered_df["Event"] == "Shot On Target") | (filtered_df["Event"] == "Shot Off Target")])}</p>

                        </div>

                        """
         st.markdown(total_shots,unsafe_allow_html=True)
         shot_details = f"""

                        <div style="display: flex; justify-content: space-between; font-size: 24px; font-family: Arial, sans-serif; color: 1E90FF;">

                        <p><strong>{team_a}</strong>: {len(filtered_df[((filtered_df["Event"] == "Shot On Target") | (filtered_df["Event"] == "Shot Off Target")) & (filtered_df["Team"] == "Prakrida FC")])}</p>

                        <p><strong>{team_b}</strong>: {len(filtered_df[((filtered_df["Event"] == "Shot On Target") | (filtered_df["Event"] == "Shot Off Target")) & (filtered_df["Team"] == "SBFC")])}</p>

                        </div>
                        """
         st.markdown(shot_details,unsafe_allow_html=True)
         shots_on_target = f"""

                                <div style="text-align: center; font-size: 24px; font-family: Arial, sans-serif; color: 1E90FF;">

                                <p><strong>Shots On Target</strong>: {len(filtered_df[(filtered_df["Event"] == "Shot On Target")])}</p>

                                </div>

                                """
         st.markdown(shots_on_target, unsafe_allow_html=True)
         shots_on_target_det = f"""
                                    <div style="display: flex; justify-content: space-between; font-size: 24px; font-family: Arial, sans-serif; color: 1E90FF;">

                                    <p><strong>{team_a}</strong>: {len(filtered_df[((filtered_df["Event"] == "Shot On Target") & (filtered_df["Team"] == "Prakrida FC"))])}</p>

                                    <p><strong>{team_b}</strong>: {len(filtered_df[((filtered_df["Event"] == "Shot On Target") & (filtered_df["Team"] == "SBFC"))])}</p>

                                    </div>
                                """
         st.markdown(shots_on_target_det, unsafe_allow_html=True)
         st.markdown("---")
         st.subheader("Shots Conversion Rate")
         st.markdown("------------------------------------------------")
         shots_conv = f"""
                     <div style="display: flex; justify-content: space-between; font-size: 24px; font-family: Arial, sans-serif; color: 1E90FF;">
                     <p><strong>{team_a}</strong>:{round((len(filtered_df[((filtered_df["Event"] == "Goal")) & (filtered_df["Team"] == "Prakrida FC")])/len(filtered_df[((filtered_df["Event"] == "Shot On Target")) & (filtered_df["Team"] == "Prakrida FC")])),2)*100}%</p>
                     <p><strong>{team_b}</strong>:{round((len(filtered_df[((filtered_df["Event"] == "Goal")) & (filtered_df["Team"] == "SBFC")])/len(filtered_df[((filtered_df["Event"] == "Shot On Target")) & (filtered_df["Team"] == "SBFC")])),1)*100}%</p>
                     """
         st.markdown(shots_conv,unsafe_allow_html=True)
         st.markdown("------------------------------------------------")
        #Shot Map

        #First Half

         st.subheader("Shot Map")
         st.markdown("------------------------------------------------")
         st.subheader("First Half")
         shot_data_fh = first_half[(first_half["Event"] == "Shot On Target") | (first_half["Event"] == "Shot Off Target")]
         shot_data_pr_fh = shot_data_fh [shot_data_fh['Team'] == 'Prakrida FC'].reset_index(drop=True)
         shot_data_sbfc_fh = shot_data_fh [shot_data_fh['Team'] == 'SBFC'].reset_index(drop=True)

         outcome_colors = {"Shot On Target": "green",
                           "Shot Off Target": "red"
                           }
         outcome_markers = {"Shot Off Target": "o", #Circle
                            "Shot On Target": "*",#Star
                            }

         # Plot shots

         st.subheader("Prakrida FC")
         pitch = Pitch(pitch_type='opta', pitch_color='white', line_color='black')
         fig, ax = pitch.draw()
         if not shot_data_pr_fh.empty:

             for outcome in shot_data_pr_fh['Event']:
             #Filter the data for the current outcome
                 outcome_data = shot_data_pr_fh[shot_data_pr_fh["Event"] == outcome]
                 ax.scatter(outcome_data["X"], outcome_data["Y"], color=outcome_colors[outcome],marker=outcome_markers[outcome], s=100, label=outcome, alpha=0.7)
             handles, labels = ax.get_legend_handles_labels()
             by_label = dict(zip(labels, handles))
             ax.legend(by_label.values(), by_label.keys())
             st.pyplot(fig)

         else:

             st.info("No shot data available for First Half.")

         st.subheader("SBFC")
         pitch = Pitch(pitch_type='opta', pitch_color='white', line_color='black')
         fig, ax = pitch.draw()

         if not shot_data_sbfc_fh.empty:

             for outcome in shot_data_sbfc_fh['Event']:

             #Filter the data for the current outcome
                 outcome_data = shot_data_sbfc_fh[shot_data_sbfc_fh["Event"] == outcome]
                 ax.scatter(outcome_data["X"], outcome_data["Y"],color=outcome_colors[outcome],marker=outcome_markers[outcome], s=100, label=outcome, alpha=0.7)

             handles, labels = ax.get_legend_handles_labels()
             by_label = dict(zip(labels, handles))
             ax.legend(by_label.values(), by_label.keys())
             st.pyplot(fig)

         else:

             st.info("No shot data available for First Half.")

         # Second Half

         st.subheader("Second Half")
         shot_data_sh = second_half[(second_half["Event"] == "Shot On Target") | (second_half["Event"] == "Shot Off Target")]
         shot_data_pr_sh = shot_data_sh [shot_data_sh['Team'] == 'Prakrida FC'].reset_index(drop=True)
         shot_data_sbfc_sh = shot_data_sh [shot_data_sh['Team'] == 'SBFC'].reset_index(drop=True)

         # Plot shots

         st.subheader("Prakrida FC")

         pitch = Pitch(pitch_type='opta', pitch_color='white', line_color='black')

         fig, ax = pitch.draw()

         if not shot_data_pr_sh.empty:



             for outcome in shot_data_pr_sh['Event']:

                 # Filter the data for the current outcome

                 outcome_data = shot_data_pr_sh[shot_data_pr_sh["Event"] == outcome]

                 ax.scatter(outcome_data["X"], outcome_data["Y"],color=outcome_colors[outcome],marker=outcome_markers[outcome], s=100, label=outcome, alpha=0.7)



             handles, labels = ax.get_legend_handles_labels()

             by_label = dict(zip(labels, handles))

             ax.legend(by_label.values(), by_label.keys())

             st.pyplot(fig)

         else:

             st.info("No shot data available for First Half.")



         st.subheader("SBFC")

         pitch = Pitch(pitch_type='opta', pitch_color='white', line_color='black')

         fig, ax = pitch.draw()

         if not shot_data_sbfc_sh.empty:



             for outcome in shot_data_sbfc_sh['Event']:

                 # Filter the data for the current outcome

                 outcome_data = shot_data_sbfc_sh[shot_data_sbfc_sh["Event"] == outcome]

                 ax.scatter(outcome_data["X"], outcome_data["Y"],color=outcome_colors[outcome],marker=outcome_markers[outcome], s=100, label=outcome, alpha=0.7)



             handles, labels = ax.get_legend_handles_labels()

             by_label = dict(zip(labels, handles))

             ax.legend(by_label.values(), by_label.keys())

             st.pyplot(fig)

         else:

             st.info("No shot data available for First Half.")

         st.markdown("-------------------------------------")

         #Pass Data
         st.subheader("Pass Data")
         st.markdown("------------------------------------------------")
         st.subheader("Total Passes")

         #First Half
         pass_data_fh = first_half[(first_half["Event"] == "Successful Pass") | (first_half["Event"] == "Unsuccessful Pass")]
         pass_data_pr_fh = len(pass_data_fh[pass_data_fh['Team'] == 'Prakrida FC'].reset_index(drop=True))
         pass_data_sbfc_fh = len(pass_data_fh[pass_data_fh['Team'] == 'SBFC'].reset_index(drop=True))
         st.markdown("----------------------------------")

         st.markdown("<h2 style='text-align: center; color: gray;'>First Half</h2>", unsafe_allow_html=True)
         pass_fh = f"""
                        <div style="text-align: center; font-size: 24px; font-family: Arial, sans-serif; color: 1E90FF;">

                        <p><strong>{team_a}</strong>: {pass_data_pr_fh}</p>

                        <p><strong>{team_b}</strong>: {pass_data_sbfc_fh}</p>

                        </div>

                 """
         st.markdown(pass_fh, unsafe_allow_html=True)

        # Second Half
         pass_data_sh = second_half[(second_half["Event"] == "Successful Pass") | (second_half["Event"] == "Unsuccessful Pass")]
         pass_data_pr_sh = len(pass_data_sh[pass_data_sh['Team'] == 'Prakrida FC'].reset_index(drop=True))
         pass_data_sbfc_sh = len(pass_data_sh[pass_data_sh['Team'] == 'SBFC'].reset_index(drop=True))

         st.markdown("<h2 style='text-align: center; color: gray;'>Second Half</h2>", unsafe_allow_html=True)
         pass_sh = f"""
                                 <div style="text-align: center; font-size: 24px; font-family: Arial, sans-serif; color: 1E90FF;">

                                 <p><strong>{team_a}</strong>: {pass_data_pr_sh}</p>

                                 <p><strong>{team_b}</strong>: {pass_data_sbfc_sh}</p>

                                 </div>

                          """
         st.markdown(pass_sh, unsafe_allow_html=True)

         #Full Time
         pass_data_pr = pass_data_pr_fh + pass_data_pr_sh
         pass_data_sbfc = pass_data_sbfc_fh + pass_data_sbfc_sh

         st.markdown("<h2 style='text-align: center; color: gray;'>Full Time</h2>", unsafe_allow_html=True)
         pass_full = f"""

                                <div style="text-align: center; font-size: 24px; font-family: Arial, sans-serif; color: 1E90FF;">

                                <p><strong>{team_a}</strong>: {pass_data_pr}</p>

                                <p><strong>{team_b}</strong>: {pass_data_sbfc}</p>

                                </div>

                                """
         st.markdown(pass_full, unsafe_allow_html=True)

         #Pass Accuracy
         st.subheader("Pass Accuracy")
         #First Half
         succ_pass_fh = first_half[(first_half["Event"] == "Successful Pass")]
         succ_pass_pr_fh = len(succ_pass_fh[succ_pass_fh['Team'] == 'Prakrida FC'].reset_index(drop=True))
         succ_pass_sbfc_fh = len(succ_pass_fh[succ_pass_fh['Team'] == 'SBFC'].reset_index(drop=True))

         pass_acc_pr_fh = round((succ_pass_pr_fh/pass_data_pr_fh),2)*100
         pass_acc_team2_fh = round((succ_pass_sbfc_fh / pass_data_sbfc_fh), 2) * 100

         st.markdown("<h2 style='text-align: center; color: gray;'>First Half</h2>", unsafe_allow_html=True)
         pass_acc_fh = f"""

                                        <div style="text-align: center; font-size: 24px; font-family: Arial, sans-serif; color: 1E90FF;">

                                        <p><strong>{team_a}</strong>: {pass_acc_pr_fh}%</p>

                                        <p><strong>{team_b}</strong>: {pass_acc_team2_fh}%</p>

                                        </div>

                                        """
         st.markdown(pass_acc_fh, unsafe_allow_html=True)

         #Second Half
         succ_pass_sh = second_half[(second_half["Event"] == "Successful Pass")]
         succ_pass_team1_sh = len(succ_pass_sh[succ_pass_sh['Team'] == 'Prakrida FC'].reset_index(drop=True))
         succ_pass_team2_sh = len(succ_pass_sh[succ_pass_sh['Team'] == 'SBFC'].reset_index(drop=True))

         pass_acc_team1_sh = round((succ_pass_team1_sh / pass_data_pr_sh), 2) * 100
         pass_acc_team2_sh = round((succ_pass_team2_sh / pass_data_sbfc_sh), 2) * 100

         st.markdown("<h2 style='text-align: center; color: gray;'>Second Half</h2>", unsafe_allow_html=True)
         pass_acc_sh = f"""

                                                <div style="text-align: center; font-size: 24px; font-family: Arial, sans-serif; color: 1E90FF;">

                                                <p><strong>{team_a}</strong>: {pass_acc_team1_sh}%</p>

                                                <p><strong>{team_b}</strong>: {pass_acc_team2_sh}%</p>

                                                </div>

                                                """
         st.markdown(pass_acc_sh, unsafe_allow_html=True)

         # Full Time
         succ_pass_team1 = succ_pass_pr_fh + succ_pass_team1_sh
         succ_pass_team2 = succ_pass_sbfc_fh + succ_pass_team2_sh

         pass_acc_team1 = round((succ_pass_team1 / pass_data_pr), 2) * 100
         pass_acc_team2 = round((succ_pass_team2 / pass_data_sbfc), 2) * 100

         st.markdown("<h2 style='text-align: center; color: gray;'>Full Time</h2>", unsafe_allow_html=True)
         pass_acc = f"""

                            <div style="text-align: center; font-size: 24px; font-family: Arial, sans-serif; color: 1E90FF;">

                            <p><strong>{team_a}</strong>: {pass_acc_team1}%</p>

                            <p><strong>{team_b}</strong>: {pass_acc_team2}%</p>

                            </div>

                        """
         st.markdown(pass_acc, unsafe_allow_html=True)
         st.markdown("------------------------------------------------")

         #Key Passes
         st.subheader("Key Passes")
         #First Half
         key_pass_fh = first_half[(first_half["Key_Pass"] == 1)]
         key_pass_team1_fh = len(key_pass_fh[key_pass_fh['Team'] == team_a].reset_index(drop=True))
         key_pass_team2_fh = len(key_pass_fh[key_pass_fh['Team'] == team_b].reset_index(drop=True))

         st.markdown("<h2 style='text-align: center; color: gray;'>First Half</h2>", unsafe_allow_html=True)
         key_pass_fh = f"""

                            <div style="text-align: center; font-size: 24px; font-family: Arial, sans-serif; color: 1E90FF;">

                            <p><strong>{team_a}</strong>: {key_pass_team1_fh}</p>

                            <p><strong>{team_b}</strong>: {key_pass_team2_fh}</p>

                            </div>

                       """
         st.markdown(key_pass_fh, unsafe_allow_html=True)

         # Second Half
         key_pass_sh = second_half[(second_half["Key_Pass"] == 1)]
         key_pass_team1_sh = len(key_pass_sh[key_pass_sh['Team'] == team_a].reset_index(drop=True))
         key_pass_team2_sh = len(key_pass_sh[key_pass_sh['Team'] == team_b].reset_index(drop=True))

         st.markdown("<h2 style='text-align: center; color: gray;'>Second Half</h2>", unsafe_allow_html=True)
         key_pass_sh = f"""

                            <div style="text-align: center; font-size: 24px; font-family: Arial, sans-serif; color: 1E90FF;">

                            <p><strong>{team_a}</strong>: {key_pass_team1_sh}</p>

                            <p><strong>{team_b}</strong>: {key_pass_team2_sh}</p>

                            </div>

                        """
         st.markdown(key_pass_sh, unsafe_allow_html=True)

         # Full Time
         key_pass_team1 = key_pass_team1_fh + key_pass_team1_sh
         key_pass_team2 = key_pass_team2_fh + key_pass_team2_sh

         st.markdown("<h2 style='text-align: center; color: gray;'>Full Time</h2>", unsafe_allow_html=True)
         key_passes = f"""

                        <div style="text-align: center; font-size: 24px; font-family: Arial, sans-serif; color: 1E90FF;">

                        <p><strong>{team_a}</strong>: {key_pass_team1}</p>

                        <p><strong>{team_b}</strong>: {key_pass_team2}</p>

                        </div>

                    """
         st.markdown(key_passes, unsafe_allow_html=True)
         st.markdown("------------------------------------------------")






         # Pass Network

         st.subheader("Pass Network")

         pass_data = filtered_df[(filtered_df["Event"] == "Successful Pass") | (filtered_df["Event"] == "Unsuccessful Pass")]

         if not pass_data.empty:

             pitch = Pitch(pitch_type='opta', pitch_color='white', line_color='black')

             fig, ax = pitch.draw()



             pass_links = pass_data.groupby(["Player", "Team"]).size().reset_index(name="count")
             #st.dataframe(pass_links)
             for _, row in pass_links.iterrows():

                 player, team, count = row["Player"], row["Team"], row["count"]

                 color = "blue" if team == "Prakrida FC" else "red"

                 ax.annotate(player, (10, 10), color=color, fontsize=10)

                 ax.plot([10, 50], [10, 50], c=color, lw=count)



             st.pyplot(fig)

         else:

             st.info("No pass data available.")



         # Key Metrics Summary

         st.subheader("Key Metrics Summary")

         st.write("Summary of team and player performance metrics:")

         st.metric("Total Shots", len(filtered_df[(filtered_df["Event"] == "Shot On Target") | (filtered_df["Event"] == "Shot Off Target")]))

         st.metric("Total Passes", len(filtered_df[(filtered_df["Event"] == "Successful Pass") | (filtered_df["Event"] == "Unsuccessful Pass")]))

         st.metric("Fouls Committed", len(filtered_df[filtered_df["Event"] == "Foul"]))

         st.metric("Goals", len(filtered_df[filtered_df["Event"] == "Goal"]))



         st.success("Analysis Complete!")

else:

     st.info("Upload a CSV file to start the analysis.")




