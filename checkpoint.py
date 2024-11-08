import requests
from lxml import html
from tqdm import tqdm
import pandas as pd
import re
from bs4 import BeautifulSoup
import os
from datetime import datetime
from urllib.parse import quote
from urllib.parse import urlparse
from PIL import Image
from colorama import init, Fore, Style
from extract_table import extract_product_specs, generate_html_table
def get_gbp_to_inr_rate():
    try:
        # Using an alternative API that provides exchange rate data
        response = requests.get("https://open.er-api.com/v6/latest/GBP")
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()
        return data['rates']['INR']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return 1  # Fallback to a default value if API call fails

# Real-time conversion rate from GBP to INR
GBP_TO_INR_CONVERSION_RATE = get_gbp_to_inr_rate()

def standardize_category(text):
    lower_text = text.lower()
    if any(term in lower_text for term in ["radio access point", "access point","Campus","campus","Hardened","hardened"]):
        return "Access Point"
    
    if any(term in lower_text for term in ["network card", "network adapter card","full/low-profile","Full/Low-Profile","10/100/1000 nic network adapter","10/100/1000 NIC Network Adapter"]):
        return "Adapter Card"
    
    if any(term in lower_text for term in ["wireless router", "wifi router","Wi-Fi system","wi-fi system"]):
        return "Wifi & Routers"
    
    if any(term in lower_text for term in ["console server"]):
        return "Console System"
    
    if any(term in lower_text for term in ["gen 2","Gen 2","gen","environment monitoring device","environmental monitoring","Temperature & humidity sensor","temperature & humidity sensor","Remote management adapter","remote management adapter"]):
        return "Monitoring device"
    
    cable_terms = [
        "category 6", "category 6a", "patch cable", "security cable lock",
        "cat 6 riser cable", "6ft locking cable incl", "usb type-c to ethernet",
        "network cable", "type-c to ethernet", "cat 5e riser cable",
        "ethernet", "cable", "ethernet cable", "fibre", "fibre optic cable",
        "1000Base-SX SC", "InfiniBand cable","ft","m/","m /",
        "antistatic wrist strap", "anti-static wrist strap", "anti static wrist strap"]
    
    if any(term in lower_text for term in cable_terms):
        return "Cables and accessories"
    
    if any(term in lower_text for term in ["lifetime warranty","software license","subscription licence","Subscription licence","Licence","licence"]):
        return "Software License"
    
    if any(term in lower_text for term in ["v1","V1","v3","V3","switch","switches"]):
        return "Switch"
    
    if any(term in lower_text for term in ["windows 10","Windows 10","windows server","Windows Server"]):
        return "Print Server"
    
    if any(term in lower_text for term in ["Essentials Edition","essentials edition","Repeater","repeater"]):
        return "Wifi range extender"
    
    if any(term in lower_text for term in ["V2", "Dual Band AC600 Wireless Dongle", "dual band ac600 wireless dongle", "Quad Port Adapter", "ST1000SPEX43", "1T1R 802.11ac", "wifi adapter","WiFi Adapter","WiFi Card"]):
        return "Network Adapter"
    
    if any(term in lower_text for term in ["usb", "USB", "Usb", "Host", "bus adapter","Host bus adapter" ,"host bus adapter"]):
        return "USB Hub"
    
    if any(term in lower_text for term in ["8 Port","8 port"]):
        return "Serial Adapter"
    
    if any(term in lower_text for term in ["sfp", "mini-gbic", "transceiver module", "gbic", "optical module", "sfp+", "xfp", "qsfp", "fiber optic transceiver"]):
        return "SFP transceiver module"
    
    if any(term in lower_text for term in ["sfp", "mini-gbic", "transceiver module", "gbic", "optical module"]):
        return "SFP transceiver module"
    
    
    return text
    
