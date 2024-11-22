import streamlit as st
import pandas as pd

# Helper functions to process each financial statement
def create_financial_table(financials, statement_type):
    """
    Create a Pandas DataFrame for a specific financial statement.

    Parameters:
    - financials (list): A list of dictionaries containing quarterly financial data.
    - statement_type (str): The type of financial statement to process 
      (e.g., 'balance_sheet', 'income_statement', 'cash_flow_statement').

    Returns:
    - pd.DataFrame: A DataFrame representing the financial data for the specified statement type.
    """
    data = {}

    # Process each quarter's financial data
    for quarter_data in financials:
        fiscal_period = f"{quarter_data['fiscal_period']} {quarter_data['fiscal_year']}"
        statement = quarter_data["financials"].get(statement_type, {})

        for key, details in statement.items():
            label = details["label"]
            value = details.get("value", None)
            if label not in data:
                data[label] = {}
            data[label][fiscal_period] = value

    # Create and return the DataFrame
    return pd.DataFrame(data).T.reset_index().rename(columns={"index": "Field"})

def display_financial_statements(financials, ticker):
    """
    Display financial statements (Balance Sheet, Income Statement, and Cash Flow Statement)
    for each quarter in Streamlit.

    Parameters:
    - financials (list): A list of dictionaries containing quarterly financial data.
    - ticker (str): The stock ticker for which the financial data is displayed.
    """
    
    # Add a main title
    st.title(f"{ticker} Financial Statements")
   
    # Display Balance Sheet
    st.subheader("Balance Sheet")
    
    try:
        balance_sheet_df = create_financial_table(financials, "balance_sheet")
        st.dataframe(balance_sheet_df)
        
    except Exception as e:
        st.error(f"Error displaying Balance Sheet: {e}")
    
    st.header("", divider=True)
    
    # Display Income Statement
    st.subheader("Income Statement")
    try:
        income_statement_df = create_financial_table(financials, "income_statement")
        
        st.dataframe(income_statement_df)
        
    except Exception as e:
        st.error(f"Error displaying Income Statement: {e}")

    st.header("", divider=True)

    # Display Cash Flow Statement
    st.subheader("Cash Flow Statement")
    try:
        cash_flow_statement_df = create_financial_table(financials, "cash_flow_statement")
        st.dataframe(cash_flow_statement_df)
        
    except Exception as e:
        st.error(f"Error displaying Cash Flow Statement: {e}")
        
    st.header("", divider=True)