# Volume Scanner - GitHub Edition

Run your stock volume scanner in the cloud using GitHub Actions. No Mac needed.

## Setup (5 minutes)

### Step 1: Create GitHub Repo

1. Go to https://github.com/new
2. Repository name: `volume-scanner`
3. Description: `Real-time stock volume scanner with Finnhub API`
4. Make it **Public** (free tier works)
5. Click "Create repository"

### Step 2: Add Files to Repo

1. Click "Add file" → "Upload files"
2. Upload these files:
   - `volume_scanner.py`
   - `test_scanner.py`
   - `requirements.txt`
   - `SETUP_GUIDE.md`
   - `QUICK_REFERENCE.md`

3. Click "Commit changes"

### Step 3: Create `.github/workflows/scanner.yml`

This file tells GitHub to run your scanner automatically.

1. In your repo, click "Add file" → "Create new file"
2. Name: `.github/workflows/scanner.yml`
3. Paste the entire workflow file (included in this repo)
4. Click "Commit changes"

### Step 4: Add Your API Key (Secret)

GitHub will use this to run your scanner securely.

1. Go to repo Settings → "Secrets and variables" → "Actions"
2. Click "New repository secret"
3. Name: `FINNHUB_API_KEY`
4. Value: (paste your Finnhub API key)
5. Click "Add secret"

**Note:** Your API key is never visible in logs or code. GitHub encrypts it.

### Step 5: Enable Actions

1. Go to "Actions" tab
2. Click "I understand my workflows, go ahead and enable them"

---

## How It Works

**Schedule:**
- Runs automatically **every trading day at 3:55 AM PST** (before pre-market)
- Scans for 5+ hours during market hours
- Commits logs to your repo each day

**Files Created:**
- `/logs/scanner_2024-06-24.log` - Daily scan log
- One file per day in the `logs` folder

**View Results:**
1. Go to repo "Actions" tab
2. Click latest run
3. Scroll to "Artifacts"
4. Download `scanner-logs` to see results
5. Or check `/logs` folder in main repo for all historical logs

---

## Customization

### Change Watchlist

Edit `volume_scanner.py` directly in GitHub:

1. Click `volume_scanner.py`
2. Click pencil icon (Edit)
3. Find line ~10: `WATCHLIST = ["NOK", "LNOK", ...]`
4. Change symbols
5. Click "Commit changes"

Next scan will use new watchlist.

### Change Scan Time

Edit `.github/workflows/scanner.yml`:

1. Click `.github/workflows/scanner.yml`
2. Click pencil icon
3. Find: `cron: '55 11 * * 1-5'`

**Cron format:** `minute hour * * day`

Examples:
- `'55 11 * * 1-5'` = 3:55 AM PST (11:55 UTC), Mon-Fri
- `'0 12 * * 1-5'` = 4:00 AM PST (12:00 UTC), Mon-Fri
- `'0 13 * * 1-5'` = 5:00 AM PST (1:00 PM UTC), Mon-Fri

**PST to UTC conversion:**
- 4 AM PST = 12:00 PM UTC (11:55 for 3:55 AM)
- 9 AM PST = 5:00 PM UTC (16:55 for 8:55 AM)

### Run Manually (Right Now)

1. Go to "Actions" tab
2. Click "Volume Scanner"
3. Click "Run workflow" button
4. Confirm

Scanner runs immediately instead of waiting for schedule.

---

## View Logs

### Option A: In GitHub (Easy)

1. Go to "Actions" tab
2. Click the latest workflow run
3. Scroll down to "Artifacts"
4. Click `scanner-logs` to download

### Option B: In Repo (Persistent)

Logs are automatically committed to `/logs` folder:

1. Click "Code" tab
2. Click `logs` folder
3. See all daily logs: `scanner_2024-06-24.log`, etc.

---

## Alerts

When scanner finds a match, it's logged as:

```
🚨 ALERT: NOK | RVOL: 1.75x + CATALYST NEWS
```

**Get notified:**

### Email Alerts (Coming)

You can add a step to `.github/workflows/scanner.yml` to email you alerts:

```yaml
- name: Send Email Alert
  if: contains(job.status, 'failure')  # On error
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.EMAIL_USER }}
    password: ${{ secrets.EMAIL_PASS }}
    subject: "Volume Scanner Alert"
    to: your@email.com
```

### Slack/Discord Alerts

Similar approach - add webhook step to workflow.

### Simple: Check GitHub Actions

1. Star your repo (bookmark it)
2. Check "Actions" tab each morning
3. Download latest logs to see alerts

---

## Cost

**Free GitHub tier:**
- ✓ Unlimited Actions runs (limited to 2,000 minutes/month per user)
- ✓ Unlimited storage
- ✓ 40,000 run minutes free per month
- ✓ Enough for daily scanning (5 hours × 20 trading days = 100 hours/month)

**You'll never hit the limit** running once per day.

---

## Monitor from iPhone

Since it's on GitHub:

1. Go to your repo on iPhone: github.com/yourusername/volume-scanner
2. Click "Actions" tab
3. See latest scan result
4. Click run → "Artifacts" to download logs
5. Or check `/logs` folder for all historical logs

Much easier than Mac!

---

## Troubleshooting

### "Workflow failed"

Click the failed run to see error:

```
ImportError: No module named 'requests'
```

→ Missing dependencies. Check `requirements.txt` is in repo.

```
401 Unauthorized
```

→ API key not set. Go to Settings → Secrets → add `FINNHUB_API_KEY`

```
No such file or directory: 'volume_scanner.py'
```

→ File not uploaded to repo. Upload all Python files.

### Logs not saving to repo

Make sure `.github/workflows/scanner.yml` has:

```yaml
- name: Commit logs back to repo
```

This step saves logs to `/logs` folder automatically.

---

## Next Steps

1. ✓ Create GitHub repo
2. ✓ Upload files
3. ✓ Add workflow file
4. ✓ Set API key secret
5. ✓ Enable Actions
6. ✓ Wait for first run (3:55 AM PST tomorrow) OR click "Run workflow" manually
7. ✓ Check `/logs` folder for results

---

## Advantages over Mac

- ✓ No Mac running 24/7 (saves power)
- ✓ Runs in cloud (more reliable)
- ✓ Automatic schedule (no manual start/stop)
- ✓ Check results from iPhone anytime
- ✓ Historical logs saved (all dates)
- ✓ Free (GitHub free tier)

---

## FAQ

**Q: Will my API key be safe?**
A: Yes. GitHub Secrets are encrypted. Your key never appears in logs or code.

**Q: Can I change watchlist anytime?**
A: Yes. Edit `volume_scanner.py` in GitHub, next scan uses new watchlist.

**Q: What if I want to run twice per day?**
A: Add another line to cron schedule in `.github/workflows/scanner.yml`

**Q: Can I run it right now (not wait for schedule)?**
A: Yes. Go to Actions → Volume Scanner → "Run workflow" button.

**Q: What happens if it fails?**
A: Logs still save. Check "Actions" tab to see error. Fix and re-run.

---

**Last Updated:** 2024-06-24  
**Status:** Production Ready
