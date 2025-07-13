import streamlit as st
import math

st.title("IV Insulin Infusion Calculator")

st.markdown("""
This tool helps calculate bolus dose and infusion rate for intravenous insulin administration.
**Note:** Use only within protocol boundaries. Do not make clinical decisions outside this.
""")

# Input fields
patient_id = st.text_input("Patient ID (for reference only)")
A = st.number_input("Initial Blood Glucose (A)", min_value=0.0, step=1.0, format="%g")
B = st.number_input("Present Blood Glucose (B)", min_value=0.0, step=1.0, format="%g")
C = st.number_input("Last Blood Glucose (C)", min_value=0.0, step=1.0, format="%g")
last_rate = st.number_input("Last Infusion Rate (units/hour)", step=0.1, format="%g")

# Output section
if A:
    bolus = round(A / 100) if A < 300 else round(A / 70)
    rate = round(A / 100, 1) if A < 300 else round(A / 70, 1)
    st.subheader("Initial Bolus and Rate")
    st.write(f"Bolus: {bolus} units")
    st.write(f"Initial Infusion Rate: {rate} units/hour")

elif B and C and last_rate is not None:
    delta = B - C
    new_rate = None
    comment = ""

    if B < 70:
        new_rate = 0
        next_check = "15 minutes"
        dextrose = round((100 - B) * 0.3, 1)
        comment = f"Give {dextrose} ml of IV 50% dextrose"
    elif 70 <= B <= 110:
        new_rate = 0
        next_check = "30 minutes"
        comment = "Consider 5 ml IV 50% dextrose if elderly or high risk"
    elif 110.1 <= B <= 139:
        if delta >= 1:
            new_rate = (B - 60) * 0.03
        elif 0 >= delta >= -20:
            new_rate = (B - 60) * 0.02
        elif -20.1 >= delta >= -40:
            new_rate = (B - 60) * 0.014
        else:
            new_rate = 0
            next_check = "30 minutes"
    elif 139.1 <= B <= 179:
        if delta >= 1:
            new_rate = (B - 60) * 0.03
        elif 0 >= delta >= -20:
            new_rate = (B - 60) * 0.02
        elif -20.1 >= delta >= -40:
            new_rate = (B - 60) * 0.014
        else:
            new_rate = 0
            next_check = "30 minutes"
    elif 179.1 <= B <= 249:
        if delta >= -10:
            new_rate = (B - 60) * ((last_rate / (B - 60)) + 0.01)
        elif -11 >= delta >= -40:
            new_rate = (B - 60) * 0.03
        elif -41 >= delta >= -80:
            new_rate = (B - 60) * 0.02
        else:
            new_rate = (B - 60) * 0.014
    elif B > 249:
        if delta >= -40:
            new_rate = (B - 60) * ((last_rate / (B - 60)) + 0.01)
        elif -41 >= delta >= -80:
            new_rate = (B - 60) * 0.03
        elif -81 >= delta >= -120:
            new_rate = (B - 60) * 0.02
        else:
            new_rate = (B - 60) * 0.014

    st.subheader("Ongoing Infusion Calculation")
    if new_rate is not None:
        st.write(f"New Infusion Rate: {round(new_rate, 1)} units/hour")
    if comment:
        st.write(comment)
    if 'next_check' in locals():
        st.write(f"Next check in: {next_check}")
else:
    st.info("Please enter either Initial Glucose (A) or all values for Present (B), Last (C), and Infusion rate.")
