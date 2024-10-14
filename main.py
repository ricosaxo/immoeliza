import time
from curl_cffi import requests as cureq
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"}


#Getting the number of listings and the number of pages

url = f"https://www.immoweb.be/nl/search-results/huis/te-koop?countries=BE&page=1&orderBy=relevance"

resp = cureq.get(url, headers=headers, impersonate="chrome")

print(resp.status_code)

data = resp.json()

total_houses_1_page = int(data['range'].split('-')[1])

total_number_of_houses= data['totalItems']

number_of_pages = total_number_of_houses//(total_houses_1_page + 1)

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


# Parse the results of the first scraping

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

#create a first listings list listings_1 

listings_1 = []  

for house in all_properties:
    listing_1 = {}  
    listing_1['id'] = house.get('id')
    listing_1['locality_name'] = house.get('locality_name')
    listing_1['Postal_code'] = house.get('locality_code')
    listing_1['Price'] = house.get('price')
    listing_1['Type_of_property'] = house.get('subtype')
    listing_1['Number_of_rooms'] = house.get('room_count')
    listing_1['Living_area'] = house.get('net_habitable_surface')
    if house.get('sale_annuity') is None:
        listing_1['Type_of_sale'] = house.get('transaction_type')
    
    listings_1.append(listing_1)  

# Convert listings_1 to DataFrame and export to CSV
dataframe_first_scrape = pd.DataFrame(listings_1)
csv_path = r"C:\Users\Rik\Desktop\immoeliza\scraper\immo_scraper_1.csv"
dataframe_first_scrape.to_csv(csv_path, index=False)

print(f"Data from first scrape saved to {csv_path}")






## SECOND SCRAPE

print("Start second scraping")
    
data_collection_2 = []

for property in listings_1:
    
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
    
    # Extract the JavaScript object
    js_content = script_tag.string
    
    # Find the start and end of the JSON object
    start = js_content.find('{')
    end = js_content.rfind('}') + 1
    
    # Extract and parse the JSON data
    json_data = json.loads(js_content[start:end])
    
    #append json_data to the list data_collection2
    data_collection_2.append(json_data)


#parse en merge the data from data_collection_2 in listings_2

listings_2 = []

for house in data_collection_2:
    listing_2 = {}
    
    
    listing_2['id'] = house.get('id', None)
    
    
    property_details = house.get('property', {})
    
    kitchen_details = property_details.get('kitchen')
    if isinstance(kitchen_details, dict) and kitchen_details.get('type') == "INSTALLED":
        listing_2['Equipped_kitchen'] = True
    else:
        listing_2['Equipped_kitchen'] = False
    
    is_furnished = property_details.get('transaction', {}).get('sale', {}).get('isFurnished')
    listing_2['Furnished'] = False if is_furnished is None else True
    
    fireplace_exists = property_details.get('fireplaceExists')
    listing_2['Open_fire'] = False if fireplace_exists is False else True
    
    has_terrace = property_details.get('hasTerrace')
    if has_terrace is False:
        listing_2['Terrace'] is None
    else:
        listing_2['Terrace'] = property_details.get('terraceSurface')
    
    has_garden = property_details.get('hasGarden')
    if has_garden is False:
        listing_2['Garden'] is None
    else:
        listing_2['Garden'] = property_details.get('gardenSurface')
    
    building_details = property_details.get('building')
    if isinstance(building_details, dict):
        listing_2['Number_of_facades'] = building_details.get('facadeCount', None)
    else:
        listing_2['Number_of_facades'] = None
    
    has_swimming_pool = property_details.get('hasSwimmingPool')
    listing_2['Swimming_Pool'] = False if has_swimming_pool is False else True
    
    if isinstance(building_details, dict):
        listing_2['State_of_building'] = building_details.get('condition', None)
    else:
        listing_2['State_of_building'] = None
    
    listings_2.append(listing_2)

# Convert listings_2 to DataFrame and export to CSV

dataframe_second_scrape = pd.DataFrame(listings_2)
csv_path = r"C:\Users\Rik\Desktop\immoeliza\scraper\immo_scraper_2.csv"
dataframe_second_scrape.to_csv(csv_path, index=False)

print(f"Data from second scrape saved to {csv_path}")

# Merge all the data to Dataframe

merged_df = pd.merge(dataframe_first_scrape, dataframe_second_scrape, on='id', how='inner')

print(merged_df)
csv_path = r"C:\Users\Rik\Desktop\immoeliza\scraper\immo_scraper_merged.csv"
merged_df.to_csv(csv_path, index=False)

print(f"Merged data saved to {csv_path}")
