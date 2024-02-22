# How to tell instagram we are logging from a known device (when we are not)

A good safety measure is to tell instagram you are using a KNOWN device, to reduce suspicious activity. For example, you have a phone, that you have been using the last year to log in into your @account. If suddenly you login from another device, and start scrapping data, it would stand out.

To fix this, you will have to follow a series of steps, in order to get your device information, and replace it in the file  "default_settings.py"

## Info you need to collect:

   - `user_agent` (you get it from instagram app)
   - `country` (two letter code)
   - `country_code` (a number)
   - `locale` (language)
   - `timezone_offset` (you calculate it)

# Collecting info

## step 1: user_agent 
Request instagram to generate a file with your personal data (by [law](https://gdprinfo.eu/en-article-15), instagram must provide it to you). This data will include a file with all the user agents of your known devices. After you downloaded your personal data (remember to include `device information` when selecting what to download).
You can retrieve the user agent from the `device information` provided by instagram/meta.

An user agent looks like this:
`Instagram 304.0.0.35.106 Android (33/13; 420dpi; 1080x2194; samsung; SM-A336M; a33x; s5e8825; en_US; 525085885)`

[How to download this data?](https://help.instagram.com/181231772500920)


## Step 2: Country, code and locale

Example:

    country = "AR"
    
    country_code = 54
    
    locale = "en_US"


## Step 3: Timezone offset

Time Zone offset... what is this number?
    
    timezone_offset= -10800
    
1) Start with the UTC offset in hours.
2) Multiply the number of hours by 3600 (the number of seconds in an hour).
3) If it's a positive offset (e.g., UTC+3), the result will be positive. If it's a negative offset (e.g., UTC-3), the result will be negative.

### Example: 
Convert UTC-3 to seconds (buenos aires, Argentina):
1) UTC offset: -3 hours 
2) -3 hours * 3600 seconds/hour = -10800 seconds
3) So, UTC-3 is equivalent to -10800 seconds.

# Final step:
Replace the collected information in the `src/default_settings.py` file. Also, if you logged in before, you gonna need to delete the saved user settings, otherwise the default_settings won't be applied. This user settings will be located in `C:/Users/your_username/AppData/local/instagrow2/settings`

# How do i know this settings worked?
When you log in, the unrecognized device email and notifications won't show up, decreasing your suspiciousness.

