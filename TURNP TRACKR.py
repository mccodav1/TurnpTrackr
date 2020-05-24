#! python3

import smtplib
import ssl
import re
import praw
import time
import winsound
import pathlib
import datetime as dt
import os
import sys
from datetime import datetime

PROGRAM_TITLE = "TRNIP TRACKR"

FILE_LOCATION = 'Files'
SMTP_FILE = os.path.join(FILE_LOCATION, 'smtp.txt')
API_FILE = os.path.join(FILE_LOCATION, 'api.txt')

GMAIL_DEFAULT_SSL_PORT = 465
GMAIL_DEFAULT_SMTP_ADDRESS = "smtp.gmail.com"


class Person:
    def __init__(self, email):
        self._email = email
        self.name = None

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        self._email = email


class Sender(Person):
    """
    Used to carry email & API details, as well as information used to decide what to parse from Reddit
    """
    def __init__(self, email='', pw='', port=None, address=None):
        self._pw = pw
        self._minOrMax = ''
        self._worth = 0
        self._credentialsValid = False
        super().__init__(email)
        self._sslPort = ''
        self._smtpAddress = ''
        self._hasSMTPFile = False
        self.hasAPIFile = False
        self._status = ''
        self._searchFor = ''
        self.personalUseScript = None
        self.apiSecret = None
        self.apiUser = None
        self.apiPw = None
        self.apiApp = None
        self.apiSubreddit = None
        self._limit = None
        self._content = None

        if port:
            self._sslPort = int(port)
        else:
            port = input(f'Please enter SSL Port or press ENTER to accept Gmail Default '
                         f'({GMAIL_DEFAULT_SSL_PORT}):')
            self._sslPort = int(port) if port else GMAIL_DEFAULT_SSL_PORT

        if address:
            self._smtpAddress = address
        else:
            address = input(f'Please enter SMTP Address or press ENTER to accept Gmail default '
                            f'("{GMAIL_DEFAULT_SMTP_ADDRESS}"):')
            self._smtpAddress = address if address else 'smtp.gmail.com'

    @property
    def hasSMTPFile(self):
        return self._hasSMTPFile

    @hasSMTPFile.setter
    def hasSMTPFile(self, boolValue):
        self._hasSMTPFile = boolValue

    @property
    def searchFor(self):
        return self._searchFor

    @searchFor.setter
    def searchFor(self, find):
        self._searchFor = find

    @property
    def sslPort(self):
        return self._sslPort

    @sslPort.setter
    def sslPort(self, port):
        self._sslPort = port

    @property
    def smtpAddress(self):
        return self._smtpAddress

    @smtpAddress.setter
    def smtpAddress(self, address):
        self._smtpAddress = address

    @property
    def pw(self):
        return self._pw

    @pw.setter
    def pw(self, pw):
        self._pw = pw

    @property
    def credentialsValid(self):
        return self._credentialsValid

    @credentialsValid.setter
    def credentialsValid(self, value):
        self._credentialsValid = value

    @property
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, limit):
        self._limit = limit

    @property
    def minOrMax(self):
        return self._minOrMax

    @minOrMax.setter
    def minOrMax(self, text):
        self._minOrMax = text

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status

    @property
    def worth(self):
        return self._worth

    @worth.setter
    def worth(self, worth):
        self._worth = worth

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, content):
        self._content = content

    def sendMail(self, receiver, post):
        """
        Sends an email to a receiver given certain post content
        :param receiver: Object containing email and name properties
        :param post: Object containing a post title, permalink URL and regular URL
        :return: None
        """
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.smtpAddress, self.sslPort, context=context) as server:
            server.login(self.email, self.pw)
            try:
                tmp = re.findall('[0-9]+', post.title)
                if tmp:
                    self.worth = int(tmp[0])
                else:
                    print("Error parsing worth in sendmail function")

                npc = 'BUYER' if self.status == 'SELLER' else 'SELLER'
                self.content = f'Subject: NEW TURNIP {npc}.- {self.worth}!' \
                               f'\n\nHello {receiver.name},' \
                               f'\n\nA new post has been made on ACNH Turnips!' \
                               f'\n\nWorth: {self.worth}' \
                               f'\nTitle: {post.title}' \
                               f'\nPermalink: www.reddit.com/{post.permalink}' \
                               f'\nURL: {post.url}' \
                               f'\n\nSent by {PROGRAM_TITLE} via Python.'
            except UnicodeEncodeError:
                self.content = f'Subject: NEW TURNIP {npc}!' \
                               f'\n\nHello {receiver.name}' \
                               f'\n\nA new post has been made on ACNH Turnips!' \
                               f'\n\nHowever, there was a problem decoding Unicode!' \
                               f'\n\nCheck out the URL instead!' \
                               f'\nPermalink: www.reddit.com/{post.permalink}' \
                               f'\nURL: {post.url}' \
                               f'\n\nSent by {PROGRAM_TITLE} via Python.'

            finally:
                server.sendmail(self.email, receiver.email, self.content)
                print(f'Email sent to {receiver.email}')

    def validateCredentials(self):
        """
        Validates sender email and password credentials, prompting user again if they are incorrect.
        :return: None
        """
        while not self.credentialsValid:  # to loop until a correct password is aqquired
            try:
                self.email = input("\nWhat is your G-mail address")
                self.pw = input('Please enter your gmail password:')
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(self.smtpAddress, self.sslPort, context=context) as server:
                    server.login(self.email, self.pw)
                self.credentialsValid = True  # sets to true if log in is successful
            except smtplib.SMTPAuthenticationError:
                print('Incorrect Username or Password. Standby for reattempt...\n')
                time.sleep(5)
        print("\nCredentials validated.\n")


