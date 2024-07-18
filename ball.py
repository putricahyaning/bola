import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Load the dataset
file_path = r'C:\Users\putri\Downloads\Data_Matrix_withPosition.xlsx'
data = pd.read_excel(file_path)

# Check if the necessary columns exist
# required_columns = ['offensive_rating', 'defensive_rating']
# for column in required_columns:
#     if column not in data.columns:
#         st.error(f"Column '{column}' not found in the dataset. Please check the dataset.")
#         st.stop()

st.set_page_config(layout="wide")

# Streamlit App
st.title('Soccer Player Comparison')

# Function to rename columns
def rename_columns(df):
    df.columns = [col.replace('_', ' ').title() for col in df.columns]
    return df

# Apply column renaming to the data
data = rename_columns(data)

# Convert all values in 'Player Name' column to strings
data['Player Name'] = data['Player Name'].astype(str)

# Main Tabs
tabs = st.tabs(['Player Comparison', 'Best Player'])

def filter_data(team=None, position=None):
    df = data
    if team:
        df = df[df['Team Name'] == team]
    if position:
        df = df[df['Position Name'] == position]
    return df

with tabs[0]:
    sub_tabs = st.tabs(['Comparison Between 2 Players', 'Radar Chart'])

    with sub_tabs[0]:
        same_league = st.checkbox('Compare only to players from the same team', value=False)

        col1, col2, col3 = st.columns([1, 0.2, 1])

        with col1:
            team1 = st.selectbox('Team', sorted(data['Team Name'].unique()), key='team1')
            position1 = st.selectbox('Position', sorted(filter_data(team=team1)['Position Name'].unique()), key='position1')
            player1 = st.selectbox('Player', sorted(filter_data(team=team1, position=position1)['Player Name'].unique()), key='player1')

        with col2:
            st.markdown('<h1 style="text-align: center; padding-top: 90px;">VS</h1>', unsafe_allow_html=True)

        with col3:
            if same_league:
                league_teams = data[data['Team Name'] == team1]['Team Name'].unique()
                team2 = st.selectbox('Team', sorted(league_teams), key='team2', disabled=True)
            else:
                team2 = st.selectbox('Team', sorted(data['Team Name'].unique()), key='team2')
            position2 = st.selectbox('Position', sorted(filter_data(team=team2)['Position Name'].unique()), key='position2')
            player2 = st.selectbox('Player', sorted(filter_data(team=team2, position=position2)['Player Name'].unique()), key='player2')

        comparison_category = st.radio(
            'Select Comparison Category',
            (
                'Overall Statistics',
                'Offensive',
                'Set Piece & Possessions',
                'Defensive',
                'Disciplinary'
            ),
            horizontal=True
        )

        category_metrics = {
            'Overall Statistics': [
                'Goals', 'Assists', 'Shots Attempt', 'Shots On Target', 'Shots Off Target', 'Key Passes',
                'Take Ons Attempt', 'Take Ons Success Rate', 'Touches', 'Passes Attempt', 'Passing Success Rate',
                'Carries', 'Corners', 'Aerial Attempts', 'Aerial Wons', 'Tackles',
                'Interceptions', 'Blocks', 'Clearances', 'Saves', 'Fouls', 'Offsides', 'Yellow Cards', 'Red Cards'
            ],
            'Offensive': [
                'Goals', 'Assists', 'Shots Attempt', 'Shots On Target', 'Shots Off Target', 'Key Passes',
                'Take Ons Attempt', 'Take Ons Success Rate'
            ],
            'Set Piece & Possessions': [
                'Touches', 'Passes Attempt', 'Passing Success Rate', 'Carries', 'Corners'
            ],
            'Defensive': [
                'Aerial Attempts', 'Aerial Wons', 'Tackles', 'Interceptions', 'Blocks', 'Clearances', 'Saves'
            ],
            'Disciplinary': [
                'Fouls', 'Offsides', 'Yellow Cards', 'Red Cards'
            ]
        }

        aggregation_type = st.selectbox('Select Aggregation Type', ['Total', 'Per-Game', 'Maximum', 'Minimum'])

        if st.button('Generate Comparison Chart'):
            st.write(f"Comparing {player1} and {player2}")

            player1_data = filter_data(team=team1, position=position1)[data['Player Name'] == player1]
            player2_data = filter_data(team=team2, position=position2)[data['Player Name'] == player2]

            metrics = category_metrics[comparison_category]
            player1_data = player1_data[metrics].select_dtypes(include='number')
            player2_data = player2_data[metrics].select_dtypes(include='number')

            if aggregation_type == 'Total':
                player1_data = player1_data.sum()
                player2_data = player2_data.sum()
            elif aggregation_type == 'Per-Game':
                player1_data = player1_data.mean()
                player2_data = player2_data.mean()
            elif aggregation_type == 'Maximum':
                player1_data = player1_data.max()
                player2_data = player2_data.max()
            elif aggregation_type == 'Minimum':
                player1_data = player1_data.min()
                player2_data = player2_data.min()

            comparison_df = pd.DataFrame({
                'Metric': player1_data.index,
                player1: player1_data.values,
                player2: player2_data.values
            })

            st.table(comparison_df.set_index('Metric').reset_index())

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=comparison_df['Metric'],
                y=comparison_df[player1],
                name=player1,
                marker_color='#66D8BA'
            ))
            fig.add_trace(go.Bar(
                x=comparison_df['Metric'],
                y=comparison_df[player2],
                name=player2,
                marker_color='#AA65B2'
            ))

            fig.update_layout(
                barmode='group',
                title=f'Comparison between {player1} and {player2}',
                xaxis_title='Metric',
                yaxis_title='Value',
                template='plotly_dark'
            )

            st.plotly_chart(fig, use_container_width=True)

    with sub_tabs[1]:
        st.subheader('Radar Chart for Selected Players')

        # Step 1: Select Position
        position = st.selectbox('Select Position', sorted(data['Position Name'].unique()), key='radar_position')

        if position:
            teams = sorted(filter_data(position=position)['Team Name'].unique())

            col1, col2, col3, col4 = st.columns(4)
            players = []

            # Step 2 and 3: Select Team and Player for each of the 4 slots
            for i, col in enumerate([col1, col2, col3, col4], start=1):
                with col:
                    team = st.selectbox(f'Select Team {i}', teams, key=f'team_{i}')
                    if team:
                        player_options = sorted(filter_data(team=team, position=position)['Player Name'].unique())
                        player = st.selectbox(f'Select Player {i}', player_options, key=f'player_{i}')
                        if player:
                            players.append(player)

            # Only use available attributes
            available_features = ['Goals', 'Assists', 'Passes', 'Shots On Target', 'Touches', 'Aerial Wons', 'Clearances', 'Tackles', 'Interceptions', 'Blocks']

            def create_radar_chart(players):
                if len(players) > 0:
                    df = data[data['Player Name'].isin(players)]
                    fig = go.Figure()

                    for player in players:
                        fig.add_trace(go.Scatterpolar(
                              r=df[df['Player Name'] == player][available_features].values.flatten().tolist(),
                              theta=available_features,
                              fill='toself',
                              name=player
                        ))

                    fig.update_layout(
                      polar=dict(
                        radialaxis=dict(
                          visible=True,
                          range=[0, df[available_features].values.max()]
                        )),
                      showlegend=True,
                      template='plotly_dark',
                      title='Radar Chart for Selected Players',
                      width=800,  # Increase the width
                      height=800  # Increase the height
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Please select Position to compare.")

            create_radar_chart(players)

with tabs[1]:
    num_competitions = data['Competition Id'].nunique()
    st.subheader(f'Top Performer Player Based On Last {num_competitions} Gameweeks')

    st.write('Top 10 Players For Every Position')

    aggregation_type = st.radio('Select Aggregation Type', ['Total', 'Pergame', 'Minimum','Maximum'], index=1)

    tab_positions = st.tabs(["Overall Player", "Goalkeeper", "Defender", "Midfielder", "Forward"])

    positions = ["Goalkeeper", "Defender", "Midfielder", "Forward"]

    def plot_top_players(players, position, aggregation_type):
        if aggregation_type == 'Total':
            avg_ratings = players.groupby(['Jersey Number', 'Player Name']).agg({
                'Player Rating': 'sum',
                'Offensive Rating': 'sum',
                'Defensive Rating': 'sum'
            }).reset_index()
            avg_ratings = avg_ratings.nlargest(10, 'Player Rating')
        elif aggregation_type == 'Pergame':
            avg_ratings = players.groupby(['Jersey Number', 'Player Name']).agg({
                'Player Rating': 'mean',
                'Offensive Rating': 'mean',
                'Defensive Rating': 'mean'
            }).reset_index()
            avg_ratings = avg_ratings.nlargest(10, 'Player Rating')
        elif aggregation_type == 'Minimum':
            avg_ratings = players.groupby(['Jersey Number', 'Player Name']).agg({
                'Player Rating': 'min',
                'Offensive Rating': 'min',
                'Defensive Rating': 'min'
            }).reset_index()
            avg_ratings = avg_ratings.nsmallest(10, 'Player Rating')
        elif aggregation_type == 'Maximum':
            avg_ratings = players.groupby(['Jersey Number', 'Player Name']).agg({
                'Player Rating': 'max',
                'Offensive Rating': 'max',
                'Defensive Rating': 'max'
            }).reset_index()
            avg_ratings = avg_ratings.nlargest(10, 'Player Rating')

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=avg_ratings['Player Name'],
            y=avg_ratings['Player Rating'],
            marker_color='#AA65B2'
        ))

        fig.update_layout(
            title=f'Top 10 {position} Based On Last {num_competitions} Gameweeks',
            xaxis_title='Player',
            yaxis_title='Player Rating',
            template='plotly_dark'
        )

        st.plotly_chart(fig, use_container_width=True)

        st.write(f"Summary of Top 10 {position} Based On Last {num_competitions} Gameweeks")
        st.table(avg_ratings[['Jersey Number', 'Player Name', 'Player Rating', 'Offensive Rating', 'Defensive Rating']])

    with tab_positions[0]:
        top_players = data
        plot_top_players(top_players, 'Players Overall', aggregation_type)

    for tab, position in zip(tab_positions[1:], positions):
        with tab:
            top_players = data[data['Position Name'] == position]
            plot_top_players(top_players, position, aggregation_type)
