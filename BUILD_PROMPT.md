# 🚀 INITIAL BUILD PROMPT

Copy and paste this prompt to start building your SaaS app:

---

## PROMPT START

I want to build a production-ready SaaS subscription app using Flask, PostgreSQL, Stripe, and deploy it to Heroku.

### **REQUIREMENTS:**

**Features:**
1. User authentication system (signup, login, logout, session management)
2. Landing page with "Get Started" call-to-action
3. User dashboard showing current subscription status
4. Subscription page with 3 tiers:
   - Basic Plan: $1/month
   - Pro Plan: $2/month
   - Premium Plan: $5/month
5. Stripe payment integration (Checkout mode)
6. Webhook endpoint to handle successful payments
7. PostgreSQL database to store users and subscription data
8. **Drawing Feature** (The Fun Part!):
   - Drawing canvas page where users can draw with mouse/touch
   - Save drawings to database (stored as base64 image data)
   - Shared gallery page showing all user drawings floating around
   - CSS animations make drawings float/move across screen
   - Feature access: Free users can draw 1 time, paid subscribers get unlimited drawings

**Tech Stack:**
- **Backend**: Flask (Python)
- **Database**: PostgreSQL with Flask-SQLAlchemy ORM
- **Authentication**: Flask-Login with bcrypt password hashing
- **Payments**: Stripe Checkout API
- **Frontend**: HTML/CSS with Bootstrap for styling
- **Deployment**: Heroku-ready (Procfile, runtime.txt, environment variables)

**Project Structure:**
```
simpleapp/
├── src/
│   ├── main.py              # Main Flask app, routes, config
│   ├── models.py            # Database models (User, Subscription, Drawing)
│   └── templates/           # HTML templates
│       ├── base.html        # Base template with navbar
│       ├── index.html       # Landing page
│       ├── login.html       # Login form
│       ├── signup.html      # Registration form
│       ├── dashboard.html   # User dashboard (shows plan)
│       ├── subscribe.html   # Subscription tier selection
│       ├── draw.html        # Drawing canvas page
│       └── gallery.html      # Gallery showing all drawings floating
├── static/
│   ├── style.css            # Custom CSS
│   └── draw.js              # Canvas drawing JavaScript
├── requirements.txt         # Python dependencies
├── Procfile                 # Heroku dyno configuration
├── runtime.txt              # Python version for Heroku
├── .env.example             # Example environment variables
├── .gitignore               # Git ignore file
└── README.md                # Setup instructions
```

**Database Schema:**

User model:
- id (primary key)
- email (unique, required)
- password_hash (bcrypt hashed)
- created_at (timestamp)
- subscription_tier (string: 'none', 'basic', 'pro', 'premium')
- subscription_active (boolean)
- stripe_customer_id (string, nullable)
- stripe_subscription_id (string, nullable)
- drawings_count (integer, default 0) - tracks how many drawings user has made

Drawing model:
- id (primary key)
- user_id (foreign key to User)
- image_data (text) - base64 encoded PNG image
- created_at (timestamp)
- user_email (string) - denormalized for easy display

**Routes:**
- `GET /` - Landing page
- `GET /signup` - Registration page
- `POST /signup` - Handle registration
- `GET /login` - Login page
- `POST /login` - Handle login
- `GET /logout` - Logout user
- `GET /dashboard` - User dashboard (protected, login required)
- `GET /subscribe` - Subscription selection page (protected)
- `POST /create-checkout-session` - Create Stripe checkout session
- `GET /success` - Payment success page
- `GET /cancel` - Payment cancelled page
- `POST /webhook` - Stripe webhook for payment events
- `GET /draw` - Drawing canvas page (protected, login required)
- `POST /save-drawing` - Save drawing to database (protected)
- `GET /gallery` - Gallery page showing all drawings floating (public or protected)

**Security Requirements:**
1. Hash all passwords with bcrypt
2. Use Flask sessions with secure secret key
3. Use environment variables for all secrets (Stripe keys, database URL, secret key)
4. Validate Stripe webhook signatures
5. Protect dashboard and subscription routes with login_required decorator

**Stripe Integration:**
1. Use Stripe Checkout (hosted payment page)
2. Create 3 products/prices in Stripe for each tier
3. Webhook listens for `checkout.session.completed` event
4. Update user subscription status when payment succeeds
5. Use test mode initially (test API keys)

**Deployment Configuration:**
1. **Procfile**: `web: gunicorn src.main:app`
2. **runtime.txt**: `python-3.11.6`
3. **requirements.txt** must include:
   - Flask
   - Flask-Login
   - Flask-SQLAlchemy
   - psycopg2-binary
   - bcrypt
   - stripe
   - python-dotenv
   - gunicorn

**Environment Variables Needed:**
```
FLASK_SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://... (Heroku provides this)
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_BASIC=price_... (Stripe Price ID)
STRIPE_PRICE_PRO=price_...
STRIPE_PRICE_PREMIUM=price_...
```

