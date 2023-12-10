from rest_framework.views import APIView
from rest_framework.response import Response
import os

from proj_backend.models import Location

global locationCity 
global locationCountry
import requests
import argparse
import json
from math import radians, sin, cos, sqrt, atan2

class Test(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        return Response({
            "state" : "success"
        })

class addLocationAndProcessQuery(APIView):
    def post(self, request):
        locationName = request.data.get('locationName')
        global locationCity
        locationCity = request.data.get('locationCity')
        global locationCountry
        locationCountry = request.data.get('locationCountry')

        #locationObj = myLocation(name=locationName, city=locationCity, country=locationCountry)
        locationObj = Location(name=locationName, city=locationCity, country=locationCountry)
        locationObj.save()

        return(Response(status=200))
    
    def get(self, request, format=None):
            target_city = ReturnEmployeeCount(locationCity, locationCountry)
            return Response({
                "locationCity" : target_city,
                "locationCountry" : locationCountry,
                "deficitRatio": target_city
            })
    


    
def haversine(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    R = 6371  # Earth radius in kilometers

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

def fix_accents(s):
    mapping_table = str.maketrans({'ș': 's', 'ă': 'a', 'î': 'i', 'â': 'a', 'ț': 't'})
    output_string = s.translate(mapping_table)
    return output_string

parser = argparse.ArgumentParser(description='Query Veridion API for companies.')

# Add command-line arguments
parser.add_argument('--country', required=True, help='Country for the company search')
parser.add_argument('--region', required=True, help='Region for the company search')
parser.add_argument('--city', required=True, help='City for the company search')

def ReturnEmployeeCount(argCity, argCountry):
        # Define the World Bank API endpoint with placeholders
    base_url = 'http://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}?format=json'

    # Define the age group indicators you are interested in
    age_group_indicators = {
        'under_15': 'SP.POP.0014.TO.ZS',
        '15_64': 'SP.POP.1564.TO.ZS',
        '65_over': 'SP.POP.65UP.TO.ZS',
    }

    # Choose the country code (e.g., IN for India)
    country_code = 'RO'

    # Initialize a dictionary to store the age distribution data
    age_distribution = {}

    # Loop through each age group and make an API request
    for group_name, indicator_code in age_group_indicators.items():
        # Build the API request URL
        url = base_url.format(country_code=country_code, indicator_code=indicator_code)

        # Make the request
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON data
            data = response.json()

            # Extract the relevant value (assuming we're interested in the most recent year)
            value = data[1][0]['value']  # This is an assumption; you'll need to parse the JSON structure correctly for your use case

            # Add the value to our age distribution dictionary
            age_distribution[group_name] = value


    cities = []

    if(argCountry == 'Romania'):
        country_code = 'RO'
        sate_si_orase = r"C:\Users\User\CS\Hack1\backend\localitati.json"
        input_mycity = fix_accents(argCity)
        # input_mycity = (argCity)
        #print(str(argCity) + "\n")
        mycity_lat = 0
        mycity_lng = 0
        with open(sate_si_orase, 'r') as file:
                data = json.load(file)

                for mycity in data:
                    mycity_name = mycity['nume']
                    if mycity_name == input_mycity:
                        mycity_lat = mycity['lat']
                        mycity_lng = mycity['lng']
                        
                    # else:
                    
                for found_city in data:
                        found_city_name = found_city['nume']
                        found_city_lat = found_city['lat']
                        found_city_lng = found_city['lng']
                        found_city_population = found_city['populatie']
                        distance_km = 25
                        latitude_change = distance_km / 111.1
                        distance_to_reference = haversine(found_city_lat, found_city_lng, mycity_lat, mycity_lng)
                        if distance_to_reference <= 25 :
                            cities.append({
                                'name': found_city_name,
                                'lat': found_city_lat,
                                'lng': found_city_lng,
                                'population': found_city_population,
                                'distance': distance_to_reference
                            })
    elif(argCountry == 'United Kingdom'):
        uk_cities = 'uk.json'
        with open(uk_cities, 'r') as file:
                data = json.load(file)
                for mycity in data['places']:
                        mycity_name = mycity['name']
                        if mycity_name == argCity:
                                mycity_lat = mycity['latitude']
                                mycity_lng = mycity['longitude']
                for found_city in data['places']:
                        found_city_name = found_city['name']
                        found_city_lat = found_city['latitude']
                        found_city_lng = found_city['longitude']
                        found_city_population = found_city['population']
                        distance_km = 100
                        latitude_change = distance_km / 111
                        distance_to_reference = haversine(found_city_lat, found_city_lng, mycity_lat, mycity_lng)
                        if distance_to_reference <= 100 :
                            cities.append({
                                'name': found_city_name,
                                'lat': found_city_lat,
                                'lng': found_city_lng,
                                'population': found_city_population,
                                'distance': distance_to_reference
                            })
              
    url = 'https://data.veridion.com/search/v2/companies'
    headers = {
        'x-api-key': 'pXStedvXkA9pMcNK1tWvx_4DesmTsIZ47qfTa6WkqFxgrCvCqJA0mpALQ53J',
        'Content-type': 'application/json'
    }

    page_size = 50  # You can adjust the page size based on your needs
    my_city_data=[]
    for city in cities:
        pagination_token = None
        employee_count = 0

        while True:
            # Construct data with pagination token
            data = {
                "filters": {
                    "and": [
                        {
                            "attribute": "company_location",
                            "relation": "in",
                            "value": [
                                {
                                    "country": argCountry,
                                    "city": city['name']
                                }
                            ],
                            "strictness": 1
                        },
                        {
                            "attribute": "company_employee_count",
                            "relation": "greater_than",
                            "value": 0
                        },
                        {
                            "attribute": "company_naics_code",
                            "relation": "in",
                            "value": ["622110", "622310", "621111", "621112", "621210", "621310", "621320", "621330", "621340", "621391", "621399", "621410", "621420", "621491", "621492", "621493", "621498", "621511", "621512", "621610", "621910", "621991", "621999", "622110", "622210", "622310", "622320", "622330", "622390", "623110"]
                        }
                    ]
                }
            }

            # Make the POST request
            response = requests.post(url, headers=headers, json=data, params={'page_size': page_size, 'pagination_token': pagination_token})
            print(response.json())

            # Check the response
            if response.status_code == 200:
                # Extract and print employee_count for each company on the current page
                result = response.json().get('result', [])
                for company in result:
                    # Add employee_count to the company dictionary
                    employee_count += company.get('employee_count', 'N/A')
                    # print(f"Company: {company.get('company_name', 'Unknown')}, Employee Count: {company['employee_count']}")

                # Check if there is a next page
                pagination = response.json().get('pagination', {})
                next_token = pagination.get('next')
                if next_token:
                    pagination_token = next_token
                else:
                    break  # Exit the loop if there is no next page
            else:
                # Print an error message if the request was not successful
                print(f"Error: {response.status_code}")
                print(response.text)
                break  # Exit the loop on error

        print(city)
        my_city_data.append({"employee_count": employee_count, "cityName": city['name'], "population": city['population'], "deficit": 0, "distance": city['distance']})
    
    if len(my_city_data) == 0:
        return {"cityName": "notFound"} 
    
    for city_data in my_city_data:
        ideal_doctor_ratio = 1 / 1000
        ideal_nr_doctors_in_area = city_data['population'] * ideal_doctor_ratio
        deficit_doc = ideal_nr_doctors_in_area - city_data['employee_count']
        city_data['deficit'] = deficit_doc
        distance_fac = 0.005
        W_age = age_distribution['under_15'] * 1.2 / 100 + age_distribution['15_64'] / 100 + age_distribution['65_over'] * 1.5 / 100
        adjusted_deficit = ((city_data['population'] * ideal_doctor_ratio * W_age) - city_data['employee_count']) * (1 + distance_fac * city_data['distance'])
        city_data['deficit'] = adjusted_deficit
        

    deficit = 0
    myCity = my_city_data[0]
    for city_data in my_city_data:
        if city_data['deficit'] > deficit:
            myCity = city_data
            deficit = myCity['deficit']

    return myCity
    



        