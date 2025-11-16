"""
Main Flask application for SaaS subscription app with drawing feature.
"""
import os
import secrets
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import stripe
import sys
import os
# Add parent directory to path so we can import models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.models import db, User, Drawing

# Load environment variables
load_dotenv()

# Initialize Flask app
# Set static folder and template folder relative to project root
app = Flask(__name__, 
            static_folder='../static',
            template_folder='templates')
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))

# Fix DATABASE_URL for Heroku (postgres:// -> postgresql://)
database_url = os.getenv('DATABASE_URL', 'sqlite:///app.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Stripe configuration
stripe_secret_key = os.getenv('STRIPE_SECRET_KEY')
if stripe_secret_key:
    stripe.api_key = stripe_secret_key
    print(f"✓ Stripe API key loaded (starts with: {stripe_secret_key[:7]}...)")
else:
    print("✗ WARNING: STRIPE_SECRET_KEY not set in environment variables!")

STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', '')
if STRIPE_PUBLISHABLE_KEY:
    print(f"✓ Stripe Publishable key loaded (starts with: {STRIPE_PUBLISHABLE_KEY[:7]}...)")
else:
    print("✗ WARNING: STRIPE_PUBLISHABLE_KEY not set!")

STRIPE_PRICE_BASIC = os.getenv('STRIPE_PRICE_BASIC', '')
STRIPE_PRICE_PRO = os.getenv('STRIPE_PRICE_PRO', '')
STRIPE_PRICE_PREMIUM = os.getenv('STRIPE_PRICE_PREMIUM', '')

# Debug: Print price IDs (first few chars only)
if STRIPE_PRICE_BASIC:
    print(f"✓ Price IDs loaded: Basic={STRIPE_PRICE_BASIC[:10]}..., Pro={STRIPE_PRICE_PRO[:10] if STRIPE_PRICE_PRO else 'NOT SET'}..., Premium={STRIPE_PRICE_PREMIUM[:10] if STRIPE_PRICE_PREMIUM else 'NOT SET'}...")
else:
    print("✗ WARNING: Stripe Price IDs not set!")


@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login."""
    return User.query.get(int(user_id))


# ==================== ROUTES ====================

@app.route('/')
def index():
    """Landing page."""
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        # Validation
        if not email or '@' not in email:
            flash('Please enter a valid email address.', 'error')
            return render_template('signup.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('signup.html')
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please login instead.', 'error')
            return redirect(url_for('login'))
        
        # Create new user
        try:
            password_hash = generate_password_hash(password)
            user = User(email=email, password_hash=password_hash)
            db.session.add(user)
            db.session.commit()
            
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating account: {str(e)}', 'error')
            return render_template('signup.html')
    
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            flash(f'Welcome back, {user.email}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing subscription status."""
    return render_template('dashboard.html', user=current_user)


@app.route('/subscribe')
@login_required
def subscribe():
    """Subscription selection page."""
    return render_template('subscribe.html', 
                         publishable_key=STRIPE_PUBLISHABLE_KEY,
                         price_basic=STRIPE_PRICE_BASIC,
                         price_pro=STRIPE_PRICE_PRO,
                         price_premium=STRIPE_PRICE_PREMIUM)


@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    """Create Stripe Checkout session."""
    try:
        # Check if Stripe is configured
        if not stripe.api_key:
            flash('Stripe is not configured. Please set STRIPE_SECRET_KEY in environment variables.', 'error')
            return redirect(url_for('subscribe'))
        
        price_id = request.form.get('price_id')
        if not price_id:
            flash('Please select a subscription plan.', 'error')
            return redirect(url_for('subscribe'))
        
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer_email=current_user.email,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.url_root + 'success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.url_root + 'cancel',
            metadata={
                'user_id': str(current_user.id),
            }
        )
        
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        flash(f'Error creating checkout session: {str(e)}', 'error')
        print(f"General error: {e}")
        import traceback
        traceback.print_exc()
        return redirect(url_for('subscribe'))


