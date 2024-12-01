import streamlit as st
import mplfinance as mpf
import polygon.data_fetcher as fetch
import indicators.calculations as calc


# Mapping of indicator names to calculation functions
indicator_functions = {
    "sma": calc.calculate_sma,
    "ema": calc.calculate_ema,
    "rsi": calc.calculate_rsi,
    "macd": calc.calculate_macd,
    "adx": calc.calculate_adx,
    "atr": calc.calculate_atr,
    "bollinger bands": calc.calculate_bollinger_bands,
    "obv": calc.calculate_obv,
    "dmi": calc.calculate_dmi,
    "parabolic sar": calc.calculate_parabolic_sar,
    "vroc": calc.calculate_vroc,
}

# Configuration dictionary for each indicator's style
indicator_config = {
    "sma": {"color": "blue", "style": "solid", "panel": 0},
    "ema": {"color": "green", "style": "solid", "panel": 0},
    "rsi": {"color": "red", "style": "solid", "panel": 1},
    "macd": {"color": "purple", "style": "solid", "panel": 1},
    "adx": {"color": "green", "style": "solid", "panel": 1},
    "atr": {"color": "magenta", "style": "solid", "panel": 1},
    "bollinger bands": {"color": "purple", "style": "solid", "panel": 0, "bands": True},
    "obv": {"color": "orange", "style": "solid", "panel": 1},
    "dmi": {"color": "blue", "style": "solid", "panel": 1},
    "parabolic sar": {"color": "green", "style": "solid", "panel": 1},
    "vroc": {"color": "orange", "style": "solid", "panel": 1},
}


def validate_data(data):
    """
    Validates if the given data is suitable for plotting.

    Parameters:
    - data: DataFrame or Series to validate.

    Returns:
    - bool: True if data is valid and contains non-null values, False otherwise.
    """
    return data is not None and not data.isnull().all()


def plot_current_indicators(ticker, indicators, timespan):
    """
    Fetches the latest stock data for the current ticker and plots the indicators requested by the user.

    Parameters:
    - ticker: str, stock ticker symbol.
    - indicators: list of str, the indicators to plot.
    - timespan: str, timespan for the stock data (e.g., 'day', 'week', 'month').

    Functionality:
    - Checks for the current ticker and indicators in session state.
    - Fetches stock data for the specified ticker.
    - Displays an error if no ticker or data is available.
    - Calls plot_indicators to visualize the ticker data and selected indicators.
    """

    # Check if a ticker is set in session state
    if ticker:

        # Fetch stock data for the specified ticker
        stock_data = fetch.fetch_stock_data(ticker, timespan)

        # Check if fetched data is empty, indicating an issue with data retrieval
        if stock_data.empty:
            st.error("No data available for the specified ticker.")

        else:
            # Plot the indicators on the fetched stock data
            plot_indicators(ticker, stock_data, indicators)

    else:
        # Display an error if no ticker is set
        st.error("No ticker or indicators to display.")


