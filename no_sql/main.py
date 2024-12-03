from pymongo import MongoClient
from pymongo.server_api import ServerApi

client = MongoClient(
    "mongodb+srv://sizovanton:SZnLeadlQNFIGIAd@cluster0.aclvi.mongodb.net/cats?retryWrites=true&w=majority&appName=Cluster0",
    server_api=ServerApi('1')
)

db = client.cats

# result_one = db.cats.insert_one(
#     {
#         "name": "barsik",
#         "age": 3,
#         "features": ["ходить в капці", "дає себе гладити", "рудий"],
#     }
# )

# result_many = db.cats.insert_many(
#     [
#         {
#             "name": "Lama",
#             "age": 2,
#             "features": ["ходить в лоток", "не дає себе гладити", "сірий"],
#         },
#         {
#             "name": "Liza",
#             "age": 4,
#             "features": ["ходить в лоток", "дає себе гладити", "білий"],
#         },
#     ]
# )

# Функція для отримання всіх записів з ДБ
def get_all_cats():
    try:
        result = db.cats.find({})

        found = False  
        for el in result:
            print(el)
            found = True
        
        if not found:
            return "Колекція 'cats' не містить жодного документа."

        return "Всі документи успішно виведені."

    except Exception as e:
       
        return f"Виникла помилка: {e}"

# get_all_cats()

# Функція знаходження кота за іменем
def get_one(name):
    try:
        if not name:
            return "Ім'я кота є обов'язковим параметром."
    
        result = db.cats.find_one({"name": name})

        return result
    except Exception as e:
        return f"Виникла помилка: {e}"

# get_one("Lama")

# Функція оновлення віку кота за ім'ям
def update_age(name, new_age):
    try:
        if not name or new_age is None:
            return "Ім'я кота та новий вік є обов'язковими параметрами."

        if not isinstance(new_age, int) or new_age < 0:
            return "Вік кота повинен бути додатним числом."
        
        result = db.cats.update_one({'name': name}, {'$set': {'age': new_age}})
         
        if result.matched_count == 0:
            return f"Кота з ім'ям '{name}' не знайдено."
        if result.modified_count == 0:
            return f"Вік кота '{name}' вже дорівнює {new_age}."
        
        return f"Вік кота '{name}' успішно оновлено до {new_age}."
        
    except Exception as e:
        return f'Виникла помилка {e}'

# print(update_age('La', 6))
# get_one("Lama")

# Оновлює список features для кота за його іменем, додаючи нову характеристику
def update_features(name, new_feature):
    try:
        if not name or not new_feature:
            return "Ім'я кота та нова характеристика є обов'язковими параметрами."
        
        result = db.cats.update_one({'name': name},
        {'$addToSet': {'features': new_feature}})

        if result.matched_count == 0:
            return f"Кота з ім'ям '{name}' не знайдено."
        if result.modified_count == 0:
            return f"Характеристика '{new_feature}' вже є у списку features кота '{name}'."
            
        return f"Характеристика '{new_feature}' успішно додана до кота '{name}'."
            
    except Exception as e:
        return f'Виникла помилка {e}'
    
# print(update_features("Lama", 'танцює'))

# Видалення кота за ім'ям
def delete_one_cat(name):
    try:
        if not name:
            return "Ім'я кота є обов'язковим параметром."

        result = db.cats.delete_one({'name': name})

        if result.deleted_count == 0:
            return f"Кота з ім'ям '{name}' не знайдено в колекції."
        
        return f"Кота з ім'ям '{name}' успішно видалено."

    except Exception as e:
        return f'Виникла помилка {e}'
    
# print(delete_one_cat('barsik'))

def delete_all():
    try:
        result = db.cats.delete_many({})

        if result.deleted_count == 0:
            return "Колекція 'cats' вже порожня."
        
        return f"Успішно видалено {result.deleted_count} записів з колекції 'cats'."

    except Exception as e:
        return f"Виникла помилка: {e}"
    
# delete_all()
    