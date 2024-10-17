from PIL import Image
import os

def resize_image(input_path, output_path, size=(420, 420)):
    try:
        with Image.open(input_path) as img:
            # Create a new image with white background
            new_img = Image.new("RGB", size, (255, 255, 255))
            
            # Resize the original image while maintaining aspect ratio
            img.thumbnail(size, Image.LANCZOS)
            
            # Calculate position to paste the resized image
            paste_box = ((size[0] - img.size[0]) // 2, (size[1] - img.size[1]) // 2)
            
            # Paste the resized image onto the white background
            new_img.paste(img, paste_box)
            
            # Save the result
            new_img.save(output_path)
        print(f"Image resized successfully and saved as {output_path}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def main():
    input_directory = "input_images"
    output_directory = "output_images"
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    # Process all images in the input directory
    for filename in os.listdir(input_directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            input_path = os.path.join(input_directory, filename)
            output_path = os.path.join(output_directory, f"{filename}")
            resize_image(input_path, output_path)

if __name__ == "__main__":
    main()