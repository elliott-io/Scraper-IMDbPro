# Copyright 2019, J. Elliott Staffer, All Rights Reserved
# Version 1.0.9 - Mac

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By

import csv
import os
import time
from datetime import datetime
    

USERNAME = "jadebrandais@gmail.com"
PASSWORD = "ekQ-bZr-b0z-Mzy"

# login with IMBd credentials
login_url = 'https://pro.imdb.com/login/imdb?u=%2F'
# url to navigate to after login
# search_url = 'https://pro.imdb.com/people?ref_=search_nv_ppl_tsm#starMeter=50000-100000,100000-&sort=ranking' # +50k starmeter
# search_url = 'https://pro.imdb.com/people?ref_=search_nv_ppl_tsm#age=20-34&starMeter=50000-100000,100000-&sort=ranking' # +50k starmeter and 20-34 age range (young adult)
# search_url = 'https://pro.imdb.com/people?ref_=search_nv_ppl_tsm#age=20-34&media=has_primary_image&starMeter=257000-&sort=ranking' # +257k starmeter and 20-34 age range (young adult) and has headshot
# search_url = 'https://pro.imdb.com/people?ref_=search_nv_ppl_tsm#age=20-34&starMeter=257000-&sort=ranking' # +257k starmeter and 20-34 age range (young adult) and has headshot
# search_url = 'https://pro.imdb.com/people?ref_=hm_nv_ppl_tsm#age=20-34&starMeter=20000-50000&media=has_primary_image&sort=ranking' # +10k-50k starmeter and 20-34 age range (young adult) and has headshot
search_url = 'https://pro.imdb.com/people?ref_=hm_nv_ppl_tsm#sort=ranking'

