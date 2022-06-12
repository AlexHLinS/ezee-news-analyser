## Приложение для проверки фейковых новостей

Используемые технологии

- Frontend: <code>in progress...</code>
- Backend: FastAPI
- Data Science: <code>in progress...</code>
- Data Base:  <code>in progress...</code>

### Структура репозитория:
- Frontend: исходные файлы клиентской части
- Backend: исходные файлы серверной части
- data_science: исходные файлы анализа данных и генерации свойств
- hypotheses: ноутбуки, скрипты и т.п. для проверки гипотез, прототипов и т.п.

### Структура приложения

Смотри [описание структуры приложения](app_description.md).

### Функции:

- Проверка новости по url, либо тексту

### Запуск на локальной машине:

#### Фронтенд:
1) Перейти в директорию frontend  
2) Установить зависимости:  
```bash
npm install
```  
3) Запустить проект в режиме разработки:  
```bash  
npm start  
```  
#### Бэкенд:  
1) Перейти в директорию backend  
2) Установить зависимости
```bash
python -m venv venv
venv/Scripts/Activate - для Win
source /venv/bin/Activate - для Nix 
pip install -r requirements.txt
```  
3) Запустить проект в режиме разработки:  
```bash
uvicorn main:app
```
Будут доступны следующие страницы приложения:

| Адрес                      | Содержание:                  |
|----------------------------|------------------------------|
| http://localhost:3000      | Основная страница приложения |        
| http://localhost:8000/docs | Документация API бекенда     |

#### Data Science:  
1) Перейти в директорию data_science  
2) Установить зависимости
```bash
conda create --name ezee-news-analyser-ds python=3.9
conda activate ezee-news-analyser-ds
pip install jupyter
pip install natasha
conda install pandas
pip install plotly
pip install dostoevsky
python -m dostoevsky download fasttext-social-network-model
pip install pyyaml
pip install -U scikit-learn
pip install nltk
pip install translate
pip install openpyxl
```      

