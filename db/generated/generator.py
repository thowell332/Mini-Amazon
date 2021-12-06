from werkzeug.security import generate_password_hash
import csv
from faker import Faker

num_accounts = 100
num_sellers = 20
num_categories = 20
num_products = 2000
num_products_per_seller = 50
num_items_per_seller = 10
num_purchases = 500
num_reviews = 500
num_carts = 100

Faker.seed(0)
fake = Faker()

def get_csv_writer(f):
    return csv.writer(f, dialect='unix')

def gen_accounts(num_accounts):
    with open('Account.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Users...', end=' ', flush=True)
        for uid in range(num_accounts):
            if uid % 10 == 0:
                print(f'{uid}', end=' ', flush=True)
            profile = fake.profile()
            email = profile['mail']
            plain_password = f'pass{uid}'
            password = generate_password_hash(plain_password)
            name_components = profile['name'].split(' ')
            firstname = name_components[0]
            lastname = name_components[-1]
            address = profile['address']
            address.replace("\n", " ")
            balance = 0
            writer.writerow([email, firstname, lastname, address, balance, password])
        print(f'{num_accounts} generated')
    return

def gen_sellers(num_sellers):
    sellers = []
    with open('Seller.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Sellers...', end=' ', flush=True)
        while len(sellers) != num_sellers:
            if len(sellers) % 10 == 0:
                print(f'{len(sellers)}', end=' ', flush=True)
            seller_id = fake.random_int(min=1, max=num_sellers)
            if seller_id not in sellers:
                writer.writerow([seller_id])
                sellers.append(seller_id)
        print(f'{num_sellers} generated')
    return sellers

def gen_categories(num_categories):
    categories = []
    with open('Category.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Categories...', end=' ', flush=True)
        for cat in range(num_categories):
            if cat % 10 == 0:
                print(f'{cat}', end=' ', flush=True)
            category = fake.unique.word()
            writer.writerow([category])
            categories.append(category)
        fake.unique.clear()
        print(f'{num_categories} generated')
    return categories

def gen_products(num_products, cat):
    available_pids = []
    with open('Product.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Products...', end=' ', flush=True)
        for pid in range(num_products):
            if pid % 100 == 0:
                print(f'{pid}', end=' ', flush=True)
            name = fake.unique.sentence(nb_words=4)[:-1]
            owner_id = fake.random_element(elements=sellers)
            description = fake.text(max_nb_chars=128)
            image = fake.image_url()
            category = fake.random_element(elements=cat)
            writer.writerow([owner_id, description, name, image, category])
            available_pids.append(pid+1)
        print(f'{num_products} generated; {len(available_pids)} available')
    return available_pids

def gen_sellsProduct(num_products_per_seller, sell, pids):
    products_sold = []
    with open('SellsProduct.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('SellsProduct...', end=' ', flush=True)
        for seller_id in sell:
            if seller_id % 10 == 0:
                print(f'{seller_id}', end=' ', flush=True)
            prods = []
            for product in range(fake.random_int(min=0, max=num_products_per_seller)):
                product_id = fake.random_element(elements=pids)
                price = f'{str(fake.random_int(max=500))}.{fake.random_int(max=99):02}'
                if product_id not in prods:
                    writer.writerow([seller_id, product_id, price])
                    products_sold.append([seller_id, product_id])
                prods.append(product_id)
            print(f'{seller_id}', end=' ', flush=True)
        print('done')
    return products_sold

def gen_sellsItem(num_items_per_seller, prods):
    items_sold = []
    with open('SellsItem.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('SellsItem...', end=' ', flush=True)
        for product in prods:
            seller_id = product[0]
            product_id = product[1]
            last_item_id = 0
            for item in items_sold:
                if item[1] == product_id:
                    if item[2] > last_item_id:
                        last_item_id = item[2]
            mi = last_item_id
            ma = last_item_id + num_items_per_seller
            for item_id in range(mi, fake.random_int(min=mi, max=ma)):
                writer.writerow([seller_id, product_id, item_id+1])
                items_sold.append([seller_id, product_id, item_id+1])
        print(f'all items generated')
    return items_sold

def gen_purchases(num_purchases, pids, num_users, itemssold):
    purchases = []
    with open('Purchases.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Purchases...', end=' ', flush=True)
        p = []
        for id in range(num_purchases):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            uid = fake.random_int(min=1, max=num_users)
            pid = fake.random_element(elements=pids)
            available_items = 0
            for item in itemssold:
                if item[1]==pid:
                    available_items += 1
            item_id = fake.random_int(max=available_items)
            status = 'ordered'
            purchase_id = fake.random_int(min=1, max=num_purchases)
            time_purchased = fake.date_time()
            if pid not in p and item_id != 0:
                writer.writerow([uid, pid, item_id, purchase_id, status, time_purchased])
                purchases.append([uid, pid, item_id])
            p.append(pid)
        print(f'{num_purchases} generated')
    return purchases

def gen_Reviews(num_reviews, purchases, items_sold):
    reviews = []
    with open('SellerReview.csv', 'w') as f:
        with open('ProductReview.csv', 'w') as g:
            seller_writer = get_csv_writer(f)
            product_writer = get_csv_writer(g)
            print('SellerReviews...', end=' ', flush=True)
            for review in range(num_reviews):
                purchase = fake.random_element(elements=purchases)
                buyer_id = purchase[0]
                if buyer_id in reviews:
                    continue
                product_id = purchase[1]
                item_id = purchase[2]
                seller_id = 0
                for items in items_sold:
                    if items[1] == product_id and items[2] == item_id:
                        seller_id = items[0]
                num_stars1 = fake.random_int(min=0, max=5)
                num_stars2 = fake.random_int(min=0, max=5)
                date1 = fake.date_time()
                date2 = fake.date_time()
                description1 = fake.paragraph(nb_sentences=5)
                description2 = fake.paragraph(nb_sentences=5)
                seller_writer.writerow([buyer_id, seller_id, num_stars1, date1, description1])
                product_writer.writerow([buyer_id, product_id, num_stars2, date2, description2])
                reviews.append(buyer_id)
            print(f'{num_reviews} Reviews generated')
    return

def gen_cart(num_carts, num_accounts, items_sold):
    print('items sold')
    print(items_sold)
    with open('Cart.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Cart...', end=' ', flush=True)
        for cart in range(num_carts):
            if cart % 10 == 0:
                print(f'{cart}', end=' ', flush=True)
            buyer_id = fake.random_int(min=1, max= num_accounts)
            item = fake.random_element(elements=items_sold)
            seller_id = item[0]
            product_id = item[1]
            available_items = 0
            for i in items_sold:
                if seller_id == i[0] and product_id == i[1]:
                    available_items += 1
            quantity = fake.random_int(max=available_items)
            saved_for_later = fake.boolean()
            writer.writerow([buyer_id, seller_id, product_id, quantity, saved_for_later])
        print(f'{num_carts} carts generated')
    return

#gen_accounts(num_accounts)
sellers = gen_sellers(num_sellers)
categories = gen_categories(num_categories)
available_pids = gen_products(num_products, categories)
products_sold = gen_sellsProduct(num_products_per_seller, sellers, available_pids)
items_sold = gen_sellsItem(num_items_per_seller, products_sold)
purchases = gen_purchases(num_purchases, available_pids, num_accounts, items_sold)
gen_Reviews(num_reviews, purchases, items_sold)
gen_cart(num_carts, num_accounts, items_sold)