# Glucommander IV Insulin Infusion Calculator

This repository contains Streamlit applications that implement the Glucommander / Yale IV insulin infusion protocol.  The tools help clinicians determine an initial bolus dose, start an insulin infusion, and titrate the hourly rate based on successive blood glucose measurements.  They are designed for educational and prototyping purposes and **must not** replace institutional policies or clinical judgment.

## Project layout

| File | Description |
| ---- | ----------- |
| `infusion.py` | Primary Streamlit app with a two-mode interface (start infusion vs. adjust infusion) built around small testable calculation functions. |
| `iv_insulin_calculator.py` | Earlier single-page prototype that combines the UI and protocol logic in one file. |
| `requirements.txt` | Python dependencies required to run the Streamlit apps. |

## Calculation logic

The current app (`infusion.py`) exposes the key protocol rules as plain Python functions:

* **`calc_initial_rate_and_bolus(bg)`** implements the startup rule set: if the initial blood glucose is ≥300 mg/dL, both the bolus dose and the starting infusion rate are `BG / 70`; otherwise they are `BG / 100`.  Results are rounded to one decimal place to match pump increments.
* **`calc_ongoing_rate(curr_bg, prev_bg, last_rate)`** computes the new infusion rate during ongoing titration.  The function:
  * Stops the infusion (rate = 0) if the current reading is <70 mg/dL.
  * Chooses a multiplier between 0.014 and 0.03 depending on the glucose band and the hourly change (ΔBG).
  * Applies an adaptive multiplier if hyperglycaemia persists despite the current rate.
  * Returns the new rate rounded to 0.1 U/h.

These pure functions make it straightforward to unit test the clinical rules separately from the Streamlit interface.

## Running the app locally

1. Create a virtual environment (optional but recommended).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Launch Streamlit with the main application:
   ```bash
   streamlit run infusion.py
   ```
4. Access the interface in your browser at the URL shown in the Streamlit terminal output (typically http://localhost:8501).

The legacy prototype can be explored with `streamlit run iv_insulin_calculator.py`.

## Using the application

The `infusion.py` UI starts by asking the user to select one of two modes:

* **Start infusion (initial bolus & rate)** – enter the first blood glucose measurement to receive the initial bolus and infusion rate recommendation.
* **Adjust infusion (ongoing)** – enter the current blood glucose, the value from one hour earlier, and the current infusion rate.  The app reports the recommended new rate and notes whether hypoglycaemia intervention steps are required.

An expandable footer summarises the Davidson / Glucommander protocol and highlights safety guidance.  Informational messages remind the user to confirm results according to local clinical governance.

## Disclaimers

The calculators are provided for demonstration purposes only.  Always validate the dose recommendations against your institution’s official protocol and consult qualified medical professionals before applying in patient care.
