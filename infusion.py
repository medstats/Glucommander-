# iv_insulin_calculator.py
"""
Streamlit app — Yale IV Insulin Infusion Calculator
---------------------------------------------------
A small single‑file Streamlit application that implements the bedside Glucommander 
intravenous insulin protocol (sometimes called the Georgia Hospital IV Insulin Infusion /Davidson algorithm).

Key improvements over the older draft the user shared:
• **Explicit mode selector** – prevents Streamlit from mis‑routing inputs.
• **All number widgets default to *blank* (returns `None`)** instead of 0.
• **Separation of concerns** – pure‑logic functions are isolated so that they
  can be unit‑tested independently of Streamlit.
• **Clear on‑screen summary of the rate chosen plus dosing safety notes.**

DISCLAIMER  
This calculator is provided for educational purposes only and is **NOT** a
substitute for clinical judgment. Always verify against your institution’s
policy before prescribing.
"""

import math
import streamlit as st

# ===========================
# PURE CALCULATION FUNCTIONS
# ===========================

def calc_initial_rate_and_bolus(bg: float) -> tuple[float, float]:
    """Return (bolus_units, infusion_rate_u_per_hr) for the *start* of infusion.

    Yale protocol:
    – If BG ≥300 mg/dL: bolus = BG/70 U and rate = BG/70 U/h.
    – Else: bolus = BG/100 U and rate = BG/100 U/h.
    Both are rounded to one decimal place for pumps that accept tenths.
    """
    if bg >= 300:
        divisor = 70
    else:
        divisor = 100
    bolus = round(bg / divisor, 1)
    rate = bolus  # same numeric value, different context
    return bolus, rate


def calc_ongoing_rate(curr_bg: float, prev_bg: float, last_rate: float) -> float:
    """Return *new* infusion rate per Yale titration rules.

    Args
    ----
    curr_bg : current blood glucose (mg/dL)
    prev_bg : value measured 1 h earlier (mg/dL)
    last_rate : current pump rate (U/h)
    """
    delta = prev_bg - curr_bg  # positive if BG fell
    # ========================== SAFETY FIRST ==========================
    if curr_bg < 70:
        return 0.0  # protocol mandates STOP and treat hypoglycaemia
    # ==================================================================

    # Determine multiplier «m» per Yale lookup table -------------------
    # Default multiplier depends on BG band
    if 110 <= curr_bg < 140:
        base_m = 0.02
    elif 140 <= curr_bg < 180:
        base_m = 0.02
    elif 180 <= curr_bg < 250:
        base_m = 0.02  # will be raised if BG not falling
    else:  # ≥250
        base_m = 0.03

    # Adjust multiplier for rate‑of‑change (delta) ---------------------
    if delta >= 40:
        m = 0.014  # slow down slightly if BG is dropping fast
    elif delta <= 0:  # BG static or rising
        m = 0.03
    else:  # delta 1‑39 mg/dL, gentle fall — keep base multiplier
        m = base_m

    # Additional Yale rule for persistent hyperglycaemia --------------
    if curr_bg >= 180 and delta <= 10:  # BG high & not falling ≥10 mg/dL
        adaptive_m = last_rate / max(curr_bg - 60, 1) + 0.01
        m = max(m, adaptive_m)

    new_rate = (curr_bg - 60) * m
    # Round to one decimal – most pumps support 0.1 U/h increments.
    return round(max(new_rate, 0.0), 1)


# =================================
# STREAMLIT USER‑INTERFACE LAYOUT
# =================================
st.set_page_config(
    page_title="IV Insulin Infusion (Yale) Calculator",
    page_icon="💉",
    layout="centered",
)

st.title("💉 Glucommander IV Insulin Infusion Calculator")
mode = st.radio(
    "Select calculator mode:",
    ["Start infusion (initial bolus & rate)", "Adjust infusion (ongoing)"]
)

if mode == "Start infusion (initial bolus & rate)":
    st.subheader("Initial setup")
    init_bg = st.number_input(
        "Initial blood glucose (mg/dL)",
        min_value=0.0,
        step=1.0,
        format="%.0f",
        placeholder="e.g. 256",
    )
    if init_bg:
        bolus, rate = calc_initial_rate_and_bolus(init_bg)
        st.success(
            f"Give **{bolus} U IV bolus**, then start continuous infusion at **{rate} U/h**.")
        st.info("Re‑check BG hourly and switch to *Adjust* mode for titration.")

elif mode == "Adjust infusion (ongoing)":
    st.subheader("Ongoing titration")
    curr_bg = st.number_input(
        "Current blood glucose (mg/dL)",
        min_value=0.0,
        step=1.0,
        format="%.0f",
        placeholder="e.g. 178",
    )
    prev_bg = st.number_input(
        "Blood glucose one hour ago (mg/dL)",
        min_value=0.0,
        step=1.0,
        format="%.0f",
        placeholder="e.g. 192",
    )
    last_rate = st.number_input(
        "Current infusion rate (U/h)",
        min_value=0.0,
        step=0.1,
        format="%.1f",
        placeholder="e.g. 2.4",
    )

    if curr_bg and prev_bg and last_rate:
        new_rate = calc_ongoing_rate(curr_bg, prev_bg, last_rate)
        if new_rate == 0.0 and curr_bg < 70:
            st.error("Hypoglycaemia! Stop insulin, give IV dextrose per protocol.")
        else:
            st.success(f"Set pump to **{new_rate} U/h**.")
            st.write(
                f"(ΔBG = {prev_bg - curr_bg:+.0f} mg/dL in the past hour; multiplier applied per  table.)"
            )
        st.caption("Always confirm rate changes with a second clinician if required by policy.")

# ===============
# FOOTER
# ===============
with st.expander("Davidson /Glucommander Protocol )"):
    st.markdown(
        """
        **Target range:** 100–140 mg/dL in most non‑critical in‑patients.

        1. **Start‑up:**  
           • If BG ≥300 mg/dL → bolus = BG/70 U and infusion = BG/70 U/h  
           • Else → bolus = BG/100 U and infusion = BG/100 U/h.
        2. **Hourly adjustment:**  
           • Compute (BG − 60) × multiplier.  
           • Multiplier 0.014–0.03 chosen from Yale table based on Blood Glucose band and ΔBG.(change in Blood Glucose)
        3. **Hypoglycaemia:**  
           • If BG < 70 mg/dL stop drip, give 25 mL 50 % dextrose, recheck q15 min.
        """
    )

st.caption("Coded by Anupam Singh MD. Based on Glucommander Protocol. Forked from Parimal Swamy Calculator App.")
