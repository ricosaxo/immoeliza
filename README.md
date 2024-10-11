ImmoEliza Web Scraping Project

Overview

This project is a web scraper designed to collect and analyze real estate data from Immoweb, a popular Belgian property listing website. The scraper is built in Python and uses various libraries to efficiently gather, process, and store property information.
Features

First scrape: Collects basic property information from multiple pages of search results.
Second scrape: Gathers detailed information for each property by visiting individual listing pages.
Data export: Saves the collected data in CSV format for further analysis.

Requirements

Python 3.7+
Required Python packages:
curl_cffi
requests
beautifulsoup4
pandas

Installation

Clone this repository:

Copy git clone https://github.com/ricosaxo/immoeliza-scraper.git

Install the required packages:

Copypip install -r requirements.txt

Usage

First Scrape:

listings = collect_data(number_of_pages, headers)
all_properties = parse_data(listings)

Second Scrape:
updated_properties = second_scrape(all_properties, headers)

Export Data:
dataframe = pd.DataFrame.from_records(updated_properties)
dataframe.to_csv("immo_scraper_all.csv", index=False)

Project Structure

main.py: The main script that orchestrates the scraping process.

Functions

collect_data(pages: int, headers: dict): Collects data from the specified number of pages.
parse_data(listings: list): Parses the raw listings data to extract relevant property details.

Data Fields
The scraper collects the following information for each property:

Basic Information: ID, type, subtype, location, bedroom count, habitable surface, land surface, etc.
Detailed Information: Building condition, kitchen details, living room details, outdoor spaces, etc.
