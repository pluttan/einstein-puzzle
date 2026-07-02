![Header](header.png)

<div align="center">

# einstein_puzzle

**Процедурный генератор головоломок Эйнштейна до 100x100**

[![License](https://img.shields.io/badge/license-MIT-2C2C2C?style=for-the-badge&labelColor=1E1E1E)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12-2C2C2C?style=for-the-badge&logo=python&labelColor=1E1E1E)]()

</div>

Генерирует логические головоломки в стиле загадки Эйнштейна (Zebra Puzzle) произвольного размера — от классических 5x5 до 100x100 и более. Каждая сгенерированная головоломка гарантированно имеет единственное решение, проверяемое встроенным CSP-солвером с поразрядным распространением ограничений и возвратом. Без внешних зависимостей.

## ■ Возможности

- ❖ **Произвольный размер** — головоломки NxM (N домов, M категорий) от 2x2 до 200x200
- ❖ **Несколько типов подсказок** — один дом, сосед, левее, абсолютная позиция
- ❖ **Гарантированно единственное решение** — CSP-солвер проверяет ровно одно допустимое присвоение
- ❖ **Поразрядный солвер** — распространение ограничений с bitmask-доменами для производительности на больших размерах
- ❖ **Адаптивная генерация** — spanning-tree + минимизация для малых N, звёздная топология для N > 10
- ❖ **Уровни сложности** — easy (больше подсказок), medium, hard (минимальный набор подсказок)
- ❖ **Двойной вывод** — читаемый текст (на русском) для N ≤ 15, JSON для бо́льших головоломок
- ❖ **Воспроизводимость** — параметр seed для детерминированной генерации
- ❖ **Ноль зависимостей** — чистый Python, pip install не требуется

## ■ Стек

<div align="center">

| Компонент | Технология |
|-----------|------------|
| Язык | Python 3.12 |
| Солвер | CSP (constraint propagation + backtracking) |
| Домены | Bitmask representation |
| Вывод | Text (Russian), JSON |

</div>

## ■ Скриншоты

<div align="center">

![Screenshot](screenshots/main.png)

*Основной вывод головоломки — сгенерированная головоломка Эйнштейна 5x5 в текстовом формате*

</div>

## ■ Запуск

```bash
make install      # создать venv (зависимости не нужны)
make run          # сгенерировать головоломку 5x5 по умолчанию
make test         # запустить тесты солвера / генератора

# Произвольные размеры
python3.12 -m src.main -n 5                          # классические 5x5
python3.12 -m src.main -n 10 --seed 42               # 10x10 с seed
python3.12 -m src.main -n 100 --format json          # 100x100 (JSON)
python3.12 -m src.main -n 5 --difficulty easy        # больше подсказок
python3.12 -m src.main -n 8 -m 5                      # 8 домов, 5 категорий
python3.12 -m src.main -n 5 --format both -o out.txt  # текст + JSON в файл
```

## ■ Project Structure

```
src/
├── main.py         — CLI entry point
├── model.py        — core data structures + bitmask utilities
├── clues.py        — clue types and constraint index
├── solver.py       — CSP solver (bitmask domains, propagation, backtracking)
├── generator.py    — puzzle generation (spanning tree / star topology)
├── vocabulary.py   — themed word lists and name generation
├── formatter.py    — text (Russian) and JSON output
├── test_solver.py  — solver / generator / round-trip tests
└── __init__.py
```

## ■ License

MIT © [pluttan](https://github.com/pluttan)
