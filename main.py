import streamlit as st
import sqlite3

class Inventory:
    def __init__(self):
        self.conn = sqlite3.connect('inventory.db')
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                            name TEXT PRIMARY KEY,
                            quantity INTEGER
                          )''')
        self.conn.commit()

    def add_product_to_db(self, name, quantity):
        #capitalize name
        name=name.capitalize()
        
        cursor = self.conn.cursor()
        cursor.execute('''SELECT quantity FROM products WHERE name=?''', (name,))
        row = cursor.fetchone()
        if row:
            existing_quantity = row[0]
            new_quantity = existing_quantity + quantity
            cursor.execute('''UPDATE products SET quantity=? WHERE name=?''', (new_quantity, name))
        else:
            cursor.execute('''INSERT INTO products (name, quantity) VALUES (?, ?)''', (name, quantity))
        self.conn.commit()        
        st.write(f"Product '{name}' (Quantity: {quantity}) added successfully.")

    def sell_product_from_db(self, name, quantity):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT quantity FROM products WHERE name=?''', (name,))
        row = cursor.fetchone()
        if row:
            available_quantity = row[0]
            if available_quantity >= quantity:
                cursor.execute('''UPDATE products SET quantity = quantity - ? WHERE name=?''', (quantity, name))
                self.conn.commit()
                st.write(f"{quantity} units of '{name}' sold.")
            else:
                st.write("Not enough stock available.")
        else:
            st.write("Product not found in inventory.")

    def delete_product(self, name):
        cursor = self.conn.cursor()
        cursor.execute('''DELETE FROM products WHERE name=?''', (name,))
        self.conn.commit()
        st.write(f"Product '{name}' deleted successfully.")     

    def adjust_quantity(self, name, quantity_reduction):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT quantity FROM products WHERE name=?''', (name,))
        row = cursor.fetchone()
        if row:
            current_quantity = row[0]
            if current_quantity >= quantity_reduction:
                new_quantity = current_quantity - quantity_reduction
                cursor.execute('''UPDATE products SET quantity=? WHERE name=?''', (new_quantity, name))
                self.conn.commit()
                st.write(f"Quantity of product '{name}' reduced by {quantity_reduction} units.")
            else:
                st.write("Error: The requested reduction exceeds the current quantity.")
        else:
            st.write("Product not found in inventory.")       

    def view_stock(self):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT * FROM products''')
        rows = cursor.fetchall()
        st.subheader("**Current Inventory**")
        for row in rows:
            name, quantity = row
            st.write(f"{name}: {quantity} units.")

    # Retrieving product names
    def get_product_names(self):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT name FROM products''')
        rows = cursor.fetchall()
        product_names = [row[0] for row in rows]
        return product_names


# Custom theme and styling code
st.set_page_config(
    page_title="Inventory Management App",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="auto",
)    

def main():
    st.title("**Streamlit Inventory Tracker: Automated SQLite Database Support**")
    st.image("image/taifa2image.jpg")

    inventory = Inventory()

    option = st.selectbox("Select Action", ["Add Product", "Sell Product", "View Stock", "Adjust Quantity", "Delete Product"])

    if option == "Add Product":
        st.header("Add Product")
        product_name = st.text_input("Product Name")
        product_quantity = st.number_input("Quantity", min_value=1, step=1)  # Minimum value set to 1
        if st.button("Add Product"):
            if product_quantity <= 0:  # Check if quantity is zero or negative
              st.error("Quantity must be a positive integer.")
            else:
               inventory.add_product_to_db(product_name, product_quantity)

    elif option == "Sell Product":
        st.header("Sell Product")
        product_names = inventory.get_product_names()  # Fetch product names here
        if not product_names:
            st.write("No products available for sale.")
        else:
            product_name = st.selectbox("Select Product to Sell", product_names)
            product_quantity = st.number_input("Quantity to sell", min_value=1, step=1)
            if st.button("Sell Product"):
                inventory.sell_product_from_db(product_name, product_quantity)
    elif option == "Delete Product":
        st.header("Delete Product")
        product_names = inventory.get_product_names()
        if not product_names:
            st.write("No products available for deletion.")
        else:
            product_to_delete = st.selectbox("Select Product to Delete", product_names)
            if st.button("Delete Product"):
                inventory.delete_product(product_to_delete)
    elif option == "Adjust Quantity":
        st.header("Adjust Quantity")
        product_names = inventory.get_product_names()
        if not product_names:
            st.write("No products available for adjustment.")
        else:
            product_to_adjust = st.selectbox("Select Product to Adjust", product_names)
            new_quantity = st.number_input("Enter New Quantity", min_value=0, step=1)  # Minimum value set to 0
        if st.button("Adjust Quantity"):
            if new_quantity < 0:  # Check if quantity is negative
                st.error("Quantity must be a non-negative integer.")
            else:
                inventory.adjust_quantity(product_to_adjust, new_quantity)
    elif option == "View Stock":
        st.subheader("**Current Inventory**")
        cursor = inventory.conn.cursor()
        cursor.execute('''SELECT * FROM products''')
        rows = cursor.fetchall()
        for row in rows:
            name, quantity = row
            if "bakers" in name.lower():
                st.write(f"{name}: {quantity} bags.")
            else:
                st.write(f"{name}: {quantity} bales.")

if __name__ == '__main__':
    main()
