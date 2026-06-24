from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .data import PRODUCTS, ORDERS, VALID_CATEGORIES, CATEGORY_NAMES
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

# Доможні функції
def product_to_dict(product_id, product):
    """Перетворює товар у словник для JSON-відповіді."""
    return {
        "id": product_id,
        "name": product["name"],
        "price": product["price"],
        "category": product["category"],
        "stock": product["stock"],
        "available": product["stock"] > 0,
    }


def apply_filters(products_dict, sort=None, in_stock=False):
    """Застосовує фільтри та сортування до словника товарів."""
    items = [product_to_dict(pid, p) for pid, p in products_dict.items()]

    if in_stock:
        items = [p for p in items if p["available"]]

    if sort == "price_asc":
        items.sort(key=lambda p: p["price"])
    elif sort == "price_desc":
        items.sort(key=lambda p: p["price"], reverse=True)
    elif sort == "name":
        items.sort(key=lambda p: p["name"])

    return items


# View функціі
def home(request):
    """ Завдання 2 — Головна сторінка """
    totalProducts = len(PRODUCTS)

    return HttpResponse(f"""
                        <h1>My Store</h1>
                        <p>Товарів: {totalProducts}</p>
                        <a href="/store/">Каталог</a>
                        <a href="/store/search">Пошук</a>
                        <a href="/store/orders">Замовлення</a>
                        """)

def product_list(request):
    """ Завдання 3 — Каталог товарів з фільтрацією """
    sort = request.GET.get("sort", "")
    in_stock = request.GET.get("in_stock") == "1"

    products = apply_filters(PRODUCTS, sort = sort, in_stock = in_stock)

    return JsonResponse({
        "filters":{
            "sort": sort or None,
            "in_stock": in_stock
        },
        "count": len(products),
        "products": products
    }, json_dumps_params = {"ensure_ascii": False, "indent": 2})


def product_detail(request, product_id):
    """Завдання 4 — Деталі товару"""
    product = PRODUCTS.get(product_id)
    if product is None:
        return JsonResponse(
            {"error": "Товар не знайдено"}, 
            status=404, 
            json_dumps_params={"ensure_ascii": False, "indent": 2}
            )
    return JsonResponse(
        product_to_dict(product_id, product),
        json_dumps_params={"ensure_ascii": False, "indent": 2}
    )


@csrf_exempt
def order_views(request, product_id):
    """Завдання 7 — Оформлення замовлення"""
    product = PRODUCTS.get(product_id)
    if product is None:
        return JsonResponse(
            {"error": "Товар не знайдено"}, 
            status=404, 
            json_dumps_params={"ensure_ascii": False, "indent": 2}
        )
        
    if request.method == "GET":
        return HttpResponse(f"""
                <h1>Оформлення замовлення для {product["name"]}</h1>
                <form method="POST">
                    <input type="text" name="name" placeholder="Ім'я"> <br>
                    <input type="text" name="phone" placeholder="Телефон"> <br>
                    <input type="text" name="quantity" placeholder="Кількість"> <br>
                    <button>Оформити замовлення</button>
                </form>
        """)
        
    if request.method == "POST":
        if product["stock"] == 0:
            return JsonResponse(
                {"error": "Товара немає на складі"}, 
                status=400, 
                json_dumps_params={"ensure_ascii": False, "indent": 2}
            )
            
        errors = {}
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        quantity_req = request.POST.get("quantity", "").strip()
        
        if not name:
            errors["name"] = "Ім'я є обов'язковим полем"
            
        if not phone:
            errors["phone"] = "Телефон є обов'язковим полем"
        elif not (10 <= len(phone) <= 13):
            errors["phone"] = "Телефон повинен бути довжиною від 10 до 13 символів"
            
        quantity = None
        if not quantity_req:
            errors["quantity"] = "Кількість є обов'язковим полем"
        else:
            try:
                quantity = int(quantity_req)
                if quantity <= 0:
                    errors["quantity"] = "Кількість має бути цілим числом > 0"
                elif quantity > product["stock"]:
                    errors["quantity"] = f"Кількість не може перевищувати наявну кількість товару ({product['stock']})"
            except ValueError:
                errors["quantity"] = "Кількість має бути цілим числом > 0"

        if errors:
            return JsonResponse(
                {"errors": errors}, 
                status=400, 
                json_dumps_params={"ensure_ascii": False, "indent": 2}
            )

        order = {
            "order_id": len(ORDERS) + 1,
            "product_id": product_id,
            "product_name": product["name"],
            "quantity": quantity,
            "total_price": quantity * product["price"],
            "customer_name": name,
            "phone": phone,
        }
        ORDERS.append(order)
        return redirect("order_list")
    

def order_list(request):
    """Завдання 8 — Список замовлень"""    
    if not ORDERS:
        return JsonResponse(
            {"message": "Замовлень поки немає", "orders": []}, 
            json_dumps_params={"ensure_ascii": False, "indent": 2})
    return JsonResponse(
        {
            "count": len(ORDERS),
            "orders": ORDERS
        },
        json_dumps_params={"ensure_ascii": False, "indent": 2}
    )


def category_view(request, category):
    """Завдання 5 — Фільтрація за категорією"""
    
    if category not in VALID_CATEGORIES:
        return JsonResponse(
            {"error": "Невідома категорія"}, 
            status=400, 
            json_dumps_params={"ensure_ascii": False, "indent": 2}
        )

    products = [
        product_to_dict(pid, p) 
        for pid, p in PRODUCTS.items() 
        if p["category"] == category
    ]
    
    return JsonResponse({
        "category": category,
        "category_name": CATEGORY_NAMES.get(category),
        "count": len(products),
        "products": products
    }, json_dumps_params={"ensure_ascii": False, "indent": 2})


def search_view(request):
    """Завдання 6 — Пошук товарів"""

    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse(
            {"error": "Вкажіть пошуковий запит"},
            status=400,
            json_dumps_params={"ensure_ascii": False, "indent": 2}
        )

    products = [
        product_to_dict(pid, p)
        for pid, p in PRODUCTS.items()
        if query.lower() in p["name"].lower()
    ]

    return JsonResponse({
        "query": query,
        "count": len(products),
        "products": products
    }, json_dumps_params={"ensure_ascii": False, "indent": 2})


def old_catalog(request):
    """Завдання 9 — Переадресація застарілого маршруту"""
    response = redirect("product_list", permanent=True)
    response['X-Redirect-Reason'] = 'page-deprecated'
    return response
