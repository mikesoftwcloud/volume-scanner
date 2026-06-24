# Volume Scanner

Real-time stock volume scanner detecting unusual relative volume (RVOL) spikes combined with catalyst news. Runs automatically in the cloud using GitHub Actions.

**Key Features:**
- ✅ Detects 50%+ volume spikes (RVOL 1.5x+)
- ✅ Filters for catalyst news (earnings, FDA, contracts, etc.)
- ✅ Runs automatically on schedule (no Mac needed)
- ✅ Pre-market hours only (4am-9am PST)
- ✅ Cloud-based (GitHub Actions - free)
- ✅ Historical logs saved
- ✅ Mobile-friendly (check results on iPhone)

---

## Quick Start (GitHub Cloud Version)

**Setup: 5 minutes**

### 1. Create GitHub Repository
```bash
# Go to https://github.com/new
# Name: volume-scanner
# Public (free)
# Create
```

### 2. Upload Files
In your new repo, click "Add file" → "Upload files"

Upload these files:
- `volume_scanner.py`
- `test_scanner.py`
- `requirements.txt`
- `.github/workflows/scanner.yml` (create as described below)

### 3. Create Workflow File
Click "Add file" → "Create new file"
- Name: `.github/workflows/scanner.yml`
- Copy content from `scanner.yml` in this repo
- Commit

