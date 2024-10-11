import time
from curl_cffi import requests as cureq
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import re

headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"}




#getting the number of online listings and pages

url = f"https://www.immoweb.be/nl/search-results/huis/te-koop?countries=BE&page=1&orderBy=relevance"

resp = cureq.get(url, headers=headers, impersonate="chrome")

print(resp.status_code)

data = resp.json()

total_houses_1_page = int(data['range'].split('-')[1])

total_number_of_houses= data['totalItems']

number_of_pages = total_number_of_houses//total_houses_1_page

print(f'Immoweb contains {total_number_of_houses} listings on {number_of_pages} pages')




#FIRST SCRAPE

def collect_data(pages: int, headers: dict):
    """
    This function collects data from the specified number of pages and returns a list.

    Args:
    pages (int): Number of pages to collect data from.
    headers (dict): HTTP headers to include in the requests.
    """
    if not headers:
        raise ValueError("Headers are required to make the request.")

    data_collection = []

    # Start the timer
    start_time = time.perf_counter()
    print(f"Start scraping {pages} pages...")

    # Loop through the pages and collect data
    for page in range(1, pages + 1):
        url = f"https://www.immoweb.be/nl/search-results/huis/te-koop?countries=BE&page={page}&orderBy=relevance"
        
        try:
            # Send the request
            print(f"Scraping page {page}...")
            resp = cureq.get(url, headers=headers, impersonate="chrome")
            resp.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)

            # Try to parse the JSON response
            data = resp.json()
            data_collection.append(data)
            print(f"Page {page} scraped successfully.")
        
        except requests.exceptions.RequestException as req_err:
            # Handle network-related errors
            print(f"Network error on page {page}: {req_err}")
        except ValueError:
            # Handle JSON decoding errors
            print(f"Error decoding JSON on page {page}.")
        except Exception as e:
            # Catch any other exceptions
            print(f"An error occurred on page {page}: {e}")

    # Stop the timer and print the elapsed time
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Data scraping completed in {elapsed_time:.2f} seconds.")

    return data_collection



def parse_data(listings: list):
    """
    Parses the listings data to extract relevant property details.

    Args:
    listings (list): List of raw listings data.

    Returns:
    all_properties (list): List of dictionaries with parsed property data.
    """
    all_properties = []

    for listing in listings:
        # Get the results list (default to an empty list if not found)
        results_list = listing.get('results', [])

        for result in results_list:
            # Extract property details using nested get() for safety
            property_details = result.get('property', {})
            location = property_details.get('location', {})
            transaction = result.get('transaction', {}).get('sale', {})

            property_data = {
                'id': result.get('id'),
                'type': property_details.get('type'),
                'subtype': property_details.get('subtype'),
                'country': location.get('country'),
                'region': location.get('region'),
                'locality_name': location.get('locality'),
                'locality_code': location.get('postalCode'),
                'bedroom_count': property_details.get('bedroomCount', "None"),
                'net_habitable_surface': property_details.get('netHabitableSurface'),
                'land_surface': property_details.get('landSurface'),
                'room_count': property_details.get('roomCount', "None"),
                'transaction_type': result.get('transaction', {}).get('type'),
                'sale_annuity': transaction.get('lifeAnnuity'),
                'price': transaction.get('price'),
                'old_price': transaction.get('oldPrice')
            }

            all_properties.append(property_data)

    print(f"Extracted {len(all_properties)} properties from data.")
    return all_properties




#Testing the first scrape

listings = collect_data(2, headers)
all_properties = parse_data(listings)

# Convert to DataFrame and export to CSV
dataframe_first_scrape = pd.DataFrame.from_records(all_properties)
csv_path = r"C:\Users\Rik\Desktop\immoeliza\scraper\immo_scraper_1.csv"
dataframe_first_scrape.to_csv(csv_path, index=False)

print(f"Data saved to {csv_path}")





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

dataframe_first_scrape.to_csv(r"C:\Users\Rik\Desktop\immoeliza\scraper\immo_scraper_1.csv", index=False)

end_time = time.perf_counter()

elapsed_time = end_time - start_time

print(f'The second scrape took {elapsed_time} seconds')

#Concatenate the dataframes
df_concat = pd.concat([dataframe_first_scrape, dataframe_second_scrape], axis=1)

df_concat.to_csv(r"C:\Users\Rik\Desktop\immoeliza\scraper\immo_scraper_all.csv", index=False)





