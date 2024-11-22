# charles

To set-up the project you will need to do the following steps locally:
1. Clone the repo to the folder of your choice
2. Navigate into the repo and checkout the desired branch
3. Create the virtual environment using the following command: python -m venv charles
4. Activate the virtual environment using the following command: charles\Scripts\activate
5. Download the .ENV file, ensure is named .ENV, from our Teams Agile Group Project and paste at the top level directory 
6. Intall the following dependencies using the following command: pip install streamlit supabase python-dotenv bcrypt matplotlib openai==0.28
7. To run the web server enter the following command: streamlit run main.py

To use the Charles - Stock Charting Assistant you will need to provide a company name or ticker in the prompt.
By default if you do not provide an indicator Charles will provide the closing price chart

You can specify one or more of the following indicators to view in a chart:
- SMA (Simple Moving Average)
- EMA (Exponential Moving Average)
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- ADX (Average Directional Index)
- Bollinger Bands
- OBV (On Balance Volume)
- DMI (Directional Movement Index)
- Parabolic SAR
- VROC (Volume Rate of Change)

You can specify one of the following timespans to view in a chart:
- Hour
- Day
- Week
- Month
- Quarter
- Year

You can specify to see the stock's news as well:
"Show news"
"Add news"
"Stop news"
"Remove news"

You can specify to see the stock's financials as well:
"Show financials"
"Add financials"
"Stop financials"
"Remove financials"


Here are some examples of prompts:
I want to see Microsoft with the following indicators SMA, VROC, OBV, and DMI
Remove DMI
Add MACD
Use Timespan of a Month
Remove SMA
Change Timespan to Week
Remove MACD and OBV
..etc

Currently the program will only show 1 stock's indicators. If you specify another stock
then the indicators that were desired for the previous stock will carry over to the desired stock.
Here are some examples of prompts:
I want to see VROC and RSI for SoFi
I want to see Palantir (this will show VROC and RSI for Palantir now and not SoFi)


