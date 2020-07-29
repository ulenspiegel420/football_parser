from enum import Enum


class ParseSource(Enum):
    file = 0
    championat_com = 1


class Entity(Enum):
    source = 0
    season_link = 1


class Sport(Enum):
    football = 0
