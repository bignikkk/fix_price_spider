### FIX_SPIDER

FIX_SPIDER - парсер, созданный с использованием Scrapy, для магазина FixPrice.


### Автор:
Автор: Nikita Blokhin
GitHub: github.com/bignikkk

### Технологии:

Python
Scrapy

### Как развернуть проект локально:

```
git clone https://github.com/bignikkk/fix_spider
```

```
cd fix_price_spider
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас windows

    ```
    source env/scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Запустить парсер со сбором данных в файл JSON:

```
scrapy crawl fixprice -o output.json
