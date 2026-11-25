
import streamlit as st
import pandas as pd
import plotly.express as px
from pyhive import hive
from datetime import datetime

st.set_page_config(
    page_title="HR Analytics Lakehouse",
    page_icon="📊",
    layout="wide"
)

# ==========================================
# 1. HIVE CONNECTION
# ==========================================

@st.cache_data(ttl=60, show_spinner=False)
def load_gold_data():

    conn = hive.Connection(
        host="localhost",
        port=10000,
        username="hive",
        database="hr_gold",
        auth="NONE"
    )

    cursor = conn.cursor()

    def query(sql):
        cursor.execute(sql)

        columns = [
            col[0].split(".")[-1]
            for col in cursor.description
        ]

        return pd.DataFrame(
            cursor.fetchall(),
            columns=columns
        )

    try:
        headcount = query("""
            SELECT department_name, headcount, location
            FROM headcount_by_department
            ORDER BY department_name
        """)

        salaries = query("""
            SELECT department_name, avg_salary
            FROM salary_by_department
            ORDER BY department_name
        """)

        attendance = query("""
            SELECT status, records
            FROM attendance_by_status
        """)

        leave = query("""
            SELECT leave_type, approval_status, requests
            FROM leave_summary
        """)

        hiring = query("""
            SELECT month, hires
            FROM hiring_trends
            ORDER BY month
        """)

        return (
            headcount,
            salaries,
            attendance,
            leave,
            hiring,
            datetime.now()
        )

    finally:
        cursor.close()
        conn.close()


# ==========================================
# 2. DASHBOARD HEADER
# ==========================================

st.title("HR Analytics Lakehouse")

st.caption(
    "Interactive HR dashboard | "
    "Connected to HiveServer2"
)

st.sidebar.header("Data Source")

if st.sidebar.button("Refresh Gold Data"):
    load_gold_data.clear()
    st.rerun()

try:
    with st.spinner("Retrieving Gold datasets from Hive..."):
        (
            headcount,
            salaries,
            attendance,
            leave,
            hiring,
            last_refresh
        ) = load_gold_data()

    st.sidebar.success("Connected to Hive")

    st.sidebar.caption(
        "Last retrieval: "
        + last_refresh.strftime("%Y-%m-%d %H:%M:%S")
    )

except Exception as e:
    st.error("Unable to retrieve data from Hive.")
    st.code(str(e))
    st.stop()


# ==========================================
# 3. RENAME COLUMNS
# ==========================================

headcount = headcount.rename(columns={
    "department_name": "Department",
    "headcount": "Employees",
    "location": "Location"
})

salaries = salaries.rename(columns={
    "department_name": "Department",
    "avg_salary": "Average Salary"
})

attendance = attendance.rename(columns={
    "status": "Status",
    "records": "Records"
})

leave = leave.rename(columns={
    "leave_type": "Leave Type",
    "approval_status": "Approval Status",
    "requests": "Requests"
})

hiring = hiring.rename(columns={
    "month": "Month",
    "hires": "Hires"
})

hiring["Month"] = pd.to_datetime(
    hiring["Month"],
    format="%Y-%m"
)

hiring = hiring.sort_values("Month")


# ==========================================
# 4. INTERACTIVE FILTERS
# ==========================================

st.sidebar.header("Filters")

available_departments = sorted(
    headcount["Department"].unique().tolist()
)

departments = st.sidebar.multiselect(
    "Select departments",
    available_departments,
    default=available_departments
)

filtered_headcount = headcount[
    headcount["Department"].isin(departments)
]

filtered_salaries = salaries[
    salaries["Department"].isin(departments)
]

st.sidebar.info(
    "Department filters apply to headcount "
    "and salary indicators. Attendance, leave "
    "and hiring indicators are company-wide."
)


# ==========================================
# 5. DYNAMIC KPI CALCULATIONS
# ==========================================

total_employees = filtered_headcount["Employees"].sum()

total_departments = filtered_headcount[
    "Department"
].nunique()

total_attendance = attendance["Records"].sum()

present_records = attendance.loc[
    attendance["Status"].str.lower() == "present",
    "Records"
].sum()

attendance_rate = (
    present_records / total_attendance * 100
    if total_attendance > 0
    else 0
)

approved_leave = leave.loc[
    leave["Approval Status"].str.lower() == "approved",
    "Requests"
].sum()


# ==========================================
# 6. KPI CARDS
# ==========================================

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Active Employees",
    f"{total_employees:,}"
)

c2.metric(
    "Attendance Rate (Global)",
    f"{attendance_rate:.2f}%"
)

c3.metric(
    "Departments",
    total_departments
)

c4.metric(
    "Approved Leave (Global)",
    f"{approved_leave:,}"
)

st.divider()


# ==========================================
# 7. WORKFORCE AND SALARY ANALYSIS
# ==========================================

left, right = st.columns(2)

with left:

    st.subheader("Headcount by Department")

    fig = px.bar(
        filtered_headcount,
        x="Department",
        y="Employees",
        color="Department",
        text="Employees"
    )

    fig.update_layout(showlegend=False)

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with right:

    st.subheader("Average Salary by Department")

    fig = px.bar(
        filtered_salaries,
        x="Department",
        y="Average Salary",
        color="Department",
        text_auto=".0f"
    )

    fig.update_layout(showlegend=False)

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()


# ==========================================
# 8. ATTENDANCE AND LEAVE ANALYSIS
# ==========================================

left, right = st.columns(2)

with left:

    st.subheader("Attendance Distribution")

    fig = px.pie(
        attendance,
        names="Status",
        values="Records",
        hole=0.5,
        color="Status",
        color_discrete_map={
            "Present": "#69B99D",
            "Absent": "#E89595"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with right:

    st.subheader("Leave Requests")

    fig = px.bar(
        leave,
        x="Leave Type",
        y="Requests",
        color="Approval Status",
        text="Requests",
        barmode="group"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()


# ==========================================
# 9. HIRING TRENDS
# ==========================================

st.subheader("Hiring Trends Over Time")

fig = px.line(
    hiring,
    x="Month",
    y="Hires",
    markers=True
)

fig.update_traces(
    line=dict(width=3, color="#829CC7")
)

fig.update_layout(
    xaxis_title="Hiring Month",
    yaxis_title="Number of Hires",
    hovermode="x unified"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()


# ==========================================
# 10. GOLD DATA EXPLORER
# ==========================================

st.subheader("Gold Data Explorer")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Headcount",
    "Salaries",
    "Attendance",
    "Leave Requests",
    "Hiring Trends"
])

with tab1:
    st.dataframe(
        filtered_headcount,
        use_container_width=True,
        hide_index=True
    )

with tab2:
    st.dataframe(
        filtered_salaries,
        use_container_width=True,
        hide_index=True
    )

with tab3:
    st.dataframe(
        attendance,
        use_container_width=True,
        hide_index=True
    )

with tab4:
    st.dataframe(
        leave,
        use_container_width=True,
        hide_index=True
    )

with tab5:
    st.dataframe(
        hiring,
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# 11. DATA SOURCE INFORMATION
# ==========================================

st.divider()

st.caption(
    "Data source: HiveServer2 | Database: hr_gold | "
    "Storage: HDFS Parquet | Processing: Apache Spark"
)

st.caption(
    "All indicators are retrieved from Gold datasets. "
    "No business values are hardcoded."
)
