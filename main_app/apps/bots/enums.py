from enum import Enum, unique

@unique
class CountryEnum(str, Enum):
    russia = 'russia'
    belarus = 'belarus'
    china = 'china'
    usa = 'usa'
