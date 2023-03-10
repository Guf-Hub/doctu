# Parser doctu.ru/msk 
Парсер на Python >= **3.9** для сбора данных о клиниках и врачах Москвы и МО с сайта [doctu.ru](https://doctu.ru/msk).<br/>

[![Donate](https://img.shields.io/badge/Donate-Yoomoney-green.svg)](https://yoomoney.ru/to/410019620244262)
![GitHub last commit](https://img.shields.io/github/last-commit/Guf-Hub/doctu)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/Guf-Hub/doctu)
![lang](https://img.shields.io/badge/lang-Python-red)

### Установка
Скачать файлы:
```bash
git clone https://github.com/Guf-Hub/doctu.git
```
Обновить pip:
```bash
pip install --upgrade pip
```
Установить зависимости:
```bash
pip install -r requirements.txt
```

### Сбор данных о клиниках
**doctu_clinics.py**
* clinic(True) - сбор данных с 0, для первого запуска;
* clinic(False) - по последнему списку ссылок полученных с сайта, при первом запуске.
```Python
if __name__ == "__main__":
    clinic(True)
```
### Сбор данных о докторах
**doctu_doctors.py**
* doctors(True) - сбор данных с 0, для первого запуска;
* doctors(False) - по последнему списку ссылок полученных с сайта, при первом запуске.
```Python
if __name__ == "__main__":
    doctors(True)
```