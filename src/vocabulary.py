"""Themed word lists and name generation for puzzle display."""

from __future__ import annotations
import random
from .model import PuzzleSpec


# ── Themed word lists (Russian) ──────────────────────────────────────────────
# Each list has up to 15 items for small-puzzle coverage.

CATEGORIES: dict[str, dict[str, list[str]]] = {
    "Национальность": {
        "name": "Национальность",
        "values": [
            "норвежец", "англичанин", "швед", "датчанин", "немец",
            "француз", "испанец", "итальянец", "японец", "китаец",
            "бразилец", "канадец", "австралиец", "индиец", "мексиканец",
        ],
    },
    "Цвет дома": {
        "name": "Цвет дома",
        "values": [
            "красный", "зелёный", "синий", "жёлтый", "белый",
            "оранжевый", "фиолетовый", "розовый", "чёрный", "серый",
            "бирюзовый", "коричневый", "бежевый", "бордовый", "салатовый",
        ],
    },
    "Напиток": {
        "name": "Напиток",
        "values": [
            "чай", "кофе", "молоко", "вода", "пиво",
            "сок", "вино", "какао", "лимонад", "квас",
            "кефир", "морс", "компот", "смузи", "эспрессо",
        ],
    },
    "Животное": {
        "name": "Животное",
        "values": [
            "кошка", "собака", "рыбка", "птица", "лошадь",
            "хомяк", "кролик", "черепаха", "попугай", "змея",
            "ящерица", "морская свинка", "хорёк", "шиншилла", "ёж",
        ],
    },
    "Сигареты": {
        "name": "Сигареты",
        "values": [
            "Marlboro", "Dunhill", "Rothmans", "Pall Mall", "Philip Morris",
            "Camel", "Lucky Strike", "Winston", "Kent", "Chesterfield",
            "Parliament", "Vogue", "Davidoff", "Sobranie", "L&M",
        ],
    },
    "Еда": {
        "name": "Еда",
        "values": [
            "пицца", "суши", "паста", "борщ", "стейк",
            "салат", "бургер", "плов", "тако", "рамен",
            "шаурма", "пельмени", "карри", "фалафель", "вареники",
        ],
    },
    "Хобби": {
        "name": "Хобби",
        "values": [
            "чтение", "рисование", "шахматы", "садоводство", "музыка",
            "фотография", "кулинария", "йога", "рыбалка", "вышивание",
            "танцы", "программирование", "велоспорт", "плавание", "кино",
        ],
    },
    "Профессия": {
        "name": "Профессия",
        "values": [
            "врач", "инженер", "учитель", "художник", "повар",
            "пилот", "юрист", "учёный", "архитектор", "журналист",
            "музыкант", "фермер", "писатель", "программист", "дизайнер",
        ],
    },
    "Музыка": {
        "name": "Музыка",
        "values": [
            "рок", "джаз", "классика", "поп", "блюз",
            "регги", "хип-хоп", "электроника", "фолк", "метал",
            "панк", "соул", "кантри", "латино", "инди",
        ],
    },
    "Транспорт": {
        "name": "Транспорт",
        "values": [
            "BMW", "Toyota", "Tesla", "Ford", "Audi",
            "Mercedes", "Volvo", "Honda", "Porsche", "Fiat",
            "Mazda", "Subaru", "Kia", "Hyundai", "Renault",
        ],
    },
    "Цветок": {
        "name": "Цветок",
        "values": [
            "роза", "тюльпан", "лилия", "ромашка", "орхидея",
            "пион", "гербера", "гвоздика", "ирис", "фиалка",
            "астра", "хризантема", "нарцисс", "лаванда", "подсолнух",
        ],
    },
    "Фрукт": {
        "name": "Фрукт",
        "values": [
            "яблоко", "банан", "апельсин", "манго", "виноград",
            "ананас", "персик", "груша", "киви", "лимон",
            "арбуз", "клубника", "вишня", "слива", "гранат",
        ],
    },
    "Спорт": {
        "name": "Спорт",
        "values": [
            "футбол", "теннис", "баскетбол", "хоккей", "волейбол",
            "бокс", "плавание", "лёгкая атлетика", "гимнастика", "гольф",
            "бадминтон", "регби", "крикет", "сквош", "фехтование",
        ],
    },
    "Одежда": {
        "name": "Одежда",
        "values": [
            "пиджак", "свитер", "футболка", "куртка", "пальто",
            "жилет", "плащ", "толстовка", "рубашка", "кардиган",
            "блейзер", "парка", "пончо", "анорак", "тренчкот",
        ],
    },
    "Инструмент": {
        "name": "Инструмент",
        "values": [
            "гитара", "пианино", "скрипка", "барабаны", "флейта",
            "саксофон", "виолончель", "труба", "арфа", "укулеле",
            "банджо", "аккордеон", "кларнет", "гобой", "контрабас",
        ],
    },
}


# ── Vocabulary builder ───────────────────────────────────────────────────────

def build_vocabulary(n: int, m: int) -> PuzzleSpec:
    """Build a PuzzleSpec with appropriate vocabulary for puzzle size."""
    cat_keys = list(CATEGORIES.keys())

    if n <= 15 and m <= len(cat_keys):
        # Use themed word lists
        selected_keys = random.sample(cat_keys, m)
        category_names = [CATEGORIES[k]["name"] for k in selected_keys]
        value_names = [CATEGORIES[k]["values"][:n] for k in selected_keys]
    else:
        # Use generated names for large puzzles
        category_names = [_gen_category_name(i) for i in range(m)]
        value_names = [_gen_value_names(i, n) for i in range(m)]

    return PuzzleSpec(
        n=n,
        m=m,
        category_names=category_names,
        value_names=value_names,
    )


def _gen_category_name(index: int) -> str:
    """Generate category name: Группа A, Группа B, ..."""
    if index < 26:
        return f"Группа {chr(ord('A') + index)}"
    hi = index // 26
    lo = index % 26
    return f"Группа {chr(ord('A') + hi - 1)}{chr(ord('A') + lo)}"


def _gen_value_names(cat_index: int, n: int) -> list[str]:
    """Generate value names: A1, A2, ... or AA1, AA2, ..."""
    if cat_index < 26:
        prefix = chr(ord('A') + cat_index)
    else:
        hi = cat_index // 26
        lo = cat_index % 26
        prefix = chr(ord('A') + hi - 1) + chr(ord('A') + lo)
    return [f"{prefix}{i + 1}" for i in range(n)]
