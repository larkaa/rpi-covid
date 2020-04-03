#!/usr/bin/python
# -*- coding:utf-8 -*-
import time
import sys
from PIL import Image,ImageDraw,ImageFont
import PIL
import epd2in7b, epdconfig
from bs4 import BeautifulSoup
import requests
import re


def eink_img(text1,text2):
    EPD_WIDTH       = 176
    EPD_HEIGHT      = 264

    epd = epd2in7b.EPD()
    epd.init()
    print("Clear...")
    epd.Clear(0xFF)
    

    HBlackimage = Image.new('1', (EPD_HEIGHT, EPD_WIDTH), 255)  
    img = Image.open('covid.png').transpose(PIL.Image.FLIP_LEFT_RIGHT)
    imgmask = img.copy()
    
    HRedimage = Image.new('1', (EPD_HEIGHT, EPD_WIDTH), 255)  # 298*126
    font1 = ImageFont.truetype('Candy Beans.otf', 14)

    offset = (105,10)
    HRedimage.paste(img, offset, imgmask)
    
    drawblack = ImageDraw.Draw(HBlackimage)
    #drawred = ImageDraw.Draw(HRedimage)
    drawblack.text((2,10), text1, font=font1)
    drawblack.text((2,105), text2, font=font1)
    
    
    epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRedimage))
    #HRedimage.save('test1.jpg')
    #HBlackimage.save('test2.jpg')
    
def time_get(url):
    print("[!] Getting response from URL")
    startTime = time.time()
    res = requests.get(url)

    print("[!] Time taken to retrieve response", round((time.time() - startTime), 2))
    return res

def search_divs(soup, class_name, pattern, findall=False):
    mydivs = soup.findAll("div",{"class":class_name})
    res = []
    for el in mydivs:
        test = re.findall(pattern, el.text.strip())
        if test:
            if not findall:
                return list(test[0])
            res.append(test[0])
    return res

# below function largely inspired from https://github.com/julianbruegger/corona-display
def getStats(country):
    url = "https://www.worldometers.info/coronavirus/country/{}/".format(country)
    url2 = "https://www.worldometers.info/coronavirus/"
 
    # Get response from first URL which contains country stats
    response = time_get(url)
 
    # Get response from second URL which contains worldwide stats
    response2 = time_get(url2)
 
    # Use BeautifulSoup library to parse the URLs we just retrieved
    soup = BeautifulSoup(response.text, "html.parser")
    soup2 = BeautifulSoup(response2.text, "html.parser")
    
    # Create empty arrays for stats
    stats = []
    stats_world = []
    
    # Search div statements for certain parts that contain the data
    stats.extend(search_divs(soup, "maincounter-number", '\d+(?:,\d+)?',findall=True))
    stats.extend(search_divs(soup, "news_body", '(\d+) new cases and (\d+) new deaths'))
    
    # do same for world stats
    stats_world.extend(search_divs(soup2, "maincounter-number", '\d+,\d+(?:,\d+)?',findall=True))
    
    # need a better way to extract world stats changes
    #stats_world.extend(search_divs(soup2, "news_body", '(\d+) new cases and (\d+) new deaths'))
    
    #total cases, total deaths, total recovered, new cases, new deaths
    str1 = "Cases in {}\nInfections: {} (+{})\nTotal Deaths: {} (+{})".format(
                    country, stats[0], stats[3], stats[1], stats[4])
    str2 = "Worldwide\nInfections: {} \nTotal Deaths: {} ".format(
                    stats_world[0], stats_world[1])
    #return stats, stats_world
    return(str1,str2)
    
def getStats2(country):

    url_c = "https://corona.help/country/{}".format(country)
    url_w ="https://corona.help/"
    
    page_c = requests.get(url_c)
    soup_c = BeautifulSoup(page_c.text, 'html.parser')
    page_w = requests.get(url_w)
    soup_w = BeautifulSoup(page_w.text, 'html.parser')
    
    country2 = soup_c.select('h2')[0].text.strip()
    infections_c = soup_c.select('h2')[1].text.strip()
    deaths_c = soup_c.select('h2')[2].text.strip()
    survived_c = soup_c.select('h2')[3].text.strip()
    today_c = soup_c.select('h2')[4].text.strip()
    deaths_t = soup_c.select('h2')[5].text.strip()
    
    first, last = country2.split()
       
    infections_w = soup_w.select('h2')[1].text.strip()
    deaths_w = soup_w.select('h2')[2].text.strip()
    survived_w = soup_w.select('h2')[3].text.strip()
    today_w = soup_w.select('h2')[4].text.strip()
    deaths_t_w = soup_w.select('h2')[5].text.strip()

    str1 = "Cases in {}\nInfections: {}\nDeaths: {} /Total: {}".format(
                    first, infections_c, deaths_t, deaths_c)
    str2 = "Worldwide\nInfections: {}\nDeaths: {} /Total {}".format(
                    infections_w, deaths_t_w, deaths_w)
    print(str1)
    print(str2)
    return(str1,str2)


def main():
    country = 'France'
    a,b = getStats(country)
    #a,b=getStats2(country)
    #print(a)
    #print(b)
    
    print(a)
    print(b)
    eink_img(a,b)
    
    
if __name__ == "__main__":
    main()
    
