import streamlit as st
import sqlite3

# Define class 'Inventory'
class Inventory:
    # Define Class constructor 'self'
    def __init__(self):
        #create a database connection object 'inventory.db'
        self.conn = sqlite3.connect('inventory.db')
        self.create_table()
    
    #Define class methods
    def create_table(self):
        #create 'cursor' object
        cursor = self.conn.cursor()
        #call of cursor objects' 'execute' method
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
        if "Bakers" in name:        
            st.write(f"Product '{name}' (Quantity: {quantity} bags) added successfully.")
        else:
            st.write(f"Product '{name}' (Quantity: {quantity} bales) added successfully.")


    def sell_product_from_db(self, name, quantity):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT quantity FROM products WHERE name=?''', (name,))
        row = cursor.fetchone()
        if row:
            available_quantity = row[0]
            if available_quantity >= quantity:
                cursor.execute('''UPDATE products SET quantity = quantity - ? WHERE name=?''', (quantity, name))
                self.conn.commit()
                if "Bakers" in name:
                    st.write(f"{quantity} bags of '{name}' sold.")
                else:
                    st.write(f"{quantity} bales of '{name}' sold.")

            else:
                st.write("Not enough stock available.")

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
    st.title("Streamlit Inventory Tracker:dart:") 
    st.header(":rainbow[Automated SQLite Database Support]:sparkles:")
    st.image("image/taifa2image.jpg")
#'_Streamlit_ is :blue[cool] :sunglasses:'
    inventory = Inventory()

    option = st.selectbox("**Select Action** :small_red_triangle_down:", ["Add Product", "Sell Product", "View Stock", "Adjust Quantity", "Delete Product"])

    
    if option == "Add Product":
        st.header("Add Product")

    # Define the list of available products
        predefined_products = ["Taifa 1/2kg","Taifa 1kg", "Taifa 2kg", "Bahari 1kg", "Bahari 2kg",
                                "Bakers 12.5kg", "Bakers 25kg", "Bakers 50kg", "Chenga 1kg"]

    # Dropdown to select product
        product_name = st.selectbox("**Choose Product Name** :arrow_down_small:", predefined_products)

        product_quantity = st.number_input("**Quantity to Add**", min_value=1, step=1)  # Minimum value set to 1

        if st.button("**Add Product**"):
            # Check if product name is provided
            if not product_name:  # If product name is empty
                st.error("Please select a product.")
            elif product_quantity <= 0:  # Check if quantity is zero or negative
                st.error("Quantity must be a positive integer.", icon="🚨")
            else:
                inventory.add_product_to_db(product_name, product_quantity)

    elif option == "Sell Product":
        st.header("Sell Product")
        product_names = inventory.get_product_names()  # Fetch product names here
        if not product_names:
            st.write("No products available for sale.")
        else:
            product_name = st.selectbox("**Select Product to Sell** :arrow_down_small:", product_names)
            product_quantity = st.number_input("**Quantity to sell**", min_value=1, step=1)
            if st.button("**Sell Product**"):
                inventory.sell_product_from_db(product_name, product_quantity)
    elif option == "Delete Product":
        st.header("Delete Product")
        product_names = inventory.get_product_names()
        if not product_names:
            st.write("No products available for deletion.")
        else:
            product_to_delete = st.selectbox("**Select Product to Delete** :arrow_down_small:", product_names)
            if st.button("**Delete Product**"):
                inventory.delete_product(product_to_delete) 
    elif option == "Adjust Quantity":
        st.header("Adjust Quantity: (Decrease)")
        product_names = inventory.get_product_names()
        if not product_names:
            st.write("No products available for adjustment.")
        else:
            product_to_adjust = st.selectbox("**Select Product to Adjust** :arrow_down_small:", product_names)
            new_quantity = st.number_input("**Enter New Quantity**", min_value=0, step=1)  # Minimum value set to 0
        if st.button("Adjust Quantity"):
            if new_quantity < 0:  # Check if quantity is negative
                st.error("Quantity must be a non-negative integer.", icon="🚨")
            else:
                inventory.adjust_quantity(product_to_adjust, new_quantity)
    elif option == "View Stock":
        st.subheader("**Current Inventory** :open_file_folder:")
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
