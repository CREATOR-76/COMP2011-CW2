from flask import render_template, redirect, url_for, flash, jsonify, request, abort, session
from app import app, db
from app.forms import SearchForm, LoginForm, RegisterForm
from app.models import Product, Category, User, Order,Cart, OrderItem, Favorite
from flask_login import current_user, login_user, logout_user, login_required
from flask import request

# Initialize the search form
@app.context_processor
def base_context():
    search_form = SearchForm()
    return dict(search_form=search_form)

@app.route('/')
def index():
    # Initialize the recommend list
    recommended_products = []
    recommended_category = None

    # Recommend based on the recently viewed
    recent_product_ids = session.get('recent_products', [])
    if recent_product_ids and current_user.is_authenticated:
        # Get the user's last viewed product
        last_viewed_product = Product.query.get(recent_product_ids[0])
        if last_viewed_product:
            # Get the products the same category
            recommended_category = last_viewed_product.category
            recommended_products = Product.query.filter(
                Product.category_id == last_viewed_product.category_id,
                Product.id != last_viewed_product.id
            ).order_by(db.func.random()).limit(4).all()

    # Recommend the highest click_amount products
    if not recommended_products:
        most_clicked_category = Category.query.order_by(Category.click_count.desc()).first()
        if most_clicked_category:
            recommended_category = most_clicked_category
            recommended_products = Product.query.filter_by(
                category_id=most_clicked_category.id
            ).order_by(db.func.random()).limit(4).all()

    # Recommend the product similar to the favorite
    favorite_recommendations = []
    if current_user.is_authenticated:
        # Get the category with the highest click amount
        most_favorited_category = db.session.query(
            Product.category_id,
            db.func.count(Favorite.product_id).label('favorite_count')
        ).join(
            Favorite, Product.id == Favorite.product_id
        ).group_by(
            Product.category_id
        ).order_by(
            db.desc('favorite_count')
        ).first()

        if most_favorited_category:
            favorite_recommendations = Product.query.filter(
                Product.category_id == most_favorited_category[0],
                ~Product.id.in_([p.id for p in recommended_products] if recommended_products else [])
            ).order_by(
                db.func.random()
            ).limit(4).all()

    # Get the favorite list
    recent_favorites = []
    if current_user.is_authenticated:
        recent_favorites = Product.query.join(
            Favorite, Product.id == Favorite.product_id
        ).filter(
            Favorite.user_id == current_user.id
        ).order_by(Favorite.created_time.desc()).limit(6).all()

    # Get the list of recently viewed
    recent_products = []
    if recent_product_ids:
        recent_products = Product.query.filter(Product.id.in_(recent_product_ids)).all()
        recent_products.sort(key=lambda x: recent_product_ids.index(x.id))

    return render_template('index.html',
                       recommended_products=recommended_products,
                       recommended_category=recommended_category,
                       favorite_recommendations=favorite_recommendations,
                       recent_favorites=recent_favorites,
                       recent_products=recent_products)

