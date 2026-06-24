PRODUCTS = {
    1: {"name": "Ноутбук Lenovo", "price": 32000, "category": "electronics", "stock": 5},
    2: {"name": "Смартфон Samsung", "price": 18000, "category": "electronics", "stock": 0},
    3: {"name": "Навушники Sony", "price": 4500, "category": "electronics", "stock": 12},
    4: {"name": "Футболка Nike", "price": 800, "category": "clothing", "stock": 30},
    5: {"name": "Джинси Levi's", "price": 2200, "category": "clothing", "stock": 8},
    6: {"name": "Книга 'Clean Code'", "price": 650, "category": "books", "stock": 15},
    7: {"name": "Книга 'Django для початківців'", "price": 480, "category": "books", "stock": 3},
}
ORDERS = [] # сюди будемо додавати замовлення
 
VALID_CATEGORIES = {"electronics", "clothing", "books"}
 
CATEGORY_NAMES = {
    "electronics": "Електроніка",
    "clothing": "Одяг",
    "books": "Книги",
}