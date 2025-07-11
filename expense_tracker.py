import pip

#pip.main(['install', 'streamlit'])
pip.main(['install', 'gspread', 'oauth2client', 'pandas'])
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["google_service_account"], scope
)

client = gspread.authorize(creds)
# Replace with your actual sheet name (visible in Google Sheets)
sheet = client.open("Saara Hisaab").sheet1
# ---------- STREAMLIT UI ----------
st.title("💸 Group Expense Splitter")
payer = st.selectbox("Who paid?", ["Venkatesh", "Arkoo", "Tanmay", "Pal"])
amount = st.number_input("Total Amount", min_value=0.01, step=0.01)
description = st.text_input("Description of Expense")
date = st.date_input("Date", value=datetime.today().date())
if st.button("Submit Expense"):
    split_amount = round(amount / 4, 2)

    # Prepare row with correct column order
    row = [
        date.strftime("%Y-%m-%d"),   # Date
        payer,                       # Payer
        description,                 # Description
        float(amount),               # Amount Paid
        split_amount, split_amount, split_amount, split_amount  # Split among 4
    ]

    # Append to the Google Sheet
    sheet.append_row(row)

    st.success("✅ Expense recorded and split successfully!")
import pandas as pd
# Fetch all sheet data
data = sheet.get_all_records()
df = pd.DataFrame(data)

if not df.empty:
    # Total paid by each person
    total_paid = df.groupby("Payer")["Amount Paid"].sum()

    # Total owed (split amount per person)
    people = ["Venkatesh", "Arkoo", "Tanmay", "Pal"]
    total_owed = df[people].sum()

    # Combine into a summary table
    summary_df = pd.DataFrame({
        "Paid": total_paid,
        "Owed": total_owed
    }).fillna(0)

    summary_df["Balance (Paid - Owed)"] = summary_df["Paid"] - summary_df["Owed"]

    st.subheader("💡 Summary of Balances")
    st.dataframe(summary_df.style.format("₹{:.2f}"))
else:
    st.info("No expenses recorded yet.")
