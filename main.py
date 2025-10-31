
import streamlit as st
import json
import plotly.express as px
import config
from streamlit_option_menu import option_menu
import mysql.connector as con
import pandas as pd
from config import get_connection

def fetch_data(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

st.set_page_config(page_title="PhonePe Pulse Dashboard", layout="wide")

st.title("📊 PhonePe Pulse Data Dashboard")

with st.sidebar:
    select = option_menu("Main Menu",["HOME","DATA EXPLORATION","TOP CHARTS"])
if select == "HOME":
    st.header("📂 Download Cleaned Datasets & Insights Report")

    st.write("Below are all the cleaned datasets used in this dashboard. You can download them for your own analysis.")

    import os

    folder_path = "clean_data"

    # Dynamically list all CSV files in the clean_data folder
    csv_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]

    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        with open(file_path, "rb") as f:
            st.download_button(
                label=f"⬇️ Download {file}",
                data=f,
                file_name=file,
                mime="text/csv"
            )

    st.divider()
    st.subheader("📘 Insights Report")

    report_path = "insights3_report.pdf"
    if os.path.exists(report_path):
        with open(report_path, "rb") as pdf:
            st.download_button(
                label="📥 Download Insights Report (PDF)",
                data=pdf,
                file_name="PhonePe_Insights_Report.pdf",
                mime="application/pdf"
            )
    else:
        st.warning("Insights report not found! Please ensure `insights_report.pdf` is in your project folder.")

elif select =="DATA EXPLORATION":
    tab1,tab2,tab3=st.tabs(["Aggregated Analysis","Map Analysis","Top Analysis"])
    with tab1:
        method=st.radio("Select The Method ",["Insurance Analysis","Transaction Analysis","User Analysis"])
        if method == "Insurance Analysis":
            st.subheader("📈 Aggregated Insurance Analysis")

# Fetch data from database
            query = """
SELECT State, Year, Quarter, SUM(Transaction_Count) AS Total_Policies, SUM(Transaction_Amount) AS Total_Amount
FROM aggregateinsurance
GROUP BY State, Year, Quarter;
"""
            df = fetch_data(query)

# Dropdown filters
            year = st.selectbox("Select Year", sorted(df["Year"].unique()))
            quarter = st.selectbox("Select Quarter", sorted(df["Quarter"].unique()))

# Filtered Data
            filtered_df = df[(df["Year"] == year) & (df["Quarter"] == quarter)]

# ----------------------
# 📊 1️⃣ State-wise Total Insurance Amount
# ----------------------
            st.markdown("### 💰 Total Insurance Amount across States")
            fig1 = px.bar(
            filtered_df.sort_values(by="Total_Amount", ascending=False),
            x="State",
            y="Total_Amount",
            color="Total_Amount",
            color_continuous_scale="Blues",
            title=f"Total Insurance Amount by State ({year} Q{quarter})"
)
            st.plotly_chart(fig1, use_container_width=True)

# ----------------------
# 📊 2️⃣ State-wise Total Insurance Policies
# ----------------------
            st.markdown("### 🧾 Total Insurance Policies across States")
            fig2 = px.bar(
            filtered_df.sort_values(by="Total_Policies", ascending=False),
            x="State",
            y="Total_Policies",
            color="Total_Policies",
            color_continuous_scale="Viridis",
            title=f"Total Insurance Policies by State ({year} Q{quarter})"
)
            st.plotly_chart(fig2, use_container_width=True)

# ----------------------
# 📊 3️⃣ Yearly Trend (Total Amount)
# ----------------------
            st.markdown("### 📅 Yearly Insurance Amount Trend")
            yearly_df = df.groupby("Year")[["Total_Amount"]].sum().reset_index()

            fig3 = px.line(
            yearly_df,
            x="Year",
            y="Total_Amount",
            markers=True,
            title="Yearly Growth of Insurance Amount"
)
            st.plotly_chart(fig3, use_container_width=True)

