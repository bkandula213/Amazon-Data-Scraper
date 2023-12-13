from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import os
import json

## ====================================================
## Chrome Config ## 

CHROME_LOCATION = os.getenv("chrome-win64/")

# uBlock origin setup (Ad-Blocker) -----------------------

options = webdriver.ChromeOptions()
ublock_path = os.path.abspath("public/vendors/Ublock-Origin.crx")
options.add_extension(ublock_path)


## Download Path Setup -----------------------------------

prefs = {"download.default_directory" : r"C:\test\laz\Scrapping\random\i"}
options.add_experimental_option('prefs', prefs) 

##  --------------------------------------------------------

driver = webdriver.Chrome(options=options)

## Main Code =========================================

def scrape_data(product, key_part):
    driver = webdriver.Chrome()
    try:

        # Navigate to Amazon
        driver.get("https://www.amazon.com/")
        # search box
        driver.find_element(By.XPATH, "//input[@id='twotabsearchtextbox']").send_keys(
            {product}
        )
        ## click search button
        driver.find_element(By.XPATH, "//input[@id='nav-search-submit-button']").click()

        ## Multiple items info, single item: name, price and more link #
        word = key_part
        
        item_blocks = driver.find_elements(
            By.XPATH,
            # "//text()[contains(., 'Results')]/following::div[@data-index]//text()[contains(., 'WF-1000XM4')]/ancestor-or-self::div[5]"
            
            f"//text()[contains(., 'Results')]/following::div[@data-index]//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{word.lower()}')]/ancestor-or-self::div[5]"
        )

        ## To calculate length of xpaths returned #
        blocks_count = len(item_blocks)

        ## All Data #
        data = []
        
        for item in item_blocks:
            try:
                item_name = item.find_element(
                    By.XPATH, f".//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{word.lower()}')]/parent::node()"
                ).text
                item_price = item.find_element(
                    By.XPATH, './/descendant::span[@class="a-price-whole"][1]'
                ).text
                
                item_link = item.find_element(
                    By.XPATH, f".//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{word.lower()}')]/ancestor-or-self::a[1][@href]"
                ).get_attribute("href")
                # print("=================================================================")
                # print("item_name: ", item_name)
                # print('item_price: ', item_price + ".99")
                # print("item_link: ", item_link)
                # print("=================================================================")
                data.append({
                    'item_name': item_name,
                    'item_price': item_price,
                    'item_link': item_link
                })
            except NoSuchElementException:
                print("One element not found! skipping to next one!")
                continue
            
        # print(data)

        i=0
        while i < len(data):
            # print(data[i]['item_name'])
            item_link = data[i]['item_link']
            try:
                driver.get(item_link)
                item_reviews = driver.find_elements(By.XPATH, '//*[@data-hook="review"]')
                reviews = []
                for item_review in item_reviews:
                    ## customer name ##
                    customer_name = item_review.find_element(By.XPATH, './/descendant::*[@class="a-profile-name"]').text
                    
                    ## customer rating ##
                    c_r_HTML = item_review.find_element(By.XPATH, './/descendant::*[contains(@class, "a-icon a-icon-star")]//text()[contains(., "stars")]/parent::node()').get_attribute('outerHTML')
                    start_index = c_r_HTML.find('>') + 1
                    end_index = c_r_HTML.find('<', start_index)
                    customer_rating = c_r_HTML[start_index:end_index]
                    
                    # append customer
                    reviews.append({
                        'customer_name': customer_name,
                        'customer_rating': customer_rating
                    })
                    
                    
                data[i]['reviews'] = reviews
                print(data[i])
                    
            except NoSuchElementException:
                print("Review for one linsk for skipped")
                continue
            i=i+1

        json_file_path = 'output.json'

        with open(json_file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)    
            
        print(f'Data has been saved to {json_file_path}')
        driver.close()
        driver.quit()
        return data

    finally:
        driver.quit()

# scrape_data('cerave acne foaming cleanser', 'cerave')

# time.sleep(30000)
# driver.close()



## Testing Area #

    # origin product
    # "sony wf-1000xm4"

    ## this will get html, which prints #
    # item_price_html = item_price.get_attribute('outerHTML')
