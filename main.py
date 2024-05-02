import streamlit as st
import sqlite3

# Define class Inventory
class Inventory:
    def __init__(self):
        # Connect to SQLite database
        self.conn = sqlite3.connect('inventory.db')
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                            name TEXT PRIMARY KEY,
                            weight REAL,
                            quantity INTEGER
                          )''')
        self.conn.commit()

    def add_product_to_db(self, name, weight, quantity):
        cursor = self.conn.cursor()
        cursor.execute('''INSERT OR REPLACE INTO products (name, weight, quantity)
                          VALUES (?, ?, ?)''', (name, weight, quantity))
        self.conn.commit()

    def sell_product_from_db(self, name, quantity):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT quantity FROM products WHERE name=?''', (name,))
        row = cursor.fetchone()
        if row:
            available_quantity = row[0]
            if available_quantity >= quantity:
                cursor.execute('''UPDATE products SET quantity = quantity - ? WHERE name=?''', (quantity, name))
                self.conn.commit()
                st.write(f"{quantity} units of {name} sold.")
            else:
                st.write("Not enough stock available.")
        else:
            st.write("Product not found in inventory.")

    # Retrieving product names
    def get_product_names(self):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT name FROM products''')
        rows = cursor.fetchall()
        return [row[0] for row in rows]

# Custom theme and styling code
st.set_page_config(
    page_title="Inventory Management App",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Initialize inventory
inventory = Inventory()

# Define App sections
header = st.container()
sidebar = st.sidebar.container()
current_stock = st.container()

with header:
    header.markdown('### **Streamlit Inventory Tracker: Automated SQLite Database Support**')
    st.image('image/taifa2image.jpg')
    header.markdown('-----')

# Sidebar for adding products
with sidebar:
    st.header("Addition or Sale of Products from Database")
    st.subheader('**Add Product**')

    product_name = st.text_input("Product Name")
    product_weight = st.number_input("Product Weight (kg)", min_value=0.5, step=0.5)
    product_quantity = st.number_input("Quantity", min_value=0, step=1)

    if st.button("Add Product"):
        inventory.add_product_to_db(product_name, product_weight, product_quantity)

# Sidebar for selling products
with sidebar:
    st.subheader("**Sell Product**")

    product_names = inventory.get_product_names()
    sell_product_name = st.selectbox("Product Name", product_names)
    sell_product_quantity = st.number_input("Quantity to Sell", min_value=1, step=1)

    if st.button("Sell Product"):
        inventory.sell_product_from_db(sell_product_name, sell_product_quantity)

# Display current inventory
with current_stock:
    st.subheader("**Current Inventory**")
    st.markdown('##### **Inventory remaining after successful Product Addition or Sale**')

    cursor = inventory.conn.cursor()
    cursor.execute('''SELECT * FROM products''')
    rows = cursor.fetchall()
    for row in rows:
        name, weight, quantity = row
        st.write(f"{name}: {quantity} units, {weight} kg each")
