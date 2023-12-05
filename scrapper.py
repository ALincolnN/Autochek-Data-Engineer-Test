import os
import csv
from datetime import datetime

from xecd_rates_client import XecdClient

currencies = ['KES', 'UGX', 'NGN', 'GHS', 'MAD', 'XOF', 'EGP']

account_id = 'autochekafrica363498181'
api_key = 'kvlqf05toguakjc599re93dmlt'

client = XecdClient(account_id, api_key)
response = client.convert_from(to_currency=', '.join(currencies))
currency_data = response.get('to')

datetime_format = '%Y-%m-%d %H:%M:%S'

# Converting the timestamp from xe exchange response
formatted_datetime = datetime.strptime(response.get('timestamp'), '%Y-%m-%dT%H:%M:%SZ').strftime(datetime_format)

data = []
for currency in currency_data:
    currency_to = currency.get('quotecurrency', '')

    # Getting the conversion of currency to usd from Xe instead of calculating manually which might be inaccurate
    currency_to_usd_data = client.convert_from(from_currency=currency_to, to_currency='USD')

    data_dict = {
        'timestamp': datetime.now().strftime(datetime_format),
        'currency_from': response.get('from', ''),
        'USD_to_currency_rate': currency.get('mid', ''),
        'currency_to_USD_rate': currency_to_usd_data.get('to')[0]['mid'],
        'currency_to': currency_to
    }
    data.append(data_dict)

print('Done Reading Currency Exchange Data')

# Creating a directory to save the currency exchange data file
path_directory = os.path.expanduser('~') + '/reports/exchange/'
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