**UI/UX Requirements:**
1. Clean, modern design using Bootstrap 5
2. Responsive (works on mobile)
3. Clear navigation with user email shown when logged in
4. Visual distinction between subscription tiers (cards with borders)
5. Success/error flash messages for user feedback
6. Professional color scheme

**Drawing Feature Requirements:**
1. HTML5 Canvas for drawing (responsive, works on desktop and mobile)
2. Mouse and touch support for drawing
3. Color picker and brush size controls
4. Clear button to reset canvas
5. Save button to save drawing (checks subscription limits)
6. Gallery page with CSS animations making drawings float around
7. Each drawing shows as an image that moves across screen
8. Drawings are randomly positioned and animated with CSS keyframes
9. Limit: Free users (no subscription) = 1 drawing max, Paid users = unlimited
10. Show drawing count on dashboard ("You've drawn 3 times")

**Instructions:**
1. Build the complete application following best practices
2. Add detailed comments explaining key sections
3. Create a comprehensive README.md with:
   - Setup instructions for local development
   - How to create Stripe products
   - How to set environment variables
   - How to deploy to Heroku
   - How to test payments
4. Create .env.example with all required variables
5. Make sure the app can run locally with SQLite for development
6. Make sure the app uses PostgreSQL in production (Heroku)
7. Add helpful print/log statements for debugging

**Testing Checklist:**
After building, I should be able to:
- [ ] Run `pip install -r requirements.txt`
- [ ] Set environment variables in `.env`
- [ ] Run `python src/main.py` and see app at localhost:5000
- [ ] Create an account
- [ ] Login successfully
- [ ] See dashboard with "No active subscription"
- [ ] Click "Draw" button, go to drawing page
- [ ] Draw something on canvas (mouse/touch works)
- [ ] Save drawing successfully (free user gets 1 drawing)
- [ ] Try to save second drawing → see message "Upgrade to draw more!"
- [ ] Click subscribe, see 3 tiers
- [ ] Click a tier, get redirected to Stripe Checkout
- [ ] Use test card (4242 4242 4242 4242) to complete payment
- [ ] Get redirected back, see success message
- [ ] Dashboard now shows active subscription plan
- [ ] Can now draw unlimited times (subscription active)
- [ ] Visit gallery page, see all drawings floating around
- [ ] Drawings animate smoothly across screen
- [ ] Deploy to Heroku successfully
- [ ] Test same flow on live Heroku URL

**Code Quality:**
- Use Python type hints where helpful
- Follow PEP 8 style guide
- Add docstrings to functions
- Handle errors gracefully (try/except blocks)
- Validate user input (email format, password length)
- Use Flask blueprints if code gets large (optional)

**IMPORTANT:**
- Build this as a COMPLETE, WORKING application
- Don't just provide code snippets - build the entire thing
- Make it production-ready from the start
- Prioritize security (never store plain passwords, validate webhooks)
- Make deployment to Heroku seamless

**Drawing Feature Implementation Notes:**
- Use HTML5 Canvas API for drawing functionality
- Store drawings as base64 PNG strings in database (simple, no file storage needed)
- Gallery page: Query all drawings, render as `<img>` tags
- CSS animations: Use `@keyframes` with `transform: translate()` for floating effect
- Each drawing gets random starting position and animation duration
- Limit check: Before saving, check if user is free (drawings_count >= 1) or paid (unlimited)
- Show friendly message if limit reached: "You've used your free drawing! Upgrade to draw unlimited times 🎨"

Please build this application now. Start with the project structure, then build incrementally: models → auth → routes → templates → Stripe integration → drawing feature → deployment files.

## PROMPT END

---

## 📝 ADDITIONAL NOTES

**After the AI builds your app:**

1. **Test Locally First**:
   ```bash
   pip install -r requirements.txt
   python src/main.py
   ```

2. **Create Stripe Products**:
   - Go to Stripe Dashboard → Products
   - Create 3 products with recurring monthly prices
   - Copy Price IDs to environment variables

3. **Deploy to Heroku**:
   ```bash
   heroku create your-app-name
   heroku addons:create heroku-postgresql:mini
   git push heroku main
   heroku config:set FLASK_SECRET_KEY=xxx
   heroku config:set STRIPE_SECRET_KEY=xxx
   # ... set all other environment variables
   ```

4. **Setup Stripe Webhook**:
   - Heroku URL: `https://your-app.herokuapp.com/webhook`
   - Add to Stripe Dashboard → Webhooks
   - Listen for `checkout.session.completed`
   - Copy webhook signing secret to Heroku config

5. **Test Live App**:
   - Visit your Heroku URL
   - Create account
   - Subscribe with test card: 4242 4242 4242 4242
   - Verify subscription shows in dashboard

---

**Good luck! 🚀**

