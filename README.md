# AI Portfolio Mentor (XIRR Agent)

## Overview
The **AI Portfolio Mentor** is an intelligent agent designed to help investors calculate their true annualized return (XIRR) from their mutual fund or stock statements. It provides a sleek, professional web interface to instantly analyze cash flows and deliver personalized portfolio health insights.

## How It Works
The agent accepts a simple statement of your historical transactions (currently optimized for CSV) and automatically determines the Extended Internal Rate of Return (XIRR) based on your historical cash outflows (SIPs/investments) and your current portfolio valuation.

### File Structure & Roles
* **`app.py`**: The frontend user interface built using the Streamlit framework. This handles the premium dark-themed web app, the drag-and-drop file uploader, and the interactive metrics cards.
* **`xirr_calculator.py`**: The mathematical brain of the agent. It leverages `pandas` for grouping dates/amounts and `pyxirr` for running the complex financial math to calculate the exact annualized return rate.
* **`portfolio_parser.py`**: A secondary tool using `PyPDF2` to extract raw text from PDF files. It serves as the foundation for scraping and parsing native PDF broker statements in the future.
* **`requirements.txt`**: The library roadmap that tells Python exactly which packages are required to run this agent.

---

## 🚀 Setup & Implementation Guide

If you are cloning this project or downloading it for the first time, follow these steps to get the agent running on your local machine:

### 1. Install Requirements
Open a terminal in the project folder and install the necessary Python libraries by running:
```bash
pip install -r requirements.txt
```

### 2. Launch the Application
Start the agent's web server by executing:
```bash
streamlit run app.py
```

### 3. Use the Agent
1. Open the `localhost` URL provided in your terminal in any web browser.
2. Under the **XIRR Calculator** tab, drop your investment statement (`.csv`) into the uploader box. (A `dummy_statement.csv` template exists for testing).
3. Type in your **Current Portfolio Value**.
4. The agent will instantly compute and display your total invested amount, current valuation, and exactly what your XIRR percentage is, along with a custom analytical recommendation!
