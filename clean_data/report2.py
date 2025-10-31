import os
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Directory setup
BASE_DIR = os.getcwd()
DATA_DIR = os.path.join(BASE_DIR, "clean_data")
REPORT_PATH = os.path.join(BASE_DIR, "PhonePe_Insights_Report.pdf")

# Helper function to safely read a CSV
def load_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"❌ Missing file: {filename}")
        return None
    print(f"✅ Loaded {filename}")
    return pd.read_csv(path)

# Load all datasets
agg_txn = load_csv("aggregatedtransaction_df.csv")
map_txn = load_csv("maptransaction_df.csv")
top_txn = load_csv("toptransaction_df.csv")
agg_user = load_csv("aggregateuser_df.csv")
top_user = load_csv("topuser_df.csv")

# Initialize report
styles = getSampleStyleSheet()
story = [Paragraph("📊 PhonePe Pulse Insights Report", styles["Title"]),
         Paragraph("This report provides statistical insights from the cleaned PhonePe Pulse datasets.", styles["Normal"]),
         Spacer(1, 12)]

# 1️⃣ Aggregated Transaction Insights
if agg_txn is not None and all(col in agg_txn.columns for col in ['State', 'Transaction_count', 'Transaction_amount']):
    total_txn = agg_txn['Transaction_count'].sum()
    total_amt = agg_txn['Transaction_amount'].sum()
    top_state = agg_txn.groupby("State")["Transaction_amount"].sum().idxmax()
    story += [
        Paragraph("■■ Aggregated Transaction Insights", styles["Heading2"]),
        Paragraph(f"• Total Transactions Recorded: {total_txn:,.0f}", styles["Normal"]),
        Paragraph(f"• Total Transaction Volume: ₹{total_amt:,.2f}", styles["Normal"]),
        Paragraph(f"• State with Highest Transaction Volume: {top_state}", styles["Normal"]),
        Spacer(1, 12)
    ]
else:
    story.append(Paragraph("■■ Aggregated Transaction data unavailable or missing columns.", styles["Normal"]))

# 2️⃣ Map Transaction Insights
if map_txn is not None and all(col in map_txn.columns for col in ['State', 'Transaction_count', 'Transaction_amount']):
    avg_txn = map_txn['Transaction_amount'].mean()
    story += [
        Paragraph("■■ Map Transaction Insights", styles["Heading2"]),
        Paragraph(f"• Average Transaction Value: ₹{avg_txn:,.2f}", styles["Normal"]),
        Paragraph(f"• Data points: {len(map_txn)}", styles["Normal"]),
        Spacer(1, 12)
    ]
else:
    story.append(Paragraph("■■ Map Transaction data unavailable or missing columns.", styles["Normal"]))

# 3️⃣ Top Transaction Insights
if top_txn is not None and all(col in top_txn.columns for col in ['State', 'Transaction_Count', 'Transaction_Amount']):
    top_states = top_txn.groupby("State")[["Transaction_Count", "Transaction_Amount"]].sum().reset_index()
    top_states = top_states.sort_values(by="Transaction_Amount", ascending=False).head(5)
    story += [
        Paragraph("■■ Top Transaction Insights", styles["Heading2"]),
        Paragraph("• Top 5 States by Transaction Volume:", styles["Normal"])
    ]
    for _, row in top_states.iterrows():
        story.append(Paragraph(f"  - {row['State']}: ₹{row['Transaction_Amount']:,.2f}", styles["Normal"]))
    story.append(Spacer(1, 12))
else:
    story.append(Paragraph("■■ Top Transaction data unavailable or missing columns.", styles["Normal"]))

# 4️⃣ Aggregated User Insights
if agg_user is not None and 'Brand' in agg_user.columns and 'Count' in agg_user.columns:
    popular_brand = agg_user.groupby("Brand")["Count"].sum().idxmax()
    brand_total = agg_user.groupby("Brand")["Count"].sum().max()
    story += [
        Paragraph("■■ Aggregated User Insights", styles["Heading2"]),
        Paragraph(f"• Most Popular Smartphone Brand: {popular_brand} ({brand_total:,} users)", styles["Normal"]),
        Spacer(1, 12)
    ]
else:
    story.append(Paragraph("■■ Aggregated User data unavailable or missing columns.", styles["Normal"]))

# 5️⃣ Top User Insights (Fixed Schema)
if top_user is not None and all(col in top_user.columns for col in ['State', 'Registered_users']):
    top_user_state = top_user.groupby("State")["Registered_users"].sum().reset_index()
    top_user_state = top_user_state.sort_values(by="Registered_users", ascending=False).head(5)
    story += [
        Paragraph("■■ Top User Insights", styles["Heading2"]),
        Paragraph("• Top 5 States by Registered Users:", styles["Normal"])
    ]
    for _, row in top_user_state.iterrows():
        story.append(Paragraph(f"  - {row['State']}: {row['Registered_users']:,} users", styles["Normal"]))
else:
    story.append(Paragraph("■■ Top User data unavailable or missing columns.", styles["Normal"]))

# Generate PDF
doc = SimpleDocTemplate(REPORT_PATH, pagesize=A4)
doc.build(story)
print(f"\n✅ Insights report generated successfully: {REPORT_PATH}")
