import os
from time import sleep
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import FirefoxProfile
from selenium.webdriver.support.select import Select

DOWNLOAD_DIR = os.path.join(os.sep, str(Path.home()), 'Downloads', 'Selenium')
if not os.path.exists(DOWNLOAD_DIR):
    os.mkdir(DOWNLOAD_DIR)


class RomDriver:

    def __init__(self):
        profile = FirefoxProfile()

        # Set Download Location
        profile.set_preference('browser.download.dir', DOWNLOAD_DIR)
        profile.set_preference('browser.download.folderList', 2)

        # Do not show the download dialog box
        profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/zip')
        #profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/x-7z-compressed')

        self.driver = webdriver.Firefox(profile)

    def close(self):
        self.driver.close()

    def navigate_to(self, url, sleep_time=1):
        self.driver.get(url)
        sleep(sleep_time)

    def find_element(self, css_selector):
        return self.driver.find_element_by_css_selector(css_selector)

    def select_combo_box_option(self, css_selector, option, sleep_time=1):
        elem = self.find_element(css_selector)
        Select(elem).select_by_visible_text(option)
        sleep(sleep_time)

    def click_element(self, css_selector, sleep_time=1):
        self.find_element(css_selector).click()
        sleep(sleep_time)

    def click_link_by_text(self, text):
        self.driver.find_element_by_link_text(text).click()

    def click_next_by_title(self, top_level_selector, title, sleep_time=1):
        top_level = self.find_element(top_level_selector)
        next_links = top_level.find_elements_by_tag_name('a')

        for nl in next_links:
            link_title = nl.get_attribute('title')
            if link_title == title:
                nl.click()
                sleep(sleep_time)
                return

    def find_rom_links(self, table_css_selector):
        table = self.find_element(table_css_selector)
        links = table.find_elements_by_tag_name('a')

        hrefs = []

        for l in links:
            hrefs.append({'title': l.get_attribute('text'), 'href': l.get_attribute('href')})

        return hrefs

    def href_by_link_text(self, text):
        elem = self.driver.find_element_by_link_text(text)
        return elem.get_attribute('href')

    def get_element_text(self, css_selector) -> str:
        elem = self.driver.find_element_by_css_selector(css_selector)
        return elem.text

    def get_text_from_selectors(self, selectors: list) -> str:
        for css_selector in selectors:
            try:
                return self.get_element_text(css_selector)
            except NoSuchElementException:
                pass

    def go_back(self):
        self.driver.back()


if __name__ == '__main__':
    rd = RomDriver()
    rd.navigate_to('https://romsmania.cc/roms/nintendo')
    sleep(1)

    rd.select_combo_box_option('div.select:nth-child(3) > select:nth-child(1)', 'USA')
    sleep(1)

    rd.find_rom_links('.table > tbody:nth-child(2)')
    sleep(1)

    rd.click_element('li.pagination__el:nth-child(7) > a:nth-child(1) > span:nth-child(1)')

    for i in range(1, 10):
        rd.click_next_by_title('.pagination__list', 'Next page')

    sleep(5)
    rd.close()