# ----------------------
# 📊 4️⃣ Quarterly Trend (for Selected Year)
# ----------------------
            st.markdown(f"### 📆 Quarterly Insurance Amount Trend ({year})")
            quarterly_df = df[df["Year"] == year].groupby("Quarter")[["Total_Amount"]].sum().reset_index()

            fig4 = px.bar(
            quarterly_df,
            x="Quarter",
            y="Total_Amount",
            text_auto=".2s",
            color="Total_Amount",
            color_continuous_scale="Magma",
            title=f"Quarterly Insurance Amount Distribution in {year}"
)
            st.plotly_chart(fig4, use_container_width=True)






            
        elif method =="Transaction Analysis":
            st.subheader("📈 Aggregated Transaction Analysis")
            query = "SELECT * FROM aggregatedtransaction;"
            df = fetch_data(query)
            state_select = st.selectbox("Select State", df['State'].unique(),key="agg_trans")
            year_select = st.selectbox("Select Year", sorted(df['Year'].unique()),key="agg_trans_year")
            filtered = df[(df['State'] == state_select) & (df['Year'] == year_select)]
            fig = px.bar(filtered, x='Quarter', y='Transaction_Amount', color='Transaction_Type',
                title=f"{state_select} - {year_select} Transaction Analysis",
                template='plotly_dark')
            st.plotly_chart(fig, use_container_width=True)

            #adding two more figures
            query = """
SELECT State, Year, Quarter, Transaction_Type,
       SUM(Transaction_Count) AS Total_Transactions,
       SUM(Transaction_Amount) AS Transaction_Amount
FROM aggregatedtransaction
GROUP BY State, Year, Quarter, Transaction_Type;
"""
            year = st.selectbox("Select Year", sorted(df["Year"].unique()), key="agg_trans_year_2")
            quarter = st.selectbox("Select Quarter", sorted(df["Quarter"].unique()), key="agg_trans_quarter_2")

            filtered_df = df[(df["Year"] == year) & (df["Quarter"] == quarter)]

# --------------------------
# 1️⃣ State-wise Transaction Amount
# --------------------------
            st.markdown("### 💰 Transaction Amount across States")
            fig1 = px.bar(
            filtered_df.sort_values(by="Transaction_Amount", ascending=False),
    x="State",
    y="Transaction_Amount",
    color="Transaction_Amount",
    color_continuous_scale="Blues",
    title=f"Total Transaction Amount by State ({year} Q{quarter})"
)
            st.plotly_chart(fig1, use_container_width=True)
            #total trans count
            st.markdown("### 🧾 Transaction Count across States")
            fig2 = px.bar(
            filtered_df.sort_values(by="Transaction_Count", ascending=False),
    x="State",
    y="Transaction_Count",
    color="Transaction_Count",
    color_continuous_scale="Viridis",
    title=f"Total Transactions by State ({year} Q{quarter})"
)
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("### 📅 Yearly Transaction Amount Trend")
            yearly_df = df.groupby("Year")[["Transaction_Amount"]].sum().reset_index()

            fig3 = px.line(
    yearly_df,
    x="Year",
    y="Transaction_Amount",
    markers=True,
    title="Yearly Growth of Transaction Amount"
)
            st.plotly_chart(fig3, use_container_width=True)
            # 4️⃣ Quarterly Trend - Selected Year
