from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import json
import codecs

base_url_kh = 'https://www.cambodiapost.post/page/postal-codes'
base_url_en = 'https://www.cambodiapost.post/en/page/postal-codes'
province_size = 25
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
chrome_driver = webdriver.Chrome(options=options)
all_data = []

for province_value in range(1, province_size + 1):
   district_names = {}
   districts = []
   communes = []
   city_param = '?city=' + str(province_value)
   scrape_url = base_url_kh + city_param
   chrome_driver.get(scrape_url)
   city_dropdown_menu = Select(chrome_driver.find_element_by_css_selector('select#city'))
   toggle_value = province_value + 1
   if toggle_value > province_size:
      toggle_value = province_value - 1
   city_dropdown_menu.select_by_value(str(toggle_value))
   city_dropdown_menu.select_by_value(str(province_value))
   # Get all district for this city
   district_dropdown_menu = chrome_driver.find_element_by_css_selector('select[name="district"]')
   district_values = []
   district_options = district_dropdown_menu.find_elements_by_css_selector('*')
   for option in district_options:
      value = option.get_attribute('value')
      district_values.append(value)
   # loop through district and get all communes for each district.
   button_search = chrome_driver.find_element_by_css_selector('form#form-post button[type="submit"]')
   for district_value in district_values:
      print('scrapping district id : ' + str(district_value))
      try:
         distict_param = '&district=' + str(district_value)
         district_dropdown_menu = chrome_driver.find_element_by_css_selector('select[name="district"]')
         Select(district_dropdown_menu).select_by_value(district_value)
         button_search = chrome_driver.find_element_by_css_selector('form#form-post button[type="submit"]')
         button_search.click()
         rows = chrome_driver.find_elements_by_css_selector('table tbody > tr')
         for row in rows:
            row_data = row.find_elements_by_css_selector('*')  # get all td element inside tr
            commune_data = {
               'en': row_data[1].text,
               'kh': row_data[0].text,
               'zipCode': row_data[2].text
            }
            communes.append(commune_data)
         # get district name both en and kh
         chrome_driver.get(base_url_kh + city_param + distict_param)
         district_name_kh = chrome_driver.find_element_by_css_selector(
            'select[name="district"] > option[selected="selected"]').text
         chrome_driver.get(base_url_en + city_param + distict_param)
         district_name_en = chrome_driver.find_element_by_css_selector(
            'select[name="district"] > option[selected="selected"]').text
         district_names = {
            'en': district_name_en,
            'kh': district_name_kh
         }
         districts.append(
            {
               'districtName': district_names,
               'commune': communes
            }
         )
      except NoSuchElementException:
         print('Scrapping error -> \n' + str(NoSuchElementException))
   # get city name both en and kh
   chrome_driver.get(base_url_en + city_param)
   province_name_en = chrome_driver.find_element_by_css_selector('#city > option[selected="selected"]').text
   chrome_driver.get(base_url_kh + city_param)
   province_name_kh = chrome_driver.find_element_by_css_selector('#city > option[selected="selected"]').text
   json_format = {
      'province': {
         'en': province_name_en,
         'kh': province_name_kh
      },
      'district': districts
   }
   all_data.append(json_format)
# save to file json
json_string = json.dumps(all_data, ensure_ascii=False)
file_name = 'cambodia-postal-code.json'
with codecs.open(file_name, 'w', encoding='utf-8') as f:
   f.write(json_string)
print('================= complete ==================')






