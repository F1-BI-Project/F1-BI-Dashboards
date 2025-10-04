# Before running this code, make sure that this python file is in the same folder as the 'components_example_data.txt' file.
# Also make sure you have the required python extensions installed: 'pandas', 'streamlit', 'matplotlib', 'numpy', and 'plotly'

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go

fl = open("components_example_data.txt", 'r', encoding= 'utf-16')
header_line = fl.readline()
columns = header_line.strip().split(",")
data = dict()

component_id = list()
component_type = list()
cycles_used = list()
expected_life_cycles = list()
replacement_cost_EUR = list()
cumulative_cost_EUR = list()
reliability_score_0_1 = list()
proj_fail_prob_next_race = list()

data[columns[0]] = component_id
data[columns[1]] = component_type
data[columns[2]] = cycles_used
data[columns[3]] = expected_life_cycles
data[columns[4]] = replacement_cost_EUR
data[columns[5]] = cumulative_cost_EUR
data[columns[6]] = reliability_score_0_1
data[columns[7]] = proj_fail_prob_next_race

j = 0
for line in fl:
    splitted = line.split(',')
    cpy = splitted.copy()
    #cpy.pop(0)
    for i in range(0,8):
        data[columns[i]].append(splitted[i])
    j = j + 1
#print(data)

data[columns[7]] = [x.strip() for x in proj_fail_prob_next_race]
print(data)

#Dashboard code <-----
df = pd.DataFrame(data)

col1, col2, col3 = st.columns(3)
col1.metric("Highest Failure Risk", f"{df['proj_fail_prob_next_race'].astype(float).max()}%")
col2.metric("Most Expensive Component", f"{df['replacement_cost_EUR'].astype(int).max()} EUR")
col3.metric("Average Reliability", f"{df['reliability_score_0_1'].astype(float).mean():.2f}")

st.subheader("Component Wear vs Failure Probability")

fig, ax = plt.subplots()

# Assign color per component type
component_types = df["component_type"].unique()
colors = plt.cm.tab10(range(len(component_types)))  # up to 10 clear colors
color_map = dict(zip(component_types, colors))

for ctype in component_types:
    subset = df[df["component_type"] == ctype]
    ax.scatter(
        subset["cycles_used"].astype(int),
        subset["proj_fail_prob_next_race"].astype(float),
        label=ctype,
        color=color_map[ctype],
        alpha=0.7
    )

ax.set_xlabel("Cycles Used")
ax.set_ylabel("Failure Probability (%)")
ax.legend(title="Component Type", fontsize=8, title_fontsize=9, loc='best', markerscale=0.7, frameon=True)
st.pyplot(fig)


st.subheader("Failure Probability by Component")
df_sorted = df.sort_values("proj_fail_prob_next_race", ascending=False)
st.bar_chart(df_sorted.set_index("component_id")["proj_fail_prob_next_race"].astype(float))

st.subheader("Reliability Score (Percentage) per Component")
# Pull reliability scores and component names from your dataframe
scores = df["reliability_score_0_1"].astype(float).tolist()
names = df["component_type"].tolist()

# Number of gauges per row
gauges_per_row = 5

for row_start in range(0, len(scores), gauges_per_row):
    cols = st.columns(gauges_per_row)
    for i, col in enumerate(cols):
        idx = row_start + i
        if idx < len(scores):
            with col:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=scores[idx]*100,
                    title={"text": f"{names[idx]}"},
                    gauge={
                        'axis': {'range': [0,100]},
                        'bar': {'color': "green" if scores[idx] > 0.7 else "orange" if scores[idx] > 0.4 else "red"}
                    }
                ))
                st.plotly_chart(fig, use_container_width=True)
                

#####
st.markdown("### Predict failure probability and expected cost: Replace Now vs. Replace Later")

# Interactive slider to simulate future laps
laps_ahead = st.slider("Number of laps to simulate", 1, 30, 5)


# Calculations
replace_now_cost = df["replacement_cost_EUR"]
replace_now_risk = 0  # If replaced now, no failure

# Convert numeric columns to float
numeric_cols = ["cycles_used", "expected_life_cycles", "replacement_cost_EUR", "reliability_score_0_1", "proj_fail_prob_next_race"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')  # converts strings to floats

# Now you can safely calculate
replace_later_prob = df["proj_fail_prob_next_race"] * ((df["cycles_used"] + laps_ahead) / df["expected_life_cycles"])
replace_later_prob = replace_later_prob.clip(0,1)

# Estimated failure probability if replaced later
replace_later_prob = df["proj_fail_prob_next_race"] * ((df["cycles_used"] + laps_ahead) / df["expected_life_cycles"])
replace_later_prob = replace_later_prob.clip(0,1)  # ensure probability is 0-1

# Expected cost if replaced later
replace_later_cost = df["replacement_cost_EUR"] * replace_later_prob

# Add to dataframe
df["Replace_Now_Cost"] = replace_now_cost
df["Replace_Later_Cost"] = replace_later_cost
df["Replace_Later_Prob"] = replace_later_prob


# Display tables
#st.markdown("#### Component Comparison Table")
#st.dataframe(df[["component_id", "component_type", "cycles_used", "expected_life_cycles",
#                 "Replace_Now_Cost", "Replace_Later_Cost", "Replace_Later_Prob"]])


# Metrics / Gauges for highest risk
highest_risk_idx = df["Replace_Later_Prob"].idxmax()
st.markdown("#### Highest-Risk Component if Replaced Later")
st.metric(label=f"{df.loc[highest_risk_idx, 'component_id']} ({df.loc[highest_risk_idx, 'component_type']})",
          value=f"{df.loc[highest_risk_idx, 'Replace_Later_Prob']:.2f}",
          delta=f"Expected Cost: €{df.loc[highest_risk_idx, 'Replace_Later_Cost']:.2f}")


# Bar chart comparison
st.markdown("#### Replace Now vs Replace Later Cost")

st.bar_chart(df.set_index("component_id")[["Replace_Now_Cost", "Replace_Later_Cost"]])
