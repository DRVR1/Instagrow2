# Instagrow2

## Project Description
Computer softare, that automatically logs in your instagram account, and performs a defined number of actions per day, increasing your account visibility. 

## Security Warning:
The misuse of this software can lead to the temporary or permanent blocking of your instagram account. Please use it carefully and read the documentation. The responsability is yours.

## Features:
- Mass follow / unfollow instagram accounts.
- Single account full scrapping
- Multiple accounts scrapping
- Scrape followers / followings
- Saves logs
- Stores and loads session data

## Coming soon:
- List people who don't follow you back and save the list
- Compatibility with linux.
- AutoStartup and automatic actions (no human intervention needed).
- Automatic content posting (posts, comments, likes, histories).
- Enable proxy settings

## Requirements
- json
- instalog
- PyQt5
- sqlalchemy
- instagrapi

## Safety measures (avoid banning/shadowbanning/thortling)
- Verifying your @account with a phone number
- Not using a cheap or a free proxy
- Using an old account
- Waiting a reasonable time between following/posting/etc
- Loging in with a sessionID

As you can see, some measures depend completely on you. This app is configured by default with the safests measures, according to the [instagrapi documentation](https://subzeroid.github.io/instagrapi/usage-guide/best-practices.html), also your sessionID will be automatically saved.

## How to use

### To start, run > python main.py

Example: i want to follow the followers of @python.hub to increase my account visibility (beacuse i make python posts too)

1. Add your instagram account (@username and password)
2. Two factor autentication must be disabled in order to login from this app.
3. Select the scrape account followers option
4. Enter the target username (@python.hub)
5. Select the max number of followers you wish to scrape (the less, the safer)
6. The scrapped followers will be saved into a json, containing names, pictures urls, and some metadata.
7. Select the mass follow option and select the previously scrapped json
8. The app will start following until it runs out of tokens (tokens are a safety measure, altough can be configured)
