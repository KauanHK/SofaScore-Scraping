import pandas as pd

class Statistics:

    def __init__(self, df: pd.DataFrame, coluna: str):
        self.df = df
        self.coluna = coluna

    def team_and_opponent(self, team: str) -> pd.DataFrame:

        df_team = self.df[self.df["Team"] == team][self.coluna].reset_index(drop = True)

        df_opponent = pd.concat([self.df[self.df["Home"] == team], self.df[self.df["Away"] == team]])
        df_opponent = df_opponent[df_opponent["Team"] != team][self.coluna].reset_index(drop = True)

        return df_team, df_opponent
    
    def team(self, team: str) -> list:
        df_team = self.df[self.df["Team"] == team][self.coluna]
        return list(df_team)
    
    def opponent(self, team: str) -> list:
        """Os valores retornados são relativos aos dos oponentes de team"""
        df_opponent = pd.concat([self.df[self.df["Home"] == team], self.df[self.df["Away"] == team]])
        df_opponent = df_opponent[df_opponent["Team"] != team][self.coluna]
        return list(df_opponent)
    
    def get_partidas(self) -> list[str]:

        partidas: list[str] = []
        for i in self.df.index[::6]:
            home = self.df.loc[i, "Team"]
            away = self.df.loc[i+1, "Team"]
            partidas.append([home, away])
        return partidas




stats = Statistics(
    df = pd.read_csv("Premier League 24-25.csv"),
    coluna = "Corner kicks"
)
partidas = stats.get_partidas()

rodadas = {}
i = 0
for j in range(0, len(partidas), 10):
    rodadas[i] = partidas[j:j+10]
    i += 1
rodadas

stats = Statistics("Corner kicks")
df_all = df[df["Period"] == 'ALL'].reset_index(drop = True)

data: dict[str, list] = {}
for team in set(df_all["Team"]):
    data[team] = [stats.team(df_all, team), stats.opponent(df_all, team)]
data

predictions: dict[str, list[int,int]] = {}
correct_predictions = {}

i = 0
for rodada in range(5, len(rodadas)):
    for p in rodadas[rodada]:
        
        home = p[0]
        away = p[1]

        home_stats, home_opponent = data[home]
        away_stats, away_opponent = data[away]
        
        home_pred = (sum(home_stats) / len(home_stats) + sum(away_opponent) / len(away_opponent)) / 2
        away_pred = (sum(away_stats) / len(away_stats) + sum(home_opponent) / len(home_opponent)) / 2

        match = f'{home} x {away}'
        predictions[match] = {
            "Predict": [home_pred, away_pred],
            "Result": [data[home][0][i+5], data[away][0][i+5]]
        }

        # if abs(predictions[match]["Predict"][0] - predictions[match]["Result"][0]) < 1 or abs(predictions[match]["Predict"][1] - predictions[match]["Result"][1]) < 1:
        #     correct_predictions[match] = predictions[match]
        if predictions[match]["Result"][0] >= predictions[match]["Predict"][0] or predictions[match]["Result"][1] >= predictions[match]["Predict"][1]:
            correct_predictions[match] = predictions[match]

    i += 1

print(len(correct_predictions))
# correct_predictions