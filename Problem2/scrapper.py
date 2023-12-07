import os
import csv
from datetime import datetime

from xecd_rates_client import XecdClient
import requests

from dotenv import load_dotenv

load_dotenv()

"""
The following code is aimed at getting currency exchange rates from the given Xecd API endpoint.
The path convert.json specifies the format the data is returned in, in my use case, json format.
You are required to place and name correctly your account id and api key as provided in the xe dashboard in the .env 
    file that you should create while initializing the project.
The data has been extracted from the url provided using the requests method and converted to json for consumption.

As commented out, you can also use the XecdClient class which is a REST client provided for by Xecd if you choose not
    to use the conventional requests method. The client will handle that part for you and you need only to provide
    your credentials while calling the class, as demonstrated in the next comment section.

More comments will be available at specified sections to elaborate what is happenning.
"""

# client = XecdClient(account_id, api_key)
# response = client.convert_from(to_currency=', '.join(currencies))
# response_data = response.get('to')

currencies = ['KES', 'UGX', 'NGN', 'GHS', 'MAD', 'XOF', 'EGP']
account_id = os.getenv('ACCOUNT_ID')
api_key = os.getenv('API_KEY')

# Joining items in the provided list to a comma separated string
params = ', '.join(currencies)

url = 'https://xecdapi.xe.com/v1/convert_from.json'
response = requests.get(url=url, auth=(account_id, api_key), params={'to': params})
response_data = response.json()

datetime_format = '%Y-%m-%d %H:%M:%S'

# Converting the timestamp from xe exchange response
formatted_datetime = datetime.strptime(response_data.get('timestamp'), '%Y-%m-%dT%H:%M:%SZ').strftime(datetime_format)

data = []

for currency in response_data.get('to'):
    currency_to = currency.get('quotecurrency', '')

    # Getting the conversion of currency to usd from Xe instead of calculating manually which might be inaccurate
    currency_to_usd_data = requests.get(url=url, auth=(account_id, api_key), params={'to': 'USD',
                                                                                     'from': currency_to}).json()

    data_dict = {
        'timestamp': datetime.now().strftime(datetime_format),
        'currency_from': response_data.get('from', ''),
        'USD_to_currency_rate': currency.get('mid', ''),
        'currency_to_USD_rate': currency_to_usd_data.get('to')[0]['mid'],
        'currency_to': currency_to
    }
    data.append(data_dict)

print('Done Reading Currency Exchange Data')

# Creating a directory to save the currency exchange data file
path_directory = '/opt/airflow/reports/'
if os.path.exists(path_directory):
    pass
else:
    path_directory = os.getcwd() + '/reports/'
    os.makedirs(name=path_directory, exist_ok=True)

file_name = path_directory + 'currency_conversion_data.csv'

# Creating the file itself. If the file exists, continue with executing code
try:
    open(file_name, 'x')
except FileExistsError:
    pass

# Writing to the file with mode as append i.e. If the file already exists, add the incoming data at the end of the
# file.
# I am using the DictWriter class since I saved the data as an array of dictionaries
with open(file=file_name, mode='a', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=data[0].keys())

    # If the file is empty(with no headers), create them using the writeheader method
    if os.path.getsize(file_name) == 0:
        writer.writeheader()

    # Write the data according to the list created earlier
    writer.writerows(data)
print(f'The data has been saved successfully as "currency_conversion_data.csv" at "{path_directory}"')
