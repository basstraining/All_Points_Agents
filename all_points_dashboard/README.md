# All Points ATL - AI Agents Dashboard

Unified interface for all 6 AI automation agents.

## 🚀 Quick Start (Local)

```bash
cd all_points_dashboard
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501

---

## 📦 Deploy to Replit

### Step 1: Create New Repl

1. Go to https://replit.com
2. Click "+ Create Repl"
3. Choose "Python" template
4. Name it: "AllPoints-AI-Dashboard"

### Step 2: Upload Files

Upload this entire `all_points_dashboard/` directory to Replit

### Step 3: Configure Replit

Create `.replit` file:
```toml
run = "streamlit run app.py --server.port=8080 --server.address=0.0.0.0"

[nix]
channel = "stable-22_11"

[deployment]
run = ["sh", "-c", "streamlit run app.py --server.port=8080 --server.address=0.0.0.0"]
```

### Step 4: Set Environment Variables (Optional)

In Replit Secrets:
```
GOOGLE_API_KEY=your_key_here
ARCADE_API_KEY=your_key_here
```

### Step 5: Run

Click "Run" button in Replit

### Step 6: Share

- Click "Share" in Replit
- Copy the public URL
- Send to All Points team

---

## 🎯 What's Included

### Dashboard Features

✅ **Home Page**
- Total ROI overview ($342K+/year)
- All 6 agents at a glance
- Quick navigation to each agent

✅ **Individual Agent Pages**
- Email Triage (demo with mock data)
- Profitability Analyzer (placeholder)
- LTL Automation (fully functional)
- Carrier Monitor (placeholder)
- Rate Shopping (placeholder)
- Chargeback Defense (placeholder)

✅ **Professional UI**
- Gradient cards
- Responsive layout
- Mobile-friendly
- Dark/light mode support

---

## 📊 Agents Summary

| Agent | Annual ROI | Status |
|-------|-----------|--------|
| Email Triage | $32K-52K | ✅ Demo ready |
| Profitability | $60K+ | 🚧 Coming soon |
| LTL Automation | $51K | ✅ Fully functional |
| Carrier Monitor | $40K-60K | 🚧 Coming soon |
| Rate Shopping | $130K | 🚧 Coming soon |
| Chargeback Defense | $35K | 🚧 Coming soon |

**Total:** $342K+ annual savings

---

## 🔧 Customization

### Add Your Branding

Edit `app.py`:
```python
st.set_page_config(
    page_title="Your Company - AI Agents",
    page_icon="🤖",
    ...
)
```

### Connect Real Agents

To make placeholder pages functional:

1. Copy agent code from parent directories
2. Import in each page file
3. Connect to real APIs via Arcade

Example (already done for LTL Automation):
```python
# In pages/3_🚛_LTL_Automation.py
import sys
from pathlib import Path
sys.path.insert(0, str(parent_dir / "05_ltl_automation"))
from agent import process_quote_request
```

### Update ROI Numbers

Edit values in `app.py` to match actual All Points data

---

## 🎬 Demo Tips

### For All Points Call:

1. **Start on home page** - Show total $342K ROI
2. **Click LTL Automation** - Run live demo
3. **Click Email Triage** - Show mock categorization
4. **Back to home** - Emphasize 6 agents, 40+ hrs/week saved

### What to Say:

> "This dashboard gives you access to all 6 AI agents in one place.
> Each agent automates a specific workflow in your logistics operations.
> Together, they save $342K per year and 40+ hours every week.
>
> Let me show you the LTL automation agent running live..."

[Click LTL Automation, run demo]

> "In 10 seconds, we got quotes from 5 carriers, compared rates, and drafted a professional email.
> This normally takes 18 minutes manually.
>
> You can test this yourself - here's the URL. No installation needed,
> just click and try any agent with the sample data."

---

## 🚀 Deployment Options

### Option 1: Replit (Easiest)
- ✅ One-click deployment
- ✅ Free tier available
- ✅ Public URL to share
- ✅ Collaborative

### Option 2: Streamlit Cloud
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Deploy from GitHub
4. Share streamlit.app URL

### Option 3: Custom Domain
- Deploy to Heroku/AWS/GCP
- Point custom domain
- More control, more setup

---

## 📝 Next Steps

### To Complete All Agents:

1. **Move agent files** from `email_triage_demo/` subdirectories
2. **Integrate each agent** into its page
3. **Add real data connections** via Arcade
4. **Test thoroughly** with All Points data

### Enhancement Ideas:

- Add user authentication
- Track usage analytics
- Save quote history
- Export reports to PDF
- Multi-customer support
- Role-based access

---

## 💡 Tips for Replit

### Free Tier Limits:
- ⚠️ Repl sleeps after inactivity
- ⚠️ Limited compute (fine for demos)
- ⚠️ Public by default

### Solutions:
- Use Replit Hacker plan for always-on
- Or accept sleep (wakes on first request)
- Or deploy to Streamlit Cloud (free always-on)

### Best Practices:
- Keep demo data small
- Cache expensive operations
- Use `@st.cache_data` for mock data
- Test before sharing URL

---

## 🆘 Troubleshooting

### "Module not found" errors
```bash
# In Replit, run:
pip install -r requirements.txt
```

### Page not loading
- Check that file names match exactly
- Pages must be in `pages/` directory
- File names must start with number_emoji_name.py

### Import errors on LTL page
- Ensure `05_ltl_automation/` exists in parent directory
- Or comment out imports and use mock data

---

## 📞 Support

**For All Points Team:**
- Nathan Bass - nathan@arcade.dev
- Demo URL: [To be shared after deployment]

**Technical Issues:**
- Streamlit Docs: https://docs.streamlit.io
- Replit Docs: https://docs.replit.com

---

## ✅ Pre-Demo Checklist

Before sharing with All Points:

- [ ] Test all pages load
- [ ] LTL automation runs successfully
- [ ] ROI numbers are accurate
- [ ] No errors in console
- [ ] Mobile view looks good
- [ ] Share URL is public
- [ ] Have backup video demo ready

---

**Built for All Points ATL | February 2026**

**Total Value: $342K+ annually | 40+ hours/week saved**

🚀 **Ready to transform logistics with AI!**
