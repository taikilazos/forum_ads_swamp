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
from src.models import db, User, Drawing, PaymentHistory
from datetime import datetime, timedelta

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
                
                # Create payment history record
                amount = 1.0  # Default
                if tier == 'pro':
                    amount = 2.0
                elif tier == 'premium':
                    amount = 5.0
                
                payment = PaymentHistory(
                    user_id=current_user.id,
                    subscription_tier=tier,
                    amount=amount,
                    stripe_subscription_id=checkout_session.subscription,
                    subscription_start=datetime.utcnow(),
                    subscription_end=None,  # Active subscription
                    status='paid'
                )
                db.session.add(payment)
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
                    # Get line items to determine price ID (checkout session doesn't include line_items directly)
                    session_id = session.get('id')
                    line_items = stripe.checkout.Session.list_line_items(session_id)
                    
                    # Determine tier from price ID
                    price_id = None
                    if line_items and len(line_items.data) > 0:
                        price_id = line_items.data[0].price.id
                    
                    tier = 'basic'  # Default
                    if price_id == STRIPE_PRICE_PRO:
                        tier = 'pro'
                    elif price_id == STRIPE_PRICE_PREMIUM:
                        tier = 'premium'
                    elif price_id == STRIPE_PRICE_BASIC:
                        tier = 'basic'
                    
                    print(f"Webhook: User {user.email}, Price ID: {price_id}, Tier: {tier}")
                    
                    # Update user subscription
                    user.subscription_tier = tier
                    user.subscription_active = True
                    user.stripe_customer_id = session.get('customer')
                    user.stripe_subscription_id = session.get('subscription')
                    
                    # Get amount from line items
                    amount = 0.0
                    if line_items and len(line_items.data) > 0:
                        amount = line_items.data[0].amount_total / 100.0  # Convert from cents
                    
                    # Fallback to tier-based pricing if amount is 0
                    if amount == 0:
                        if tier == 'pro':
                            amount = 2.0
                        elif tier == 'premium':
                            amount = 5.0
                        else:
                            amount = 1.0
                    
                    # Get subscription start date from Stripe subscription if available
                    subscription_start = datetime.utcnow()
                    if session.get('subscription'):
                        try:
                            subscription = stripe.Subscription.retrieve(session.get('subscription'))
                            subscription_start = datetime.fromtimestamp(subscription.created)
                        except:
                            pass  # Use current time as fallback
                    
                    # Create payment history record
                    payment = PaymentHistory(
                        user_id=user.id,
                        subscription_tier=tier,
                        amount=amount,
                        stripe_subscription_id=session.get('subscription'),
                        subscription_start=subscription_start,
                        subscription_end=None,  # Active subscription
                        status='paid'
                    )
                    db.session.add(payment)
                    db.session.commit()
                    print(f"Webhook: Updated subscription for user {user.email} to {tier} tier")
        
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
        message = (data.get('message') or '').strip() or None
        has_background = data.get('has_background', True)
        has_stickers = data.get('has_stickers', False)

        # Validate sticker usage
        if has_stickers and not current_user.can_use_stickers:
            return jsonify({
                'success': False,
                'message': "Stickers are a Pro feature! Upgrade to use them 🌟"
            }), 403
        
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
    """Gallery page showing all drawings floating with retention logic."""
    now = datetime.utcnow()
    cutoff_24h = now - timedelta(hours=24)
    cutoff_7d = now - timedelta(days=7)
    cutoff_30d = now - timedelta(days=30)

    # Filter drawings based on user's tier and creation time
    # Premium: Forever
    # Pro: 30 days
    # Basic: 7 days
    # Free: 24 hours
    drawings = db.session.query(Drawing).join(User).filter(
        db.or_(
            User.subscription_tier == 'premium',
            db.and_(User.subscription_tier == 'pro', Drawing.created_at > cutoff_30d),
            db.and_(User.subscription_tier == 'basic', Drawing.created_at > cutoff_7d),
            db.and_(db.or_(User.subscription_tier == 'none', User.subscription_tier == None), Drawing.created_at > cutoff_24h)
        )
    ).order_by(Drawing.created_at.desc()).all()

    return render_template('gallery.html', drawings=drawings)


@app.route('/manage-subscription')
@login_required
def manage_subscription():
    """Subscription management page with upgrade/downgrade options."""
    # Verify user has a valid Stripe subscription
    if not current_user.subscription_active or not current_user.stripe_subscription_id:
        flash('You need an active subscription to manage your plan. Please subscribe first.', 'error')
        return redirect(url_for('subscribe'))
    
    # Verify subscription exists in Stripe
    try:
        subscription = stripe.Subscription.retrieve(current_user.stripe_subscription_id)
        if subscription.status not in ['active', 'trialing']:
            flash('Your subscription is not active. Please subscribe again.', 'error')
            return redirect(url_for('subscribe'))
    except stripe.error.InvalidRequestError:
        flash('Subscription not found in Stripe. Please subscribe again.', 'error')
        return redirect(url_for('subscribe'))
    
    return render_template('manage_subscription.html', 
                         user=current_user,
                         price_basic=STRIPE_PRICE_BASIC,
                         price_pro=STRIPE_PRICE_PRO,
                         price_premium=STRIPE_PRICE_PREMIUM)


