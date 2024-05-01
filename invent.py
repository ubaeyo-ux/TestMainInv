# Necessary Importations
import streamlit as st
import mysql.connector


# Define class inventory
class Inventory:
    # Define constructor for the class 
    def __init__(self):
        # Load database configuration from secrets.toml
        db_config = {
            "host": st.secrets["DB_HOST"],
            "port": st.secrets["PORT"],
            "user": st.secrets["DB_USER"],
            "password": st.secrets["DB_PASSWORD"],
            "database": st.secrets["DB_DATABASE"]
        }

        # Connect to MySQL database
        self.conn = mysql.connector.connect(**db_config)
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
    header.markdown('### **This streamlit app supports Automated SQL Server Database Inventory System**')
    st.image('../Inventory-Management-App/image/taifa2image.jpg')
    header.markdown('-----')
    
# Sidebar for adding products
with sidebar:
    st.header("Addition or Sale of Products from Database")

    product_name = st.text_input("Product Name")
    product_weight = st.number_input("Product Weight (kg)", min_value=0.5, step=0.5)
    product_quantity = st.number_input("Quantity", min_value=0, step=1)

    if st.button("Add Product"):
        inventory.add_product_to_db(product_name, product_weight, product_quantity)

# Sidebar for selling products
with sidebar:
    st.header("**Sell Product**")

    product_names = inventory.get_product_names()
    sell_product_name = st.selectbox("Product Name", product_names)
    sell_product_quantity = st.number_input("Quantity to Sell", min_value=1, step=1)

    if st.button("Sell Product"):
        inventory.sell_product_from_db(sell_product_name, sell_product_quantity)

# Display current inventory
with current_stock:
    st.subheader("**Current Inventory**")
    st.markdown('##### **Inventory remaining after a successful Sale**')

    cursor = inventory.conn.cursor()
    cursor.execute('''SELECT * FROM products''')
    rows = cursor.fetchall()
    for row in rows:
        name, weight, quantity = row
        st.write(f"{name}: {quantity} units, {weight} kg each")
