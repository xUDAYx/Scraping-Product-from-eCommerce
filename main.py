import requests
from lxml import html
import pandas as pd
import re
from bs4 import BeautifulSoup

# Example conversion rate from GBP to INR
GBP_TO_INR_CONVERSION_RATE = 100  # Replace this with the actual rate if dynamic

def standardize_category(text):
    lower_text = text.lower()
    if any(term in lower_text for term in ["radio access point", "access point"]):
        return "Access Point"
    return text

def extract_product_data(tree):
    product_data = {
        'ID': '',
        'Type': 'simple',
        'SKU': '',
        'Name': '',
        'Published': 1,
        'Is featured?': 0,
        'Visibility in catalog': 'visible',
        'Short description': '',
        'Description': '',
        'Date sale price starts': '',
        'Tax status': 'taxable',
        'Tax class': '',
        'In stock?': 1,
        'Stock': '',
        'Regular price': '',  # Only INR price will be stored here
        'Categories': '',
        'Tags': '',
        'Images': '',
        'Attribute 1 name': 'brand',
        'Attribute 1 value(s)': '',
        'Attribute 1 visible': 1,
        'Attribute 1 global': 1
    }
    
    try:
        # Extract SKU
        sku = tree.xpath('//span[contains(text(), "SKU#:")]/text()')
        if sku:
            product_data['SKU'] = sku[0].split(':')[-1].strip()
        
        # Extract Name
        name_element = tree.xpath('/html/body/div[4]/main/div[2]/div/div[1]/div[1]/div[2]/h1/span')
        if name_element:
            name = name_element[0].text_content().strip()  # Extract text content, then strip
            product_data['Name'] = name
            # Assuming the brand is the first word of the product name
            brand = name.split()[0]
            product_data['Attribute 1 value(s)'] = brand
        
        # Extract Price and convert to INR
        price_element = tree.xpath('/html/body/div[4]/main/div[2]/div/div[1]/div[1]/div[3]/div[3]/span/span/span')
        if price_element:
            price_text = price_element[0].text_content()  # Get text content of the price element
            price_match = re.search(r'£(\d+\.\d+)', price_text)  # Use regex to match price pattern
            if price_match:
                price_gbp = float(price_match.group(1))  # Extract the price in GBP
                
                # Convert price to INR
                price_inr = price_gbp * GBP_TO_INR_CONVERSION_RATE
                product_data['Regular price'] = round(price_inr, 2)  # Store only INR price
        
        # Extract Short Description
        short_desc_items = tree.xpath('/html/body/div[4]/main/div[2]/div/div[2]/div/div[2]/div/div[2]/div[1]/div')
        if short_desc_items:
            product_data['Short description'] = ' '.join([item.text_content().strip() for item in short_desc_items])
        
        # Extract Full Description
        overview = tree.xpath('/html/body/div[4]/main/div[2]/div/div[2]/div/div[4]/div/div/div[2]')
        if overview:
            product_data['Description'] = ' '.join([item.strip() for item in overview]).strip()
        
        
        # Extract Images
        image = tree.xpath('/html/body/div[4]/main/div[2]/div/div[1]/div[2]/div[3]/div[2]/div[2]/div[1]/div[3]/div[2]')
        if image:
            product_data['Images'] = image[0]
        
        
        # Extract Specifications from a table (if available)
        spec_rows = tree.xpath('//table[@class="specification-table"]//tr')
        if spec_rows:
            specs = []
            for row in spec_rows:
                cells = row.xpath('.//td/text()')
                if len(cells) == 2:
                    label = cells[0].strip()
                    value = cells[1].strip()
                    specs.append(f"{label}: {value}")
                    
                    # Check if this specification is for brand
                    if label.lower() == 'brand':
                        product_data['Attribute 1 value(s)'] = value
            
            if specs:
                product_data['Description'] += '\n\nSpecifications:\n' + '\n'.join(specs)
        
        # Extract Categories
        category_elements = tree.xpath('/html/body/div[4]/main/div[2]/div/div[2]/div/div[2]/div/div[1]/ul/li[2]')
        if category_elements:
            category = category_elements[0].text_content().strip()
            standardized_category = standardize_category(category)
            product_data['Categories'] = f"Networking, Networking > {standardized_category}"

        # Set Tags
        brand = product_data['Attribute 1 value(s)']
        standardized_category = standardize_category(category)
        product_data['Tags'] = f"{brand},{standardized_category}"
        
    except Exception as e:
        print(f"Error extracting data: {str(e)}")
    
    return product_data
def extract_product_urls(num_pages):
    base_url = "https://www.stonegroup.co.uk/hardware/networking/"
    product_links = []

    for page in range(1, num_pages + 1):
        url = f"{base_url}?p={page}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        product_containers = soup.find_all('div', class_='product-item-info')
        
        for container in product_containers:
            link = container.find('a', class_='product-item-link')
            if link:
                product_links.append(link['href'])
    
    return product_links

def scrape_stone_group():
    products_data = []
    
    num_pages = int(input("Enter the number of pages to scrape: "))
    product_urls = extract_product_urls(num_pages)
    
    for url in product_urls:
        try:
            response = requests.get(url)
            tree = html.fromstring(response.content)
            product_data = extract_product_data(tree)
            products_data.append(product_data)
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
    
    # Create DataFrame and export to CSV
    df = pd.DataFrame(products_data)
    df.to_csv('stone_group_products.csv', index=False)

if __name__ == "__main__":
    scrape_stone_group()



