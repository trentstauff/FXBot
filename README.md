[![Codacy Badge](https://app.codacy.com/project/badge/Grade/4d81d46fe74d40ba8d405550e644a812)](https://www.codacy.com/gh/trentstauff/FXBot/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=trentstauff/FXBot&amp;utm_campaign=Badge_Grade)
[![PRs Welcome](https://img.shields.io/badge/PRs%20-welcome-brightgreen.svg)](#contributing)

# FXBot

![image](https://user-images.githubusercontent.com/53923200/128397947-04711cb7-0b16-4ed6-8c84-3fdacdc2fadc.png)

**FXBot** is just what you guessed- a **Forex trading bot!** It's been developed in Python, enabled by the OANDA V20 API.

This trading bot allows users to **backtest** and **analyze** their favourite strategies executed on the most popular currency pairs, while also enabling users to dive straight into trading these forex pairs in **real-time, through algorithmic live trading.**

As we all know, algorithmic trading is the **future of finance**. When looking at the top trading firms in the world, all of them are making a shift towards automated trading, and are investing heavily in the space. The ones who don't automate, are at risk of falling behind their competitors!

That's what inspired me to make this bot, and to expose to the public how really anyone this day and age can jump headfirst into the algorithmic trading world.

## Disclaimer

Before downloading and using this bot, please make sure to understand the following:

Through OANDA, you do NOT need to trade real money, and the same is true with respect to using this bot. OANDA offers practice accounts, which this bot is **highly recommended** to utilize.

If you do decide to trade real money, this disclaimer is for you.

### Understand the Risk
Trading Forex involves a risk of loss. Please consider carefully if such trading is appropriate for you. Past performance is not indicative of future results. FXBot has been created solely for educational purposes only and its calculations do not constitute investment recommendations or advice, and it is strongly recommended that you **use this bot as a learning tool.**

If you are to trade using this bot, understand that algorithmic trading involves a high level of risk and is not appropriate for everyone. No guarantee is being made that by using this bot, the algorithmic trading strategies will result in profitable trading or be free of risk of loss. There is a possibility that you could lose some or all of your investment.

## What FXBot Can Do For You

When you first run FXBot, you will be prompted to enter the following:

1) The currency pair you would like to analyze/trade
2) Whether to conduct backtesting or live trading on said currency pair

![image](https://user-images.githubusercontent.com/53923200/128404575-c66b07cc-fc77-4d28-8d35-58d7ae2d120c.png)

### Backtesting

Backtesting is a method for seeing how well a strategy would have performed on historical data. This powerful technique can gather a lot of important information about the strategy- such as when is the best time for the strategy to operate, which currency pairs it should execute on, and much more. 
If the strategy performs well during backtesting, then individuals can look into putting the strategy into a production environment and try to beat the market.

FXBot enables users to backtest their strategies, alongside giving flexibility and customization surrounding the parameters passed to the backtester.

When running the backtesting section of the bot, users will be prompted to specify the following:

1) The strategy to backtest
2) The date range the backtest should occur over
3) Whether the strategy should consider trading costs
4) The granularity for the backtest session (IE how often should the bot analyze the data and consider positions)?
5) Values unique to the strategy (if these values are with respect to time, such as moving averages, the time unit is the same as your specified granularity)

![image](https://user-images.githubusercontent.com/53923200/128403680-72bfc834-aa76-4f1f-a1a0-295f24c9ebcf.png)

After entering this, the bot will go ahead and conduct the backtesting.

Not only will it test the user's specified parameter choices onto the currency pair, but the bot will also find the most **optimal** parameter values for that time period that allows for the highest ROI. This optimization gives critical information that can be further analyzed by the user to find the best values for their trading situation.

Finally, the bot will plot the results so that the user can tangibly see the performance of the strategy.

### Live Trading

Once you believe you have found a good strategy and have optimized its unique parameters, you can jump into live trading.

Live trading is exactly how it sounds, it utilizes algorithmic, event-driven trading that allows the user to execute the strategy on data as it happens in real-time. 
This is where you can realize the full potential of your strategy and see how it performs against the market.

When running the live trading section of the bot, users will be prompted to specify the following:

1) The strategy to backtest
2) The date range the backtest should occur over
3) The granularity for the trading session (IE how often should the bot analyze the data and consider positions)?
4) The number of units to trade with (IE the size you want your positions to be)
5) OPTIONAL: A "stop profit" to halt trading if you reach
6) OPTIONAL: A "stop-loss" to halt trading if you go below
7) Values unique to the strategy (if these values are with respect to time, such as moving averages, the time unit is the same as your specified granularity)