def extract_product_data(tree, url):
    # Define the existing HTML content in the description
    existing_description = '''<!-- wp:woocommerce/product-tab {"id":"general","title":"General"} /-->\n\n<!-- wp:woocommerce/product-tab {"id":"pricing","title":"Pricing"} /-->\n\n<!-- wp:woocommerce/product-tab {"id":"inventory","title":"Inventory"} /-->\n\n<!-- wp:woocommerce/product-tab {"id":"shipping","title":"Shipping"} /-->\n\n<!-- wp:group {"align":"full","style":{"spacing":{"blockGap":"60px"}},"layout":{"type":"constrained","contentSize":"1920px"}} -->\n<div class="wp-block-group alignfull"><!-- wp:group {"align":"full","layout":{"type":"constrained","contentSize":"1400px"}} -->\n<div class="wp-block-group alignfull"><!-- wp:columns {"style":{"spacing":{"blockGap":{"left":"19.4%"}}}} -->\n<div class="wp-block-columns"><!-- wp:column {"width":"324px"} -->\n<div class="wp-block-column" style="flex-basis:324px"><!-- wp:heading {"className":"has-dm-sans-font-family","style":{"typography":{"fontSize":"25px","fontStyle":"normal","fontWeight":"700","lineHeight":"1.6"}},"textColor":"contrast"} -->\n<h2 class="wp-block-heading has-dm-sans-font-family has-contrast-color has-text-color" style="font-size:25px;font-style:normal;font-weight:700;line-height:1.6"><strong>Product details</strong></h2>\n<!-- /wp:heading --></div>\n<!-- /wp:column -->\n\n<!-- wp:column {"width":"805px"} -->\n<div class="wp-block-column" style="flex-basis:805px"><!-- wp:group {"style":{"spacing":{"blockGap":"60px"}},"layout":{"type":"constrained"}} -->\n<div class="wp-block-group"><!-- wp:group {"layout":{"type":"constrained"}} -->\n<div class="wp-block-group"><!-- wp:heading {"className":"has-dm-sans-font-family","style":{"typography":{"fontSize":"17px","fontStyle":"normal","fontWeight":"700","lineHeight":1.6},"spacing":{"margin":{"bottom":"10px"}}},"textColor":"contrast"} -->\n<h2 class="wp-block-heading has-dm-sans-font-family has-contrast-color has-text-color" style="margin-bottom:10px;font-size:17px;font-style:normal;font-weight:700;line-height:1.6"><strong>{card_pro_name}</strong></h2>\n<!-- /wp:heading -->\n\n<!-- wp:paragraph {"style":{"spacing":{"padding":{"top":"0","right":"0","bottom":"0","left":"0"},"margin":{"top":"0","right":"0","bottom":"0","left":"0"}},"typography":{"fontSize":"15px","fontStyle":"normal","fontWeight":"400","lineHeight":"1.6"}},"textColor":"contrast"} -->\n<p class="has-contrast-color has-text-color" style="margin-top:0;margin-right:0;margin-bottom:0;margin-left:0;padding-top:0;padding-right:0;padding-bottom:0;padding-left:0;font-size:15px;font-style:normal;font-weight:400;line-height:1.6"><strong>Overview</strong></p>\n<!-- /wp:paragraph -->\n\n<!-- wp:paragraph {"style":{"spacing":{"padding":{"top":"0","right":"0","bottom":"0","left":"0"},"margin":{"top":"0","right":"0","bottom":"0","left":"0"}},"typography":{"fontSize":"15px","fontStyle":"normal","fontWeight":"400","lineHeight":"1.6"}},"textColor":"contrast"} -->\n<p class="has-contrast-color has-text-color" style="margin-top:0;margin-right:0;margin-bottom:0;margin-left:0;padding-top:0;padding-right:0;padding-bottom:0;padding-left:0;font-size:15px;font-style:normal;font-weight:400;line-height:1.6">{SHORT DESCRIPTION}</p>\n<!-- /wp:paragraph -->\n\n<!-- wp:list -->\n<ul class="wp-block-list"><!-- wp:list-item -->\n<li>{FEATURE 1}</li>\n<!-- /wp:list-item -->\n\n<!-- wp:list-item -->\n<li>{FEATURE 2}</li>\n<!-- /wp:list-item -->\n\n<!-- wp:list-item -->\n<li>{FEATURE 3}</li>\n<!-- /wp:list-item -->\n\n<!-- wp:list-item -->\n<li>{FEATURE 4}</li>\n<!-- /wp:list-item --></ul>\n<!-- /wp:list --></div>\n<!-- /wp:group --></div>\n<!-- /wp:group --></div>\n<!-- /wp:column --></div>\n<!-- /wp:columns --></div>\n<!-- /wp:group -->\n\n<!-- wp:table {"className":"is-style-stripes"} /-->\n\n<!-- wp:group {"align":"full","style":{"spacing":{"blockGap":"0px"}},"layout":{"type":"constrained","contentSize":"1400px"}} -->\n<div class="wp-block-group alignfull"><!-- wp:columns {"verticalAlignment":"center","style":{"spacing":{"blockGap":{"top":"0","left":"0"},"padding":{"top":"0","right":"0","bottom":"0","left":"0"}},"border":{"radius":"8px"}}} -->\n<div class="wp-block-columns are-vertically-aligned-center" style="border-radius:8px;padding-top:0;padding-right:0;padding-bottom:0;padding-left:0"><!-- wp:column {"verticalAlignment":"center","width":"595px","style":{"spacing":{"padding":{"top":"0","bottom":"0"}}}} -->\n<div class="wp-block-column is-vertically-aligned-center" style="padding-top:0;padding-bottom:0;flex-basis:595px"><!-- wp:group {"className":"title-with-image","style":{"color":{"background":"#f5f5f7"},"border":{"radius":{"topLeft":"8px","bottomLeft":"8px"}},"spacing":{"padding":{"right":"14%","left":"11.7%"}}},"layout":{"type":"constrained","contentSize":""}} -->\n<div class="wp-block-group title-with-image has-background" style="border-top-left-radius:8px;border-bottom-left-radius:8px;background-color:#f5f5f7;padding-right:14%;padding-left:11.7%"><!-- wp:heading {"textAlign":"left","className":"has-dm-sans-font-family","style":{"typography":{"fontSize":"36px","fontStyle":"normal","fontWeight":"700","lineHeight":"1.3"}}} -->\n<h2 class="wp-block-heading has-text-align-left has-dm-sans-font-family" style="font-size:36px;font-style:normal;font-weight:700;line-height:1.3"><strong>{card_pro_name}</strong></h2>\n<!-- /wp:heading -->\n\n<!-- wp:paragraph -->\n<p>{card_pro_des}</p>\n<!-- /wp:paragraph --></div>\n<!-- /wp:group --></div>\n<!-- /wp:column -->\n\n<!-- wp:column {"verticalAlignment":"center"} -->\n<div class="wp-block-column is-vertically-aligned-center"><!-- wp:image {"id":6384,"width":"257px","height":"auto","sizeSlug":"full","linkDestination":"none","style":{"border":{"radius":{"topRight":"8px","bottomRight":"8px"}}}} -->\n<figure class="wp-block-image size-full is-resized has-custom-border"><img src="{IMAGE}" alt="" class="wp-image-6384" style="border-top-right-radius:8px;border-bottom-right-radius:8px;width:257px;height:auto"/></figure>\n<!-- /wp:image --></div>\n<!-- /wp:column --></div>\n<!-- /wp:columns --></div>\n<!-- /wp:group -->\n\n<!-- wp:group {"align":"full","layout":{"type":"constrained","contentSize":"1400px"}} -->\n<div class="wp-block-group alignfull"><!-- wp:columns {"style":{"spacing":{"blockGap":{"left":"19.4%"}}}} -->\n<div class="wp-block-columns"><!-- wp:column {"width":"805px"} -->\n<div class="wp-block-column" style="flex-basis:805px"><!-- wp:paragraph {"className":"has-dm-sans-font-family","style":{"typography":{"fontSize":"15px","lineHeight":"1.6","fontStyle":"normal","fontWeight":"400"}},"textColor":"contrast"} -->\n<p class="has-dm-sans-font-family has-contrast-color has-text-color" style="font-size:15px;font-style:normal;font-weight:400;line-height:1.6"></p>\n<!-- /wp:paragraph -->\n\n<!-- wp:paragraph -->\n<p></p>\n<!-- /wp:paragraph -->\n\n<!-- wp:paragraph -->\n<p></p>\n<!-- /wp:paragraph -->\n\n<!-- wp:heading {"level":1} -->\n<h1 class="wp-block-heading">Specification</h1>\n<!-- /wp:heading -->\n\n<!-- wp:table {"className":"is-style-stripes","style":{"border":{"width":"0px","style":"none"},"spacing":{"margin":{"top":"var:preset|spacing|30","bottom":"var:preset|spacing|30"}}}} -->\n'''

    product_data = {
        'ID': '',
        'Type': 'simple',
        'SKU': '',
        'Name': '',
        'Published': 1,
        'Is featured?': 0,
        'Visibility in catalog': 'visible',
        'Short description': '',
        'Description': existing_description.replace("{PRODUCT NAME}", "{PRODUCT NAME}").replace("{SHORT DESCRIPTION}", "{SHORT DESCRIPTION}").strip(),
        'Date sale price starts': '',
        'Tax status': 'taxable',
        'Tax class': '',
        'In stock?': 1,
        'Stock': '',
        'Regular price': '',  # INR price
        'Categories': '',
        'Tags': '',
        'Images': '',
        'Attribute 1 name': 'brand',
        'Attribute 1 value(s)': '',
        'Attribute 1 visible': 1,
        'Attribute 1 global': 1,
        'Product URL': '',
        'Product Code':'',
        'Meta: _product_code': '',
    }

    try:
        # Inside extract_product_data function
        image_element = tree.xpath('//img[@class="gallery-placeholder__image"]/@src')
        if image_element:
            image_url = image_element[0]
            if not image_url.startswith(('http://', 'https://')):
                # If the URL is relative, make it absolute
                parsed_url = urlparse(url)
                image_url = f"{parsed_url.scheme}://{parsed_url.netloc}{image_url}"
            print(f"Image URL found: {image_url}")
            product_data['image_url'] = image_url
            
        else:
            print("No image URL found")
            
                    
        # Extract SKU
        sku = tree.xpath('//span[contains(text(), "SKU#:")]/text()')
        if sku:
            product_data['SKU'] = sku[0].split(':')[-1].strip()

        # Extract Name
        name_element = tree.xpath('/html/body/div[4]/main/div[2]/div/div[1]/div[1]/div[2]/h1/span')
        brand_element = tree.xpath('/html/body/div[4]/main/div[2]/div/div[1]/div[1]/div[1]/div[1]/strong/text()')

        if name_element:
            name = name_element[0].text_content().strip()
            product_data['Name'] = name

        if brand_element:
            brand = brand_element[0].strip()
            product_data['Attribute 1 value(s)'] = brand

        # Extract Price
        price_element = tree.xpath('/html/body/div[4]/main/div[2]/div/div[1]/div[1]/div[3]/div[3]/span/span/span')
        if price_element:
            price_text = price_element[0].text_content()
            price_match = re.search(r'£(\d+\.\d+)', price_text)
            if price_match:
                price_gbp = float(price_match.group(1))
                price_inr = price_gbp * GBP_TO_INR_CONVERSION_RATE
                product_data['Regular price'] = round(price_inr, 2)

        # Extract Short Description
        short_desc_items = tree.xpath('/html/body/div[4]/main/div[2]/div/div[2]/div/div[2]/div/div[2]/div[1]/div')
        if short_desc_items:
            short_description = ' '.join([item.text_content().strip() for item in short_desc_items])
            product_data['Short description'] = short_description
        
        # Extract Features
        features_elements = tree.xpath('//ul[@class="short-overview"]/li/text()')
        features = [feature.strip() for feature in features_elements if feature.strip()]

        # Prepare a list of features, ensuring it has exactly 4 elements (with placeholders for missing ones)
        for i in range(1, 5):
            if i <= len(features):
                product_data[f'FEATURE {i}'] = features[i - 1]
            else:
                product_data[f'FEATURE {i}'] = ""

        # Update the Description with dynamic features
        product_data['Description'] = product_data['Description'].replace("{FEATURE 1}", product_data['FEATURE 1'])
        product_data['Description'] = product_data['Description'].replace("{FEATURE 2}", product_data['FEATURE 2'])
        product_data['Description'] = product_data['Description'].replace("{FEATURE 3}", product_data['FEATURE 3'])
        product_data['Description'] = product_data['Description'].replace("{FEATURE 4}", product_data['FEATURE 4'])

        # Update the Description with the dynamic values
        # product_data['Description'] = product_data['Description'].replace("{PRODUCT NAME}", product_data['Name'])
        product_data['Description'] = product_data['Description'].replace("{SHORT DESCRIPTION}", product_data['Short description'])
        
        # Extract Categories
        category_elements = tree.xpath('/html/body/div[4]/main/div[2]/div/div[2]/div/div[2]/div/div[1]/ul/li[2]')
        if category_elements:
            category = category_elements[0].text_content().strip()
            standardized_category = standardize_category(category)
            if standardized_category in ["Cables and accessories", "Software License"]:
                product_data['Categories'] = standardized_category
            else:
                product_data['Categories'] = f"Networking, Networking > {standardized_category}"


        # Set Tags
        product_data['Tags'] = f"{product_data['Attribute 1 value(s)']},{standardized_category}"

        # Add product URL
        product_data['Product URL'] = url

        # Extract specifications and generate table
        specs, card_pro_name, card_pro_des = extract_product_specs(url)
        if isinstance(specs, dict):
            table_html = generate_html_table(specs)
            product_data['Description'] += table_html  # Append table to the existing description

        # Update the Description with card_pro_name and card_pro_des
        product_data['Description'] = product_data['Description'].replace("{card_pro_name}", card_pro_name)
        product_data['Description'] = product_data['Description'].replace("{card_pro_des}", card_pro_des)
        print(card_pro_des, card_pro_name)
        
        # Extract Manufacture Code
        manufacture_code_element = tree.xpath('//div[@class="manufacture-code"]/span/text()')
        if manufacture_code_element:
            manufacture_code = manufacture_code_element[0].replace('Manufacture#:', '').strip()
            product_data['Product Code'] = manufacture_code
            product_data['Meta: _product_code'] = manufacture_code
    

    except Exception as e:
        print(f"Error extracting data: {str(e)}")

    return product_data

