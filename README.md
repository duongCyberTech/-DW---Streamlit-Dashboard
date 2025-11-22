# Warehouse DSS - Mall Profit Optimization

A Decision Support System (DSS) for optimizing mall selection to maximize profit through targeted investments in product categories. This project uses linear programming and Monte Carlo simulation to analyze and recommend the best malls for increasing sales.

## Features

- **Data Analysis**: Load and analyze customer profile data with sales information.
- **Profit Optimization**: Use linear programming to select optimal malls for investment within budget constraints.
- **Monte Carlo Simulation**: Run simulations to assess risk and expected profits under uncertainty.
- **Interactive UI**: Streamlit-based web interface for easy parameter adjustment and result visualization.
- **Visualization**: Charts showing profit distributions and simulation results.

## Installation

1. Clone the repository or download the files.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Ensure `DM_customer_profile.csv` is in the project directory.

## Usage

### Run Virtual Environment (venv) and install package
Execute the Python script directly:
```
python -m venv venv
venv/Scripts/Activate
pip install -r requirements.txt
```

### Running the Script
Execute the Python script directly:
```
cd frontend/dss
python warehousedss.py
```
This will run the optimization and display results in the console, including plots.

### Running the Web App
Launch the Flask backend:
```
cd backend
python app.py
```
Launch the interactive Streamlit app:
```
cd frontend
streamlit run app.py
```
Open the provided URL in your browser to access the UI.

### Parameters
- **Number of malls (k)**: How many malls to select for optimization.
- **Increase percentage**: Percentage to increase quantity in selected categories.
- **Investment percentage**: Portion of expected revenue used as cost.
- **Budget limit**: Maximum investment amount.
- **Category limit**: Product categories to target (or select all).

## Project Structure

- `warehousedss.py`: Main script with data processing, optimization, and simulation.
- `streamlit_app.py`: Streamlit web application for interactive use.
- `requirements.txt`: Python dependencies.
- `DM_customer_profile.csv`: Sample customer data (not included; provide your own).
- `README.md`: This file.