![image](https://user-images.githubusercontent.com/53923200/128405363-900d8ddb-6b43-4dae-bfdf-7fdfbe1b4007.png)

Once the bot is set up and ready to trade, the trading stream will open. For the duration of the session, the console will continuously output each "tick" of data that is being streamed back to the bot, which contains the time of the tick, the bid price, and the ask price.

Every "granularity", the bot will analyze the current market and determine if it should open, close, modify, or hold a position, which is based on the underlying strategy.

![image](https://user-images.githubusercontent.com/53923200/128405765-15760e5f-1807-42a5-997a-06d975a5ea1f.png)

If any of the stop thresholds have been crossed, or if the user terminates the session, the bot will automatically exit all of its current positions, and the console will default back to the start, where the user can start over.

![image](https://user-images.githubusercontent.com/53923200/128405987-c60bbea3-7c1c-4cae-8b5f-c5e0dab8fea4.png)


## Current Strategies

- SMA https://www.google.com/search?q=sma+strategy&oq=SMA+strategy&aqs=chrome.0.0i512j0i67j0i512l2j0i22i30l6.1680j0j7&sourceid=chrome&ie=UTF-8
- Bollinger Bands https://www.investopedia.com/trading/using-bollinger-bands-to-gauge-trends/
- Contrarian https://www.investopedia.com/terms/c/contrarian.asp
- Momentum https://www.investopedia.com/terms/m/momentum_investing.asp
- Machine Learning Classification Analysis
- Machine Learning Regression Analysis
- And much more to come!

## How to Setup FXBot

### Requirements

First, you need to have at least a practice account with Oanda (https://oanda.com/). Once logged in, you must create an API token and copy your account number. 

#### API Token
![image](https://user-images.githubusercontent.com/53923200/128407124-08f22bff-a82e-4c47-b150-a3f743e7a38b.png)

This green button will say "Generate". Click it, and copy the API Token.
![image](https://user-images.githubusercontent.com/53923200/128407767-7e8e738a-2a88-42c1-9744-273b31f63dfc.png)

Navigate back to your account, so you can get your account number.
![image](https://user-images.githubusercontent.com/53923200/128407881-538e26ac-6e17-46b8-a07b-ce025d4cf527.png)

#### Account Number

Click "Add Account".
![image](https://user-images.githubusercontent.com/53923200/128408490-e0aa2fe3-daac-4f04-8301-0654b9993f37.png)

Make an account.
**Make sure to select 'v20 fxTrade'**
![image](https://user-images.githubusercontent.com/53923200/128408746-e17439b8-e97b-4513-9691-c23643040552.png)

Once you have made an account, grab your account number.
![image](https://user-images.githubusercontent.com/53923200/128408956-b9bc4f3f-a939-4945-b3a5-2b6736d75548.png)

**Now that you have an OANDA account and these values, you'll need to store them for the bot to use.**

These values need to be put into a configuration file, with the name `oanda.cfg`, as follows:

(You can make it a .txt file first, type the data, and then rename the file to .cfg)

    [oanda]
    account_id = XYZ-ABC-...
    access_token = ZYXCAB...
    account_type = practice (default) or live

**Place the oanda.cfg file into the same directory as the main.py file in the cloned repository folder.**

After cloning the repo, run `pip install -r requirements.txt` to get the required packages.

### Running the application

After installing the requirements, open a command prompt and you can start up the program by typing `python main.py` (python3 on Linux, if applicable) while in its directory.

### Thats all! I hope that this bot helps you to see how awesome algorithmic trading can be. 
### If you need any help setting things up, feel free to email me at tstauffe@uwaterloo.ca
### Have a good one!