def extract_product_urls(start_page, end_page):
    # Get base URL from user input
    base_url = input("Enter the base URL (e.g., https://www.stonegroup.co.uk/hardware/storage-and-memory/): ")
    brand_id = input("Enter the brand ID (e.g., 6409) or press Enter if none: ")
    product_links = []

    for page in range(start_page, end_page + 1):
        # Construct URL with optional brand parameter
        url = f"{base_url}?p={page}"
        if brand_id:
            url = f"{base_url}?brand={brand_id}&p={page}"
            
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        product_containers = soup.find_all('div', class_='product-item-info')
        
        for container in product_containers:
            link = container.find('a', class_='product-item-link')
            if link:
                product_links.append(link['href'])
    return product_links

import re

def download_image(image_url, product_code, save_directory):
    # Replace special characters with underscores
    safe_product_code = re.sub(r'[^\w\-_\. ]', '_', product_code)
    filename = f"{safe_product_code}.jpg"
    filepath = os.path.join(save_directory, filename)
    
    try:
        print(f"Attempting to download image from: {image_url}")
        
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        
        if 'image' not in response.headers.get('Content-Type', ''):
            print(f"URL does not point to an image: {image_url}")
            return None
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)
        
        try:
            with Image.open(filepath) as img:
                img.verify()
            print(f"Image downloaded and verified successfully: {filepath}")
            
            current_date = datetime.now()
            year = current_date.year
            month = current_date.strftime("%m")
            
            new_image_url = f"https://www.movantechonline.com/wp-content/uploads/{year}/{month}/{filename}"
            
            return new_image_url
        except Exception as e:
            print(f"Downloaded file is not a valid image: {str(e)}")
            os.remove(filepath)
            return None
        
    except requests.RequestException as e:
        print(f"Error downloading image for {product_code}: {str(e)}")
        return None

