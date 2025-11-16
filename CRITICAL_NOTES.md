# ⚠️ CRITICAL NOTES & POTENTIAL ISSUES

## ✅ What I'm Confident About

1. **Flask App Structure** - Standard Flask setup, should work
2. **Database Models** - User and Drawing models are correct
3. **Authentication** - Flask-Login integration is standard
4. **HTML Templates** - All templates created with Bootstrap
5. **Canvas Drawing** - JavaScript should work, but needs testing
6. **Basic Routes** - Login, signup, dashboard routes are standard

## ⚠️ Areas That Might Need Adjustment

### 1. Stripe Webhook Signature Validation
**Location**: `src/main.py` line ~200

**Issue**: Webhook signature validation might need adjustment based on your Stripe setup.

**What to check**:
- Make sure `STRIPE_WEBHOOK_SECRET` is set correctly
- Test webhook in Stripe Dashboard → Webhooks → Send test webhook
- If webhook fails, check Heroku logs: `heroku logs --tail`

**If it doesn't work**:
- The webhook endpoint might need the exact signature format
- Check Stripe docs: https://stripe.com/docs/webhooks/signatures

### 2. Stripe Price ID Mapping
**Location**: `src/main.py` lines ~150-160, ~220-230

**Issue**: The code maps price IDs to tier names. This assumes:
- `STRIPE_PRICE_BASIC` maps to 'basic'
- `STRIPE_PRICE_PRO` maps to 'pro'  
- `STRIPE_PRICE_PREMIUM` maps to 'premium'

**What to check**:
- After creating products in Stripe, verify the Price IDs match what's in your `.env`
- The mapping logic might need adjustment if Stripe returns different data

**If it doesn't work**:
- Check Stripe Dashboard → Products → Your product → Pricing
- Verify the Price ID matches your `.env` file
- The webhook might need to extract price differently

### 3. Canvas Drawing JavaScript
**Location**: `static/draw.js`

**Issue**: Canvas drawing should work, but touch events might need testing on mobile.

**What to check**:
- Test drawing with mouse (should work)
- Test drawing on mobile/touch device
- Canvas size is fixed (800x600) - might need responsive adjustment

**If it doesn't work**:
- Check browser console for JavaScript errors
- Touch events might need `preventDefault()` adjustments
- Canvas scaling might need fixes for different screen sizes

### 4. Gallery Floating Animations
**Location**: `src/templates/gallery.html`

**Issue**: CSS animations should work, but positioning might look odd with many drawings.

**What to check**:
- Animations use CSS `@keyframes` - should work in all modern browsers
- Drawings positioned with percentages - might overlap
- Animation durations vary (10-20s) - should look smooth

**If it doesn't work**:
- Check browser console for CSS errors
- Animations might need adjustment for better visual effect
- Too many drawings might cause performance issues

### 5. Database Initialization
**Location**: `src/main.py` line ~280

**Issue**: Database tables are created when you run `python src/main.py` the first time.

**What to check**:
- Run `python src/main.py` once locally to create tables
- On Heroku, run: `heroku run python src/main.py` once
- Check if `app.db` file is created locally

**If it doesn't work**:
- Database URL might be wrong
- SQLite file permissions issue
- PostgreSQL connection string might be incorrect

### 6. Import Paths
**Location**: `src/main.py` line 7

**Issue**: Uses `from src.models import db, User, Drawing`

**What to check**:
- Make sure you run from project root: `python src/main.py`
- Not from `src/` directory
- If import fails, might need to adjust Python path

**If it doesn't work**:
- Try: `cd src && python main.py` (but adjust imports)
- Or add project root to PYTHONPATH
- Or use relative imports

## 🐛 Common Issues & Fixes

### "ModuleNotFoundError: No module named 'src'"
**Fix**: Run from project root, not from `src/` directory
```bash
cd /path/to/simpleapp
python src/main.py
```

### "Table 'users' doesn't exist"
**Fix**: Run the app once to create tables
```bash
python src/main.py
# Let it start, then Ctrl+C to stop
```

### "Stripe webhook returns 400"
**Fix**: Check webhook secret is correct
```bash
heroku config:get STRIPE_WEBHOOK_SECRET
# Should start with whsec_
```

### "Canvas drawing doesn't work"
**Fix**: Check browser console for errors
- Make sure `draw.js` is loaded
- Check canvas element exists
- Verify JavaScript isn't blocked

### "Drawings don't save"
**Fix**: Check:
- User is logged in
- User hasn't exceeded free limit (if not subscribed)
- Database connection works
- Check browser console for fetch errors

## 📝 Testing Checklist

Before deploying, test:
- [ ] Can create account
- [ ] Can login
- [ ] Can see dashboard
- [ ] Can draw on canvas (mouse works)
- [ ] Can save drawing
- [ ] Can see drawing in gallery
- [ ] Can subscribe (test mode)
- [ ] Payment redirects correctly
- [ ] Webhook updates subscription (check Stripe Dashboard → Webhooks → Events)

## 🚀 If Something Breaks

1. **Check Heroku logs**: `heroku logs --tail`
2. **Check browser console**: F12 → Console tab
3. **Check Stripe Dashboard**: Webhooks → Events (see if webhook is called)
4. **Test locally first**: Fix issues locally before deploying
5. **Ask for help**: Share error messages and logs

## 💡 Honest Assessment

**What will definitely work:**
- Basic Flask app structure ✅
- User authentication ✅
- Database models ✅
- HTML templates ✅
- Basic Stripe checkout ✅

**What might need tweaking:**
- Webhook signature validation (might need exact format)
- Price ID mapping (depends on Stripe response structure)
- Canvas touch events (needs mobile testing)
- Gallery animations (might need visual adjustments)

**Estimated debugging time if issues occur:**
- Webhook issues: 15-30 min
- Canvas issues: 10-20 min
- Database issues: 5-10 min
- Stripe integration: 15-30 min

**Total worst case**: ~1-2 hours of debugging

---

**Remember**: Most issues are small fixes. The core structure is solid! 🚀

