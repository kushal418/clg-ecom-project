import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from database import (
    create_connection, register_user, login_user, setup_database, login_admin
)

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this for security
bcrypt = Bcrypt(app)

UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

setup_database()  # Run database setup when the server starts

# Home Page (Requires Login)
@app.route('/')
def home():
    if "user_id" in session:  
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)  # ✅ Fetch results as dictionaries

        cursor.execute("SELECT * FROM products")  # ✅ Fetch all products
        products = cursor.fetchall()

        conn.close()
        return render_template('index.html', username=session['username'], products=products)

    flash("Please log in first!", "warning")
    return redirect(url_for('login'))

# Admin Dashboard (Requires Admin Login)
@app.route('/admin-dashboard')
def admin_dashboard():
    if "admin_id" in session:
        return render_template('admin/admin_dashboard.html', admin_username=session['admin_username'])
    flash("Admin login required!", "danger")
    return redirect(url_for('admin_login'))

# Manage Products (Admin Only)
@app.route('/manage-products')
def manage_products():
    if "admin_id" in session:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)  # ✅ Ensure dictionary output

        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()  # ✅ Fetch all products from DB

        conn.close()
        return render_template('admin/manage_products.html', products=products)  # ✅ Pass data to template

    flash("Admin login required!", "danger")
    return redirect(url_for('admin_login'))

# Add Product (Admin Only)
# Add Product (Admin Only)
@app.route('/add-product', methods=['POST'])
def add_product():
    if "admin_id" in session:
        product_name = request.form['product_name']
        description = request.form['description']
        price = request.form['price']
        image = request.files['image']

        # Save image
        image_path = os.path.join(UPLOAD_FOLDER, image.filename)
        image.save(image_path)

        conn = create_connection()
        cursor = conn.cursor()

        # ✅ Fix: Use `%s` placeholders for MySQL instead of `?`
        cursor.execute(
            "INSERT INTO products (name, description, price, image) VALUES (%s, %s, %s, %s)",
            (product_name, description, price, image_path)
        )

        conn.commit()
        conn.close()

        flash("Product added successfully!", "success")
        return redirect(url_for('manage_products'))

    flash("Admin login required!", "danger")
    return redirect(url_for('admin_login'))

# Delete Product (Admin Only)
@app.route('/delete-product/<int:product_id>')
def delete_product(product_id):
    if "admin_id" in session:
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
        
        conn.commit()
        cursor.close()
        conn.close()

        flash("Product deleted successfully!", "success")
        return redirect(url_for('manage_products'))
    
    flash("Admin login required!", "danger")
    return redirect(url_for('admin_login'))

# Signup Route (User)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        mobile = request.form['mobile']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('signup'))

        if register_user(username, email, mobile, password):
            flash("Signup successful! Please log in.", "success")
            return redirect(url_for('login'))
        else:
            flash("Email already exists!", "danger")
            return redirect(url_for('signup'))

    return render_template('signup.html')

# Login Route (User)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = login_user(email, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f"Welcome {user['username']}!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid email or password!", "danger")

    return render_template('login.html')

# Admin Login Route
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        admin = login_admin(email, password)
        if admin:
            session['admin_id'] = admin['id']
            session['admin_username'] = admin['username']
            flash("Admin login successful!", "success")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid admin credentials!", "danger")

    return render_template('admin/admin_login.html')

# Logout Route (User)
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for('login'))

# Admin Logout Route
@app.route('/admin-logout')
def admin_logout():
    session.clear()
    flash("Admin logged out successfully!", "info")
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)
