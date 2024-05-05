import streamlit as st
import sqlite3
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Set page configuration
st.set_page_config(
    page_title="Inventory Management App",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="auto",
)

# Display app title and image
st.title("Streamlit Inventory Tracker:dart:") 
st.header(":rainbow[Automated SQLite Database Support]:sparkles:")
st.image("image/taifa2image.jpg")

# Load hashed passwords
with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

# Add css to hide item with title "show password text"
st.markdown(
    """ 
<style>
    [title = "Show password text"] {
       display : none;
    }
  </style>  
""",
   unsafe_allow_html=True
)

# Define class 'Inventory'
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
        st.write(f"Product '{name}' deleted successfully from Database.")     

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
                if 'Bakers' in name:
                    st.write(f"Quantity of product '{name}' reduced by {quantity_reduction} bags.")
                else:
                    st.write(f"Quantity of product '{name}' reduced by {quantity_reduction} bales.")

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


def main():
    # Check if user is authenticated
    if not st.session_state.get("authentication_status"):
        # Render login module
        authenticator.login("main", clear_on_submit=True)

        if st.session_state["authentication_status"] is None:
            st.warning('Please enter your username and password')
            return
        elif not st.session_state["authentication_status"]:
            st.error('Username/password is incorrect')
            return
    
    # If user is authenticated, proceed with the app functionality
    authenticator.logout()
    st.write(f'Welcome *{st.session_state["name"]}*')

    # Create an instance of Inventory class
    inventory = Inventory()

    # Display sidebar options
    sidebar_option = st.sidebar.selectbox("Select Option:", ["Change Password", "Register New User", "Forgot Password"])

    # Handle sidebar options
    # Implement functionality to change password new here 
    if sidebar_option == "Change Password":
        if st.session_state["authentication_status"]:
            try:
                if authenticator.reset_password(st.session_state["username"], fields={'Form name':'Reset password', 'Current password':'Current password', 'New password':'New password', 'Repeat password': 'Repeat password', 'Reset':'Reset'},
                                                 location="sidebar", clear_on_submit=True ):
                    st.success('Password modified successfully')
            except Exception as e:
                    st.error(e)

     # Implement functionality to register new user here               
    elif sidebar_option == "Register New User":
        st.sidebar.header("Register New User")
        try:
            email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(
                fields={'Form name':'Register user', 'Email':'Email', 'Username':'Username', 'Password':'Password', 'Repeat password':'Repeat password', 'Register':'Register'},location="sidebar", clear_on_submit=True, pre_authorization=False)
            if email_of_registered_user:
                st.success('User registered successfully')
        except Exception as e:
                st.error(e)
        
    # Implement functionality for forgot password here    
    elif sidebar_option == "Forgot Password":
        st.sidebar.header("Forgot Password")
    try:
        username_of_forgotten_password, email_of_forgotten_password, new_random_password = authenticator.forgot_password(location="sidebar",fields={'Form name':'Forgot password', 'Username':'Username', 'Submit':'Submit'})
        if username_of_forgotten_password:
            st.success('New password to be sent securely')
        # The developer should securely transfer the new password to the user.
        elif username_of_forgotten_password == False:
            st.error('Username not found')
    except Exception as e:
        st.error(e)
        
    # Update the configuration file
    with open('config.yaml', 'w') as file:
        yaml.dump(config, file)

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
        st.header("Adjust Quantity: (Minimize Stock)")
        product_names = inventory.get_product_names()
        if not product_names:
            st.write("No products available for adjustment.")
        else:
            product_to_adjust = st.selectbox("**Select Product to Adjust** :arrow_down_small:", product_names)
            new_quantity = st.number_input("**Enter Quantity**", min_value=0, step=1)  # Minimum value set to 0
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