@app.route('/success')
@login_required
def success():
    """Payment success page."""
    session_id = request.args.get('session_id')
    if session_id:
        try:
            # Retrieve session from Stripe
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            print(f"DEBUG: Checkout session status: {checkout_session.payment_status}")
            print(f"DEBUG: Checkout session mode: {checkout_session.mode}")
            
            # Update user subscription (webhook will handle this, but we can update here too)
            if checkout_session.payment_status == 'paid':
                # Get line items to determine price
                line_items = stripe.checkout.Session.list_line_items(session_id)
                price_id = None
                if line_items and len(line_items.data) > 0:
                    price_id = line_items.data[0].price.id
                    print(f"DEBUG: Price ID from line items: {price_id}")
                
                # Map price ID to tier name
                tier = 'basic'
                if price_id == STRIPE_PRICE_PRO:
                    tier = 'pro'
                elif price_id == STRIPE_PRICE_PREMIUM:
                    tier = 'premium'
                
                print(f"DEBUG: Setting tier to: {tier}")
                
                current_user.subscription_tier = tier
                current_user.subscription_active = True
                current_user.stripe_customer_id = checkout_session.customer
                current_user.stripe_subscription_id = checkout_session.subscription
                db.session.commit()
                
                print(f"DEBUG: Updated user {current_user.email} subscription to {tier}")
                flash('Subscription activated successfully!', 'success')
            else:
                print(f"DEBUG: Payment status is not 'paid': {checkout_session.payment_status}")
                flash('Payment received! Your subscription will be activated shortly.', 'info')
        except Exception as e:
            print(f"Error processing success: {e}")
            import traceback
            traceback.print_exc()
            flash('Payment received! Your subscription will be activated shortly.', 'info')
    else:
        print("DEBUG: No session_id in URL")
    
    return render_template('success.html')


@app.route('/cancel')
def cancel():
    """Payment cancelled page."""
    flash('Payment was cancelled.', 'info')
    return redirect(url_for('subscribe'))


@app.route('/webhook', methods=['POST'])
def webhook():
    """Stripe webhook endpoint for payment events."""
    # NOTE: Webhook signature validation is IMPORTANT for production
    # For now, we'll do basic validation. In production, validate the signature!
    # See: https://stripe.com/docs/webhooks/signatures
    
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    try:
        if webhook_secret:
            # Validate webhook signature
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        else:
            # For testing without webhook secret
            import json
            event = json.loads(payload)
        
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            user_id = session.get('metadata', {}).get('user_id')
            
            if user_id:
                user = User.query.get(int(user_id))
                if user:
                    # Determine tier from price
                    # NOTE: This might need adjustment based on your Stripe setup
                    price_id = session.get('line_items', {}).get('data', [{}])[0].get('price', {}).get('id', '')
                    tier = 'basic'
                    if price_id == STRIPE_PRICE_PRO:
                        tier = 'pro'
                    elif price_id == STRIPE_PRICE_PREMIUM:
                        tier = 'premium'
                    
                    user.subscription_tier = tier
                    user.subscription_active = True
                    user.stripe_customer_id = session.get('customer')
                    user.stripe_subscription_id = session.get('subscription')
                    db.session.commit()
                    print(f"Updated subscription for user {user.email}")
        
        return jsonify({'status': 'success'}), 200
    except ValueError as e:
        print(f"Invalid payload: {e}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        print(f"Invalid signature: {e}")
        return jsonify({'error': 'Invalid signature'}), 400
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/draw')
@login_required
def draw():
    """Drawing canvas page."""
    return render_template('draw.html', user=current_user)


@app.route('/save-drawing', methods=['POST'])
@login_required
def save_drawing():
    """Save drawing to database."""
    try:
        # Check if user can draw
        if not current_user.can_draw():
            return jsonify({
                'success': False,
                'message': "You've used your free drawing! Upgrade to draw unlimited times 🎨"
            }), 403
        
        # Get image data from request
        data = request.get_json()
        image_data = data.get('image_data', '')
        message = data.get('message', '').strip() or None
        has_background = data.get('has_background', True)
        
        if not image_data:
            return jsonify({'success': False, 'message': 'No image data provided'}), 400
        
        # Save drawing
        drawing = Drawing(
            user_id=current_user.id,
            image_data=image_data,
            message=message,
            has_background=has_background,
            user_email=current_user.email
        )
        db.session.add(drawing)
        
        # Update user's drawing count
        current_user.drawings_count += 1
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Drawing saved successfully!',
            'drawings_count': current_user.drawings_count
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error saving drawing: {e}")
        return jsonify({'success': False, 'message': f'Error saving drawing: {str(e)}'}), 500


@app.route('/gallery')
def gallery():
    """Gallery page showing all drawings floating."""
    # Get all drawings, ordered by newest first
    drawings = Drawing.query.order_by(Drawing.created_at.desc()).all()
    return render_template('gallery.html', drawings=drawings)


# ==================== INITIALIZATION ====================

def create_tables():
    """Create database tables."""
    with app.app_context():
        db.create_all()
        print("Database tables created!")


if __name__ == '__main__':
    # Create tables if they don't exist
    create_tables()
    
    # Run app
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

