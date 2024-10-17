import os
import requests
from requests_html import HTMLSession

def download_image(url, save_directory):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            image_name = url.split("/")[-1]
            image_path = os.path.join(save_directory, image_name)
            with open(image_path, 'wb') as file:
                file.write(response.content)
            print(f"[SUCCESS] Downloaded: {image_name}")
        else:
            print(f"[ERROR] Failed to download {url}. Status code: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] An error occurred while downloading {url}: {e}")

def scrape_specific_image(website_url, save_directory):
    print(f"\n[INFO] Starting to scrape images from: {website_url}\n")
    
    # Create an HTML session
    session = HTMLSession()
    response = session.get(website_url)
    
    # Render the JavaScript
    response.html.render(timeout=20)

    # Locate the specific image using the provided CSS selector
    specific_img = response.html.find('.fotorama__stage__frame > img:nth-child(1)', first=True)
    
    if specific_img and 'src' in specific_img.attrs:
        img_url = specific_img.attrs['src']
        
        # Print URL of the image
        print(f"  - [INFO] Image URL: {img_url}")

        # Download the specific image
        download_image(img_url, save_directory)

        print(f"\n[INFO] Finished downloading the image.")
    else:
        print("[ERROR] Image not found at the specified selector.")

def main():
    # The website URL to scrape
    website_url = "https://www.stonegroup.co.uk/extreme-networks-extremewireless-ap510c-radio-access-point-1tnetrrb-004596/"
    
    # Specify the directory to save images
    save_directory = "downloaded_images"

    # Create directory if it does not exist
    os.makedirs(save_directory, exist_ok=True)

    scrape_specific_image(website_url, save_directory)

if __name__ == "__main__":
    main()
