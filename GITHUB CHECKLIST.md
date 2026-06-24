# GitHub Setup Checklist

Follow these steps in order. Takes 5 minutes.

---

## ✅ Step 1: Create GitHub Repository

- [ ] Go to https://github.com/new
- [ ] Name: `volume-scanner`
- [ ] Description: `Stock volume scanner with Finnhub`
- [ ] Select **Public** (free tier)
- [ ] Click "Create repository"
- [ ] You now have empty repo

---

## ✅ Step 2: Get Finnhub API Key

- [ ] Go to https://finnhub.io/
- [ ] Click "Sign Up"
- [ ] Fill in email/password
- [ ] Verify email (check inbox)
- [ ] Log in
- [ ] Copy your API key from Dashboard
- [ ] Save it somewhere (you'll need it soon)

Example key: `c1a2b3c4d5e6f7g8h9i0j1k2`

---

## ✅ Step 3: Upload Python Files

In your GitHub repo (github.com/yourusername/volume-scanner):

- [ ] Click "Add file" → "Upload files"
- [ ] Upload these 3 files:
  - [ ] `volume_scanner.py`
  - [ ] `test_scanner.py`
  - [ ] `requirements.txt`
- [ ] Click "Commit changes"

---

## ✅ Step 4: Create Workflow File

This tells GitHub to run your scanner automatically.

- [ ] Click "Add file" → "Create new file"
- [ ] Type filename: `.github/workflows/scanner.yml`
- [ ] Copy/paste entire content from `scanner.yml` file in this repo
- [ ] Click "Commit new file"

---

## ✅ Step 5: Add API Key as Secret

GitHub will use this to run your scanner safely.

- [ ] Go to "Settings" tab (top right)
- [ ] Click "Secrets and variables" (left sidebar)
- [ ] Click "Actions"
- [ ] Click "New repository secret" (green button)
- [ ] Name: `FINNHUB_API_KEY`
- [ ] Value: (paste your API key from Step 2)
- [ ] Click "Add secret"

Your key is now encrypted. It's never visible in logs.

---

## ✅ Step 6: Enable GitHub Actions

- [ ] Go to "Actions" tab (top of repo)
- [ ] See message: "Actions is disabled for this repository"
- [ ] Click "I understand my workflows, go ahead and enable them"
- [ ] Actions now enabled

---

## ✅ Step 7: Test It (Optional)

Want to run scanner right now instead of waiting for 3:55 AM?

- [ ] Go to "Actions" tab
- [ ] Click "Volume Scanner" (workflow)
- [ ] Click "Run workflow" (blue button)
- [ ] Select "main" branch
- [ ] Click "Run workflow"
- [ ] Scanner runs immediately

---

## ✅ Step 8: Monitor Results

After workflow completes (5-15 minutes):

### Option A: Download Logs
- [ ] Go to "Actions" tab
- [ ] Click the workflow run
- [ ] Scroll to "Artifacts"
- [ ] Click "scanner-logs"
- [ ] Extract ZIP file
- [ ] Open `volume_scanner.log` in text editor

### Option B: View in Repo
- [ ] Go to "Code" tab
- [ ] Open `logs` folder
- [ ] See daily log files: `scanner_2024-06-24.log`

---

## ✅ Step 9: Customize (Optional)

### Change Watchlist
- [ ] Click `volume_scanner.py`
- [ ] Click pencil icon (Edit)
- [ ] Find line: `WATCHLIST = ["NOK", "LNOK", ...]`
- [ ] Change symbols (e.g., `["AAPL", "TSLA"]`)
- [ ] Click "Commit changes"
- [ ] Next scan uses new watchlist

### Change Scan Time
- [ ] Click `.github/workflows/scanner.yml`
- [ ] Click pencil icon (Edit)
- [ ] Find line: `cron: '55 11 * * 1-5'`
- [ ] Change time (11 = 3 AM PST, 12 = 4 AM PST)
- [ ] Click "Commit changes"
- [ ] Next scheduled run uses new time

---

## ✅ Done!

Your scanner is now running in the cloud.

**What happens next:**
- ✓ Runs automatically at 3:55 AM PST (Mon-Fri)
- ✓ Scans your watchlist for volume spikes
- ✓ Checks for catalyst news
- ✓ Logs all activity to `/logs` folder
- ✓ You can check results anytime from iPhone, Mac, or PC

**Monitor from iPhone:**
1. Go to github.com/yourusername/volume-scanner
2. Click "Code" tab
3. Open `logs` folder
4. See today's scan: `scanner_2024-06-24.log`

---

## Troubleshooting

### "Workflow failed" error

1. Go to Actions tab
2. Click the failed run
3. See error message at bottom
4. Common fixes:

| Error | Fix |
|-------|-----|
| "401 Unauthorized" | Check API key in Settings → Secrets |
| "ModuleNotFoundError" | Verify `requirements.txt` uploaded |
| "No such file" | Upload `volume_scanner.py` |

### No logs in `/logs` folder

- [ ] Check Actions tab - did workflow complete?
- [ ] Click workflow → scroll to Artifacts
- [ ] Or wait for next scheduled run (3:55 AM PST)

### Want to run again right now?

- [ ] Go to Actions tab
- [ ] Click "Volume Scanner"
- [ ] Click "Run workflow" button

---

## That's It!

You now have a cloud-based stock scanner running automatically. No Mac needed.

For more details, see:
- `README.md` - Overview
- `GITHUB_SETUP.md` - Detailed guide
- `QUICK_REFERENCE.md` - Common commands

Enjoy!
