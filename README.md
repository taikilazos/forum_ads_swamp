# 🎨 DrawSaaS - Subscription-Based Drawing App

A production-ready SaaS application built with Flask, PostgreSQL, Stripe, and deployed on Heroku. Users can create drawings, subscribe to plans, and see all drawings floating in a shared gallery.

## Features

- ✅ User authentication (signup, login, logout)
- ✅ Subscription management (3 tiers: $1, $2, $5/month)
- ✅ Stripe payment integration
- ✅ Drawing canvas with mouse/touch support
- ✅ Shared gallery with floating animations
- ✅ Free users: 1 drawing, Paid users: unlimited

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL (Heroku) / SQLite (local)
- **Authentication**: Flask-Login + bcrypt
- **Payments**: Stripe Checkout
- **Frontend**: Bootstrap 5, HTML5 Canvas
- **Hosting**: Heroku

## Setup Instructions

### 1. Clone and Install

```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the project root:

```bash
FLASK_SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///app.db
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...  # Get this after setting up webhook
STRIPE_PRICE_BASIC=price_...     # Create products in Stripe Dashboard
STRIPE_PRICE_PRO=price_...
STRIPE_PRICE_PREMIUM=price_...
```

**Generate Flask Secret Key:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Create Stripe Products

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/test/products)
2. Create 3 products:
   - **Basic Plan**: $1/month (recurring)
   - **Pro Plan**: $2/month (recurring)
   - **Premium Plan**: $5/month (recurring)
3. Copy each **Price ID** (starts with `price_`)
4. Add them to your `.env` file

### 4. Run Locally

```bash
python src/main.py
```

Visit `http://localhost:5000`

## Deployment to Heroku

### 1. Create Heroku App

```bash
heroku create your-app-name
```

### 2. Add PostgreSQL Database

```bash
heroku addons:create heroku-postgresql:essential-0
# Note: The 'mini' plan is deprecated. Use 'essential-0' instead ($5/month)
```

### 3. Set Environment Variables

```bash
heroku config:set FLASK_SECRET_KEY=your-secret-key
heroku config:set STRIPE_PUBLISHABLE_KEY=pk_test_...
heroku config:set STRIPE_SECRET_KEY=sk_test_...
heroku config:set STRIPE_PRICE_BASIC=price_...
heroku config:set STRIPE_PRICE_PRO=price_...
heroku config:set STRIPE_PRICE_PREMIUM=price_...
```

### 4. Setup Stripe Webhook

1. Go to Stripe Dashboard → Webhooks
2. Click "Add Endpoint"
3. URL: `https://your-app.herokuapp.com/webhook`
4. Select event: `checkout.session.completed`
5. Copy the **Signing Secret** (starts with `whsec_`)
6. Add to Heroku:
   ```bash
   heroku config:set STRIPE_WEBHOOK_SECRET=whsec_...
   ```

### 5. Deploy

```bash
git add .
git commit -m "Initial deployment"
git push heroku main
```

### 6. Initialize Database

```bash
heroku run python init_db.py
# This will create the tables
```

## 🚀 Current Deployment Status

**✅ DEPLOYED AND LIVE!**

- **App URL**: https://quiet-wildwood-76497-10fd279504c8.herokuapp.com
- **Heroku App**: `quiet-wildwood-76497`
- **Database**: PostgreSQL Essential-0 (initialized)
- **Stripe**: Test mode configured with webhook
- **Status**: Ready for testing!

## 📝 How to Update Your Code

When you make changes to your code, follow these steps to deploy updates:

### 1. Make Your Changes Locally
- Edit files in your project
- Test locally: `python src/main.py`
- Make sure everything works!

### 2. Commit Changes to Git
```bash
git add .
git commit -m "Description of your changes"
```

### 3. Deploy to Heroku
```bash
git push heroku main
```

That's it! Heroku will:
- Build your app
- Install any new dependencies
- Restart your app with the new code
- Usually takes 1-2 minutes

### 4. Check Deployment Status
```bash
# View logs to see if deployment succeeded
heroku logs --tail

# Or check in browser
# Visit: https://quiet-wildwood-76497-10fd279504c8.herokuapp.com
```

### Common Update Scenarios

**Adding a new Python package:**
1. Add to `requirements.txt`
2. `git add requirements.txt`
3. `git commit -m "Add new package"`
4. `git push heroku main`

**Changing database models:**
1. Update `src/models.py`
2. Deploy: `git push heroku main`
3. Run migrations: `heroku run python init_db.py` (if needed)

**Updating environment variables:**
```bash
heroku config:set VARIABLE_NAME=new_value
# App restarts automatically
```

**Viewing current config:**
```bash
heroku config
```

**Rolling back to previous version:**
```bash
heroku releases  # See all versions
heroku rollback v9  # Rollback to version 9
```

## Testing Payments

Use Stripe's test card:
- **Card**: `4242 4242 4242 4242`
- **Expiry**: Any future date (e.g., 12/25)
- **CVC**: Any 3 digits (e.g., 123)

## Project Structure

```
simpleapp/
├── src/
│   ├── main.py              # Flask app and routes
│   ├── models.py            # Database models
│   └── templates/          # HTML templates
├── static/
│   ├── style.css            # Custom CSS
│   └── draw.js              # Canvas drawing JavaScript
├── requirements.txt         # Python dependencies
├── Procfile                 # Heroku configuration
├── runtime.txt              # Python version
└── README.md                # This file
```

## Troubleshooting

**App won't start locally:**
- Check `.env` file exists and has all variables
- Run `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.11.x)

**Stripe payments not working:**
- Verify API keys are correct
- Check webhook is set up correctly
- Use test card: 4242 4242 4242 4242

**Database errors:**
- Make sure database tables are created: `python src/main.py` (runs once)
- On Heroku: `heroku run python src/main.py`

**Webhook not working:**
- Make sure webhook URL is correct: `https://your-app.herokuapp.com/webhook`
- Check webhook secret is set in Heroku config
- View webhook logs in Stripe Dashboard

## Notes

- **Webhook Signature Validation**: Currently basic. For production, ensure proper signature validation.
- **Database**: Uses SQLite locally, PostgreSQL on Heroku (automatic via DATABASE_URL)
- **Drawing Storage**: Drawings stored as base64 strings in database (simple, but not ideal for large scale)

## License

MIT License - Feel free to use this for your own projects!

---

**Built with ❤️ using Flask, Stripe, and Heroku**

