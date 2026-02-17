# Demo Scenarios — All Points ATL

Pre-crafted prompts for live sales demos. Copy-paste these into Claude to kick off each scenario. Each one is designed to show cross-system orchestration: data pulls → analysis → real artifact delivered to the prospect's tools.

---

## Scenario 1: Monday Morning Triage

**The story:** It's Monday morning. Walk me through everything I need to know before the ops meeting.

**Prompt:**
```
Give me a Monday morning operations briefing. I need to know:
- Any critical shipment exceptions that need immediate attention
- Unread emails that need a human response (skip anything auto-resolved)
- Chargebacks with deadlines expiring this week
- Any clients with profitability concerns

Prioritize by urgency. If anything needs immediate action, flag it at the top.
```

**What it shows:** All 6 tool domains queried at once, cross-referenced, and prioritized into a single actionable briefing.

---

## Scenario 2: Chargeback Sprint

**The story:** We have chargebacks about to expire. Build the defense and notify the team.

**Prompt:**
```
Show me all chargebacks with deadlines expiring in the next 10 days. For the highest-dollar one, pull up the full details including evidence files and violation description. Then draft an email to the client summarizing what was charged back, what evidence we have to dispute it, and what we need from them to proceed.
```

**Follow-up prompt (after email is drafted):**
```
Send that email. Then post a summary in Slack letting the team know we have [X] chargebacks expiring this week with $[X] at risk.
```

**What it shows:** Data query → analysis → email drafted and sent to real inbox → Slack alert posted to real channel.

---

## Scenario 3: Client Profitability Deep Dive

**The story:** A client QBR is coming up. Prep the analysis and build the deck.

**Prompt:**
```
I have a QBR with TurtleBox Audio next week. Pull together their profitability analysis — revenue, labor costs, margin, and how it breaks down by service type. Also check their shipment exception rate and any open chargebacks. I need to understand the full picture.
```

**Follow-up prompt:**
```
Build a Google Slides deck for the QBR with:
- Slide 1: Account overview (revenue, margin, order volume)
- Slide 2: Labor cost breakdown by service type
- Slide 3: Shipping performance (exceptions, carrier breakdown)
- Slide 4: Chargeback status and compliance summary
- Slide 5: Recommendations
```

**What it shows:** Multi-domain data pull → synthesized into a presentation → delivered as a real Google Slides deck.

---

## Scenario 4: Rate Shopping Batch

**The story:** We have 80+ orders waiting to ship. Find the cheapest rates across all of them.

**Prompt:**
```
Rate shop all open orders and tell me how much we'd save by always picking the cheapest carrier. Break it down by which carriers win most often. Also flag if any carrier that wins on price has a high exception rate — I don't want to optimize cost and tank delivery quality.
```

**What it shows:** Batch rate shopping (83 orders at once) → carrier comparison → cross-referenced against exception data from a different system. The cost-vs-quality insight is something no single tool can surface alone.

---

## Scenario 5: Exception Escalation

**The story:** A customer is asking about a delayed shipment. Handle it end-to-end.

**Prompt:**
```
A customer emailed about a late delivery. Check the unread emails for any shipping issues, find the shipment in our system, and tell me what happened. If there's an active exception, draft a response to the customer with the current status and expected resolution.
```

**Follow-up prompt (after draft is ready):**
```
Send that response. Then check if this client has other shipments with exceptions right now — I want to get ahead of any more complaints.
```

**What it shows:** Email triage → shipment lookup → exception investigation → customer response sent to real inbox → proactive check across remaining shipments.

---

## Scenario 6: LTL Cost Comparison

**The story:** We're shipping heavy freight and want to compare carriers across lanes.

**Prompt:**
```
Compare LTL carrier pricing for PeakGear Outdoors across all their lanes. Which carrier is cheapest on average? How much would we save annually if we always used the cheapest option per lane? Also pull up any confirmed bookings that are still pending pickup.
```

**What it shows:** LTL freight quoting → carrier comparison by lane → savings projection → booking status check.

---

## Scenario 7: Cross-Client Pattern Detection

**The story:** Step back from individual accounts and look at the whole operation.

**Prompt:**
```
Give me a cross-client health check. For each of our 8 clients, show me:
- Profit margin category (Excellent/Good/Acceptable/Poor/Losing Money)
- Number of open exceptions
- Number of open chargebacks
- Invoice payment status (paid/pending/overdue)

Sort by whoever needs the most attention. If any client is both low-margin and has overdue invoices, call that out specifically.
```

**What it shows:** Three different systems (profitability, exceptions, chargebacks) unified into a single cross-client view that no existing dashboard provides.

---

## Tips for Running the Demo

1. **Authenticate first.** Before the call, make sure the prospect has connected their Gmail and Slack through the Arcade Gateway. The "check your inbox" moment only works if their real accounts are connected.

2. **Start with Scenario 1 (Monday Morning Triage).** It touches everything and sets context for the deeper dives. It's also the most relatable — everyone has a Monday morning.

3. **Let them drive.** After the first scenario, ask "What would you want to ask next?" The system prompt handles arbitrary questions — they don't need to stick to scripts.

4. **The "check your inbox" moment.** When an email gets sent or a Slack message posts, pause and let them actually go check. That's the moment it clicks.

5. **Don't explain the tech.** If they ask how it works, keep it simple: "Your systems are connected through Arcade's Gateway. Claude can read from and write to all of them through a single conversation." Save architecture deep-dives for the technical follow-up.
