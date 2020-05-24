David McConnell's TURNP TRACKER!

This project monitors Reddit's 'Animal Crossing New Horizons Turnip Market' Subreddit to do the following:

    * Monitor for islands with Daisy selling Turnips below your desired maximum buy price.
    * Monitor for islands with Nooks buying Turnips above your desired minimum sell price.
    * Parse post to give you an easily identifiable turnip.exchange signup link, if available
    * Automatically email you when a fitting post is made

This app utilizes PRAW with Reddit API. On first use, the application will prompt you to create and input API details, offering the option to save it for future use to avoid reentry.

This app utilizes Gmail SMTP Address and Port by default in order to send SSL email notifications; you can change this to fit your requirements. This, too, can be saved to avoid reentry in the future.

This app prompts for, but never saves, email addresses and passwords.

This app prompts for, and gives the option to save, default SMTP address and SSL Port, in Files/smtp.txt

This app prompts for, and gives the option to save, required Reddit API credentials, in Files/api.txt

Please note: API details are not currently encrypted in any fashion. Please use caution when utilizing.
