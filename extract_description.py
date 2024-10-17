
import requests
from lxml import html

def extract_product_info(url):
    # Send a GET request to the URL
    response = requests.get(url)

    # Parse the HTML content
    tree = html.fromstring(response.content)

    # Extract product name
    product_name_elements = tree.xpath('//ul[@class="product-item-main-features"]/li[1]/text()')
    product_name = product_name_elements[0].strip() if product_name_elements else "Product name not found"

    # Extract product description
    description_element = tree.xpath('//div[@class="product attribute test1 description"]/div[@class="value"]/text()')
    description = description_element[0].strip() if description_element else "Description not found"

    # Extract features
    features_elements = tree.xpath('//ul[@class="short-overview"]/li/text()')
    features = [feature.strip() for feature in features_elements if feature.strip()]

    return {
        'name': product_name,
        'description': description,
        'features': features
    }

# Example usage
url = "https://www.stonegroup.co.uk/startech-com-1000-ft-bulk-roll-of-black-cmr-cat6-solid-utp-riser-cable-cat-6-riser-cable-cat-6-cmr-ethernet-cable-23-awg-black-wir6cmrbk-bulk-cable-304-9-m-black-1tacccab-055960/"
product_info = extract_product_info(url)

print("Product Name:", product_info['name'])
print("Description:", product_info['description'])
print("Features:")
for feature in product_info['features']:
    print("- ", feature)