def main():

    # mv chrome driver from Downloads to Applications 
    chromedriver = "/applications/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver

    
    driver = webdriver.Chrome(chromedriver)
    driver.get(login_url)

    username_form = driver.find_element_by_id("ap_email")
    username_form.send_keys(USERNAME)

    password_form=driver.find_element_by_id('ap_password')
    password_form.send_keys(PASSWORD)

    password_form.send_keys(Keys.RETURN)
    ### login completed
    
    # allow time to type in captcha if needed - wait up to 1 minute for user to handle captcha
    WebDriverWait(driver, 60).until(EC.invisibility_of_element((By.ID, 'browser-block__modal')))
    # i = 0
    # interval = 3 # seconds
    # while len(driver.find_elements_by_id('browser-block__modal')) > 0:
    #     i += interval
    #     time.sleep(interval)
    #     print("captcha present, waited for user for {} seconds...".format(i))
    print('captcha removed from DOM')
    
    driver.get(search_url)

    # wait for results list to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="results"]/ul/li/a')))

    # there are about 25 profiles per page, change i_thousand to select how many thousand profiles to process (approximately)
    # 40 scrolls = ~1000 profiles loaded into results infinite scroll
    # IMDb only allows you to load to 'page=399' and each scroll counts as a page, as can be seen in their url which changes after each scroll
    print('url before scroll: ', driver.current_url)
    for i in range(0,405):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        print("scrolled: ", i + 1)

    print('url after scroll: ', driver.current_url)

    #resultList = driver.find_element_by_id("results")
    items = driver.find_elements_by_xpath('//*[@id="results"]/ul/li/a')
    print('number of profiles to process: ', len(items))

    # print links for debug logging
    # for link in items:
    #     print(link.text)
    #     print(link.get_attribute("href"))

    #create file name
    now = datetime.now() # current date and time
    start_time = now.strftime("%Y-%m-%d-t-%H-%M-%S")

    direct_contacts_found_count = 0

    # make output folder if not existing
    folder = 'output'
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    # create csv to write to
    f = open('{0}/{1}.IMDbProfiles.{2}.csv'.format(folder, len(items), start_time), 'w', newline='')
    csvWriter = csv.writer(f, dialect='excel')
    #csvWriter = csv.writer(open('test.csv', 'w', newline=''), delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    # csvWriter.writerow(['full_name', 'first_name', 'last_name', 'starMeter', 'direct_contact', 'professions', 'link_imdb_pro', 'link_imdb', 'link_img', 'source_summary', 'source_contacts', 'source_filmography', 'source_about', 'source_images', 'source_starMeter_graph'])
    csvWriter.writerow(['full_name', 'first_name', 'last_name', 'starMeter', 'direct_contact', 'professions', 'link_imdb_pro', 'link_imdb', 'link_img', 'source_summary', 'source_contacts'])

    print("==================")
    # iterate through items
    for link in items: #pageLinks:
        #print name and link
        #print(link.text)
        print('link for user tab: ', link.get_attribute("href"))
        # Open a new window
        driver.execute_script("window.open('" + link.get_attribute("href") + "');")
        # Switch to the new window and open URL B
        driver.switch_to.window(driver.window_handles[1])
        # wait until left column loads - left column holds Contacts
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="tabs_row"]/div/div/div/div/div[1]')))
        
        # get full name
        # get name header element
        full_name = driver.find_element_by_xpath('//*[@id="name_heading"]/div/div/div[2]/div[1]/h1/span').text
        name_array = full_name.split()
        print('full_name: ', full_name)
        first_name = name_array[0].strip()
        last_name = "unknown"
        names_count = len(name_array)
        if names_count == 2:
            last_name = name_array[-1].strip()
        elif names_count > 2:
            # -1 to account for zero-based index of array
            for i in range(names_count - 1, 0, -1):
                if not name_array[i].strip().startswith('('):
                    last_name = name_array[i].strip()
                    break
                else:
                    continue
        print("first_name: ", first_name)
        print("last_name: ", last_name)
        
        # get professions
        professions = 'not checked'
        try:
            professions = driver.find_element_by_xpath('//*[@id="name_heading"]/div/div/div[2]/div[2]').text
        except:
            professions = 'na'
        print('professions: ', professions)
        
        # get starMeter
        starMeter = ''
        try:
            starMeter = driver.find_element_by_xpath('//*[@id="popularity_widget"]/div[2]/div/div/div[1]/div[2]/div/div[2]/span/span/a').text
        except:
            starMeter = 'not found'
        print('starMeter: ', starMeter)
            

        # get direct contact
        direct_contact_value = "not checked"
        try:
            direct_contact_section_header = "not checked"
            direct_contact_section = ""
            try:                                                       
                direct_contact_section = driver.find_element_by_xpath('//*[@id="contacts"]/div[1]/div[1]/div/span')
            except:
                direct_contact_section = "unknown"
                direct_contact_value = "na"            
            try:
                direct_contact_section_header = direct_contact_section.text
            except:
                direct_contact_section_header = "unknown"
                direct_contact_value = "na"
            print("direct_contact_section_header: ", direct_contact_section_header)

            if direct_contact_section_header == "Direct Contact":
                try:
                    direct_contact__parent_div = driver.find_element_by_xpath('//*[@id="contacts"]/div[1]')
                    direct_contact_items = direct_contact__parent_div.find_elements_by_tag_name('a')
                    if len(direct_contact_items) == 0:
                        direct_contact_value = "na"
                    else:
                        for item in direct_contact_items:
                            item_href = item.get_attribute("href")
                            if item_href.startswith("mailto:") and "@" in item_href:
                                direct_contact_value = item.text
                                break
                            else:
                                direct_contact_value = "na"
                                continue
                except:
                    direct_contact_value = "na"
            else:
                direct_contact_value = "na"
            print("direct_contact_value: ", direct_contact_value)
            if direct_contact_value != "na":
                direct_contacts_found_count += 1
            
            #####
            # location of "birthday" data varies, this code is not complete
            #get source code for name_heading element and all children
            # name_heading = driver.find_element_by_id("name_heading")            
            # source_heading = name_heading.get_attribute("outerHTML")
            # birthday = ""
            # try:
            #     birthday = driver.find_element_by_xpath('//*[@id="const_page_summary_section"]/div[3]/div/div[2]/span').text
            # except:
            #     birthday = "unknown"
            #####
        except: 
            print("direct contact not found")

        # get contacts source
        source_contacts = ""
        try:
            contacts = driver.find_element_by_id("contacts")
            #get source code for contacts element and all children
            source_contacts = contacts.get_attribute("outerHTML")
        except:
            source_contacts = 'not found'
            print("no contacts section")
        
        # get imdb profile link
        link_imdb_pro = driver.current_url
        link_imdb = link_imdb_pro
        if '?ref_' in link_imdb_pro: 
            link_imdb = link_imdb_pro.split('?ref_')[0]
            link_imdb_pro = link_imdb
        if 'https://pro.' in link_imdb:
            link_imdb = link_imdb.replace('https://pro.', 'https://')
        print('link_imdb_pro: ', link_imdb_pro)
        print('link_imdb: ', link_imdb)

        # get thumbnail image link
        link_img = "not checked"
        try:
            img = driver.find_element_by_class_name('primary_image_highlight')
            link_img = img.get_attribute('src')
        except:
            link_img = "na"
        print('link_img', link_img)

        # get summary source
        source_summary = ""
        try:
            summary_section = driver.find_element_by_xpath('//*[@id="const_page_summary_section"]')
            # summary_section_items = summary_section.find_elements_by_tag_name('div')
            source_summary = summary_section.get_attribute("outerHTML")
            # print(source_summary)
        except:
            source_summary = 'not found'
            print("no summary section found")

        # # get filmography source
        # source_filmography = ''
        # try:
        #     filmography_section = driver.find_element_by_xpath('//*[@id="const_tabs"]/div[1]')
        #     source_filmography = filmography_section.get_attribute("outerHTML")
        #     # print(source_filmography)
        # except:
        #     source_filmography = 'not found'
        #     print("no filmography section found")

        # # get starMeter graph source
        # source_starMeter_graph = ''
        # try:
        #     starMeter_graph_section = driver.find_element_by_xpath('//*[@id="meters_row"]/div/div/div[1]/div/div[1]')
        #     source_starMeter_graph = starMeter_graph_section.get_attribute("outerHTML")
        #     # print(source_starMeter_graph)
        # except:
        #     source_starMeter_graph = 'not found'
        #     print("no filmography section found")
        
        # # move to About tab
        # driver.get(link_imdb_pro + 'about')               
        # # wait for about box contents to load
        # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="const_tabs"]/div[2]')))
        # source_about = ''
        # try:
        #     about_section = driver.find_element_by_xpath('//*[@id="const_tabs"]/div[2]')
        #     # summary_section_items = summary_section.find_elements_by_tag_name('div')
        #     source_about = about_section.get_attribute("outerHTML")
        #     # print(source_about)
        # except:
        #     source_about = 'not found'
        #     print("no about section found")

        # # move to Images tab
        # driver.get(link_imdb_pro + 'images')               
        # # wait for about box contents to load
        # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="const_tabs"]/div[3]')))
        # # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="photo_set"]')))
        
        # source_images = ''
        # try:
        #     images_section = driver.find_element_by_xpath('//*[@id="const_tabs"]/div[3]')
        #     # summary_section_items = summary_section.find_elements_by_tag_name('div')
        #     source_images = images_section.get_attribute("outerHTML")
        #     # print(source_images)
        # except:
        #     source_images = 'not found'
        #     print("no images section found")

        # write to csv
        # csvWriter.writerow([full_name, first_name, last_name, starMeter, direct_contact_value, professions, link_imdb_pro, link_imdb, link_img, source_summary, source_contacts, source_filmography, source_about, source_images, source_starMeter_graph])
        csvWriter.writerow([full_name, first_name, last_name, starMeter, direct_contact_value, professions, link_imdb_pro, link_imdb, link_img, source_summary, source_contacts])
        # Close the tab with URL B
        driver.close()
        print('user tab closed...')
        # Switch back to the first tab with search results
        driver.switch_to.window(driver.window_handles[0])
        print("***##################")
        print("Completed ", items.index(link) + 1) # +1 for zero-based index of array
        print("of ", len(items))
        print("Direct contacts found count: ", direct_contacts_found_count)
        print("***##################")
        # continue
        # for debug testing to limit items
        # if items.index(link) == 3:
        #     break
        # else:
        #     continue 

    f.close()
    driver.close()
    print("ending...")
    print("start time: ", start_time)
    end_now = datetime.now() # ending date and time
    end_time = end_now.strftime("%Y-%m-%d-t-%H-%M-%S")
    print("end time: ", end_time)

if __name__ == '__main__':
    main()