class Receiver(Person):
    pass


class Post:
    def __init__(self, postId, title, url, permalink, selfTest, created):
        self._id = postId
        self._title = title
        self._url = url
        self._permalink = permalink
        self._selfText = selfTest
        self._created = created
        self._turnipLink = ''

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, postId):
        self._id = postId

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    @property
    def created(self):
        return get_date(self._created)

    @created.setter
    def created(self, created):
        self._created = created

    @property
    def permalink(self):
        return self._permalink

    @permalink.setter
    def permalink(self, perma):
        self._permalink = perma

    @property
    def selftext(self):
        return self._selfText

    @selftext.setter
    def selftext(self, selftext):
        self._selfText = selftext

    @property  # the getter. modify what we have before returning
    def turnipLink(self):
        pattern = r"https://turnip.exchange/island/\S+"
        link = re.findall(pattern, self.title)
        if link:
            self.turnipLink = link[0]
        else:
            link = re.findall(pattern, self.selftext)
            if link:
                self.turnipLink = link[0]
            else:
                link = re.findall(pattern, self.url)
                if link:
                    self.turnipLink = link[0]
                else:
                    self.turnipLink = "No Turnip Exchange link available."
        return self._turnipLink

    @turnipLink.setter
    def turnipLink(self, link):
        self._turnipLink = link


def get_date(created):
    return dt.datetime.fromtimestamp(created)


def beep():
    if os.name == 'nt':
        # Windows Machine
        frequency = 2500  # Set Frequency To 2500 Hertz
        duration = 250  # Set Duration To 250 ms == .25 second
        winsound.Beep(frequency, duration)
    elif os.name == 'posix':
        sys.stdout.write('\a')
        sys.stdout.flush()


def getReceiver():
    receiverInputEmail = input("\nWho should receive your email notifications?")
    while not receiverInputEmail:
        print('Invalid entry- email cannot be blank.')
        receiverInputEmail = input("Who should receive your email notifications?")
    return Receiver(receiverInputEmail)  # returns an object of type Receiver


def createSender():
    validPort = False
    validAddress = False
    pathlib.Path(FILE_LOCATION).mkdir(parents=True, exist_ok=True)
    smtpfile = pathlib.Path(SMTP_FILE)
    if smtpfile.exists():
        print("SMTP File Available. Would you like to import saved SMTP variables? Y/N:\t")
        use = input().lower()
        while use not in ['y', 'n']:
            print('Invalid entry.')
            print("SMTP File Available. Would you like to import saved SMTP variables? Y/N:\t")
            use = input().lower()
        if use == 'y':
            with open(smtpfile, 'r') as file:
                port = file.readline()
                if port:
                    print('SSL Port:' + port)
                    validPort = True
                else:
                    port = None
                    print("SSL Port unavaiable.")
                address = file.readline()
                if address:
                    print('SMTP Address:' + address)
                    validAddress = True
                else:
                    address = None
                    print("SMTP Address unavailable.")
            sender = Sender(port=port, address=address)
        else:
            sender = Sender()
    else:
        print("SMTP File unavailable. Please enter SMTP variables for email functionality.")
        sender = Sender()
    if validPort and validAddress:
        sender.hasSMTPFile = True
    return sender


