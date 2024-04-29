import streamlit as st
import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Inventory:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_DATABASE")
        )
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                            name VARCHAR(255) PRIMARY KEY,
                            weight INT,
                            quantity INT
                          )''')
        self.conn.commit()

    def add_product_to_db(self, name, weight, quantity):
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO products (name, weight, quantity)
                          VALUES (%s, %s, %s)
                          ON DUPLICATE KEY UPDATE
                          weight = VALUES(weight),
                          quantity = quantity + VALUES(quantity)''', (name, weight, quantity))
        self.conn.commit()

    def sell_product_from_db(self, name, quantity):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT quantity FROM products WHERE name=%s''', (name,))
        row = cursor.fetchone()
        if row:
            available_quantity = row[0]
            if available_quantity >= quantity:
                cursor.execute('''UPDATE products SET quantity = quantity - %s WHERE name=%s''', (quantity, name))
                self.conn.commit()
                st.write(f"{quantity} units of {name} sold.")
            else:
                st.write("Not enough stock available.")
        else:
            st.write("Product not found in inventory.")

    def get_product_names(self):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT name FROM products''')
        rows = cursor.fetchall()
        return [row[0] for row in rows]

# Initialize inventory
inventory = Inventory()

# Sidebar for adding products
st.sidebar.header("Add Product")
product_name = st.sidebar.text_input("Product Name")
product_weight = st.sidebar.number_input("Product Weight (kg)", min_value=0.5, step=0.5)
product_quantity = st.sidebar.number_input("Quantity", min_value=0, step=1)
if st.sidebar.button("Add Product"):
    inventory.add_product_to_db(product_name, product_weight, product_quantity)

# Sidebar for selling products
st.sidebar.header("Sell Product")
product_names = inventory.get_product_names()
sell_product_name = st.sidebar.selectbox("Product Name", product_names)
sell_product_quantity = st.sidebar.number_input("Quantity to Sell", min_value=1, step=1)
if st.sidebar.button("Sell Product"):
    inventory.sell_product_from_db(sell_product_name, sell_product_quantity)

# Display current inventory
st.write("Current Inventory:")
cursor = inventory.conn.cursor()
cursor.execute('''SELECT * FROM products''')
rows = cursor.fetchall()
for row in rows:
    name, weight, quantity = row
    st.write(f"{name}: {quantity} units, {weight} kg each")