def plot_indicators(ticker, stock_data, indicators):
    """
    Plots the main stock price and specified technical indicators for the given ticker symbol.

    Parameters:
    - ticker: str, the stock ticker symbol
    - stock_data: DataFrame, containing the stock's OHLC and volume data
    - indicators: list of str, the names of the indicators to plot

    Returns:
    - None, displays plots using Streamlit
    """

    # Remove any empty strings or "None" entries from the indicators list
    indicators = [
        indicator.lower()
        for indicator in indicators
        if indicator.strip() and indicator != "None"
    ]

    # Determine whether to plot volume or close price based on indicators
    volume_requested = "volume" in indicators

    mpf_kwargs = {
        "type": "candle",  # Default to candlestick chart
        "style": "charles",
        "title": f"{ticker}",
        "ylabel": "Price (USD)",
        "addplot": [],
        "volume": False,  # Default to not showing volume
    }

    # Loop through indicators and plot them on the stock data
    for indicator in indicators:

        # Ensure the indicator is defined in the functions
        if indicator in indicator_functions:

            try:
                # Calculate the indicator values
                indicator_values = indicator_functions[indicator](stock_data)

                # Get the specific plot configuration for this indicator
                config = indicator_config.get(indicator, {})
                color = config.get("color", "orange")
                linestyle = config.get("style", "solid")
                panel = config.get("panel", 1)

                # Simple Moving Average
                if volume_requested:
                    # Change volume flag to true
                    mpf_kwargs["volume"] = True

                elif indicator == "sma":

                    sma_plotted = False

                    # Generate SMAs with different time periods and add them to the stock_data DataFrame
                    stock_data["SMA_5"] = calc.calculate_sma(stock_data, period=5)
                    stock_data["SMA_10"] = calc.calculate_sma(stock_data, period=10)
                    stock_data["SMA_20"] = calc.calculate_sma(stock_data, period=20)
                    stock_data["SMA_50"] = calc.calculate_sma(stock_data, period=50)
                    stock_data["SMA_100"] = calc.calculate_sma(stock_data, period=100)
                    stock_data["SMA_200"] = calc.calculate_sma(stock_data, period=200)

                    # Check if the 5, 10, and 20 period SMAs have valid data (i.e., not all NaN/None)
                    if (
                        validate_data(stock_data["SMA_5"])
                        and validate_data(stock_data["SMA_10"])
                        and validate_data(stock_data["SMA_20"])
                    ):

                        sma_plotted = True

                        # Add the 5, 10, and 20 period SMAs to the plot
                        mpf_kwargs["addplot"].append(
                            mpf.make_addplot(
                                stock_data["SMA_5"], color="blue", label="5 period SMA"
                            )
                        )
                        mpf_kwargs["addplot"].append(
                            mpf.make_addplot(
                                stock_data["SMA_10"],
                                color="green",
                                label="10 period SMA",
                            )
                        )
                        mpf_kwargs["addplot"].append(
                            mpf.make_addplot(
                                stock_data["SMA_20"], color="red", label="20 period SMA"
                            )
                        )

                    # Check if the 50 and 100 period SMAs have valid data
                    if validate_data(stock_data["SMA_50"]) and validate_data(
                        stock_data["SMA_100"]
                    ):
                        sma_plotted = True

                        # Add the 50 and 100 period SMAs to the plot
                        mpf_kwargs["addplot"].append(
                            mpf.make_addplot(
                                stock_data["SMA_50"],
                                color="purple",
                                label="50 period SMA",
                            )
                        )
                        mpf_kwargs["addplot"].append(
                            mpf.make_addplot(
                                stock_data["SMA_100"],
                                color="orange",
                                label="100 period SMA",
                            )
                        )

                    # Separate display for 200 period SMA if it has valid data
                    if validate_data(stock_data["SMA_200"]):
                        sma_plotted = True

                        # Add the 200 period SMA to the plot
                        mpf_kwargs["addplot"].append(
                            mpf.make_addplot(
                                stock_data["SMA_200"],
                                color="brown",
                                label="200 period SMA",
                            )
                        )

                    # If none of the SMA's were plotted and the indicator was requested then report a warning
                    elif not sma_plotted:
                        st.warning(
                            f"Cannot plot {indicator.upper()} due to insufficient data"
                        )

                # Exponential Moving Average
                elif indicator == "ema":

                    ema_plotted = False

                    # Generate EMAs with specified time periods
                    stock_data["EMA_12"] = calc.calculate_ema(stock_data, period=12)
                    stock_data["EMA_26"] = calc.calculate_ema(stock_data, period=26)
                    stock_data["EMA_50"] = calc.calculate_ema(stock_data, period=50)
                    stock_data["EMA_200"] = calc.calculate_ema(stock_data, period=200)

                    # Check if the 12 and 26 period EMAs have valid data
                    if validate_data(stock_data["EMA_12"]) and validate_data(
                        stock_data["EMA_26"]
                    ):
                        ema_plotted = True

                        # Add the 12 and 26 period EMAs to the plot
                        mpf_kwargs["addplot"].append(
                            mpf.make_addplot(
                                stock_data["EMA_12"],
                                color="blue",
                                label="12 period EMA",
                            )
                        )
                        mpf_kwargs["addplot"].append(
                            mpf.make_addplot(
                                stock_data["EMA_26"],
                                color="green",
                                label="26 period EMA",
                            )
                        )

                    # Check if the 50 period EMA has valid data
                    if validate_data(stock_data["EMA_50"]):
                        ema_plotted = True

                        # Add the 50 period EMA to the plot
                        mpf_kwargs["addplot"].append(
                            mpf.make_addplot(
                                stock_data["EMA_50"],
                                color="purple",
                                label="50 period EMA",
                            )
                        )

                    # Check if the 200 period EMA has valid data
                    if validate_data(stock_data["EMA_200"]):
                        ema_plotted = True

                        # Add the 200 period EMA to the plot
                        mpf_kwargs["addplot"].append(
                            mpf.make_addplot(
                                stock_data["EMA_200"],
                                color="orange",
                                label="200 period EMA",
                            )
                        )

                    # If none of the EMA's were plotted and the indicator was requested then report a warning
                    elif not ema_plotted:
                        st.warning(
                            f"Cannot plot {indicator.upper()} due to insufficient data"
                        )

                # Special handling for Bollinger Bands, which has upper and lower bands
                elif indicator == "bollinger bands":

                    if (
                        isinstance(indicator_values, tuple)
                        and len(indicator_values) == 2
                    ):
                        stock_data["BB_upper"], stock_data["BB_lower"] = (
                            indicator_values
                        )

                    else:
                        st.warning(
                            f"Invalid Bollinger Bands data for {ticker}. Skipping plot."
                        )
                        continue

                    # Check if the stock data has data
                    if validate_data(stock_data["BB_upper"]) and validate_data(
                        stock_data["BB_lower"]
                    ):

                        # Add the Bollinger Bands to the plot
                        mpf_kwargs["addplot"].append(
                            mpf.make_addplot(
                                stock_data["BB_upper"],
                                panel=panel,
                                color=color,
                                linestyle="--",
                                label="Upper Band",
                            )
                        )
                        mpf_kwargs["addplot"].append(
                            mpf.make_addplot(
                                stock_data["BB_lower"],
                                panel=panel,
                                color=color,
                                linestyle="--",
                                label="Lower Band",
                            )
                        )

                    else:
                        st.warning(
                            f"Cannot plot {indicator.upper()} due to insufficient data"
                        )

                # Special handling for MACD, requires the histogram, signal line and MACD line
                elif indicator == "macd":

                    # Calculate the MACD components
                    macd_line, signal_line, histogram = calc.calculate_macd(stock_data)

                    # Check if MACD calculation succeeded
                    if (
                        validate_data(macd_line)
                        and validate_data(signal_line)
                        and validate_data(histogram)
                    ):

                        # Add the MACD chart to the plot
                        mpf_kwargs["addplot"].append(
                            mpf.make_addplot(
                                macd_line,
                                panel=panel,
                                color="blue",
                                label="MACD Line",
                                secondary_y=False,
                            )
                        )
                        mpf_kwargs["addplot"].append(
                            mpf.make_addplot(
                                signal_line,
                                panel=panel,
                                color="red",
                                label="Signal Line",
                                secondary_y=False,
                            )
                        )
                        mpf_kwargs["addplot"].append(
                            mpf.make_addplot(
                                histogram,
                                panel=panel,
                                type="bar",
                                color="grey",
                                label="Histogram",
                                secondary_y=False,
                            )
                        )
                    else:
                        st.warning(
                            f"Cannot plot {indicator.upper()} due to insufficient data"
                        )

                # Plotting Parabolic SAR Indicator
                elif indicator == "parabolic sar":

                    # Calculate the Parabolic SAR values for the stock data
                    sar = calc.calculate_parabolic_sar(stock_data)

                    # Check if the stock data has data
                    if validate_data(sar):

                        # Add the Parabolic SAR values to the plot
                        mpf_kwargs["addplot"].append(
                            mpf.make_addplot(
                                sar,
                                type="scatter",
                                markersize=5,
                                marker=".",
                                color="red",
                            )
                        )

                    else:
                        st.warning(
                            f"Cannot plot {indicator.upper()} due to insufficient data"
                        )

                # Plotting Directional Movement Index (DMI) Indicator
                elif indicator == "dmi":

                    # Calculate +DI and -DI values for Directional Movement Index
                    plus_di, minus_di = calc.calculate_dmi(stock_data)

                    # Check if the stock data has data
                    if validate_data(plus_di) and validate_data(minus_di):

                        # Add the +DI and -DI values to the plot
                        mpf_kwargs["addplot"].append(
                            mpf.make_addplot(
                                plus_di,
                                panel=config["panel"],
                                color=config["color"],
                                label="+DI",
                            )
                        )
                        mpf_kwargs["addplot"].append(
                            mpf.make_addplot(
                                minus_di,
                                panel=config["panel"],
                                color="red",
                                label="-DI",
                            )
                        )
                    else:
                        st.warning(
                            f"Cannot plot {indicator.upper()} due to insufficient data"
                        )

                # Handle all other indicators
                else:

                    # Assign the calculated indicator values to a DataFrame column if they match the data length
                    if len(indicator_values) == len(stock_data):
                        stock_data[indicator] = indicator_values

                    else:
                        st.warning(
                            f"{indicator.upper()} calculation mismatch for {ticker}. Skipping plot."
                        )
                        continue

                    # Check if the stock data has data
                    if validate_data(stock_data[indicator]):
                        # Plot the indicator chart
                        mpf_kwargs["addplot"].append(
                            mpf.make_addplot(
                                stock_data[indicator],
                                panel=panel,
                                color=color,
                                linestyle=linestyle,
                                label=f"{indicator.upper()}",
                            )
                        )

                    else:
                        st.warning(
                            f"Cannot plot {indicator.upper()} due to insufficient data"
                        )

            except Exception as e:
                st.error(f"Error plotting {indicator.upper()} for {ticker}: {e}")
                continue

    # Plot
    fig, ax = mpf.plot(stock_data, **mpf_kwargs, returnfig=True)
    st.pyplot(fig)
