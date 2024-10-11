from curl_cffi import requests as cureq
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import re
import time

headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"}
  

#getting the number of pages

url = f"https://www.immoweb.be/nl/search-results/huis/te-koop?countries=BE&page=1&orderBy=relevance"

resp = cureq.get(url, headers=headers, impersonate="chrome")

print(resp.status_code)

data = resp.json()

print(data.keys())

total_houses_1_page = int(data['range'].split('-')[1])

total_number_of_houses= data['totalItems']

number_of_pages = total_number_of_houses//total_houses_1_page

print(number_of_pages)

#looping through the pages and start collecting the data

data_collection = []

start_time = time.perf_counter()

for page in range(1, 3):
  url = f"https://www.immoweb.be/nl/search-results/huis/te-koop?countries=BE&page={page}&orderBy=relevance"
  
  resp = cureq.get(url, headers=headers, impersonate="chrome")

  data_collection.append(resp.json())

end_time = time.perf_counter()

elapsed_time = end_time - start_time

print(f"Data loaded in data.json, in {elapsed_time} seconds.")

#Start to parse the data_collection
all_properties = []
for i in range(len(data_collection)):
  
  results_list = data_collection[i].get('results', [])

  for i, property in enumerate(results_list):
    property = {}
    property['id'] = results_list[i].get('id')
    property['type'] = results_list[i].get('property', {}).get('type')
    property['subtype'] = results_list[i].get('property', {}).get('subtype')
    property['country'] = results_list[i].get('property', {}).get('location', {}).get('country')
    property['region'] = results_list[i].get('property', {}).get('location', {}).get('region')
    property['locality_name'] = results_list[i].get('property', {}).get('location', {}).get('locality')
    property['locality_code'] = results_list[i].get('property', {}).get('location', {}).get('postalCode')

    property['bedroomcount'] = results_list[i].get('property', {}).get('bedroomCount', "None")

    property['netHabitableSurface'] = results_list[i].get('property', {}).get('netHabitableSurface')
    property['land_surface'] = results_list[i].get('property', {}).get('landSurface')
    property['roomcount'] = results_list[i].get('property', {}).get('roomCount', "None")

    property['transactionType'] = results_list[i].get('transaction', {}).get('type')
    property['sale_annuity'] = results_list[i].get('transaction', {}).get('sale', {}).get('lifeAnnuity')
    property['price'] = results_list[i].get('transaction', {}).get('sale', {}).get('price')
    property['oldPrice'] = results_list[i].get('transaction', {}).get('sale', {}).get('oldPrice')

    all_properties.append(property)
    
    
print("All proporties extracted from data_collection:", len(all_properties), type(all_properties))


#
print(type(all_properties))  
print(type(all_properties[0]))

dataframe_first_scrape = pd.DataFrame.from_records(all_properties)

dataframe_first_scrape.to_csv(r"C:\Users\Rik\Desktop\immoeliza\scraper\immo_scraper_1.csv", index=False)









## SECOND SCRAPE

# Start the timer
start_time = time.perf_counter()
print("Start second scraping")
    
data_collection_2 = []

for property in all_properties:
  
    if 'type' in property and property['type'] == "HOUSE":
        
        # Check if 'property_type2' exists and that the value is 'house'
        base_url = "https://www.immoweb.be/nl/zoekertje/"
        property_url = base_url + str(property['id'])
        
        try:
            # Send request to property URL
            r = requests.get(property_url, headers=headers)
            r.raise_for_status()  
            
            # Parse the page content
            soup = BeautifulSoup(r.content, "html.parser")
            print(f"Page {property_url} scraped successfully.")
            
            # Try to extract the specific script tag
            script_tag = soup.select_one('div.classified script[type="text/javascript"]')
            
            if script_tag:
                # Process the script_tag here
                print("Script tag found and processed.")
            else:
                print(f"No script tag found on {property_url}")
        
        except Exception as e:
            # Print the error message and continue to the next property
            print(f"Error on page {property_url}: {e}")
            continue
        
        js_content = script_tag.string
        
        # Find the start and end of the JSON object
        start = js_content.find('{')
        end = js_content.rfind('}') + 1
        
        # Extract and parse the JSON data
        json_data = json.loads(js_content[start:end])
        
        property_data = json_data.get('property', {})
        building_data = property_data.get('building')
        kitchen_data = property_data.get('kitchen')
        living_room_data = property_data.get('livingRoom')

        property['furnished'] = json_data.get('transaction', {}).get('sale', {}).get('isFurnished', "None")

        if isinstance(building_data, dict):
            property['building'] = building_data
            property['building_condition'] = building_data.get('condition', "None")
            property['facade_count'] = building_data.get('facadeCount', "None")
        else:
            property['building'] = "None"

        property['pool'] = property_data.get('hasSwimmingPool', "None")

        if isinstance(kitchen_data, dict):
            property['kitchen'] = kitchen_data
            property['kitchen_area'] = kitchen_data.get('surface', "None")
            property['kitchen_type'] = kitchen_data.get('type', "None")
        else:
            property['kitchen'] = "None"

        if isinstance(living_room_data, dict):
            property['living_room'] = living_room_data
            property['living_room_area'] = living_room_data.get('surface', "None")
        else:
            property['living_room'] = "None"

        property['hasLivingRoom'] = property_data.get('hasLivingRoom', "None")

        property['garden'] = property_data.get('hasGarden', "None")
        property['garden_area'] = property_data.get('gardenSurface', "None")

        property['terrace'] = property_data.get('hasTerrace', "None")
        property['terrace_area'] = property_data.get('terraceSurface', "None")

        property['fireplace'] = property_data.get('fireplaceExists', "None")

# load the data_collection in a file

dataframe_second_scrape = pd.DataFrame.from_records(all_properties)

print(dataframe_second_scrape)

dataframe_first_scrape.to_csv(r"C:\Users\Rik\Desktop\immoeliza\scraper\immo_scraper_1.csv", index=False)

end_time = time.perf_counter()

elapsed_time = end_time - start_time

print(f'The second scrape took {elapsed_time} seconds')

#Concatenate the dataframes
df_concat = pd.concat([dataframe_first_scrape, dataframe_second_scrape], axis=1)
print(df_concat)

df_concat.to_csv(r"C:\Users\Rik\Desktop\immoeliza\scraper\immo_scraper_all.csv", index=False)

