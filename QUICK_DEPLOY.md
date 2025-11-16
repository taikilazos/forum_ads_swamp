# 🚀 Quick Deploy Guide

## When You Want to Deploy Changes to Heroku

### Simple 3-Step Process:

```bash
# 1. Commit your changes
git add .
git commit -m "Description of changes"

# 2. Push to Heroku (this deploys!)
git push heroku main

# 3. Done! Wait 1-2 minutes for deployment
```

**That's it!** Your app updates automatically.

---

## Optional: Save to GitHub

If you want to backup to GitHub:

```bash
# After committing locally
git push origin main  # Push to GitHub (if you have a remote)
```

**Note:** GitHub and Heroku are separate. You can:
- Push to Heroku only (for deployment)
- Push to GitHub only (for backup)
- Push to both (recommended)

---

## When You Come Back from Break

### 1. Check Current Status
```bash
# See what's deployed
heroku logs --tail

# Check app status
heroku ps
```

### 2. Test Locally First
```bash
python src/main.py
# Visit http://localhost:5000
```

### 3. Deploy When Ready
```bash
git add .
git commit -m "Your changes"
git push heroku main
```

---

## Common Commands

```bash
# View live logs
heroku logs --tail

# Check environment variables
heroku config

# Run database migration
heroku run python init_db.py

# Open app in browser
heroku open
```

---

## 💡 Pro Tip

**You don't need to push to GitHub every time!** 

- **Heroku**: For deploying your app (required)
- **GitHub**: For backing up code (optional but recommended)

Most developers push to both, but Heroku is what actually runs your app.

---

**Take your break! When you come back, just run `git push heroku main` to deploy any changes.** 🎉

