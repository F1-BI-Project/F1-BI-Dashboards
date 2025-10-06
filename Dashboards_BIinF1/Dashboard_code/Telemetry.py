# Before running this code, make sure that this python file is in the same folder as the 'telemetry_30laps.txt' file.
# Also make sure you have the required python extensions installed: 'pandas', 'streamlit', 'matplotlib', 'numpy', and 'altair'

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import altair as alt
import io
import request


# Try to open the telemetry file
try:
    url = "https://raw.githubusercontent.com/F1-BI-Project/F1-BI-Dashboards/main/Dashboards_BIinF1/Data_samples/telemetry_30laps.txt"
    response = requests.get(url)
    response.raise_for_status()

    fl = io.StringIO(response.content.decode('utf-16'))

except Exception as e:
    st.warning("Unable to fetch data from GitHub. Please upload the telemetry file manually.")
    uploaded = st.file_uploader("Upload telemetry_30laps.txt", type=["txt"])
    if uploaded is not None:
        fl = io.StringIO(uploaded.getvalue().decode('utf-16'))
    else:
        st.stop()

#fl = open("https://raw.githubusercontent.com/F1-BI-Project/F1-BI-Dashboards/main/Dashboards_BIinF1/Data_samples/telemetry_30laps.txt", encoding='utf-16') #To run the code on your computer comment this line out
# and uncomment the line below 
#fl = open("telemetry_30laps.txt", 'r', encoding= 'utf-16') #uncomment this line
header_line = fl.readline()
#print(header_line)
#quit()
columns = header_line.split()
#print(columns)
data = dict()
data_per_lap = dict()
#quit()

lap_number = list()
timestamp = list()
speed_kph = list()
rpm = list()
throttle_pct = list()
brake_pct = list()
tire_temp_FL_C = list()
tire_temp_FR_C = list()
tire_temp_RL_C = list()
tire_temp_RR_C = list()
tire_wear_pct = list()
front_pressure_psi = list()
track_temp = list()
gap_car_ahead_s = list()
lap_time = list()
est_remaining_laps = list()

data[columns[0]] = lap_number
data[columns[1]] = timestamp
data[columns[2]] = speed_kph
data[columns[3]] = rpm
data[columns[4]] = throttle_pct
data[columns[5]] = brake_pct
data[columns[6]] = tire_temp_FL_C
data[columns[7]] = tire_temp_FR_C
data[columns[8]] = tire_temp_RL_C
data[columns[9]] = tire_temp_RR_C
data[columns[10]] = tire_wear_pct
data[columns[11]] = front_pressure_psi
data[columns[12]] = track_temp
data[columns[13]] = gap_car_ahead_s
data[columns[14]] = lap_time
data[columns[15]] = est_remaining_laps

#print(data)
j = 0
for line in fl:
    splitted = line.split()
    cpy = splitted.copy()
    cpy.pop(0)
    for i in range(0,16):
        data[columns[i]].append(splitted[i])
        #data_per_lap[i+1] = cpy.pop(0)
    data_per_lap[j+1] = cpy
    j = j + 1
#print(data_per_lap)

#checks if one of the 4 tyres has a temperature greater than "temperature" on lap "lap"
def check_tyre_temp(temperature, lap):
    if float(data["tire_temp_FL_C"][lap-1]) > temperature or float(data["tire_temp_FR_C"][lap-1]) > temperature or float(data["tire_temp_RL_C"][lap-1]) > temperature or float(data["tire_temp_RR_C"][lap-1]) > temperature:
        return True
    return False

def average_tyre_temp(dataInput, lap):
    res = (float(data["tire_temp_FL_C"][lap-1]) + float(data["tire_temp_FR_C"][lap-1]) + float(data["tire_temp_RL_C"][lap-1]) + float(data["tire_temp_RR_C"][lap-1])) / 4
    return res

#calculate the failure risk based on tire wear, tire temp, track temp, and lap time.
def calculate_failure_risk(dataInput, lap):
    risk = 0
    if float(dataInput["tire_wear_pct"][lap-1]) > 70:
        risk = risk + 0.2
    if check_tyre_temp(95, lap):
        risk = risk + 0.3 #105 as an overheating threshold
    if float(dataInput["track_temp_C"][lap -1]) > 35 and check_tyre_temp(105, lap):
        risk = risk + 0.2
    if float(dataInput["lap_time_s"][lap-1]) > 92.6:
        risk = risk + 0.1
    return min(risk, 1.0)

def average_lap_time(dataInput):
    avg = 0.0
    for i in range(1,31):
        avg = avg + float(dataInput["lap_time_s"][i-1])
    return (avg/float(len(data["lap"])))

risk_score_list = list()
avg_tyre_temp_list = list()
for i in data["lap"]:
    risk_score = calculate_failure_risk(data, int(i))
    risk_score_list.append(risk_score)
    avg_tyre_temp = average_tyre_temp(data, int(i))
    avg_tyre_temp_list.append(avg_tyre_temp)
#print(risk_score_list, avg_tyre_temp_list)

def avg_failure_risk(rlist):
    rmean = 0.0
    for i in range(1,31):
        rmean = rmean + float(rlist[i-1])
    return (rmean/float(len(rlist)))