def addApiDetails(senderObj):
    def addIt(sendObj):
        sendObj.personalUseScript = input("Enter API Personal Use Script:")
        sendObj.apiSecret = input("Enter API Secret:")
        sendObj.apiUser = input("Enter API User:")
        sendObj.apiPw = input("Enter API PW:")
        sendObj.apiApp = input("Enter API App:")
        apiUsesSubreddit = input("Enter API Subreddit, or press ENTER to use Default (ACNHTurnips)")
        if apiUsesSubreddit:
            sendObj.apiSubreddit = apiUsesSubreddit
        else:
            sendObj.apiSubreddit = 'ACNHTurnips'

    apiFile = pathlib.Path(API_FILE)
    if apiFile.exists():
        senderObj.hasAPIFile = True
        print("Reddit API File Available. Would you like to import saved API variables? Y/N:\t")
        use = input().lower()
        while use not in ['y', 'n']:
            print('Invalid entry.')
            print("Reddit API File Available. Would you like to import saved API variables? Y/N:\t")
            use = input().lower()
        if use == 'y':
            with open(apiFile, 'r') as file:
                apiPersonalUseScript = file.readline().rstrip('\n')
                if apiPersonalUseScript:
                    print('Personal Use Script:' + apiPersonalUseScript)
                    senderObj.personalUseScript = apiPersonalUseScript
                else:
                    print("Personal Use Script Unavailable.")
                    senderObj.hasAPIFile = False
                    senderObj.personalUseScript = input("Enter API Personal Use Script:")

                apiSecret = file.readline().rstrip('\n')
                if apiSecret:
                    print('Secret:' + apiSecret)
                    senderObj.apiSecret = apiSecret
                else:
                    senderObj.hasAPIFile = False
                    print("Secret unavailable.")
                    senderObj.apiSecret = input("Enter API Secret:")

                apiUser = file.readline().rstrip('\n')
                if apiUser:
                    print('User:' + apiUser)
                    senderObj.apiUser = apiUser
                else:
                    senderObj.hasAPIFile = False
                    print("User unavailable.")
                    senderObj.apiUser = input("Enter API User:")

                apiPw = file.readline().rstrip('\n')
                if apiPw:
                    print('PW:' + apiPw)
                    senderObj.apiPw = apiPw
                else:
                    senderObj.hasAPIFile = False
                    print("PW Unavailable.")
                    senderObj.apiPw = input("Enter API PW:")

                apiApp = file.readline().rstrip('\n')
                if apiApp:
                    print('App:' + apiApp)
                    senderObj.apiApp = apiApp
                else:
                    senderObj.hasAPIFile = False
                    print("App unavailable.")
                    senderObj.apiApp = input("Enter API App:")

                apiSubreddit = file.readline().rstrip('\n')
                if apiSubreddit:
                    print("Subreddit:" + apiSubreddit)
                    senderObj.apiSubreddit = apiSubreddit
                else:
                    senderObj.hasAPIFile = False
                    print("Subreddit Unavailable")
                    apiSubreddit = input("Enter API Subreddit, or press ENTER to use Default (ACNHTurnips)")
                    if apiSubreddit:
                        senderObj.apiSubreddit = apiSubreddit
                    else:
                        senderObj.apiSubreddit = 'ACNHTurnips'
        else:
            addIt(senderObj)
    else:
        print("API File unavailable. Please enter API variables for email functionality.")
        addIt(senderObj)


