import pandas as pd
import streamlit as st


def calculate_sma(data, period=50):
    """
    Calculates the Simple Moving Average (SMA) for a specified period.
    
    Parameters:
    - data: DataFrame, must contain a 'Close' column with closing prices.
    - period: int, the number of periods over which to calculate the SMA (default is 50).
    
    Returns:
    - Series of SMA values with the same length as the input data, or None if input is invalid.
    """
    
    # Compute and return the SMA
    try:
        sma = data['Close'].rolling(window=period).mean()
        return sma
    
    except Exception as e:
        st.error(f"Error calculating SMA: {e}")
        return None


def calculate_ema(data, period=50):
    """
    Calculates the Exponential Moving Average (EMA) for a specified period.
    
    Parameters:
    - data: DataFrame, must contain a 'Close' column with closing prices.
    - period: int, the number of periods over which to calculate the EMA (default is 50).
    
    Returns:
    - Series of EMA values with the same length as the input data, or None if input is invalid.
    """
    
    # Compute and return the EMA
    try:
        ema = data['Close'].ewm(span=period, adjust=False).mean()
        return ema
    
    except Exception as e:
        st.error(f"Error calculating EMA: {e}")
        return None


def calculate_rsi(data, period=14):
    """
    Calculates the Relative Strength Index (RSI) for a specified period.

    Parameters:
    - data: DataFrame, must contain a 'Close' column with closing prices.
    - period: int, the number of periods over which to calculate the RSI (default is 14).

    Returns:
    - Series of RSI values with the same length as the input data, or None if input is invalid.
    """

    try:
        # Calculate the daily price changes
        delta = data['Close'].diff()

        # Calculate gains (positive changes) and losses (negative changes)
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        # Calculate the Relative Strength (RS)
        rs = gain / loss

        # Calculate the RSI
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    except Exception as e:
        st.error(f"Error calculating RSI: {e}")
        return None


def calculate_macd(data):
    """
    Calculates the Moving Average Convergence Divergence (MACD) line.

    Parameters:
    - data: DataFrame, must contain a 'Close' column with closing prices.

    Returns:
    - Series of MACD values with the same length as the input data, or None if input is invalid.
    """
    
    try:
        # Calculate the 12-period Exponential Moving Average (EMA)
        ema12 = data['Close'].ewm(span=12, adjust=False).mean()

        # Calculate the 26-period Exponential Moving Average (EMA)
        ema26 = data['Close'].ewm(span=26, adjust=False).mean()

        # MACD line is the difference between the 12-period EMA and 26-period EMA
        macd = ema12 - ema26
        return macd
    
    except Exception as e:
        st.error(f"Error calculating MACD: {e}")
        return None


def calculate_adx(data, period=14):
    """
    Calculates the Average Directional Index (ADX), an indicator of trend strength.

    Parameters:
    - data: DataFrame, must contain 'High', 'Low', and 'Close' columns.
    - period: int, the period over which to calculate ADX (default is 14).

    Returns:
    - Series of ADX values with the same length as the input data, or None if input is invalid.
    """
    
    try:
        # Calculate the difference between current and previous highs and lows
        high_diff = data['High'].diff()
        low_diff = data['Low'].diff()

        # Calculate +DM and -DM (Directional Movement)
        plus_dm = high_diff.where((high_diff > 0) & (high_diff > low_diff), 0)
        minus_dm = -low_diff.where((low_diff > 0) & (low_diff > high_diff), 0)

        # Calculate the Average True Range (ATR) for the given period
        atr = calculate_atr(data, period)
        if atr is None:
            st.error("Failed to calculate ATR, which is required for ADX calculation.")
            return None

        # Calculate +DI and -DI (Directional Indicators)
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)

        # Calculate the DX (Directional Movement Index)
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)

        # Calculate the ADX as a smoothed average of DX values
        adx = dx.rolling(window=period).mean()
        return adx
    
    except Exception as e:
        st.error(f"Error calculating ADX: {e}")
        return None
    
    
def calculate_atr(data, period=14):
    """
    Calculates the Average True Range (ATR), a measure of market volatility.

    Parameters:
    - data: DataFrame, must contain 'High', 'Low', and 'Close' columns.
    - period: int, the period over which to calculate ATR (default is 14).

    Returns:
    - Series of ATR values with the same length as the input data, or None if input is invalid.
    """
    
    try:
        # Step 1: Calculate high-low range for each period
        high_low = data['High'] - data['Low']

        # Step 2: Calculate high-close range (using previous close)
        high_close = (data['High'] - data['Close'].shift()).abs()

        # Step 3: Calculate low-close range (using previous close)
        low_close = (data['Low'] - data['Close'].shift()).abs()

        # Step 4: Calculate True Range (TR) as the max of high-low, high-close, and low-close for each period
        tr = high_low.combine(high_close, max).combine(low_close, max)

        # Step 5: Calculate the ATR by taking a rolling mean of the True Range
        atr = tr.rolling(window=period).mean()
        return atr
    
    except Exception as e:
        st.error(f"Error calculating ATR: {e}")
        return None

def calculate_bollinger_bands(data, period=20):
    """
    Calculates the Bollinger Bands, which consist of an upper and lower band around a Simple Moving Average (SMA).
    Bollinger Bands measure market volatility and indicate potential price levels for the security.

    Parameters:
    - data: DataFrame, must contain a 'Close' column.
    - period: int, the period over which to calculate the SMA and standard deviation (default is 20).

    Returns:
    - A tuple of two Series: (upper_band, lower_band).
      - upper_band: SMA + 2 * standard deviation.
      - lower_band: SMA - 2 * standard deviation.
      - Returns (None, None) if input is invalid.
    """
    
    try:
        # Step 1: Calculate the Simple Moving Average (SMA)
        sma = data['Close'].rolling(window=period).mean()

        # Step 2: Calculate the rolling standard deviation
        std = data['Close'].rolling(window=period).std()

        # Step 3: Calculate the upper and lower Bollinger Bands
        upper_band = sma + (2 * std)
        lower_band = sma - (2 * std)

        return upper_band, lower_band
    
    except Exception as e:
        st.error(f"Error calculating Bollinger Bands: {e}")
        return None, None

def calculate_obv(data):
    """
    Calculates the On-Balance Volume (OBV), a momentum indicator that uses volume flow to predict changes in stock price.

    Parameters:
    - data: DataFrame, must contain 'Close' and 'Volume' columns.

    Returns:
    - Series of OBV values, or None if input is invalid.
    """
    
    try:
        # Step 1: Calculate daily volume flow based on price direction
        volume_flow = data['Volume'] * ((data['Close'] > data['Close'].shift()).astype(int) - 
                                        (data['Close'] < data['Close'].shift()).astype(int))

        # Step 2: Cumulatively sum the volume flow to obtain OBV
        obv = volume_flow.cumsum()

        return obv
    
    except Exception as e:
        st.error(f"Error calculating OBV: {e}")
        return None