### 4. Add API Key (Secret)
Go to Settings → Secrets and variables → Actions → New repository secret
- Name: `FINNHUB_API_KEY`
- Value: (get from https://finnhub.io/)

### 5. Enable Actions
Go to Actions tab → "I understand my workflows, go ahead and enable them"

### Done!
Scanner runs automatically at **3:55 AM PST every trading day**.

---

## Check Results (iPhone, Mac, or PC)

1. Go to your GitHub repo
2. Click "Actions" tab
3. Click latest workflow run
4. Download `scanner-logs` artifact
5. OR check `/logs` folder for all daily logs

---

## Files Explained

| File | Purpose |
|------|---------|
| `volume_scanner.py` | Main scanner (fetches data, detects alerts) |
| `test_scanner.py` | Validation tests (run before deploying) |
| `requirements.txt` | Python dependencies |
| `.github/workflows/scanner.yml` | GitHub Actions automation |
| `GITHUB_SETUP.md` | Detailed setup guide |
| `SETUP_GUIDE.md` | General documentation |
| `QUICK_REFERENCE.md` | Common commands & configs |

---

## Configuration

### Change Watchlist
Edit `volume_scanner.py` → Line 10
```python
WATCHLIST = ["NOK", "LNOK", "AAPL", "TSLA"]
```

### Change RVOL Threshold
Edit `volume_scanner.py` → Line 11
```python
RVOL_THRESHOLD = 1.5  # Lower = more alerts
```

### Change Scan Time
Edit `.github/workflows/scanner.yml` → Line 8
```yaml
cron: '55 11 * * 1-5'  # 3:55 AM PST, Mon-Fri
```

See `GITHUB_SETUP.md` for more options.

---

## View Logs

Logs auto-save to `/logs` folder:
- `scanner_2024-06-24.log`
- `scanner_2024-06-25.log`
- etc.

Each contains:
```
2024-06-24 08:15:33 - INFO - NOK | RVOL: 1.75x | 45,230,000 / 25,800,000
2024-06-24 08:15:35 - WARNING - 🚨 ALERT: NOK | RVOL: 1.75x + CATALYST NEWS
```

---

## Run Manually (Right Now)

Want to test before waiting for schedule?

1. Go to "Actions" tab
2. Click "Volume Scanner"
3. Click "Run workflow"
4. Confirm

Runs immediately.

---

## How It Works

**Relative Volume (RVOL) Calculation:**
```
RVOL = Current Volume / 20-Day Average Volume

Alert triggers when:
1. RVOL >= 1.5x (50% above average)
2. Recent news contains catalyst keywords
3. Not already alerted today
```

**Catalyst Keywords:**
`earnings`, `contract`, `FDA`, `approval`, `acquisition`, `partnership`, `deal`, `patent`, `5G`, `defense`, `AI`, etc.

**Example:**
- Current: 45M shares traded
- 20-day avg: 25M shares
- RVOL: 1.75x ✓
- News: "Nokia wins defense contract"
- Result: **ALERT** 🚨

---

## API Key Setup

### Get Free API Key
1. Go to https://finnhub.io/
2. Sign up (takes 2 minutes)
3. Verify email
4. Copy API key from dashboard

### Add to GitHub
1. Go to repo Settings
2. Click "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Name: `FINNHUB_API_KEY`
5. Value: (paste your key)
6. Your key is encrypted and never visible in logs

---

## Cost

**Free GitHub tier:**
- ✓ Unlimited workflow runs
- ✓ 2,000 free runner minutes/month
- ✓ Unlimited storage
- Your usage: ~100 minutes/month (5 hours × 20 trading days)
- **You'll never hit the limit**

---

## Troubleshooting

### "Workflow failed"
1. Go to Actions tab
2. Click failed run
3. See error message
4. Common fixes in `GITHUB_SETUP.md`

### "No logs saved"
Check that `.github/workflows/scanner.yml` includes:
```yaml
- name: Commit logs back to repo
```

### "401 Unauthorized"
API key not set correctly:
1. Go to Settings → Secrets
2. Verify `FINNHUB_API_KEY` is added
3. Check key spelling (no spaces)

### "No such file or directory"
Files not uploaded to repo. Upload:
- `volume_scanner.py`
- `test_scanner.py`
- `requirements.txt`

---

## Local Testing (Optional)

Want to test on your Mac first?

```bash
# Install dependencies
pip3 install -r requirements.txt

# Create .env file with API key
python3 setup.py

# Run tests
python3 test_scanner.py

# Start scanner (creates logs, no file control needed)
python3 volume_scanner.py
```

---

## Advanced Options

### Email Alerts
Add to `.github/workflows/scanner.yml` to email you when alerts trigger.

### Slack/Discord Notifications
Add webhook step to workflow.

### Database Logging
Modify `volume_scanner.py` to save alerts to database instead of files.

See `SETUP_GUIDE.md` for integration examples.

---

## FAQ

**Q: Will GitHub keep my API key safe?**
A: Yes. GitHub Secrets are encrypted. Your key never appears in logs or code.

**Q: Can I change symbols anytime?**
A: Yes. Edit `volume_scanner.py`, push, next scan uses new watchlist.

**Q: What's the difference between 1.5x and 1.75x RVOL?**
A: 1.5x = 50% above average (more alerts)
   1.75x = 75% above average (fewer, higher quality)

**Q: How do I know if it ran?**
A: Check "Actions" tab. Green checkmark = success. Red X = failed.

**Q: Can I run it twice per day?**
A: Yes. Add another line to cron schedule in `.github/workflows/scanner.yml`

**Q: What symbols should I use?**
A: Any ticker on Finnhub (AAPL, TSLA, NOK, etc.). Test with `test_scanner.py` first.

---

## Next Steps

1. ✅ Create GitHub repo
2. ✅ Upload files
3. ✅ Add workflow file
4. ✅ Set API key secret
5. ✅ Enable Actions
6. ✅ Run workflow manually to test
7. ✅ Check `/logs` for results
8. ✅ Customize watchlist/settings
9. ✅ Monitor from iPhone anytime

---

## Support

**Full Guides:**
- `GITHUB_SETUP.md` - Detailed GitHub setup
- `SETUP_GUIDE.md` - General documentation
- `QUICK_REFERENCE.md` - Common commands

**Issues?**
1. Check logs in Actions tab
2. Re-read troubleshooting section
3. Verify API key is set
4. Test manually with `python3 test_scanner.py`

---

**Version:** 1.0 (GitHub Cloud Edition)  
**Status:** Production Ready  
**Last Updated:** 2024-06-24

---

## Built for

Designed for active traders monitoring:
- **NOK/LNOK** - 5G, defense contracts, earnings catalysts
- **Tech stocks** - AAPL, TSLA, NVDA earnings/news
- **Any volatile ticker** - Earnings season, merger activity, FDA approvals

Track unusual volume combined with catalyst news for early entry opportunities.
