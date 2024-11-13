import pandas as pd
import numpy as np
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


def calculate_macd(data, short_period=12, long_period=26, signal_period=9):
    """
    Calculates the MACD line, Signal line, and Histogram.
    
    Parameters:
    - data: DataFrame, must contain a 'Close' column with closing prices.
    - short_period: int, the short EMA period (default is 12).
    - long_period: int, the long EMA period (default is 26).
    - signal_period: int, the signal EMA period (default is 9).
    
    Returns:
    - A tuple of three Series: (macd_line, signal_line, histogram).
    """
    try:
        # Calculate short and long EMAs
        ema_short = data['Close'].ewm(span=short_period, adjust=False).mean()
        ema_long = data['Close'].ewm(span=long_period, adjust=False).mean()

        # MACD Line is the difference between short and long EMAs
        macd_line = ema_short - ema_long

        # Signal Line is the EMA of the MACD Line
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()

        # Histogram is the difference between the MACD Line and Signal Line
        histogram = macd_line - signal_line

        return macd_line, signal_line, histogram
    
    except Exception as e:
        st.error(f"Error calculating MACD: {e}")
        return None, None, None


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
    
    
# Directional Movement Index (DMI)
def calculate_dmi(data, period=14):
    """
    Calculates the Directional Movement Index (DMI), which consists of the Positive Directional Indicator (+DI)
    and Negative Directional Indicator (-DI). The DMI helps identify the strength and direction of a trend.

    Parameters:
    - data (DataFrame): A DataFrame containing 'High' and 'Low' columns with high and low price data.
    - period (int): The period over which to calculate the DMI (default is 14).

    Returns:
    - tuple: (plus_di, minus_di), where:
        - plus_di (Series): Positive Directional Indicator (in %), highlighting upward movement strength.
        - minus_di (Series): Negative Directional Indicator (in %), highlighting downward movement strength.
        - Returns (None, None) if an error occurs during calculation.

    """
    
    try:
        # Calculate directional movement
        high_diff = data['High'].diff()
        low_diff = data['Low'].diff()
        plus_dm = high_diff.where((high_diff > 0) & (high_diff > low_diff), 0)
        minus_dm = -low_diff.where((low_diff > 0) & (low_diff > high_diff), 0)
        
        # Calculate ATR, used for normalization
        atr = calculate_atr(data, period)
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        return plus_di, minus_di
    except Exception as e:
        st.error(f"Error calculating DMI: {e}")
        return None, None


# Parabolic SAR
def calculate_parabolic_sar(data, initial_af=0.02, max_af=0.2):
    """
    Calculates the Parabolic Stop and Reverse (SAR), a trend-following indicator that
    provides trailing stop points for both upward and downward trends.

    Parameters:
    - data (DataFrame): A DataFrame containing 'High' and 'Low' columns with high and low price data.
    - initial_af (float): The initial acceleration factor, typically set to 0.02 (default is 0.02).
    - max_af (float): The maximum acceleration factor, which stops the SAR from increasing indefinitely (default is 0.2).

    Returns:
    - Series: A pandas Series containing the SAR values for each period, where the SAR values 
              trail the price in an uptrend and lead it in a downtrend. Returns None if there 
              is an error during calculation.
    """
    
    try:
        # Ensure 'High' and 'Low' columns are present
        if 'High' not in data or 'Low' not in data:
            st.error("Data must contain 'High' and 'Low' columns.")
            return data

        # Initialize variables
        sar = pd.Series(np.nan, index=data.index)
        high, low = data['High'], data['Low']
        af = initial_af  # acceleration factor
        ep = low.iloc[0]  # extreme price
        trend = 1  # 1 for uptrend, -1 for downtrend

        # Set the initial SAR value
        sar.iloc[0] = low.iloc[0]

        # Iterate through each time period
        for i in range(1, len(data)):
            # Calculate SAR based on trend
            sar.iloc[i] = sar.iloc[i - 1] + af * (ep - sar.iloc[i - 1])

            if trend == 1:  # Uptrend
                # Check for trend reversal to downtrend
                if low.iloc[i] < sar.iloc[i]:
                    trend = -1
                    sar.iloc[i] = ep
                    af = initial_af
                    ep = high.iloc[i]
                else:
                    # Update extreme price and acceleration factor for uptrend
                    if high.iloc[i] > ep:
                        ep = high.iloc[i]
                        af = min(af + initial_af, max_af)
            else:  # Downtrend
                # Check for trend reversal to uptrend
                if high.iloc[i] > sar.iloc[i]:
                    trend = 1
                    sar.iloc[i] = ep
                    af = initial_af
                    ep = low.iloc[i]
                else:
                    # Update extreme price and acceleration factor for downtrend
                    if low.iloc[i] < ep:
                        ep = low.iloc[i]
                        af = min(af + initial_af, max_af)

        return sar

    except Exception as e:
        st.error(f"Error calculating Parabolic SAR: {e}")
        return data

# Volume Rate of Change (VROC)
def calculate_vroc(data, period=14):
    """
    Calculates the Volume Rate of Change (VROC), a momentum indicator that 
    measures the rate of change in volume over a specified period.

    Parameters:
    - data (DataFrame): A DataFrame containing a 'Volume' column with volume data.
    - period (int): The period over which to calculate VROC (default is 14).

    Returns:
    - Series: A pandas Series containing VROC values for the given period.
              The result is in percentage form, indicating the rate of volume change.
              Returns None if there is an error during calculation.

    """
    
    try:
        vroc = ((data['Volume'] - data['Volume'].shift(period)) / data['Volume'].shift(period)) * 100
        return vroc
    except Exception as e:
        st.error(f"Error calculating VROC: {e}")
        return None