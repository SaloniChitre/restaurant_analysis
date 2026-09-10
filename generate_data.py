



#!/usr/bin/env python
# coding: utf-8

# In[ ]:





# In[4]:


import sqlite3
import numpy as np
from faker import Faker
from datetime import date, timedelta

fake = Faker()
Faker.seed(42)
np.random.seed(42)

conn = sqlite3.connect("restaurant.db")
cur = conn.cursor()

cur.executescript("""
DROP TABLE IF EXISTS locations; DROP TABLE IF EXISTS dishes;
DROP TABLE IF EXISTS ingredients; DROP TABLE IF EXISTS dish_ingredients;
DROP TABLE IF EXISTS orders; DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS labor_hours; DROP TABLE IF EXISTS customers;

CREATE TABLE locations (location_id INTEGER PRIMARY KEY, location_name TEXT, region TEXT, open_date DATE);
CREATE TABLE dishes (dish_id INTEGER PRIMARY KEY, dish_name TEXT, category TEXT, menu_price REAL);
CREATE TABLE ingredients (ingredient_id INTEGER PRIMARY KEY, ingredient_name TEXT, unit_cost REAL, unit TEXT);
CREATE TABLE dish_ingredients (dish_id INTEGER, ingredient_id INTEGER, quantity_used REAL);
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, customer_name TEXT, email TEXT, signup_date DATE);
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, location_id INTEGER, order_date DATE, customer_id INTEGER);
CREATE TABLE order_items (order_item_id INTEGER PRIMARY KEY, order_id INTEGER, dish_id INTEGER, quantity INTEGER, item_price REAL);
CREATE TABLE labor_hours (employee_id INTEGER, location_id INTEGER, work_date DATE, hours_worked REAL, hourly_rate REAL);
""")


# --- Locations ---
regions = ["NJ-North", "NJ-South", "NY-Metro", "CT"]
locations = []
for i in range(1, 9):
    open_offset = np.random.randint(30, 900)
    city = fake.city()
    locations.append((i, f"{city} Location", np.random.choice(regions),
                       (date(2024,1,1) - timedelta(days=open_offset)).isoformat()))
cur.executemany("INSERT INTO locations VALUES (?,?,?,?)", locations)

# --- Dishes ---
dish_defs = [
    (1,"Grilled Chicken Sandwich","Entree",14.99),(2,"Classic Cheeseburger","Entree",13.99),
    (3,"Caesar Salad","Salad",11.99),(4,"Margherita Pizza","Entree",15.99),
    (5,"Fish Tacos","Entree",16.99),(6,"French Fries","Side",5.99),
    (7,"Chocolate Lava Cake","Dessert",8.99),(8,"Buffalo Wings","Appetizer",12.99),
]
cur.executemany("INSERT INTO dishes VALUES (?,?,?,?)", dish_defs)

# --- Ingredients ---
ing_defs = [
    (1,"Chicken Breast",3.20,"lb"),(2,"Beef Patty",2.80,"lb"),(3,"Romaine Lettuce",1.10,"lb"),
    (4,"Pizza Dough",0.90,"each"),(5,"Mozzarella",4.50,"lb"),(6,"Tilapia",5.20,"lb"),
    (7,"Potatoes",0.60,"lb"),(8,"Chocolate",6.00,"lb"),(9,"Chicken Wings",3.80,"lb"),
    (10,"Buns",0.35,"each"),(11,"Tomato Sauce",1.20,"lb"),(12,"Corn Tortillas",0.20,"each"),
]
cur.executemany("INSERT INTO ingredients VALUES (?,?,?,?)", ing_defs)

# --- Dish-Ingredient recipe mapping ---
dish_ing = [(1,1,0.35),(1,10,1),(2,2,0.35),(2,10,1),(3,3,0.25),(4,4,1),(4,5,0.3),
            (4,11,0.2),(5,6,0.3),(5,12,3),(6,7,0.5),(7,8,0.2),(8,9,0.6)]
cur.executemany("INSERT INTO dish_ingredients VALUES (?,?,?)", dish_ing)

# --- Customers (Faker) ---
customers = []
for cid in range(1000, 5000):
    customers.append((cid, fake.name(), fake.email(),
                       fake.date_between(start_date="-2y", end_date="today").isoformat()))
cur.executemany("INSERT INTO customers VALUES (?,?,?,?)", customers)

# --- Orders + Order Items (18 months, seasonal + weekend + growth trend) ---
start, end = date(2024,6,1), date(2025,12,1)
days = (end - start).days
order_id, oi_id = 1, 1
orders_rows, oi_rows, labor_rows = [], [], []

for loc_id,_,_,open_date_str in locations:
    open_d = date.fromisoformat(open_date_str)
    for d in range(days):
        cur_date = start + timedelta(days=d)
        if cur_date < open_d:
            continue
        dow_factor = 1.4 if cur_date.weekday() >= 4 else 1.0
        month_factor = 1.15 if cur_date.month in (11,12,7) else 1.0
        trend = 1 + (d/days)*0.15
        n_orders = int(np.random.poisson(18*dow_factor*month_factor*trend))
        for _ in range(n_orders):
            cust_id = np.random.randint(1000,5000)
            orders_rows.append((order_id, loc_id, cur_date.isoformat(), cust_id))
            for _ in range(np.random.randint(1,4)):
                dish_id = int(np.random.choice([x[0] for x in dish_defs]))
                qty = np.random.randint(1,3)
                price = next(x[3] for x in dish_defs if x[0]==dish_id)
                oi_rows.append((oi_id, order_id, dish_id, qty, price))
                oi_id += 1
            order_id += 1
        for _ in range(np.random.randint(8,15)):
            labor_rows.append((np.random.randint(1,200), loc_id, cur_date.isoformat(),
                                round(np.random.uniform(4,9),1), round(np.random.uniform(15.5,22),2)))

cur.executemany("INSERT INTO orders VALUES (?,?,?,?)", orders_rows)
cur.executemany("INSERT INTO order_items VALUES (?,?,?,?,?)", oi_rows)
cur.executemany("INSERT INTO labor_hours VALUES (?,?,?,?,?)", labor_rows)
conn.commit()
print(f"Locations: {len(locations)} | Customers: {len(customers)} | Orders: {len(orders_rows)} | Items: {len(oi_rows)} | Labor rows: {len(labor_rows)}")
conn.close()


# In[ ]:




