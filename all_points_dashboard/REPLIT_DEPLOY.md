# Deploy to Replit - Quick Guide

## 🚀 5-Minute Deployment

### Step 1: Create Replit Account (1 min)
1. Go to https://replit.com
2. Sign up with Google/GitHub (free)

### Step 2: Create New Repl (1 min)
1. Click "+ Create Repl"
2. Select "Import from GitHub" OR "Python" template
3. Name: "AllPoints-AI-Dashboard"

### Step 3: Upload Files (2 min)
Drag and drop this entire `all_points_dashboard/` folder into Replit

**Or** use GitHub:
```bash
git init
git add .
git commit -m "All Points dashboard"
git push to github
# Then import in Replit
```

### Step 4: Click Run (1 min)
Click the big green "Run" button

Replit will:
- Install dependencies automatically
- Start Streamlit server
- Open in webview

### Step 5: Share ✨
1. Click "Share" button (top right)
2. Toggle "Public" on
3. Copy URL
4. Send to All Points team

**Done!** 🎉

---

## 📧 Share with All Points

Email template:

```
Subject: All Points AI Agents - Live Demo

Hi Michael, Adam, and Oliver,

I've built a unified dashboard showcasing all 6 AI agents we discussed.

🔗 Live Demo: [Your Replit URL]

You can:
- See $342K+ total annual ROI
- Test the LTL automation agent with real quotes
- Explore each agent's capabilities
- No installation needed - just click the link

The dashboard shows:
✅ Email Triage ($32K-52K/year savings)
✅ Profitability Analyzer ($60K+/year value)
✅ LTL Automation ($51K/year) - **fully functional demo**
✅ Carrier Monitor ($40K-60K/year)
✅ Rate Shopping ($130K/year)
✅ Chargeback Defense ($35K/year)

Try the LTL Automation page - enter any shipment details and get
real quotes from 5+ carriers in seconds.

Looking forward to discussing!

Best,
Nathan
```

---

## 🎬 Demo Flow (5 Minutes)

### **Minute 1: Home Page**
> "This dashboard brings all 6 agents together. Total annual value: $342K+"

[Show the 3 metric cards at top]

### **Minute 2: Overview**
> "Here's what each agent does..."

[Scroll through the 6 agent cards]

### **Minute 3-4: Live Demo**
> "Let me show you the LTL automation running live..."

[Click LTL Automation, fill in sample data, click "Get Quotes"]

> "In 10 seconds, we have quotes from 5 carriers, AI-drafted email, and savings calculated."

### **Minute 5: Next Steps**
> "You can test this yourself right now - here's the URL. No setup needed.
>
> Next steps:
> 1. Your team explores the demos
> 2. We schedule a follow-up to discuss production deployment
> 3. Connect your real APIs (MyCarrier, ShipStation, etc.)
> 4. Deploy to production in 2-3 weeks"

---

## 🔧 Optional: Custom Domain

If you want `allpoints.yourdomain.com` instead of `replit.app`:

1. Upgrade to Replit Hacker ($7/month)
2. Go to Repl Settings → Domains
3. Add custom domain
4. Update DNS (CNAME record)

---

## ⚡ Performance Tips

### Free Tier:
- Repl sleeps after 1 hour inactivity
- Wakes up on first request (5-10 seconds)
- Fine for demos, not ideal for production

### Solutions:
1. **Upgrade to Hacker** - Always-on ($7/month)
2. **Use Streamlit Cloud** - Free always-on
3. **Deploy to production** - AWS/GCP/Azure

### For Demo:
- Free tier is perfect
- Just warn All Points: "First load may take 5-10 seconds"
- After that, instant

---

## 🎯 Success Checklist

Before sharing URL:

- [ ] Dashboard loads without errors
- [ ] All navigation links work
- [ ] LTL Automation demo runs successfully
- [ ] Metrics display correctly
- [ ] Mobile view looks good
- [ ] URL is public (not private)
- [ ] Tested in incognito/private window

---

## 🐛 Common Issues

### "Package not found"
**Fix:** Replit auto-installs from `requirements.txt`. If not:
```bash
# In Replit Shell:
pip install -r requirements.txt
```

### "Port 8501 already in use"
**Fix:** Replit handles ports automatically. Use port 8080 in `.replit` file (already configured)

### "Module not found: agent"
**Fix:** Make sure parent directories are in path. LTL page already handles this.

### Page shows "404"
**Fix:**
- File must be in `pages/` directory
- Must start with number_emoji_name.py
- Check exact spelling

---

## 📊 Analytics (Optional)

Track who's using your demo:

1. Add Google Analytics to `app.py`
2. Use Replit Analytics (Hacker plan)
3. Add simple counter in sidebar

```python
# Simple usage counter
if 'visits' not in st.session_state:
    st.session_state.visits = 0
st.session_state.visits += 1
st.sidebar.metric("Demo Views", st.session_state.visits)
```

---

## 🚀 You're Ready!

1. Upload to Replit
2. Click Run
3. Share URL
4. Show All Points the future of logistics automation

**Total build time: 5 minutes**
**Total value: $342K+ annually**

Let's go! 🎉
