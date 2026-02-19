import streamlit as st
import pandas as pd
import mysql.connector
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="Smart Factory", page_icon="🏭", layout="wide")
st.title("🏭 Real-Time IIoT Analytics")

# --- DATABASE CONNECTION ---
@st.cache_resource
def init_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Password123!",
        database="factory_io",
        auth_plugin="mysql_native_password"
    )

def get_data():
    try:
        conn = init_connection()
        if not conn.is_connected():
            conn.reconnect()
        
        # --- THE FIX: Force MySQL to refresh its snapshot of the data ---
        conn.commit() 
        
        # Use a dictionary cursor to bypass the Pandas SQLAlchemy warning
        cursor = conn.cursor(dictionary=True)
        query = "SELECT timestamp, cv, pv, motor_status FROM machine_log ORDER BY timestamp DESC LIMIT 60"
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert the raw dictionary rows into a Pandas DataFrame
        df = pd.DataFrame(rows)
        
        if not df.empty:
            # Reverse the dataframe so the chart flows left-to-right (oldest to newest)
            df = df.iloc[::-1].reset_index(drop=True)
            
        return df
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()

# --- FETCH DATA ---
df = get_data()

if not df.empty:
    # Get the absolute latest row for the top metrics
    latest = df.iloc[-1]
    cv = int(latest['cv'])
    pv = int(latest['pv'])
    motor = int(latest['motor_status'])
    
    status_text = "RUNNING" if motor == 1 else "STOPPED"
    status_color = "🔴" if motor == 0 else "🟢"

    # --- UI LAYOUT ---
    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Counter (CV)", cv)
    col2.metric("🎯 Target (PV)", pv)
    col3.markdown(f"### ⚙️ Status\n**{status_text}** {status_color}")

    # --- CHART ---
    st.markdown("### 📈 Live Production Trend 🔗")
    # Set timestamp as index so the line chart handles the X-axis automatically
    chart_data = df.set_index('timestamp')[['cv', 'pv']]
    st.line_chart(chart_data, color=["#00ff00", "#0000ff"])

    # --- RAW DATA TABLE ---
    with st.expander("🔍 View Raw Data Logs"):
        # Fixed the Streamlit deprecation warning here
        st.dataframe(df.sort_values(by='timestamp', ascending=False), width='stretch')
else:
    st.warning("⏳ Waiting for data from MySQL...")

# --- AUTO REFRESH ---
time.sleep(1)
st.rerun()