# --------------------------
            st.markdown(f"### 📆 Quarterly Transaction Trend ({year})")
            quarterly_df = df[df["Year"] == year].groupby("Quarter")[["Transaction_Amount"]].sum().reset_index()

            fig4 = px.bar(
    quarterly_df,
    x="Quarter",
    y="Transaction_Amount",
    text_auto=".2s",
    color="Transaction_Amount",
    color_continuous_scale="Magma",
    title=f"Quarterly Transaction Amount Distribution in {year}"
)
            st.plotly_chart(fig4, use_container_width=True)



            
        elif method =="User Analysis":

            st.subheader("👤 Aggregated User Analysis")

    # --------------------------
    # 📦 Fetch Data
    # --------------------------
            query = """
    SELECT State, Year, Quarter, Brand, SUM(Transaction_count) AS Total_Transactions, 
           AVG(Percentage) AS Avg_Percentage
    FROM aggregateuser
    GROUP BY State, Year, Quarter, Brand;
    """
            df = fetch_data(query)

    # --------------------------
    # 🔹 Filters
    # --------------------------
            year = st.selectbox("Select Year", sorted(df["Year"].unique()), key="agg_user_year")
            quarter = st.selectbox("Select Quarter", sorted(df["Quarter"].unique()), key="agg_user_quarter")
            filtered_df = df[(df["Year"] == year) & (df["Quarter"] == quarter)]

    # --------------------------
    # 1️⃣ Brand-wise User Distribution
    # --------------------------
            st.markdown("### 📱 Brand-wise Distribution of Transactions")
            brand_df = (
            filtered_df.groupby("Brand")[["Total_Transactions"]]
        .sum()
        .reset_index()
        .sort_values(by="Total_Transactions", ascending=False)
    )

            fig1 = px.pie(
        brand_df,
        values="Total_Transactions",
        names="Brand",
        title=f"Brand-wise Transaction Share ({year} Q{quarter})",
        hole=0.5,
        color_discrete_sequence=px.colors.sequential.Viridis
    )
            st.plotly_chart(fig1, use_container_width=True)

    # --------------------------
    # 2️⃣ Top 10 States by Transaction Count
    # --------------------------
            st.markdown("### 🏆 Top 10 States by Transaction Count")
            state_df = (
            filtered_df.groupby("State")[["Total_Transactions"]]
        .sum()
        .reset_index()
        .sort_values(by="Total_Transactions", ascending=False)
        .head(10)
    )

            fig2 = px.bar(
        state_df,
        x="State",
        y="Total_Transactions",
        color="Total_Transactions",
        color_continuous_scale="Blues",
        text_auto=".2s",
        title=f"Top 10 States by Transactions ({year} Q{quarter})"
    )
            st.plotly_chart(fig2, use_container_width=True)

    # --------------------------
    # 3️⃣ Yearly Growth of User Transactions
    # --------------------------
            st.markdown("### 📈 Yearly Growth of Transactions")
            yearly_df = df.groupby("Year")[["Total_Transactions"]].sum().reset_index()

            fig3 = px.line(
            yearly_df,
            x="Year",
            y="Total_Transactions",
            markers=True,
            title="Yearly Growth of User Transactions"
    )
            st.plotly_chart(fig3, use_container_width=True)
           




            
    with tab2:
        method_2= st.radio("Select The Method",["Map Insurance","Map Transaction","Map User"])
        if method_2 =="Map Insurance":
            st.subheader("🗺️ Insurance Distribution Across States")

# Fetch aggregated insurance data
            query = "SELECT State, SUM(Transaction_Count) AS Total_Policies, SUM(Transaction_Amount) AS Total_Amount FROM mapinsurance GROUP BY State;"
            df = fetch_data(query)

# Load India GeoJSON file (from your local directory)
            with open("clean_data/india_states.geojson", "r") as f:
                india_states = json.load(f)

# Fix state name mismatches if any
            df['State'] = df['State'].replace({
    "Andaman & Nicobar Islands": "Andaman & Nicobar Island",
    "NCT of Delhi": "Delhi",
    "Jammu & Kashmir": "Jammu and Kashmir",
    "Orissa": "Odisha",
})

# Dropdown selector for user to choose what to visualize
            metric = st.radio("Select Metric", ["Total Policies", "Total Amount"], horizontal=True)

            if metric == "Total Policies":
                color_col = "Total_Policies"
                color_label = "Total Policies"
            else:
                color_col = "Total_Amount"
                color_label = "Total Amount (₹)"

# Create choropleth map
            fig = px.choropleth(
                df,
                geojson=india_states,
                featureidkey="properties.ST_NM",
                locations="State",
                color=color_col,
                color_continuous_scale="Viridis",
                title=f"Insurance {color_label} Distribution (State-wise)"
                )

# Focus map on India
            fig.update_geos(fitbounds="locations", visible=False)

# Beautify layout
            fig.update_layout(
                geo=dict(bgcolor="rgba(0,0,0,0)"),
                coloraxis_colorbar=dict(title=color_label),
                title_x=0.25
)

# Show map
            st.plotly_chart(fig, use_container_width=True)








            
        elif method_2 =="Map Transaction":
            st.subheader("🗺️ Transaction Distribution Across States")

# Fetch data from your SQL table
            query = "SELECT State, SUM(Transaction_Amount) AS Total_Amount FROM maptransaction GROUP BY State;"
            df = fetch_data(query)

# Load the India GeoJSON file from local directory
            with open("clean_data/india_states.geojson", "r") as f:
                india_states = json.load(f)

# 🧹 Optional: Standardize some common mismatched state names if necessary
            df['State'] = df['State'].replace({
    "Andaman & Nicobar Islands": "Andaman & Nicobar Island",
    "NCT of Delhi": "Delhi",
    "Jammu & Kashmir": "Jammu and Kashmir",
    "Orissa": "Odisha",
})

# 🎨 Create the choropleth map
            fig = px.choropleth(
                df,
                geojson=india_states,
                featureidkey="properties.ST_NM",  # must match the key in geojson
                locations="State",
                color="Total_Amount",
                color_continuous_scale="Viridis",
                title="Transaction Amount Distribution (State-wise)",
)

