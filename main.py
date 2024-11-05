"""Executa o programa"""

def main():

    print('Inicializando...')
    from database import MainTournaments
    
    main_tournaments = MainTournaments()
    t = main_tournaments.input()
    season = t.input()
    rounds = season.input()
    for round in rounds:
        for match in round.load():
            match.save()


if __name__ == '__main__':
    main()