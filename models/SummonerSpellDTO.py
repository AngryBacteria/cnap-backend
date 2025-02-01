from models.GlobalPydanticConfig import BaseConfig


class SummonerSpellDTO(BaseConfig):
    id: int
    name: str
    description: str
    summonerLevel: int
    cooldown: int
    gameModes: list[str]
    iconPath: str