# 🗺️ Adjust layout to focus only on India
            fig.update_geos(fitbounds="locations", visible=False)

# 🪄 Optional: Beautify layout
            fig.update_layout(
    geo=dict(bgcolor="rgba(0,0,0,0)"),
    coloraxis_colorbar=dict(title="₹ Total Amount"),
    title_x=0.25
)

# Show map
            st.plotly_chart(fig, use_container_width=True)

            

            

          
        elif method_2=="Map User":
            df = pd.read_csv("clean_data/map_user_df.csv")

            st.write("### 🗺️ User Map Visualization")

    # Load GeoJSON of India states
            india_states = json.load(open("clean_data/india_states.geojson", "r"))

    # Check your CSV columns (example: State, Year, Registered_Users)
            st.dataframe(df.head())  # to verify column names once

    # Dropdowns to filter
            year = st.selectbox("Select Year", sorted(df["Year"].unique()),key="map_user_year")
            quarter = st.selectbox("Select Quarter", sorted(df["Quarter"].unique()),key="map_user_quarter")

    # Filter data
            df_year = df[(df["Year"] == year) & (df["Quarter"] == quarter)]

    # Choropleth map
            fig = px.choropleth(
                df,
                geojson=india_states,
                featureidkey="properties.ST_NM",
                locations="State",
                color="Registered_users",
                hover_name="State",
                color_continuous_scale="Viridis",
                title=f"Registered Users across States ({year} Q{quarter})"
                )

            fig.update_geos(
                fitbounds="locations",          # Fits map tightly around your state shapes
                visible=False,                  # Hides world outline
                projection_type="mercator",     # Accurate flat projection for India
                center={"lat": 22, "lon": 78},  # Centers over India
                lataxis_range=[6, 38],          # South to North bounds
                lonaxis_range=[68, 98],         # West to East bounds
                )
            fig.update_layout(
               title_text=f"Registered Users across States ({year} Q{quarter})",
               geo=dict(bgcolor='rgba(0,0,0,0)'),  # Transparent background
               margin={"r":0,"t":30,"l":0,"b":0},
            )
            st.plotly_chart(fig, use_container_width=True)
            

            
            
    with tab3:
        method_3= st.radio("Select The Method",["Top Insurance","Top Transaction","Top User"])
        if method_3 =="Top Insurance":
                st.subheader("💼 Top Insurance Analysis")

    # ---------------------------------
    # 📦 Fetch Data
    # ---------------------------------
                query = """
    SELECT State, Year, Quarter, District, 
           SUM(Transaction_count) AS Total_Transactions, 
           SUM(Transaction_amount) AS Total_Amount,
           Region
    FROM topinsurance
    GROUP BY State, Year, Quarter, District, Region;
    """
                df = fetch_data(query)

    # ---------------------------------
    # 🔹 Filters
    # ---------------------------------
                year = st.selectbox("Select Year", sorted(df["Year"].unique()), key="top_insurance_year")
                quarter = st.selectbox("Select Quarter", sorted(df["Quarter"].unique()), key="top_insurance_quarter")

                filtered_df = df[(df["Year"] == year) & (df["Quarter"] == quarter)]

    # ---------------------------------
    # 1️⃣ Top 10 States by Insurance Transaction Amount
    # ---------------------------------
                st.markdown("### 🏆 Top 10 States by Insurance Transaction Amount")

                top_states = (
        filtered_df.groupby("State")[["Total_Amount"]]
        .sum()
        .reset_index()
        .sort_values(by="Total_Amount", ascending=False)
        .head(10)
    )

                fig1 = px.bar(
        top_states,
        x="State",
        y="Total_Amount",
        color="Total_Amount",
        color_continuous_scale="Viridis",
        text_auto=".2s",
        title=f"Top 10 States by Insurance Transaction Amount ({year} Q{quarter})"
    )
                st.plotly_chart(fig1, use_container_width=True)

    # ---------------------------------
    # 2️⃣ Top 10 Districts by Insurance Transaction Count
    # ---------------------------------
                st.markdown("### 🏙️ Top 10 Districts by Insurance Transaction Count")

                top_districts = (
        filtered_df.groupby("District")[["Total_Transactions"]]
        .sum()
        .reset_index()
        .sort_values(by="Total_Transactions", ascending=False)
        .head(10)
    )

                fig2 = px.bar(
        top_districts,
        x="District",
        y="Total_Transactions",
        color="Total_Transactions",
        color_continuous_scale="Blues",
        text_auto=".2s",
        title=f"Top 10 Districts by Insurance Transaction Count ({year} Q{quarter})"
    )
                st.plotly_chart(fig2, use_container_width=True)

    # ---------------------------------
    # 3️⃣ Yearly Growth in Insurance Transactions
    # ---------------------------------
                st.markdown("### 📈 Yearly Growth of Insurance Transactions")

                yearly_trend = (
        df.groupby("Year")[["Total_Amount", "Total_Transactions"]]
        .sum()
        .reset_index()
    )

                fig3 = px.line(
        yearly_trend,
        x="Year",
        y="Total_Amount",
        markers=True,
        title="Yearly Growth of Insurance Transaction Amount"
    )
                st.plotly_chart(fig3, use_container_width=True)



















            
        elif method_3 =="Top Transaction":
                
                                
                st.subheader("💸 Top Transaction Analysis")

    # ---------------------------------
    # 📦 Fetch Data
    # ---------------------------------
                query = """
    SELECT State, Year, Quarter, District,
           SUM(Transaction_count) AS Total_Transactions,
           SUM(Transaction_amount) AS Total_Amount,
           Region
    FROM toptransaction
    GROUP BY State, Year, Quarter, District, Region;
    """
                df = fetch_data(query)

    # ---------------------------------
    # 🔹 Filters
    # ---------------------------------
                year = st.selectbox("Select Year", sorted(df["Year"].unique()), key="top_txn_year")
                quarter = st.selectbox("Select Quarter", sorted(df["Quarter"].unique()), key="top_txn_quarter")

                filtered_df = df[(df["Year"] == year) & (df["Quarter"] == quarter)]

    # ---------------------------------
    # 1️⃣ Top 10 States by Transaction Amount
    # ---------------------------------
                st.markdown("### 🏆 Top 10 States by Transaction Amount")

                top_states = (
        filtered_df.groupby("State")[["Total_Amount"]]
        .sum()
        .reset_index()
        .sort_values(by="Total_Amount", ascending=False)
        .head(10)
    )

                fig1 = px.bar(
        top_states,
        x="State",
        y="Total_Amount",
        color="Total_Amount",
        color_continuous_scale="Viridis",
        text_auto=".2s",
        title=f"Top 10 States by Transaction Amount ({year} Q{quarter})"
    )
                st.plotly_chart(fig1, use_container_width=True)

    # ---------------------------------
    # 2️⃣ Top 10 Districts by Transaction Count
    # ---------------------------------
                st.markdown("### 🏙️ Top 10 Districts by Transaction Count")

                top_districts = (
        filtered_df.groupby("District")[["Total_Transactions"]]
        .sum()
        .reset_index()
        .sort_values(by="Total_Transactions", ascending=False)
        .head(10)
    )

                fig2 = px.bar(
        top_districts,
        x="District",
        y="Total_Transactions",
        color="Total_Transactions",
        color_continuous_scale="Blues",
        text_auto=".2s",
        title=f"Top 10 Districts by Transaction Count ({year} Q{quarter})"
    )
                st.plotly_chart(fig2, use_container_width=True)

    # ---------------------------------
    # 3️⃣ Yearly Growth in Transaction Amount
    # ---------------------------------
                st.markdown("### 📈 Yearly Growth of Total Transactions")

                yearly_trend = (
        df.groupby("Year")[["Total_Amount", "Total_Transactions"]]
        .sum()
        .reset_index()
    )

                fig3 = px.line(
        yearly_trend,
        x="Year",
        y="Total_Amount",
        markers=True,
        title="Yearly Growth of Transaction Amount"
    )
                st.plotly_chart(fig3, use_container_width=True)









            
        elif method_3=="Top User":
            st.subheader("👥 Top User Analysis")

    # ---------------------------------
    # 📦 Fetch Data
    # ---------------------------------
            query = """
    SELECT State, Year, Quarter, District,
           SUM(Registered_users) AS Total_Users,
           Region
    FROM topuser
    GROUP BY State, Year, Quarter, District, Region;
    """
            df = fetch_data(query)

    # ---------------------------------
    # 🔹 Filters
    # ---------------------------------
            year = st.selectbox("Select Year", sorted(df["Year"].unique()), key="top_user_year")
            quarter = st.selectbox("Select Quarter", sorted(df["Quarter"].unique()), key="top_user_quarter")

            filtered_df = df[(df["Year"] == year) & (df["Quarter"] == quarter)]

    # ---------------------------------
    # 1️⃣ Top 10 States by Registered Users
    # ---------------------------------
            st.markdown("### 🏆 Top 10 States by Registered Users")

            top_states = (
        filtered_df.groupby("State")[["Total_Users"]]
        .sum()
        .reset_index()
        .sort_values(by="Total_Users", ascending=False)
        .head(10)
    )

            fig1 = px.bar(
        top_states,
        x="State",
        y="Total_Users",
        color="Total_Users",
        color_continuous_scale="Blues",
        text_auto=".2s",
        title=f"Top 10 States by Registered Users ({year} Q{quarter})"
    )
            st.plotly_chart(fig1, use_container_width=True)

    # ---------------------------------
    # 2️⃣ Top 10 Districts by Registered Users
    # ---------------------------------
            st.markdown("### 🏙️ Top 10 Districts by Registered Users")

            top_districts = (
        filtered_df.groupby("District")[["Total_Users"]]
        .sum()
        .reset_index()
        .sort_values(by="Total_Users", ascending=False)
        .head(10)
    )

            fig2 = px.bar(
        top_districts,
        x="District",
        y="Total_Users",
        color="Total_Users",
        color_continuous_scale="Viridis",
        text_auto=".2s",
        title=f"Top 10 Districts by Registered Users ({year} Q{quarter})"
    )
            st.plotly_chart(fig2, use_container_width=True)

    # ---------------------------------
    # 3️⃣ Yearly Growth in User Registration
    # ---------------------------------
            st.markdown("### 📈 Yearly Growth in User Registration")

            yearly_trend = (
        df.groupby("Year")[["Total_Users"]]
        .sum()
        .reset_index()
    )

            fig3 = px.line(
        yearly_trend,
        x="Year",
        y="Total_Users",
        markers=True,
        title="Yearly Growth in Registered Users"
    )
            st.plotly_chart(fig3, use_container_width=True)

            
            

