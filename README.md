# Instagrow2

## Project Description
Computer software, that automatically logs in your instagram account, and performs a defined number of actions per day, increasing your account visibility. 

## Warning
By using this software, you are breaking the instagram's [terms of use](https://help.instagram.com/581066165581870).<br>
The misuse of this software can lead to the temporary or permanent blocking of your instagram account. Please use it carefully and read the documentation.<br>
Remember that instagram implements powerful algorithms and artificial intelligence to detect whether requests to it are made by human users or by automated tools. Once it detects suspicious behaviors and patterns, it imposes a block, temporary at best or permanent at worst.<br>The responsability is yours.

## Features
- Mass follow / unfollow instagram accounts.
- Single account full scrapping
- Scrape followers / followings
- Saves logs
- Saves scrapped followers into json files
- Stores and loads session data
- List people who don't follow you back and save the list
- Executable setup for windows
- Compatibility with linux.

## Coming soon
- Human-like behavior
- AutoStartup and automatic actions (no human intervention needed).
- Automatic content posting (posts, comments, likes, histories).
- Enable proxy settings

## Safety measures (avoid banning/shadowbanning/thortling)
- Verifying your @account with a phone number
- Not using a cheap or a free proxy (proxy support coming soon)
- Using an old account
- Waiting a reasonable time between following/posting/etc (automatic and configurable)
- Loging in with a sessionID (automatic)
- [Use a recognized device](https://github.com/DRVR1/Instagrow2/blob/main/docs/Fix%20unrecognized%20device%20altert.md)
- Not scrapping foreign info

What safety measures you take, depends on your usecase. This app is configured by default with the safests measures, according to the [instagrapi documentation](https://subzeroid.github.io/instagrapi/usage-guide/best-practices.html), also your sessionID will be automatically saved.

## How to use

Having python3 installed and the console opened in the project folder:

`pip install -r requirements.txt`

`python main.py`

(Please install the requirements from the file, this app uses forks)

Example 1: i want to follow the followers of @python.hub to increase my account visibility (beacuse i make python posts too)

1. Add your instagram account (@username and password) (as you are extracting foreign info, use an account you can afford to lose).
2. Two factor autentication must be disabled in order to login from this app.
3. Select the scrape account followers option
4. Enter the target username (@python.hub)
5. Select the max number of followers you wish to scrape (the less, the safer)
6. The scrapped followers will be saved into a json, containing names, pictures urls, and some metadata.
7. Select the mass follow option and select the previously scrapped json
8. The app will start following until it runs out of tokens (tokens are a safety measure, altough can be configured)

# Screenshots

![main](https://i.imgur.com/lgoh0yp.png)
![botconfig](https://i.imgur.com/w3iFxkB.png)
![botstats](https://i.imgur.com/PSv2VMf.png)

## Files

![files](https://i.imgur.com/4ntuqhd.png)

## Scrapped @instagram
![scrapped](https://i.imgur.com/AK6Izqh.png)
