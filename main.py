import google.generativeai as genai
import pandas as pd
import json
import re


# Setup Gemini API and create the Generative Model instance
genai.configure()
model = genai.GenerativeModel('gemini-2.5-flash')
# set the GEMINI_API_KEY as environment variable


# Function to clean the input csv file
def clean_csv_file(input_file, output_file):
    """ Converts input file to correct csv format"""
    cleaned_lines = []

    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # Remove outer quotes if present
            if line.startswith('"') and line.endswith('"'):
                line = line[1:-1]

            # Replace doubled quotes ("") with single quotes (")
            line = re.sub(r'""', '"', line)

            cleaned_lines.append(line)

    with open(output_file, "w", encoding="utf-8") as f:
        for l in cleaned_lines:
            f.write(l + "\n")

    print(f"Saved cleaned file to {output_file}")

# Function to extract json from model response
def extract_json(raw_text):
    """
    Extracts JSON object {...}, wrapped in ```json ... ``` or extra quotes.
    """

    # Remove surrounding quotes if present
    if raw_text.startswith('"') and raw_text.endswith('"'):
        raw_text = raw_text[1:-1]

    # Extract JSON inside triple backticks if they exist
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_text, flags=re.DOTALL)
    if fenced:
        json_text = fenced.group(1)
    else:
        # fallback → extract first {...} block
        match = re.search(r"\{.*\}", raw_text, flags=re.DOTALL)
        if not match:
            raise ValueError("No JSON object found")
        json_text = match.group(0)

    # Load JSON into Python dict
    return json.loads(json_text)


# Function to call Gemini for enrichment
def enrich_lead(job_title, comment):
    """
    Function to call Gemini to enrich the input.
    Provides the response in json format.
    """

    prompt = f"""
        You are an AI that extracts structured insight from inbound leads.

        Given the following fields:
        job_title: "{job_title}"
        comment: "{comment}"

        Return ONLY a JSON object with exactly these keys:
        - urgency: one of ["High", "Medium", "Low"]
        - persona_type: one of ["Decision Maker", "Practitioner", "Other"] ("Other" includes student or researcher)
        - summary: a single-sentence summary of the user's request

        Rules:
        - If the person controls budgets or is senior (C-level, VP, Head) → Decision Maker
        - If the person is hands-on (Analyst, Engineer, Specialist) → Practitioner
        - Students or researchers → Other
        - Urgency determination:
            * High → explicitly asks for demo, sales contact, technical meeting, evaluation, or active project
            * Medium → general interest or exploratory questions
            * Low → educational or academic, not for purchase
        - Only return the json response in curly brackets without any other text
        Example output:
        {{
        "urgency": "High",
        "persona_type": "Decision Maker",
        "summary": "The user needs to improve order management efficiency and is available for a technical deep dive next week."
        }}
        """

    response = model.generate_content(prompt)
    # print("AI Response", response)
    
    # Gemini may return code-block formatting, so strip anything extra
    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
    try:
        # print("TEXT", text)
        enriched = extract_json(text)
    except json.JSONDecodeError:
        # Fallback: try to repair or return defaults
        enriched = {
            "urgency": "Medium",
            "persona_type": "Other",
            "summary": "Could not parse AI response."
        }
    return enriched


# Routing Logic
def assign_team(urgency, persona_type):
    if urgency == "High" and persona_type == "Decision Maker":
        return "Strategic Sales"
    if urgency == "High" and persona_type == "Practitioner":
        return "Enterprise Sales"
    if urgency == "Medium":
        return "Sales Development"
    return "Nurture Campaign"


def main():

    input_file = "leads.csv"
    output_file = "leads_clean.csv"
    clean_csv_file(input_file, output_file)

    df = pd.read_csv(output_file, header=None, names=["email", "job_title", "comment"])

    output_rows = []

    print("Processing the leads...")
    # Process each lead
    for _, row in df.iterrows():
        enriched = enrich_lead(row["job_title"], row["comment"])

        assigned_team = assign_team(enriched["urgency"], enriched["persona_type"])

        output_rows.append({
            "email": row["email"],
            "job_title": row["job_title"],
            "comment": row["comment"],
            "urgency": enriched["urgency"],
            "persona_type": enriched["persona_type"],
            "summary": enriched["summary"],
            "assigned_team": assigned_team
        })


    # Write Output JSON
    with open("output_enriched_leads.json", "w") as f:
        json.dump(output_rows, f, indent=4)

    print("Processing complete. Output saved to output_enriched_leads.json")


if __name__ == '__main__':
    main()