@app.route('/upgrade-subscription', methods=['POST'])
@login_required
def upgrade_subscription():
    """Handle subscription upgrade/downgrade."""
    # Strict validation - must have active subscription AND Stripe subscription ID
    if not current_user.subscription_active or not current_user.stripe_subscription_id:
        flash('You need an active subscription to change plans. Please subscribe first.', 'error')
        return redirect(url_for('subscribe'))
    
    new_price_id = request.form.get('price_id')
    if not new_price_id:
        flash('Please select a plan.', 'error')
        return redirect(url_for('manage_subscription'))
    
    try:
        # Verify subscription exists and is active in Stripe
        subscription = stripe.Subscription.retrieve(current_user.stripe_subscription_id)
        
        if subscription.status not in ['active', 'trialing']:
            flash('Your subscription is not active. Please subscribe again.', 'error')
            return redirect(url_for('subscribe'))
        
        # Prevent upgrading to same plan
        current_price_id = subscription['items']['data'][0].price.id
        if current_price_id == new_price_id:
            flash('You are already on this plan!', 'info')
            return redirect(url_for('manage_subscription'))
        
        # Update subscription to new price with immediate billing
        # 'always_invoice' creates prorations and invoices the customer immediately
        stripe.Subscription.modify(
            current_user.stripe_subscription_id,
            items=[{
                'id': subscription['items']['data'][0].id,
                'price': new_price_id,
            }],
            proration_behavior='always_invoice'  # Invoice immediately for prorated amount
        )
        
        # Determine new tier
        tier = 'basic'
        if new_price_id == STRIPE_PRICE_PRO:
            tier = 'pro'
        elif new_price_id == STRIPE_PRICE_PREMIUM:
            tier = 'premium'
        
        current_user.subscription_tier = tier
        db.session.commit()
        
        flash(f'Subscription changed to {tier.title()} plan! You have been charged immediately.', 'success')
    except stripe.error.InvalidRequestError as e:
        print(f"Stripe error upgrading subscription: {e}")
        flash('Subscription not found in Stripe. Please subscribe again.', 'error')
    except Exception as e:
        print(f"Error upgrading subscription: {e}")
        flash(f'Error changing subscription: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))


@app.route('/sync-subscription')
@login_required
def sync_subscription():
    """Manually sync subscription status from Stripe (for debugging/fixing)."""
    if not current_user.stripe_subscription_id:
        flash('No Stripe subscription ID found. Please subscribe first.', 'error')
        return redirect(url_for('subscribe'))
    
    try:
        # Retrieve subscription from Stripe
        subscription = stripe.Subscription.retrieve(current_user.stripe_subscription_id)
        
        # Get the price ID from subscription
        price_id = subscription['items']['data'][0].price.id
        
        # Determine tier
        tier = 'basic'
        if price_id == STRIPE_PRICE_PRO:
            tier = 'pro'
        elif price_id == STRIPE_PRICE_PREMIUM:
            tier = 'premium'
        
        # Update user
        current_user.subscription_tier = tier
        current_user.subscription_active = subscription.status in ['active', 'trialing']
        current_user.stripe_customer_id = subscription.customer
        current_user.stripe_subscription_id = subscription.id
        
        db.session.commit()
        
        flash(f'Subscription synced! Status: {subscription.status}, Tier: {tier.title()}', 'success')
    except stripe.error.InvalidRequestError as e:
        flash(f'Subscription not found in Stripe: {str(e)}', 'error')
    except Exception as e:
        flash(f'Error syncing subscription: {str(e)}', 'error')
        print(f"Sync error: {e}")
    
    return redirect(url_for('dashboard'))


@app.route('/payment-history')
@login_required
def payment_history():
    """Display payment history with subscription duration."""
    # Backfill payment history for users who subscribed before PaymentHistory was added
    if current_user.subscription_active and current_user.stripe_subscription_id:
        existing_payment = PaymentHistory.query.filter_by(
            user_id=current_user.id,
            stripe_subscription_id=current_user.stripe_subscription_id,
            status='paid'
        ).first()
        
        if not existing_payment:
            # Create payment history record for existing subscription
            try:
                subscription = stripe.Subscription.retrieve(current_user.stripe_subscription_id)
                amount = 1.0
                if current_user.subscription_tier == 'pro':
                    amount = 2.0
                elif current_user.subscription_tier == 'premium':
                    amount = 5.0
                
                # Get subscription start date from Stripe
                subscription_start = datetime.fromtimestamp(subscription.created)
                
                payment = PaymentHistory(
                    user_id=current_user.id,
                    subscription_tier=current_user.subscription_tier,
                    amount=amount,
                    stripe_subscription_id=current_user.stripe_subscription_id,
                    subscription_start=subscription_start,
                    subscription_end=None,  # Active subscription
                    status='paid'
                )
                db.session.add(payment)
                db.session.commit()
                print(f"Created payment history for existing subscription: {current_user.email}")
            except Exception as e:
                print(f"Error backfilling payment history: {e}")
                db.session.rollback()
    
    payments = PaymentHistory.query.filter_by(user_id=current_user.id)\
        .order_by(PaymentHistory.payment_date.desc()).all()
    
    # Get tier prices for display
    tier_prices = {
        'basic': 1.0,
        'pro': 2.0,
        'premium': 5.0
    }
    
    return render_template('payment_history.html', 
                         payments=payments,
                         tier_prices=tier_prices)


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