# Search form
@app.route('/search', methods=['GET', 'POST'])
def search():
    search_form = SearchForm()
    if request.method == 'POST' and search_form.validate_on_submit():
        search_query = search_form.query.data.strip()
        return redirect(url_for('search', query=search_query))

    search_query = request.args.get('query', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 12

    if search_query:

        pagination = Product.query.filter(
            Product.name.ilike(f'%{search_query}%')
        ).paginate(page=page, per_page=per_page, error_out=False)

        products = pagination.items

        return render_template('search_list.html',
                               products=products,
                               pagination=pagination,
                               search_query=search_query,
                               search_form=search_form)

    return redirect(url_for('index'))

# Login/Register form
@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    login_form = LoginForm()
    register_form = RegisterForm()

    # Check the form that been submitted
    form_type = request.form.get('form_type')

    if request.method == 'POST':
        if form_type == 'login' and login_form.validate_on_submit():
            user = User.query.filter_by(email=login_form.email.data).first()
            if user and user.check_password(login_form.password.data):
                login_user(user)
                return redirect(url_for('index'))
            flash('The wrong email or the passport', 'error')

        elif form_type == 'register' and register_form.validate_on_submit():
            # Check if the username has existed
            if User.query.filter_by(username=register_form.username.data).first():
                flash('The username has existed', 'error')
                return render_template('auth.html',
                                       login_form=login_form,
                                       register_form=register_form)

            # Check if the email has existed
            if User.query.filter_by(email=register_form.email.data).first():
                flash('The email has been used', 'error')
                return render_template('auth.html',
                                       login_form=login_form,
                                       register_form=register_form)

            # Create the new user
            try:
                user = User(
                    username=register_form.username.data,
                    email=register_form.email.data
                )
                user.set_password(register_form.password.data)
                db.session.add(user)
                db.session.commit()
                flash('Successfully register!', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Failed to register...', 'error')
                print(f"Registration error: {str(e)}")  # 记录错误信息以便调试

            return render_template('auth.html',
                                   login_form=login_form,
                                   register_form=register_form)

    return render_template('auth.html',
                           login_form=login_form,
                           register_form=register_form)

# Log out
@app.route('/logout')
@login_required
def logout():
    # Use Flask-Login to log out
    logout_user()

    # Back to homepage
    return redirect(url_for('index'))

# User information
@app.route('/user_profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    if request.method == 'POST':
        # Update user information
        current_user.username = request.form.get('username')
        current_user.email = request.form.get('email')
        current_user.gender = request.form.get('gender')
        current_user.bio = request.form.get('bio')
        current_user.address = request.form.get('address')

        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('user_profile'))

    return render_template('user_profile.html', user=current_user)

# Products list
@app.route('/products')
def product_list():
    # Get the first page as 1
    page = request.args.get('page', 1, type=int)

    # Get the category id
    category_id = request.args.get('category', type=int)

    if category_id:
        # Show the products of the point category
        products = Product.query.filter_by(category_id=category_id) \
            .paginate(page=page, per_page=12)
    else:
        # Show all the product
        products = Product.query.paginate(page=page, per_page=12)

    # Get all the categories
    categories = Category.query.all()

    return render_template('list.html',
                           products=products,
                           categories=categories)

# The product detail
@app.route('/product/<int:id>')
def product_detail(id):
    product = Product.query.get_or_404(id)

    # Deal with the click amount
    if product.click_count is None:
        product.click_count = 1
    else:
        product.click_count += 1

    # Update the click amount
    category = product.category
    category.click_count += 1

    db.session.commit()

    # Update the viewed history
    if current_user.is_authenticated:
        recent_products = session.get('recent_products', [])
        if id in recent_products:
            recent_products.remove(id)
        recent_products.insert(0, id)
        recent_products = recent_products[:6]
        session['recent_products'] = recent_products

    # Get the product recommendation
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != id
    ).limit(4).all()

    return render_template('detail.html',
                           product=product,
                           related_products=related_products)

# Category
@app.route('/category/<string:gender>')
def category(gender):
    page = request.args.get('page', 1, type=int)
    per_page = 12

    pagination = Product.query.filter(
        Product.Gender == gender
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('list.html',
                           products=pagination.items,
                           gender=gender,
                           pagination=pagination)

# Cart
@app.route('/cart')
@login_required
def cart():
    # Get the user's items in cart
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()

    # Calculate the total price
    total = sum(item.product.price * item.quantity for item in cart_items)

    return render_template('cart.html',
                           cart_items=cart_items,
                           total=total)

# Add the product to the cart
@app.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    try:
        # Get the product
        product = Product.query.get_or_404(product_id)
        # Get the amount of the product
        data = request.get_json()
        quantity = int(data.get('quantity', 1))

        # Check the stock
        if product.stock < quantity:
            return jsonify({'status': 'error', 'message': 'Insufficient stock'}), 400

        # Check if the item existed in cart
        cart_item = Cart.query.filter_by(
            user_id=current_user.id,
            product_id=product_id
        ).first()

        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = Cart(
                user_id=current_user.id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(cart_item)

        # Save the change
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Product added to cart successfully!'}), 200

    except ValueError:
        return jsonify({'status': 'error', 'message': 'Invalid quantity'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Remove the item in cart
@app.route('/cart/remove/<int:product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    # Check the cart
    cart_item = Cart.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first_or_404()

    # Delete from the cart in database
    db.session.delete(cart_item)
    db.session.commit()

    flash('Has removed from the cart', 'success')
    return redirect(url_for('cart'))

@app.route('/cart/update/<int:product_id>', methods=['POST'])
@login_required
def update_cart(product_id):
    # Check the cart
    cart_item = Cart.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first_or_404()

    # Get the new amount
    quantity = request.form.get('quantity', type=int)

    if quantity <= 0:
        # If the amount is 0, delete the item
        db.session.delete(cart_item)
    else:
        # Check the stock
        if quantity > cart_item.product.stock:
            flash('The product is not enough', 'error')
            return redirect(url_for('cart'))

        #Updata the quantity
        cart_item.quantity = quantity

    db.session.commit()
    return redirect(url_for('cart'))

# Clear all the item in the cart
@app.route('/cart/clear', methods=['POST'])
@login_required
def clear_cart():
    Cart.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash('Shopping cart has been cleared', 'success')
    return redirect(url_for('cart'))

# List all the order
@app.route('/orders')
@login_required
def order_list():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_time.desc()).all()
    return render_template('order_list.html', orders=orders)

# Create the order
@app.route('/order/create', methods=['POST'])
@login_required
def create_order():
    # Get user's cart items
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()

    if not cart_items:
        flash('Your cart is empty', 'error')
        return redirect(url_for('cart'))

    # Get shipping address from form
    shipping_address = request.form.get('shipping_address') or current_user.address
    if not shipping_address:
        flash('Please provide a shipping address', 'error')
        return redirect(url_for('cart'))

    # Calculate total amount
    total_amount = sum(item.product.price * item.quantity for item in cart_items)

    try:
        # Create new order
        order = Order(
            user_id=current_user.id,
            total_amount=total_amount,
            status='pending',
            shipping_address=shipping_address
        )
        db.session.add(order)
        db.session.commit()  # Commit to get the order ID

        # Create order items
        for cart_item in cart_items:
            # Check stock
            if cart_item.quantity > cart_item.product.stock:
                db.session.rollback()
                flash(f'Insufficient stock for {cart_item.product.name}', 'error')
                return redirect(url_for('cart'))

            # Create order item
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            db.session.add(order_item)

            # Update product stock
            cart_item.product.stock -= cart_item.quantity

        # Clear cart
        Cart.query.filter_by(user_id=current_user.id).delete()

        # Commit all changes
        db.session.commit()
        flash('Order placed successfully', 'success')
        return redirect(url_for('order_detail', order_id=order.id))

    except Exception as e:
        db.session.rollback()
        flash('An error occurred while processing your order', 'error')
        return redirect(url_for('cart'))

# The order detail
@app.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    # Ensure user can only view their own orders
    if order.user_id != current_user.id:
        abort(403)
    return render_template('order_detail.html', order=order)

# Change the user's passport
@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    # Return JSON
    if not current_user.check_password(current_password):
        return jsonify({'status': 'error', 'message': 'Current password is incorrect'})

    if new_password != confirm_password:
        return jsonify({'status': 'error', 'message': 'New passwords do not match'})

    if len(new_password) < 6:
        return jsonify({'status': 'error', 'message': 'New password must be at least 6 characters long'})

    try:
        current_user.set_password(new_password)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Password has been updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Failed to update password'})

# The favorite list
@app.route('/favorite/<int:product_id>', methods=['POST'])
@login_required
def toggle_favorite(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        favorite = Favorite.query.filter_by(
            user_id=current_user.id,
            product_id=product_id
        ).first()

        if favorite:
            db.session.delete(favorite)
            is_favorite = False
        else:
            favorite = Favorite(user_id=current_user.id, product_id=product_id)
            db.session.add(favorite)
            is_favorite = True

        db.session.commit()
        return jsonify({
            'status': 'success',
            'is_favorite': is_favorite,
            'message': 'Successfully updated favorite status'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# The favorite detail
@app.route('/is_favorite/<int:product_id>')
@login_required
def is_favorite(product_id):
    try:
        favorite = Favorite.query.filter_by(
            user_id=current_user.id,
            product_id=product_id
        ).first()
        return jsonify({
            'status': 'success',
            'is_favorite': favorite is not None
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Clear the old flash error
@app.before_request
def before_request():
    # Clear old flash messages at the start of each request
    session.pop('_flashes', None)