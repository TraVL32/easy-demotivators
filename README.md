# easy-demotivators

Небольшая библиотека на Pillow для генерации демотиваторов. Python 3.11+.

## Установка

```bash
pip install git+https://github.com/TraVL32/demotivator.git
```

## Использование

```python
from demotivator import create_demotivator, DemotivatorStyle

style = DemotivatorStyle(title_font="assets/fonts/times.ttf", upper=True)
img = create_demotivator("photo.jpg", "ЗАГОЛОВОК", "подпись поменьше", style)
img.save("out.jpg")
```

Принимает путь, `bytes`, файловый объект или `PIL.Image`. `demotivator_bytes(...)` возвращает готовые байты.

### aiogram 3

```python
import asyncio
from aiogram.types import BufferedInputFile
from demotivator import demotivator_bytes

data = await asyncio.to_thread(demotivator_bytes, photo_bytes, "Текст", "Подпись")
await message.answer_photo(BufferedInputFile(data, "demot.jpg"))
```

Генерация синхронная, поэтому в боте вызывай её через `asyncio.to_thread`.

### CLI

```bash
demotivator in.jpg out.jpg -t "Заголовок" -s "Подпись" --upper
```

## Шрифты

Если шрифт не указан, ищутся Times New Roman, Liberation Serif и DejaVu Serif, иначе берётся встроенный шрифт Pillow. Для кириллицы лучше передать свой `.ttf`.

## Лицензия

MIT
