from unittest import TestCase, main
import chempionat_ru_parser
import parsing_functions
import start
from bs4 import BeautifulSoup as Bs


class TestParsing(TestCase):
    with open('../assets/HtmlStatTagWithPenalty.txt', 'r', encoding="utf-8") as handler: StatTagHtml = handler.read()
    Soup = Bs(StatTagHtml, 'html.parser')
    StatTag = Soup.find('div', attrs={'data-type': 'stats'})

    def test_GetGoalsStatWithPenalty(self):
        Goals = chempionat_ru_parser.GetGoalsStat(self.StatTag)
        PenaltyStates = [g['IsPenalty'] for g in Goals]
        self.assertIn(True, PenaltyStates)

    def test_GetGoalsStatWithAutoGoal(self):
        Goals = chempionat_ru_parser.GetGoalsStat(self.StatTag)
        PenaltyStates = [g['IsAuto'] for g in Goals]
        self.assertIn(True, PenaltyStates)

    # def test_GetPenalties(self):
    #     Root = chempionat_ru_parser.Node(key=chempionat_ru_parser.ParsingTypes.root)
    #     Lineups = chempionat_ru_parser.GetLineups(self.Soup)
    #     Root.AddChildren(Lineups[0])
    #     Root.AddChildren(Lineups[1])
    #     for penalty in chempionat_ru_parser.GetPenalties(self.StatTag):
    #         Penalty = chempionat_ru_parser.Node(key=chempionat_ru_parser.ParsingTypes.Penalty, data={k: v for k, v in penalty.items()})
    #         Lineup = Root.search_node(penalty['PlayerId'], 'Id', chempionat_ru_parser.ParsingTypes.Lineup)
    #         if Lineup: Lineup.set_child(Penalty)
    #
    #
    #     PenaltyStates = [g['IsAuto'] for g in Goals]
    #     self.assertIn(True, PenaltyStates)


if __name__ == '__main__':
    main()
