# Author: Harish
# Name: GMaps Scrapper
# Version: 2.0
# Description: Scraps data(name, category, address, geocode and contact) from google maps

from splinter import Browser
from easygui import *
from sys import exit
from time import sleep
from re import sub
from os import path, makedirs

# Recursive function that does the actual scrapping
# @type flag: bool
# @rtype: None


def scrapper_recursion(flag):
    if chrome.is_element_present_by_xpath(
            "//div[contains(@class,'cards-categorical-list-scrollbox jfk-scrollbar jfk-scrollbar-borderless')]"):
        for each_div in chrome.find_by_xpath(
                "//div[contains(@jsaction, "
                "'mousemove:categorical.hoverListItem;mouseout:categorical.unhoverListItem;"
                "focus:categorical.hoverListItem;blur:categorical.unhoverListItem')]"):
            # noinspection PyBroadException
            try:
                each_div.click()
                sleep(2)
                name = chrome.find_by_xpath(
                    "//h1[contains(@class, 'cards-entity-title cards-strong cards-text-truncate-and-wrap')]").text
                print name
                address = " ".join(
                    chrome.find_by_xpath("//div[contains(@class, 'cards-entity-address cards-strong')]").text.split(
                        "\n"))
                phone_no = chrome.find_by_xpath("//div[contains(@class, 'cards-entity-phone')]").text
                category = chrome.find_by_xpath("//span[contains(@class, 'cards-social-termlink')]").last.text
                geocode_url = chrome.url.split("@")
                geocode_arr = geocode_url[1].split(",")
                lat = geocode_arr[0]
                lng = geocode_arr[1]
                file_handler.write(name.strip().encode("UTF-8") + "\t" + category.strip().encode(
                    "UTF-8") + "\t" + address.strip().encode("UTF-8") + "\t" + str(lat) + "\t" + str(
                    lng) + "\t" + phone_no.strip().encode("UTF-8") + "\n")
                chrome.find_by_xpath("//div[contains(@class, 'cards-categorical-list-context-card')]").click()
                sleep(2)
            except:
                continue

        if chrome.is_element_present_by_xpath(
                '//a[@class="cards-categorical-pagination-button cards-categorical-pagination-button-inactive"]') \
                and flag:
            print "Successfully Scrapped All Available Data!"
            file_handler.close()
        else:
            # noinspection PyBroadException
            try:
                chrome.find_by_xpath("//span[contains(@class,'cards-categorical-pagination-button-right')]").click()
                sleep(5)
                while 1:
                    if chrome.is_element_present_by_xpath(
                            "//button[contains(@class, "
                            "'widget-zoom-button widget-zoom-in widget-zoom-button-disabled')]"):
                        break
                    chrome.find_by_xpath("//button[contains(@class, 'widget-zoom-button widget-zoom-in')]").click()
                chrome.find_by_id("searchboxinput").mouse_over()
                sleep(2)
                scrapper_recursion(True)
            except:
                print "Successfully Scrapped All Available Data!"
                file_handler.close()
    else:
        print "No data Available"
        file_handler.close()

# GUI creation
msg = "Enter required * information"
title = "BI GMaps Scrapper"
fieldNames = ["Folder Name * (Enter City Name)",
              "Lifestyle Indicator Name *",
              "Places * (Separate each place with a ('$') dollar)"]
fieldValues = multenterbox(msg, title, fieldNames)
while 1:  # make sure that none of the fields was left blank
    if fieldValues is None:
        break
    errmsg = ""
    for i in range(len(fieldNames)):
        if fieldValues[i].strip() == "":
            errmsg += '"%s" is a required field.\n\n' % fieldNames[i]
    if errmsg == "":  # if no problems found
        break
    fieldValues = multenterbox(errmsg, title, fieldNames, fieldValues)

if fieldValues is None:
    exit(0)

# Processing input and sending it to the scrapper function
folder_name = "XLS\\" + fieldValues[0].lower()
lifestyle_indicator = sub(r"\s+", '+', fieldValues[1].lower())
places = fieldValues[2]
print "Connecting To Google Maps..."
places_arr = places.split("$")
chrome = Browser("chrome")
for place in places_arr:
    place = sub(r"\s+", '+', place)
    chrome.visit("https://www.google.co.in/maps/search/" + lifestyle_indicator.strip() + "+in+" + place.strip() +
                 "/@13.0318799,80.1985061,21z")
    sleep(5)
    if not path.exists(folder_name):
        makedirs(folder_name)
    if not path.exists(folder_name + "/" + lifestyle_indicator):
        makedirs(folder_name + "/" + lifestyle_indicator)
    file_handler = open(folder_name + "/" + lifestyle_indicator + "/" + place.strip() + "_" +
                        lifestyle_indicator.strip() + ".xls", "w")
    file_handler.write("Name\tCategory\tAddress\tLatitude\tLongitude\tContact\n")
    scrapper_recursion(False)

print "Disconnecting Google Maps..."
chrome.quit()
