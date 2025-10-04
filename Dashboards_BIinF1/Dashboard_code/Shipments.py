import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


fl = open("shipments_example_data.txt", 'r', encoding= 'utf-16')
header_line = fl.readline()
columns = header_line.strip().split(",")
data = dict()

shipment_id = list()
origin = list()
destination = list()
departure_date = list()
ETA_date = list()
current_status = list()
delay_hours = list()
item_type = list()
quantity = list()
carrier = list()
customs_clearance = list()
transport_cost_EUR = list()

data[columns[0]] = shipment_id
data[columns[1]] = origin
data[columns[2]] = destination
data[columns[3]] = departure_date
data[columns[4]] = ETA_date
data[columns[5]] = current_status
data[columns[6]] = delay_hours
data[columns[7]] = item_type
data[columns[8]] = quantity
data[columns[9]] = carrier
data[columns[10]] = customs_clearance
data[columns[11]] = transport_cost_EUR

j = 0
for line in fl:
    splitted = line.split(',')
    cpy = splitted.copy()
    for i in range(0,12):
        data[columns[i]].append(splitted[i])
    j = j + 1
#print(data)

data[columns[11]] = [x.strip() for x in transport_cost_EUR]
print(data)

#Dashboard Code <-----
df = pd.DataFrame(data)
#print(df)

#1
st.subheader("Shipment Overview")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Shipments", len(df))
col2.metric("Average Delay (hrs)", round(df["delay_hours"].astype(float).mean(),2))
col3.metric("Max Transport Cost (€)", round(df["transport_cost_EUR"].astype(float).max(),2))
df["delay_hours"] = df["delay_hours"].astype(float)
most_delayed_carrier = df.groupby("carrier")["delay_hours"].mean().idxmax()
col4.metric("Carrier with Most Delay", most_delayed_carrier)

#2
st.subheader("Delay Distribution")
# Convert to float just in case
df["delay_hours"] = df["delay_hours"].astype(float)
fig = px.histogram(
    df, 
    x="delay_hours", 
    nbins=10, # number of bins
    color="current_status", # color by shipment status
    hover_data=["shipment_id", "carrier", "origin", "destination"], 
    title="Delay Distribution by Shipment Status"
)
fig.update_layout(
    xaxis_title="Delay (hours)",
    yaxis_title="Number of Shipments",
    bargap=0.2
)
st.plotly_chart(fig)

#3
st.subheader("Transport Cost vs Delay")
fig, ax = plt.subplots()
# Loop through each carrier
for carrier_name, group in df.groupby("carrier"):
    ax.scatter(
        group["delay_hours"].astype(float),
        group["transport_cost_EUR"].astype(float),
        label=carrier_name,
        alpha=0.7
    )
ax.set_xlabel("Delay (hours)")
ax.set_ylabel("Transport Cost (€)")
ax.legend(title="Carrier")
st.pyplot(fig)

#4
st.subheader("Shipment Status Overview")
status_counts = df["current_status"].value_counts()
fig = go.Figure(go.Pie(
    labels=status_counts.index,
    values=status_counts.values,
    hole=0.3
))
st.plotly_chart(fig)

#5
st.subheader("Shipment Details")
st.dataframe(df[["shipment_id", "origin", "destination", "carrier", "delay_hours", "transport_cost_EUR", "current_status"]])

######
# Make sure numeric columns are actually numeric
df["delay_hours"] = pd.to_numeric(df["delay_hours"], errors="coerce")
df["transport_cost_EUR"] = pd.to_numeric(df["transport_cost_EUR"], errors="coerce")

st.header("Shipments Decision Support Panel")

col1, col2, col3 = st.columns(3)
on_time = (df["delay_hours"] <= 0).mean() * 100
avg_delay = df["delay_hours"].mean()
most_reliable = df.groupby("carrier")["delay_hours"].mean().idxmin()

col1.metric("On-Time Deliveries", f"{on_time:.1f}%")
col2.metric("Average Delay (hrs)", f"{avg_delay:.1f}")
col3.metric("Best Carrier", most_reliable)

#Risk alerts
st.subheader("Shipments at Risk")
risk_threshold = st.slider("Select delay threshold (hrs):", 6, 48, 24)
at_risk = df[df["delay_hours"] > risk_threshold]

if not at_risk.empty:
    for _, row in at_risk.iterrows():
        st.error(
            f"Shipment {row['shipment_id']} ({row['item_type']}, {row['quantity']} units) "
            f"delayed {row['delay_hours']} hrs → Risk of missing ETA {row['ETA_date']}."
        )
else:
    st.success("No shipments currently above risk threshold ✅")

#Carrier recommendations
st.subheader("Carrier Recommendations")
carrier_perf = df.groupby("carrier").agg(
    avg_delay=("delay_hours", "mean"),
    avg_cost=("transport_cost_EUR", "mean"),
    count=("shipment_id", "count")
).reset_index()

st.write("### Carrier Performance Overview")
st.dataframe(carrier_perf)

# Suggest best/worst carriers
worst_carrier = carrier_perf.loc[carrier_perf["avg_delay"].idxmax()]
best_carrier = carrier_perf.loc[carrier_perf["avg_delay"].idxmin()]

st.warning(
    f"⚠️ Avoid using **{worst_carrier['carrier']}** "
    f"(avg delay {worst_carrier['avg_delay']:.1f} hrs, {worst_carrier['count']} shipments)."
)
st.success(
    f"✅ Recommended: **{best_carrier['carrier']}** "
    f"(avg delay {best_carrier['avg_delay']:.1f} hrs, {best_carrier['count']} shipments)."
)