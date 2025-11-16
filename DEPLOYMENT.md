# 🚀 Deployment Guide

Quick reference for deploying and updating your SaaS app.

## 📍 Current Deployment

- **Heroku App**: `quiet-wildwood-76497`
- **Live URL**: https://quiet-wildwood-76497-10fd279504c8.herokuapp.com
- **Database**: PostgreSQL Essential-0
- **Status**: ✅ Live and running

## 🔄 Updating Your Code

### Standard Workflow (3 Steps)

```bash
# 1. Make changes locally and test
python src/main.py

# 2. Commit changes
git add .
git commit -m "Description of changes"

# 3. Deploy to Heroku
git push heroku main
```

**That's it!** Heroku automatically:
- Builds your app
- Installs dependencies
- Restarts with new code
- Takes ~1-2 minutes

### Check Deployment Status

```bash
# View live logs
heroku logs --tail

# Check app status
heroku ps

# View all releases
heroku releases
```

## 🛠️ Common Tasks

### Add a New Python Package

1. Add to `requirements.txt`:
   ```
   new-package==1.0.0
   ```
2. Deploy:
   ```bash
   git add requirements.txt
   git commit -m "Add new-package"
   git push heroku main
   ```

### Update Environment Variables

```bash
# Set a variable
heroku config:set VARIABLE_NAME=value

# View all variables
heroku config

# Remove a variable
heroku config:unset VARIABLE_NAME
```

### Update Database Schema

1. Modify `src/models.py`
2. Deploy: `git push heroku main`
3. If needed, run migrations:
   ```bash
   heroku run python init_db.py
   ```

### Rollback to Previous Version

```bash
# See all versions
heroku releases

# Rollback to specific version
heroku rollback v9
```

### View App Logs

```bash
# Live logs (updates in real-time)
heroku logs --tail

# Last 100 lines
heroku logs -n 100

# Filter for errors
heroku logs --tail | grep ERROR
```

## 🔍 Troubleshooting

### App Won't Start

```bash
# Check logs for errors
heroku logs --tail

# Common issues:
# - Missing environment variable → Set it with heroku config:set
# - Syntax error → Check logs for line numbers
# - Import error → Check requirements.txt
```

### Database Issues

```bash
# Reinitialize database (WARNING: deletes all data!)
heroku run python init_db.py

# Connect to database directly
heroku pg:psql
```

### Deployment Failed

```bash
# Check build logs
heroku logs --tail

# Common fixes:
# - Fix syntax errors
# - Update requirements.txt if package version is wrong
# - Check Procfile is correct
```

## 📦 Project Structure

```
simpleapp/
├── src/
│   ├── main.py          # Flask app (edit this!)
│   ├── models.py        # Database models (edit this!)
│   └── templates/       # HTML templates (edit these!)
├── static/
│   ├── style.css        # CSS (edit this!)
│   └── draw.js          # JavaScript (edit this!)
├── requirements.txt     # Python packages (edit this!)
├── Procfile             # Heroku config (usually don't touch)
├── runtime.txt          # Python version (usually don't touch)
└── init_db.py           # Database initialization script
```

## 🎯 Quick Commands Cheat Sheet

```bash
# Deploy updates
git push heroku main

# View logs
heroku logs --tail

# Check config
heroku config

# Run one-off command
heroku run python script.py

# Open app in browser
heroku open

# Restart app
heroku restart

# Scale dynos (if needed)
heroku ps:scale web=1
```

## 💡 Pro Tips

1. **Always test locally first** - `python src/main.py` before deploying
2. **Check logs after deployment** - `heroku logs --tail` to catch errors
3. **Use descriptive commit messages** - Helps track what changed
4. **Keep `.env` file local only** - Never commit secrets to git
5. **Database changes are permanent** - Be careful with migrations!

---

**Remember**: `git push heroku main` is your friend! 🚀

