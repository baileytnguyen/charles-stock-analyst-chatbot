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



def plot_current_indicators(ticker, indicators):
    """
    Fetches the latest stock data for the current ticker and plots the indicators requested by the user.
    
    Parameters:
    - None. This function relies on Streamlit session state variables for the current ticker and indicators.

    Functionality:
    - Checks for the current ticker and indicators in session state.
    - Fetches stock data for the specified ticker.
    - Displays an error if no ticker or data is available.
    - Calls plot_indicators to visualize the ticker data and selected indicators.
    """

    # Check if a ticker is set in session state
    if ticker:
        
        # Fetch stock data for the specified ticker
        stock_data = fetch.fetch_stock_data(ticker)
        
        timespan = st.session_state.current_timespan
        
        # Check if fetched data is empty, indicating an issue with data retrieval
        if stock_data.empty:
            st.error("No data available for the specified ticker.")
            
        else:
            # Plot the indicators on the fetched stock data
            plot_indicators(ticker, stock_data, indicators, timespan=timespan)
            
    else:
        # Display an error if no ticker is set
        st.error("No ticker or indicators to display.")



def plot_indicators(ticker, stock_data, indicators, timespan):
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
    indicators = [indicator for indicator in indicators if indicator.strip() and indicator != "None"]
    
    
    if (indicators):
        # Convert indicators to lowercase for case-insensitive checking
        indicators = [indicator.lower() for indicator in indicators]

    # Determine whether to plot volume or close price based on indicators
    volume_requested = "volume" in indicators
    price_requested = "candlestick" in indicators or "price" in indicators or not indicators  # Default to close price if no indicator

    # Plot the main stock price chart
    if price_requested:
        
        mpf_kwargs = {
            "type": "candle" if "candlestick" in indicators else "line",
            "style": "charles",
            "title": f"{ticker} Stock Price",
            "ylabel": "Price (USD)",
            "volume": False,  # Volume will be plotted separately if requested
        }
        fig, ax = mpf.plot(stock_data, **mpf_kwargs, returnfig=True)
        st.pyplot(fig)
        

    # Loop through indicators to plot each as a separate chart
    for indicator in indicators:
        
        # Ensure the indicator is defined in the functions and skip Volume
        if indicator in indicator_functions and indicator != "volume":
            
            try:
                # Calculate the indicator values
                indicator_values = indicator_functions[indicator](stock_data)
                
                # Get the specific plot configuration for this indicator
                config = indicator_config.get(indicator, {})
                color = config.get("color", "orange")
                linestyle = config.get("style", "solid")
                panel = config.get("panel", 1)
                
                # Simple Moving Average
                if indicator == "sma":
                    
                    # Generate SMAs with different time periods and add them to the stock_data DataFrame
                    stock_data['SMA_5'] = calc.calculate_sma(stock_data, period=5)
                    stock_data['SMA_10'] = calc.calculate_sma(stock_data, period=10)
                    stock_data['SMA_20'] = calc.calculate_sma(stock_data, period=20)
                    stock_data['SMA_50'] = calc.calculate_sma(stock_data, period=50)
                    stock_data['SMA_100'] = calc.calculate_sma(stock_data, period=100)
                    stock_data['SMA_200'] = calc.calculate_sma(stock_data, period=200)
                    
                    # Check if the 5, 10, and 20-day SMAs have valid data (i.e., not all NaN/None)
                    if (not(stock_data['SMA_5'].isnull().all()) and
                        not(stock_data['SMA_10'].isnull().all()) and
                        not(stock_data['SMA_20'].isnull().all())):
                    
                        # Define plotting parameters for 5, 10, and 20-day SMAs
                        mpf_kwargs = {
            				"type": "candle",  
            				"style": "charles",
            				"title": f"{ticker} 5, 10, and 20-day SMAs",
            				"ylabel": "Price (USD)",
            				"addplot": [
                                mpf.make_addplot(stock_data['SMA_5'], color="blue", label="5-day SMA"),
                                mpf.make_addplot(stock_data['SMA_10'], color="green", label="10-day SMA"),
                                mpf.make_addplot(stock_data['SMA_20'], color="red", label="20-day SMA"),
                            ],
            				"volume": False,
            			}
                        
            			# Plot the 5, 10, and 20-day SMAs
                        fig, axlist = mpf.plot(stock_data, **mpf_kwargs, returnfig=True)
                        st.pyplot(fig)
                        
                    # Check if the 50 and 100-day SMAs have valid data
                    if (not(stock_data['SMA_50'].isnull().all()) and
                        not(stock_data['SMA_100'].isnull().all())):
                    
                        # Define plotting parameters for 50 and 100-day SMAs
                        mpf_kwargs = {
            				"type": "candle",  
            				"style": "charles",
            				"title": f"{ticker} 50 and 100-day SMAs",
            				"ylabel": "Price (USD)",
            				"addplot": [
                                mpf.make_addplot(stock_data['SMA_50'], color="purple", label="50-day SMA"),
                                mpf.make_addplot(stock_data['SMA_100'], color="orange", label="100-day SMA"),
                            ],
            				"volume": False,
            			}
                        
            			# Plot the 50 and 100-day SMAs
                        fig, axlist = mpf.plot(stock_data, **mpf_kwargs, returnfig=True)
                        st.pyplot(fig)
                        
                    # Separate display for 200-day SMA if it has valid data
                    if (not(stock_data['SMA_200'].isnull().all())):      
                    
                        # Define plotting parameters for the 200-day SMA
                        mpf_kwargs = {
            				"type": "candle",  
            				"style": "charles",
            				"title": f"{ticker} 200-day SMA",
            				"ylabel": "Price (USD)",
            				"addplot": [
                                mpf.make_addplot(stock_data['SMA_200'], color="brown", label="200-day SMA"),
                            ],
            				"volume": False,
            			}
                        
            			# Plot the 200-day SMA
                        fig, axlist = mpf.plot(stock_data, **mpf_kwargs, returnfig=True)
                        st.pyplot(fig)

                # Exponential Moving Average
                elif indicator == "ema":
                    
                    # Generate EMAs with specified time periods
                    stock_data['EMA_12'] = calc.calculate_ema(stock_data, period=12)
                    stock_data['EMA_26'] = calc.calculate_ema(stock_data, period=26)
                    stock_data['EMA_50'] = calc.calculate_ema(stock_data, period=50)
                    stock_data['EMA_200'] = calc.calculate_ema(stock_data, period=200)
                
                    # Check if the 12 and 26-day EMAs have valid data
                    if (not stock_data['EMA_12'].isnull().all() and 
                        not stock_data['EMA_26'].isnull().all()):
                        
                        # Define plotting parameters for 12 and 26-day EMAs
                        mpf_kwargs = {
                            "type": "candle",
                            "style": "charles",
                            "title": f"{ticker} 12 and 26-day EMAs",
                            "ylabel": "Price (USD)",
                            "addplot": [
                                mpf.make_addplot(stock_data['EMA_12'], color="blue", label="12-day EMA"),
                                mpf.make_addplot(stock_data['EMA_26'], color="green", label="26-day EMA"),
                            ],
                            "volume": False,
                        }
                
                        # Plot the 12 and 26-day EMAs
                        fig, axlist = mpf.plot(stock_data, **mpf_kwargs, returnfig=True)
                        st.pyplot(fig)
                    
                    # Check if the 50-day EMA has valid data
                    if (not stock_data['EMA_50'].isnull().all()):
                        
                        # Define plotting parameters for the 50-day EMA
                        mpf_kwargs = {
                            "type": "candle",
                            "style": "charles",
                            "title": f"{ticker} 50-day EMA",
                            "ylabel": "Price (USD)",
                            "addplot": [
                                mpf.make_addplot(stock_data['EMA_50'], color="purple", label="50-day EMA"),
                            ],
                            "volume": False,
                        }
                
                        # Plot the 50-day EMA
                        fig, axlist = mpf.plot(stock_data, **mpf_kwargs, returnfig=True)
                        st.pyplot(fig)
                    
                    # Check if the 200-day EMA has valid data
                    if (not stock_data['EMA_200'].isnull().all()):
                        
                        # Define plotting parameters for the 200-day EMA
                        mpf_kwargs = {
                            "type": "candle",
                            "style": "charles",
                            "title": f"{ticker} 200-day EMA",
                            "ylabel": "Price (USD)",
                            "addplot": [
                                mpf.make_addplot(stock_data['EMA_200'], color="orange", label="200-day EMA"),
                            ],
                            "volume": False,
                        }
                
                        # Plot the 200-day EMA
                        fig, axlist = mpf.plot(stock_data, **mpf_kwargs, returnfig=True)
                        st.pyplot(fig)

                
                # Special handling for Bollinger Bands, which has upper and lower bands
                elif indicator == "bollinger bands":
                    
                    if isinstance(indicator_values, tuple) and len(indicator_values) == 2:
                        stock_data['BB_upper'], stock_data['BB_lower'] = indicator_values
                        
                    else:
                        st.warning(f"Invalid Bollinger Bands data for {ticker}. Skipping plot.")
                        continue
                    
                    mpf_kwargs = {
        				"type": "line",
        				"style": "charles",
        				"title": f"{ticker} Bollinger Bands",
        				"ylabel": "Price (USD)",
        				"addplot": [
                            mpf.make_addplot(stock_data['BB_upper'], panel=panel, color=color, linestyle="--", label="Upper Band"),
                            mpf.make_addplot(stock_data['BB_lower'], panel=panel, color=color, linestyle="--", label="Lower Band"),
        				],
        				"volume": False,          # Exclude volume from the main chart
        			}
                    
        			# Plot the indicator chart
                    fig, axlist = mpf.plot(stock_data, **mpf_kwargs, returnfig=True)
                    st.pyplot(fig)
                    
                    
                # Special handling for MACD, requires the histogram, signal line and MACD line
                elif indicator == "macd":
                    
                    # Calculate the MACD components
                    macd_line, signal_line, histogram = calc.calculate_macd(stock_data)
                    
                    # Check if MACD calculation succeeded
                    if macd_line is not None and signal_line is not None and histogram is not None:
                        # Add the three components to the plot
                        mpf_kwargs = {
                            "type": "line",
                            "style": "charles",
                            "title": f"{ticker} MACD",
                            "ylabel": "Price (USD)",
                            "addplot": [
                                mpf.make_addplot(macd_line, panel=panel, color="blue", label="MACD Line", secondary_y=False),
                                mpf.make_addplot(signal_line, panel=panel, color="red", label="Signal Line", secondary_y=False),
                                mpf.make_addplot(histogram, panel=panel, type="bar", color="grey", label="Histogram", secondary_y=False)
                            ],
                            "volume": False,
                        }
                        
            			# Plot the indicator chart
                        fig, axlist = mpf.plot(stock_data, **mpf_kwargs, returnfig=True)
                        st.pyplot(fig)
                        
                    else:
                        st.warning("MACD components could not be calculated for the plot.")
                        
                        
                # Plotting Parabolic SAR Indicator
                elif indicator == "parabolic sar":
                    
                    # Calculate the Parabolic SAR values for the stock data
                    sar = calc.calculate_parabolic_sar(stock_data)
                    
                    mpf_kwargs = {
                        "type": "line",
                        "style": "charles",
                        "title": f"{ticker} Parabolic SAR",
                        "ylabel": "Price (USD)",
                        "addplot": [
                            mpf.make_addplot(sar, type='scatter', markersize=5, marker='.', color='red'),
                        ],
                        "volume": False,
                    }
                    
        			# Plot the indicator chart
                    fig, axlist = mpf.plot(stock_data, **mpf_kwargs, returnfig=True)
                    st.pyplot(fig)
                        
                    
                # Plotting Directional Movement Index (DMI) Indicator
                elif indicator == "dmi":
                    
                    # Calculate +DI and -DI values for Directional Movement Index
                    plus_di, minus_di = calc.calculate_dmi(stock_data)
                    
                    mpf_kwargs = {
                        "type": "line",
                        "style": "charles",
                        "title": f"{ticker} DMI (+DI / -DI)",
                        "addplot": [
                            mpf.make_addplot(plus_di, panel=config["panel"], color=config["color"], label="+DI"),
                            mpf.make_addplot(minus_di, panel=config["panel"], color="red", label="-DI"),
                        ]
                    }
                    
        			# Plot the indicator chart
                    fig, axlist = mpf.plot(stock_data, **mpf_kwargs, returnfig=True)
                    st.pyplot(fig)

                    
                # Handle all other individual indicators that are plotted independently
                else:
                    
                    # Assign the calculated indicator values to a DataFrame column if they match the data length
                    if len(indicator_values) == len(stock_data):
                        stock_data[indicator] = indicator_values
                        
                    else:
                        st.warning(f"{indicator.upper()} calculation mismatch for {ticker}. Skipping plot.")
                        continue
                    
                    mpf_kwargs = {
        				"type": "line",  
        				"style": "charles",
        				"title": f"{ticker} {indicator.upper()}",
        				"ylabel": "Price (USD)",
        				"addplot": [
        					mpf.make_addplot(stock_data[indicator], panel=panel, color=color, linestyle=linestyle, label=f"{indicator.upper()}", ylabel=indicator.upper())  # Separate panel with custom ylabel
        				],
        				"volume": False,
        			}
                    
        			# Plot the indicator chart
                    fig, axlist = mpf.plot(stock_data, **mpf_kwargs, returnfig=True)
                    st.pyplot(fig)
    
                    
            except Exception as e:
                st.error(f"Error plotting {indicator.upper()} for {ticker}: {e}")
                continue

    # Plot volume chart as a standalone panel if requested
    if volume_requested:
        
        try: 
            mpf_kwargs = {
                "type": "line",
                "style": "charles",
                "title": f"{ticker} Volume",
                "volume": True,  # Display volume as a standalone chart
                "ylabel_lower": "Volume",
            }
            fig, ax = mpf.plot(stock_data, **mpf_kwargs, returnfig=True)
            st.pyplot(fig)
            
        except Exception as e:
            st.error(f"Error plotting volume for {ticker}: {e}")