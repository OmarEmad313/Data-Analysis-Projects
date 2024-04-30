import httpx
from selectolax.parser import HTMLParser
import csv
url ='https://www.rei.com/c/camping-and-hiking/f/scd-deals'
headers={"User-Agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'}
resp = httpx.get(url,headers=headers)
html = HTMLParser(resp.text)


# Dictionary to store product names and prices
products = {}

def get_price_details(product):
    # Initialize the dictionary to store price details
    price_details = {'price': None, 'status': None}
    
    # Handle price range or single price
    full_price_tag = product.css_first('span[data-ui="full-price"]')
    if full_price_tag:
        full_price = full_price_tag.text().strip()
        price_details['price'] = full_price
        if '-' in full_price:
            price_details['status'] = 'Price Range'
        else:
            price_details['status'] = 'Single Price'

    # Handle sale price, savings, and comparison price
    sale_price_tag = product.css_first('span[data-ui="sale-price"]')
    if sale_price_tag:
        sale_price = sale_price_tag.text().strip()
        compare_price_tag = product.css_first('span[data-ui="compare-at-price"]')
        savings_tag = product.css_first('div[data-ui="savings-percent-variant2"]')
        if compare_price_tag:
            compare_price = compare_price_tag.text().strip()
            savings = savings_tag.text().strip() if savings_tag else 'No savings info'
            price_details['price'] = f"Sale: {sale_price}, Originally: {compare_price}, Savings: {savings}"
            price_details['status'] = 'Sale Price'
        else:
            full_price = full_price_tag.text().strip()
            price_details['price'] = f"Sale: {sale_price}, Originally: {full_price}"    
            price_details['status'] = 'Sale Price (unknown savings %)'

    return price_details

# Find all product elements (assuming each product is in a <li> tag as shown)
for product in html.css('li.VcGDfKKy_dvNbxUqm29K'):
    # Extracting the product name
    name_tag = product.css('h2.dBj29YaudGjV80UCeSh_')
    if name_tag:
        brand = name_tag[0].css('span.nL0nEPe34KFncpRNS29I')[0].text().strip() if name_tag[0].css('span.nL0nEPe34KFncpRNS29I') else ''
        title = name_tag[0].css('span.Xpx0MUGhB7jSm5UvK2EY')[0].text().strip() if name_tag[0].css('span.Xpx0MUGhB7jSm5UvK2EY') else ''
        product_name = f"{brand} {title}"
    
     # Initialize pricing information
    price = None
    price_status = None

    # Check for different types of pricing information
    if product.css('span[data-ui="full-price"]'):
        price = product.css('span[data-ui="full-price"]')[0].text().strip()
        price_status = "Price Range" if "-" in price else "Single Price"

    # Check for sale price
    if product.css('span[data-ui="sale-price"]'):
        sale_price = product.css('span[data-ui="sale-price"]')[0].text().strip()
        original_price = product.css('span[data-ui="compare-at-price"]')[0].text().strip() if product.css('span[data-ui="compare-at-price"]') else None
        savings = product.css('div[data-ui="savings-percent-variant2"]')[0].text().strip() if product.css('div[data-ui="savings-percent-variant2"]') else None
        price = f"Sale: {sale_price}, Originally: {original_price}, Savings: {savings}"
        price_status = "Sale Price"

    # Store product data
    price_info = get_price_details(product)
    if product_name and price_info['price']:
        products[product_name] = price_info
# Output the dictionary
print(products)

# CSV file path
csv_file_path = 'products_detailed.csv'

# Writing to a CSV file
with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Product Name', 'Price Details', 'Status'])  # Column headers
    for product, details in products.items():
        writer.writerow([product, details['price'], details['status']])

print(f"CSV file has been created and saved as '{csv_file_path}'.")
