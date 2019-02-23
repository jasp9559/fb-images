import random
from decimal import Decimal
from time import sleep
from glob import glob
from datetime import datetime
from shutil import move
from os import getcwd, makedirs
from os.path import expanduser, getctime
from selenium import webdriver
import pandas as pd
import imageio

SLEEP_INTERVAL = 0.1
first_img_download_name = None
count = 0

# Open browser
driver = webdriver.Chrome("../chromedriver")
driver.get('https://facebook.com/login')

# Log in
login, password = pd.read_csv('../login.csv').values[0]
async_send_keys('input[@id="email"]', login)
async_send_keys('input[@id="pass"]', password)
async_click('button[@id="loginbutton"]')

# Click on profile and get username
async_click('a[@title="Profile"]/span')
url = driver.current_url
username = url[url.find('.com/') + 5:]

# Hide window
driver.minimize_window()

# Go to photos
async_click('a[contains(text(), "Photos")]')

# Click on first image
xpath('div[@class="tagWrapper"]').click()

# Make directory and store album xpath for future reference
makedirs('../Photos of You')

while True:
    sleep(0.5)
    img_link = xpath('img[@class="spotlight"]').get_attribute('src')
    img = imageio.imread(img_link)

    if first_img is None:
        first_img = img_link
        # Make sure that we're not re-downloading the first image in the album
    elif first_img == last_download:
        print('Download complete')
        driver.close()
        sleep(15)
        break
    # Continue with main loop
    else:
        count +=1
        filename = rename_img(count)
        imageio.imwrite(filename, img)

        # Go to next image
        async_click('a[@title="Next"]')


# Functions
def xpath(path):
    return driver.find_element_by_xpath('//' + path)

def async_send_keys(path, val, x=0):
    if x > 600:
        return 'Failed after 60 seconds.  Aborting early.'
    else:
        try:
            xpath(path).send_keys(val)
        except:
            sleep(SLEEP_INTERVAL)
            return async_send_keys(path, val, x+1)

def async_click(path, x=0):
    if x > 600:
        return 'Failed after 60 seconds.  Aborting early.'
    else:
        try:
            xpath(path).click()
        except:
            sleep(SLEEP_INTERVAL)
            return async_click(path, x+1)

def rename_img(i):
    date = xpath('span[@id="fbPhotoSnowliftTimestamp"]/a/abbr').get_attribute('title')
    # Shorten string from `Monday, Januaray 31, 2018 at 5:15pm`to `January 31, 2018`
    date = date[date.find(', ')+2: date.find(' at')]
    # Add 0 to the date string if it's a single-digit # day
    date_10_digit = date.find(', 20') - 2
    if date_10_digit == ' ':
        date = date[:day_10_digit+1] + '0' + date[day_10_digit+1:]
    # long string => datetime => short string
    file_date = datetime.strftime(datetime.strptime(date, '%B %d, %Y'), '%Y-%m-%d')
    # Add image numbering convention from 0001 to 9999
    file_num = '0' * (4-len(str(i))) + str(count)
    filename = '../Photos of You/' + file_date + '-' + file_num + '.jpg'
    return filename
