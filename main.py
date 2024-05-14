import streamlit as st
import requests
import zipfile
import io
from PIL import Image


def fetch_image_urls(registration_number):
    # Assuming the API returns a list of image URLs for a given registration number
    api_url = "https://api-procx-v1.drivex.in/api/leads/vehicle/images/"
    response = requests.get(api_url, params={"reg_num": registration_number})
    if response.status_code == 200:
        return response.json()[
            "data"
        ]  # Assuming the API returns JSON with URLs
    else:
        print(f"Failed to fetch URLs. Status code: {response.status_code}")
        return []


def download_image(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"Downloaded {filename}")
    else:
        print(
            f"Failed to download {filename}. Status code: {response.status_code}"
        )


def main():
    st.title("Vehicle Images Fetch and Download")
    query = st.text_input("Enter Registration Number:")
    submit = st.button("Submit")

    if submit:
        image_urls = fetch_image_urls(query)
        if image_urls:
            st.write(f"Found {len(image_urls)} images for '{query}':")

            # Create a bytes buffer for the zip file
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(
                zip_buffer, "w", zipfile.ZIP_DEFLATED
            ) as zip_file:
                for i, url in enumerate(image_urls):
                    filename = f"{query}_{i+1}.jpeg"  # Change the file extension to .png
                    response = requests.get(url)
                    if response.status_code == 200:
                        # Convert the image from webp to png
                        image = Image.open(io.BytesIO(response.content))
                        png_buffer = io.BytesIO()
                        image.save(png_buffer, format="JPEG")
                        png_buffer.seek(0)
                        # Write the converted image to the zip
                        zip_file.writestr(filename, png_buffer.getvalue())
                    else:
                        st.write(
                            f"Failed to download {filename}. Status code: {response.status_code}"
                        )

            # Provide a download button for the zip file
            zip_buffer.seek(0)
            st.download_button(
                label="Download All Images",
                data=zip_buffer,
                file_name=f"{query}_images.zip",
                mime="application/zip",
            )
        else:
            st.write(f"No images found for '{query}'.")


if __name__ == "__main__":
    main()