def saveSMTPFile(senderObject):
    save = input("Would you like to save these SMTP variables for later use? Enter Y or N:\t")
    while save.lower() not in ['y', 'n']:
        print('Invalid entry.')
        save = input("Would you like to save these SMTP variables for later use? Enter Y or N:\t")
    if save == 'y':
        with open(SMTP_FILE, 'w') as file:
            file.write(str(senderObject.sslPort))
            file.write('\n')
            file.write(str(senderObject.smtpAddress))
        print('File saved.')
    else:
        print('Variables not saved. You will need to enter SMTP variables next runtime.')


def saveApiFile(senderObject):
    save = input("Would you like to save these API variables for later use? Enter Y or N:\t")
    while save.lower() not in ['y', 'n']:
        print('Invalid entry.')
        save = input("Would you like to save these API variables for later use? Enter Y or N:\t")
    if save == 'y':
        with open(API_FILE, 'w') as file:
            file.write(str(senderObject.personalUseScript))
            file.write('\n')
            file.write(str(senderObject.apiSecret))
            file.write('\n')
            file.write(str(senderObject.apiUser))
            file.write('\n')
            file.write(str(senderObject.apiPw))
            file.write('\n')
            file.write(str(senderObject.apiApp))
            file.write('\n')
            file.write(str(senderObject.apiSubreddit))
        print('File saved.')
    else:
        print('Variables not saved. You will need to enter API variables next runtime.')


def main():
    sender = createSender()
    sender.validateCredentials()
    if not sender.hasSMTPFile:
        saveSMTPFile(sender)
    addApiDetails(sender)
    if not sender.hasAPIFile:
        saveApiFile(sender)

    receiver = getReceiver()

    reddit = praw.Reddit(client_id=sender.personalUseScript,
                         client_secret=sender.apiSecret,
                         user_agent=sender.apiApp,
                         username=sender.apiUser,
                         password=sender.apiPw)

    subreddit = reddit.subreddit(sender.apiSubreddit)

    modes = {'b': 'BUYER', 's': 'SELLER'}
    mode = input("\nAre you looking to buy or sell? Press B to buy or S to sell, then ENTER to continue:\t").lower()
    while mode not in modes.keys():
        print("Invalid entry. Press B to buy or S to sell, then ENTER to continue:\t")
        mode = input().lower()
    sender.status = modes[mode]

    # parse loop
    firstCheck = True
    if sender.status == 'SELLER':
        receiver.name = input("\nWhat is your in-game name?")
        sender.minOrMax = 'minimum'
        tmp = 'sell'
        sender.searchFor = 'nook'
    else:
        tmp = 'buy'
        sender.minOrMax = 'maximum'
        sender.searchFor = 'daisy'
    sender.limit = int(input(f'\nFinally, what is the {sender.minOrMax} amount you\'d like to {tmp} for?'))
    try:
        postList = []
        startTime = time.time()
        while True:
            new = False
            for submission in subreddit.new(limit=5):
                if sender.searchFor in submission.title.lower():
                    postWorth = int(re.findall('[0-9]+', submission.title)[0])
                    if submission.id not in postList:
                        postList.append(submission.id)
                        if (sender.status == 'SELLER' and postWorth > sender.limit) \
                                or (sender.status == 'BUYER' and postWorth < sender.limit):
                            post = Post(submission.id,
                                        submission.title,
                                        submission.url,
                                        submission.permalink,
                                        submission.selftext,
                                        submission.created)
                            new = True
                            if not firstCheck:
                                try:
                                    print(f"\n\n\nCreated: {post.created}\tTitle: {post.title}\t\t\t\t\t\t\t"
                                          f"ID: {post.id}\t"
                                          f"URL:{post.url}"
                                          f"\n\nPermalink: www.reddit.com/{post.permalink}")
                                    print("\n" + post.turnipLink + "\n")
                                    startTime = time.time()
                                    beep()
                                    sender.sendMail(receiver, post)
                                except smtplib.SMTPDataError:
                                    time.sleep(15)
                                    startTime = time.time()
                                    sender.sendMail(receiver, post)
            if firstCheck:
                print("\nParser initialized.\n")
                firstCheck = False
                startTime = time.time()

            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if not new:
                if time.time() - startTime >= 30:
                    print('Nothing new as of ' + current_time)
                    startTime = time.time()
            time.sleep(5)
    except KeyboardInterrupt:
        print("Exiting.")
        return


if __name__ == '__main__':
    main()
