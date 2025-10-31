import pandas as pd
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

# ===== CONFIG =====
CLEAN_DATA_PATH = "clean_data"
REPORT_PATH = "insights3_report.pdf"

# ===== LOAD DATA =====
def load_csv(filename):
    path = os.path.join(CLEAN_DATA_PATH, filename)
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        print(f"❌ Missing file: {filename}")
        return None

agg_trans = load_csv("aggregatedtransaction_df.csv")
map_trans = load_csv("maptransaction_df.csv")
top_trans = load_csv("toptransaction_df.csv")
agg_user = load_csv("aggregateuser_df.csv")
top_user = load_csv("topuser_df.csv")

# ===== CREATE DOCUMENT =====
doc = SimpleDocTemplate(REPORT_PATH, pagesize=A4)
styles = getSampleStyleSheet()
story = []

# ===== TITLE =====
story.append(Paragraph("<b>📊 PhonePe Pulse Insights Report</b>", styles["Title"]))
story.append(Spacer(1, 12))
story.append(Paragraph("This report provides statistical insights from the cleaned PhonePe Pulse datasets.", styles["Normal"]))
story.append(Spacer(1, 20))

# ===== AGGREGATED TRANSACTION INSIGHTS =====
if agg_trans is not None and all(col in agg_trans.columns for col in ['State', 'Transaction_Count', 'Transaction_Amount']):
    story.append(Paragraph("<b>1️⃣ Aggregated Transaction Insights</b>", styles["Heading2"]))
    total_txn = agg_trans["Transaction_Count"].sum()
    total_amt = agg_trans["Transaction_Amount"].sum()
    top_state = agg_trans.groupby("State")["Transaction_Amount"].sum().idxmax()
    top_state_amt = agg_trans.groupby("State")["Transaction_Amount"].sum().max()
    story.append(Paragraph(f"• Total Transaction Value: ₹{total_amt:,.2f}", styles["Normal"]))
    story.append(Paragraph(f"• Total Transaction Count: {int(total_txn):,}", styles["Normal"]))
    story.append(Paragraph(f"• Top Performing State: {top_state} (₹{top_state_amt:,.2f})", styles["Normal"]))
    story.append(Spacer(1, 12))
else:
    story.append(Paragraph("■■ Aggregated Transaction data unavailable or missing columns.", styles["Normal"]))

# ===== MAP TRANSACTION INSIGHTS =====
if map_trans is not None and all(col in map_trans.columns for col in ['District', 'Transaction_count', 'Transaction_amount']):
    story.append(Paragraph("<b>2️⃣ Map Transaction Insights</b>", styles["Heading2"]))

    total_txn = map_trans["Transaction_count"].sum()
    total_amt = map_trans["Transaction_amount"].sum()
    avg_value = total_amt / total_txn if total_txn > 0 else 0

    top_district = map_trans.groupby("District")["Transaction_amount"].sum().idxmax()
    top_district_amt = map_trans.groupby("District")["Transaction_amount"].sum().max()

    story.append(Paragraph(f"• Total Transaction Value: ₹{total_amt:,.2f}", styles["Normal"]))
    story.append(Paragraph(f"• Total Transaction Count: {int(total_txn):,}", styles["Normal"]))
    story.append(Paragraph(f"• Average Transaction Value: ₹{avg_value:,.2f}", styles["Normal"]))
    story.append(Paragraph(f"• Top Performing District: {top_district} (₹{top_district_amt:,.2f})", styles["Normal"]))
    story.append(Spacer(1, 12))
else:
    story.append(Paragraph("■■ Map Transaction data unavailable or missing columns.", styles["Normal"]))


# ===== TOP TRANSACTION INSIGHTS =====
if top_trans is not None and all(col in top_trans.columns for col in ['State', 'Transaction_count', 'Transaction_amount']):
    story.append(Paragraph("<b>3️⃣ Top Transaction Insights</b>", styles["Heading2"]))
    top_10_states = top_trans.groupby("State")["Transaction_amount"].sum().nlargest(10).reset_index()
    story.append(Paragraph("• Top 10 States by Transaction Volume", styles["Normal"]))
    table_data = [["State", "Transaction Amount (₹)"]] + [[row["State"], f"{row['Transaction_amount']:,.2f}"] for _, row in top_10_states.iterrows()]
    table = Table(table_data, colWidths=[200, 200])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(table)
    story.append(Spacer(1, 20))
else:
    story.append(Paragraph("■■ Top Transaction data unavailable or missing columns.", styles["Normal"]))

# ===== AGGREGATED USER INSIGHTS =====
if agg_user is not None and all(col in agg_user.columns for col in ['Brand', 'Transaction_count']):
    story.append(Paragraph("<b>4️⃣ Aggregated User Insights</b>", styles["Heading2"]))
    popular_brand = agg_user.groupby("Brand")["Transaction_count"].sum().idxmax()
    brand_total = agg_user.groupby("Brand")["Transaction_count"].sum().max()
    story.append(Paragraph(f"• Most Popular Smartphone Brand: {popular_brand} ({brand_total:,.0f} transactions)", styles["Normal"]))
    story.append(Spacer(1, 12))
else:
    story.append(Paragraph("■■ Aggregated User data unavailable or missing columns.", styles["Normal"]))

# ===== TOP USER INSIGHTS =====
if top_user is not None and all(col in top_user.columns for col in ['State', 'Registered_users']):
    story.append(Paragraph("<b>5️⃣ Top User Insights</b>", styles["Heading2"]))
    top_states = top_user.groupby("State")["Registered_users"].sum().nlargest(5)
    story.append(Paragraph("• Top 5 States by Registered Users:", styles["Normal"]))
    for state, users in top_states.items():
        story.append(Paragraph(f"- {state}: {users:,.0f} users", styles["Normal"]))
    story.append(Spacer(1, 12))
else:
    story.append(Paragraph("■■ Top User data unavailable or missing columns.", styles["Normal"]))

# ===== FOOTER =====
story.append(Spacer(1, 30))
story.append(Paragraph("<b>Report Generated Automatically Using Streamlit + Python</b>", styles["Italic"]))

# ===== BUILD PDF =====
doc.build(story)
print(f"✅ Insights report generated successfully: {REPORT_PATH}")