def scrape_stone_group():
    products_data = []
    unique_product_codes = set()
    
    start_page = int(input("Enter the starting page number: "))
    end_page = int(input("Enter the ending page number: "))
    
    product_urls = extract_product_urls(start_page, end_page)
    total_products = len(product_urls)
    
    print(f"Found {total_products} products to scrape.")
    
    # Create a directory for saving images
    image_directory = "product_images"
    os.makedirs(image_directory, exist_ok=True)
    print(f"Image directory created: {os.path.abspath(image_directory)}")

    
    for url in tqdm(product_urls, desc="Scraping Products", unit="product"):
        try:
            response = requests.get(url)
            tree = html.fromstring(response.content)
            product_data = extract_product_data(tree, url)
            
            # Check if the Product Code is unique
            if product_data['Product Code'] not in unique_product_codes:
                unique_product_codes.add(product_data['Product Code'])
                
                # Download the image if URL is available
                if 'image_url' in product_data:
                    new_image_url = download_image(product_data['image_url'], product_data['Product Code'], image_directory)
                    if new_image_url:
                        product_data['Images'] = new_image_url
                        product_data['Description'] = product_data['Description'].replace("{IMAGE}", new_image_url)
                    else:
                        print(f"Failed to download image for {product_data['Name']}")
                        product_data['Images'] = ''
                
                tqdm.write(f"Scraped: {product_data['Name']}")
                products_data.append(product_data)
            else:
                tqdm.write(f"Skipped duplicate: {product_data['Name']} (Product Code: {product_data['Product Code']})")
        except Exception as e:
            tqdm.write(f"Error scraping {url}: {str(e)}")
    
    print("Scraping completed. Exporting data to CSV...")
    
    # Create DataFrame and export to CSV
    df = pd.DataFrame(products_data)
    df.to_csv('stone_group_products.csv', index=False)
    
    print("Data exported successfully to stone_group_products.csv")

if __name__ == "__main__":
    scrape_stone_group()