elif select == "TOP CHARTS":
    st.title("🏆 Top Charts Dashboard")

    # 1️⃣ Top 10 States by Total Transaction Amount
    st.subheader("💰 Top 10 States by Total Transaction Amount")
    query1 = """
    SELECT State, SUM(Transaction_amount) AS Total_Amount
    FROM aggregatedtransaction
    GROUP BY State
    ORDER BY Total_Amount DESC
    LIMIT 10;
    """
    df1 = fetch_data(query1)

    fig1 = px.bar(
        df1,
        x="State",
        y="Total_Amount",
        color="Total_Amount",
        color_continuous_scale="Tealgrn",
        title="Top 10 States by Total Transaction Amount"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # 2️⃣ Top 10 States by Registered Users
    st.subheader("👥 Top 10 States by Registered Users")
    query2 = """
    SELECT State, SUM(Registered_users) AS Total_Users
    FROM topuser
    GROUP BY State
    ORDER BY Total_Users DESC
    LIMIT 10;
    """
    df2 = fetch_data(query2)

    fig2 = px.bar(
        df2,
        x="State",
        y="Total_Users",
        color="Total_Users",
        color_continuous_scale="Blues",
        title="Top 10 States by Registered Users"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # 3️⃣ Top 10 States by Insurance Transaction Amount
    st.subheader("🛡️ Top 10 States by Insurance Transaction Amount")
    query3 = """
    SELECT State, SUM(Transaction_amount) AS Total_Insurance_Amount
    FROM aggregateinsurance
    GROUP BY State
    ORDER BY Total_Insurance_Amount DESC
    LIMIT 10;
    """
    df3 = fetch_data(query3)

    fig3 = px.bar(
        df3,
        x="State",
        y="Total_Insurance_Amount",
        color="Total_Insurance_Amount",
        color_continuous_scale="Purples",
        title="Top 10 States by Insurance Transaction Amount"
    )
    st.plotly_chart(fig3, use_container_width=True)

    # 4️⃣ Yearly Transaction Growth Trend
    st.subheader("📈 Yearly Transaction Growth Trend")
    query4 = """
    SELECT Year, SUM(Transaction_amount) AS Total_Amount
    FROM aggregatedtransaction
    GROUP BY Year
    ORDER BY Year;
    """
    df4 = fetch_data(query4)

    fig4 = px.line(
        df4,
        x="Year",
        y="Total_Amount",
        markers=True,
        title="Yearly Growth in Total Transactions"
    )
    st.plotly_chart(fig4, use_container_width=True)


    


