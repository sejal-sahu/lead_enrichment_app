# lead_enrichment_app

# AI-Powered Lead Enrichment & Routing

## 1. Business Summary

Marketing Operations receives thousands of inbound leads every month through the "Contact Us" form. Each lead contains a free-text comment describing what the prospect needs. Today, someone must read every message manually to determine urgency, persona, and which internal team should follow up.  
This process is:

- Time-consuming (2–4 hours/day of manual review)
- Inconsistent (different reviewers interpret messages differently)
- Slower for prospects (delays in routing reduce conversion rates)

### **What this solution delivers**
This project automates the interpretation and routing of incoming leads using Google’s Gemini AI model.

**Business benefits:**

- 🕒 **Saves 10–20 hours/week** of manual lead review  
- 🎯 **Improves routing accuracy and consistency**  
- ⚡ **Accelerates response times for high-value prospects**  
- 📈 **Allows Marketing Ops to scale lead volume without adding headcount**  

---

## 2. How It Works (Simple Explanation)

This solution uses a four-step workflow:

1. **Read the leads file** (`leads.csv`)  
   Each row contains: email, job title, and free-text comment.

2. **Ask Gemini AI to analyze each lead**  
   The model reads the job title + comment and returns structured info:
   - Urgency (High / Medium / Low)
   - Persona type (Decision Maker / Practitioner / Other)
   - One-sentence summary of the request

3. **Apply routing rules**  
   Based on AI output:
   - High + Decision Maker → **Strategic Sales**
   - High + Practitioner → **Enterprise Sales**
   - Medium → **Sales Development**
   - Low → **Nurture Campaign**

4. **Export final results**  
   The script produces a JSON file with:
   - Original fields
   - Enriched fields
   - Assigned team

---

## 3. Technical Deep Dive

This section explains the design decisions for the technical reviewer.

### **3.1 Architecture**

- **Pandas** is used to ingest and clean the CSV file  
- **Gemini 2.5 flash API** performs natural-language analysis  
- A custom **JSON-extraction function** ensures the model output is machine-readable  
- A simple **rule-based router** assigns leads to internal teams  
- Final output is saved as `output_enriched_leads.json`  

### **3.2 Prompt Engineering**

The prompt is deliberately constrained to force Gemini to produce a **strict JSON schema**.  
It asks the model to behave deterministically and classify leads using predefined categories.


### **Why this approach works**

- Minimizes hallucination by providing **closed-choice labels**  
- Ensures structured, parseable output  
- Keeps token cost low by restricting instruction complexity  
- Easy to adjust categories in the future  

### **3.3 JSON Extraction Logic**

Because LLMs sometimes wrap responses in markdown code blocks, a robust regex is used to extract only the `{ ... }` block, even if surrounded by:

- Triple backticks  
- Extra quotes  
- Additional comments  

This ensures safe parsing via `json.loads()`.

---

## 4. Setup & Run Instructions

### **4.1 Requirements**
- Python 3.11+
- Google Gemini API key
- Packages:
  - pandas  
  - google-genai  
  - python-dotenv (optional)

Install dependencies:

```bash
pip install pandas python-dotenv
```

```bash
pip install google-generativeai
```
set the GEMINI_API_KEY

```bash
export GEMINI_API_KEY="your-gemini-key"

```

### **4.2 Requirements**
## 4.2 Run the Script

```bash
python main.py
```

## 5. Future Improvements

### 5.1 Error Handling Enhancements
- Add retry logic for API timeouts  
- Gracefully handle malformed inputs  
- Improve logging for long-term monitoring and debugging  

### 5.2 Cost Optimization
- Cache repeated lead texts to prevent duplicate API calls  
- Batch multiple leads in a single request  
- Add token usage and cost reporting  

### 5.3 Expanded Data Sources
- Add webhook support for real-time lead ingestion  
- Support CSV, JSONL, and API-based ingestion

### 5.4 Advanced Preprocessing
- Strip HTML signatures, quoted email chains, and trackers  
- Auto-detect and normalize multilingual lead messages  
- Clean whitespace, emojis, and unusual formatting  

### 5.5 Output & Workflow Integrations
- Auto-route leads to CRM queues or campaigns  
- Push AI summaries and classifications to Slack  
- Export enriched data to BigQuery, Snowflake, etc.  
- Add optional AI confidence scoring  

### 5.6 Productization Enhancements
- Create a lightweight UI dashboard for non-technical users  
- Add scheduling or queue-based batch processing  
- Introduce a configuration file for routing rules  


