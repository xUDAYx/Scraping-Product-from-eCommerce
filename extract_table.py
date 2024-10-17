import requests
from bs4 import BeautifulSoup

# Function to extract product specifications from the webpage
def extract_product_specs(url):
    response = requests.get(url)
   
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        left_column = soup.select_one('div.column-left')
        right_column = soup.select_one('div.column-right')
       
        if left_column and right_column:
            specs = {}
            card_pro_name = ""
            card_pro_des = ""
           
            def extract_specs_from_column(column):
                spec_rows = column.find_all('div', class_='specification-row')
                for row in spec_rows:
                    title_tag = row.find('strong', class_='specification-row-title')
                    info_tag = row.find('span', class_='specification-info')
                    if title_tag and info_tag:
                        title = title_tag.text.strip()
                        info = info_tag.text.strip()
                        specs[title] = info

            extract_specs_from_column(right_column)
            extract_specs_from_column(left_column)
            
            # Check if there's a product description and split it
            if "Product Description" in specs:
                full_description = specs["Product Description"]
                split_description = full_description.split(" - ", 1)
                if len(split_description) > 1:
                    card_pro_name = split_description[0].strip()
                    card_pro_des = split_description[1].strip()
                else:
                    card_pro_name = full_description
                del specs["Product Description"]
           
            return specs, card_pro_name, card_pro_des
        else:
            return "One or both specification columns not found on the page.", "", ""
    else:
        return f"Failed to retrieve the webpage. Status code: {response.status_code}", "", ""

# Function to capitalize the first word of a string
def capitalize_first_word(text):
    if text:
        words = text.split()
        if len(words) > 0:
            words[0] = words[0].capitalize()
        return ' '.join(words)
    return text

# Function to generate HTML table for product specifications
def generate_html_table(specs):
    
    html_table = """
    <figure class="wp-block-table is-style-stripes" style="margin-top:var(--wp--preset--spacing--30);margin-bottom:var(--wp--preset--spacing--30)">
    <table class="has-fixed-layout" style="border-style:none;border-width:0px">
    <tbody>
    """
    
    for title, info in specs.items():
        html_table += f"""
        <tr>
            <td><strong>{title}</strong></td>
            <td>{info}</td>
        </tr>
        """
    
    html_table += """
    </tbody></table></figure>\n<!-- /wp:table -->\n\n<!-- wp:paragraph {"className":"has-dm-sans-font-family","style":{"typography":{"fontSize":"15px","fontStyle":"normal","fontWeight":"400","lineHeight":"1.6"}}} -->\n<p class="has-dm-sans-font-family" style="font-size:15px;font-style:normal;font-weight:400;line-height:1.6"></p>\n<!-- /wp:paragraph --></div>\n<!-- /wp:column --></div>\n<!-- /wp:columns --></div>\n<!-- /wp:group --></div>\n<!-- /wp:group -->\n\n<!-- wp:paragraph -->\n<p></p>\n<!-- /wp:paragraph -->
    """
    
    return html_table  

# URL of the product page (example)
url = "https://www.stonegroup.co.uk/netgear-nighthawk-rax30-wireless-router-802-11a-b-g-n-ac-ax-desktop-1tnetrrb-004740/"
# Extract the product specifications, name, and description
product_specs, card_pro_name, card_pro_des = extract_product_specs(url)

# Capitalize the first word of card_pro_des
card_pro_des = capitalize_first_word(card_pro_des)

# Use the product_specs, card_pro_name, and updated card_pro_des as needed
if isinstance(product_specs, dict):
    generated_table_html = generate_html_table(product_specs)
    print(f"Card Product Name: {card_pro_name}")
    print(f"Card Product Description (with capitalized first word): {card_pro_des}")
else:
    print(product_specs)