#Dashboard Code <-----
df = pd.DataFrame(data)
df["risk_score"] = risk_score_list
df["lap"] = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
#print(df)
#quit()
#print(df)
#st.line_chart(df[["lap_time_s"]])
#st.line_chart(df[["tire_temp_FL_C", "tire_temp_FR_C", "tire_temp_RL_C", "tire_temp_RR_C"]])
#plt.figure()
#plt.plot(df["lap"], df["lap_time_s"], marker = 'x')
#plt.xlim(float(df["lap_time_s"].min()) - 0.1, float(df["lap_time_s"].max()) + 0.1)
#plt.ylim(int(df["lap"].min()) - 1, int(df["lap"].max()) + 1)
#plt.xticks(np.arange(float(df["lap_time_s"].min()) - 0.1, float(df["lap_time_s"].max()) + 0.1, 0.5))
#plt.xlabel("Lap")
#plt.ylabel("Lap Time (s)")
#st.pyplot(plt)
#print(float(df["lap_time_s"].min()), float(df["lap_time_s"].max()))
#df_sorted = df.sort_values("lap")
#df_index_lap = df_sorted.set_index("lap")
#st.line_chart(df_index_lap[["lap_time_s"]])

st.title("F1 Telemetry and BI Dashboard")

# Row 1: KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Current Lap", f"{df['lap'].max()}")
#col2.metric("Expected Lap Time", f"{float(df['lap_time_s'].iloc[-1]):.2f}s", delta= f"{float(df['lap_time_s'].iloc[-1]) - float(df['lap_time_s'].iloc[-2]):.2f}s") 
col2.metric(
    "Expected Lap Time",
    f"{float(df['lap_time_s'].iloc[-1]):.2f}s",
    delta=f"{(float(df['lap_time_s'].iloc[-2]) - float(df['lap_time_s'].iloc[-1])):.2f}s",
    delta_color="normal"
)

col3.metric("Failure Risk", f"{float(df['risk_score'].iloc[-1]*100):.1f}%") 


# Row 2: Lap Times + Failure Risk
st.subheader("Lap Performance and Failure Risk")
#col4, col5 = st.columns(2)
#with col4:
    #st.line_chart(df.set_index("lap")[["lap_time_s"]])  # Lap times
#with col5:
    #st.area_chart(df.set_index("lap")[["risk_score"]])  # Risk over time
chart_lap_time = alt.Chart(df).mark_line(point=True).encode(
    x=alt.X("lap", title="Lap Number"),
    y=alt.Y("lap_time_s", title="Lap Time (s)")
).properties(
    title="Lap Time per Lap"
)
st.altair_chart(chart_lap_time, use_container_width=True)
# Example: Risk score vs Lap
chart_risk = alt.Chart(df).mark_line(point=True).encode(
    x=alt.X("lap", title="Lap Number"),
    y=alt.Y("risk_score", title="Risk Score (0-1)"),
    tooltip=["lap", "risk_score"]  # show values on hover
).properties(
    title="Risk Score per Lap"
)
st.altair_chart(chart_risk, use_container_width=True)


# Row 3: Tire Temperatures
st.subheader("Tire Temperatures")
st.line_chart(df.set_index("lap")[["tire_temp_FL_C", "tire_temp_FR_C", "tire_temp_RL_C", "tire_temp_RR_C"]])

# Row 4: Component Wear (Bar Chart)
st.subheader("Component Wear")
component_data = {
    "Component": ["Engine", "Gearbox", "Brakes", "ERS"],
    "Remaining Life (%)": [72, 85, 65, 90]   # Example values
}
comp_df = pd.DataFrame(component_data)

st.bar_chart(comp_df.set_index("Component"))


# Row 5: Correlation (Lap Time vs Tire Temp)
st.subheader("Correlation: Lap Time vs Average Tire Temp")
#df["avg_tire_temp"] = df[["tire_temp_FL_C","tire_temp_FR_C","tire_temp_RL_C","tire_temp_RR_C"]].mean(axis=1)
df["avg_tire_temp"] = 0
for i in range(len(df)):
    #df['avg_tire_temp'].append(average_tyre_temp(data, i))
    df.at[i, 'avg_tire_temp'] = average_tyre_temp(data, i)

fig, ax = plt.subplots()
ax.scatter(df["avg_tire_temp"], df["lap_time_s"])
ax.set_xlabel("Average Tire Temp (°C)")
ax.set_ylabel("Lap Time (s)")
st.pyplot(fig)


# Row 6: Summary Table
st.subheader("Summary Statistics")
summary = {
    "Avg Lap Time": average_lap_time(data),
    "Fastest Lap": df["lap_time_s"].min(),
    "Slowest Lap": df["lap_time_s"].max(),
    "Average Failure Risk": avg_failure_risk(risk_score_list)
}
st.table(pd.DataFrame(summary, index=["Values"]))
# Example thresholds (you can refine with your data)
latest_lap = float(df['lap_time_s'].iloc[-2])
prev_lap = float(df['lap_time_s'].iloc[-3])
avg_tire_temp = float(average_tyre_temp(data, 29))
# Calculate degradation trend
lap_delta = latest_lap - prev_lap
# Decision logic
if lap_delta > 0.5 and avg_tire_temp > 95:
    est_gain = 1.2 * (10 - df['lap'].iloc[-2])  # e.g., assume 1.5s gain per lap left
    st.success(f"⚠️ Pit Now -> Estimated gain of {est_gain:.1f}s in final race time")
    st.warning("Stay out -> Estimated loss of 0.4s per lap")
elif lap_delta > 0.2:
    st.warning("⏳ Consider pitting soon -> lap times are degrading.")
else:
    st.success("✅ Stay Out -> Pace is stable and tire temps are under control.")






