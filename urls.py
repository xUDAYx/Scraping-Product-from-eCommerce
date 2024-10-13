import requests
from bs4 import BeautifulSoup

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

if __name__ == "__main__":
    num_pages = int(input("Enter the number of pages to scrape: "))
    product_urls = extract_product_urls(num_pages)
    for url in product_urls:
        print(url)
