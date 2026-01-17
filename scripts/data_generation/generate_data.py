import os
import random
from datetime import date, timedelta
import pandas as pd

random.seed(42)

OUT_DIR = "data/raw/generated"
os.makedirs(OUT_DIR, exist_ok=True)

def daterange(start: date, end: date):
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)

regions = ["NA", "EMEA", "APAC"]
countries = {
    "NA": ["USA", "Canada"],
    "EMEA": ["Germany", "France", "UK"],
    "APAC": ["Japan", "Korea", "Singapore"]
}
segments = ["Orthodontic Clinic", "DSO"]
channels = ["Paid Search", "LinkedIn", "Webinar", "Display", "Partners"]
product_lines = ["Clear Aligners", "Scanner", "Imaging"]

# ---------- DIM: accounts ----------
def make_accounts(n=250):
    rows = []
    for i in range(1, n+1):
        region = random.choice(regions)
        country = random.choice(countries[region])
        seg = random.choice(segments)
        created = date(2023, 1, 1) + timedelta(days=random.randint(0, 700))
        rows.append({
            "account_id": f"ACC-{i:04d}",
            "account_name": f"Account {i:04d}",
            "region": region,
            "country": country,
            "segment": seg,
            "created_date": created.isoformat(),
            "is_active": True
        })
    return pd.DataFrame(rows)

# ---------- DIM: campaigns ----------
def make_campaigns(n=30):
    rows = []
    for i in range(1, n+1):
        region = random.choice(regions)
        channel = random.choice(channels)
        start = date(2024, 1, 1) + timedelta(days=random.randint(0, 500))
        end = start + timedelta(days=random.randint(14, 90))
        spend = random.randint(8000, 120000)
        rows.append({
            "campaign_id": f"CMP-{1000+i}",
            "campaign_name": f"{channel}-Campaign-{i:02d}",
            "channel": channel,
            "region": region,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "objective": random.choice(["Lead Gen", "Demand Gen", "Conversion", "Pipeline"]),
            "spend_usd": spend
        })
    return pd.DataFrame(rows)

# ---------- FACT: leads ----------
def make_leads(accounts_df, campaigns_df, n=8000):
    rows = []
    campaign_ids = campaigns_df["campaign_id"].tolist()

    for i in range(1, n+1):
        created = date(2024, 1, 1) + timedelta(days=random.randint(0, 730))
        camp = random.choice(campaign_ids)
        camp_row = campaigns_df.loc[campaigns_df["campaign_id"] == camp].iloc[0]
        region = camp_row["region"]
        channel = camp_row["channel"]

        # Funnel progression probabilities (tunable)
        p_mql = 0.35 if channel in ["Paid Search", "LinkedIn"] else 0.25
        p_sql = 0.45
        is_mql = random.random() < p_mql
        is_sql = is_mql and (random.random() < p_sql)

        mql_date = (created + timedelta(days=random.randint(2, 21))).isoformat() if is_mql else ""
        sql_date = (created + timedelta(days=random.randint(10, 45))).isoformat() if is_sql else ""

        converted = ""
        if is_mql and random.random() < 0.60:
            converted = accounts_df.sample(1).iloc[0]["account_id"]

        status = "Lead"
        if is_sql:
            status = "SQL"
        elif is_mql:
            status = "MQL"

        rows.append({
            "lead_id": f"LEAD-{100000+i}",
            "created_date": created.isoformat(),
            "region": region,
            "channel": channel,
            "campaign_id": camp,
            "lead_status": status,
            "mql_date": mql_date,
            "sql_date": sql_date,
            "converted_account_id": converted
        })

    return pd.DataFrame(rows)

# ---------- FACT: opportunities ----------
def make_opportunities(leads_df, accounts_df, n=2500):
    rows = []

    sql_leads = leads_df[leads_df["lead_status"] == "SQL"].copy()
    if len(sql_leads) == 0:
        return pd.DataFrame(rows)

    sampled = sql_leads.sample(min(n, len(sql_leads)))

    for idx, lead in sampled.iterrows():
        created = date.fromisoformat(lead["created_date"])
        region = lead["region"]

        # If lead converted to an account use it; else assign one
        account_id = lead["converted_account_id"] if lead["converted_account_id"] else accounts_df.sample(1).iloc[0]["account_id"]

        product = random.choices(product_lines, weights=[0.65, 0.20, 0.15])[0]
        base_amt = {"Clear Aligners": 55000, "Scanner": 35000, "Imaging": 25000}[product]
        amount = int(random.gauss(base_amt, base_amt * 0.35))
        amount = max(5000, amount)

        stage = random.choices(
            ["Closed Won", "Closed Lost", "Negotiation", "Proposal"],
            weights=[0.42, 0.18, 0.20, 0.20]
        )[0]

        close_date = ""
        if stage in ["Closed Won", "Closed Lost"]:
            close = created + timedelta(days=random.randint(15, 120))
            close_date = close.isoformat()

        rows.append({
            "opp_id": f"OPP-{200000+len(rows)+1}",
            "account_id": account_id,
            "lead_id": lead["lead_id"],
            "created_date": created.isoformat(),
            "close_date": close_date,
            "stage": stage,
            "amount_usd": amount,
            "product_line": product,
            "region": region
        })

    return pd.DataFrame(rows)

# ---------- FACT: shipments ----------
def make_shipments(accounts_df, n=6000):
    rows = []
    for i in range(1, n+1):
        ship = date(2024, 1, 1) + timedelta(days=random.randint(0, 730))
        acc = accounts_df.sample(1).iloc[0]
        region = acc["region"]
        product = random.choices(product_lines, weights=[0.75, 0.15, 0.10])[0]
        doctor_id = f"DR-{random.randint(9000, 9999)}"
        cases = random.randint(1, 8) if product == "Clear Aligners" else random.randint(1, 2)

        rows.append({
            "shipment_id": f"SHP-{300000+i}",
            "ship_date": ship.isoformat(),
            "region": region,
            "account_id": acc["account_id"],
            "doctor_id": doctor_id,
            "product_line": product,
            "cases_shipped": cases
        })
    return pd.DataFrame(rows)

def main():
    accounts = make_accounts()
    campaigns = make_campaigns()
    leads = make_leads(accounts, campaigns)
    opps = make_opportunities(leads, accounts)
    shipments = make_shipments(accounts)

    accounts.to_csv(os.path.join(OUT_DIR, "crm_accounts_full.csv"), index=False)
    campaigns.to_csv(os.path.join(OUT_DIR, "marketing_campaigns_full.csv"), index=False)
    leads.to_csv(os.path.join(OUT_DIR, "crm_leads_full.csv"), index=False)
    opps.to_csv(os.path.join(OUT_DIR, "crm_opportunities_full.csv"), index=False)
    shipments.to_csv(os.path.join(OUT_DIR, "erp_shipments_full.csv"), index=False)

    print("Generated:", OUT_DIR)

if __name__ == "__main__":
    main()
