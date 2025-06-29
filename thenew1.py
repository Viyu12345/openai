import boto3
from botocore import UNSIGNED
from botocore.config import Config
import openai
import base64
import requests
from PIL import Image
from io import BytesIO
import os
import math
import rasterio
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np
nature = ""
nature1 = ""
def resize_image(img, max_pixels=89478485):
    current_pixels = img.width * img.height
    if current_pixels <= max_pixels:
        return img
    scale_factor = math.sqrt(max_pixels / current_pixels)
    new_width = int(img.width * scale_factor)
    new_height = int(img.height * scale_factor)
    return img.resize((new_width, new_height), Image.LANCZOS)

api_key = ""
client = openai.OpenAI(api_key=api_key)
images = []
responses = []
cop30 = []
articles = []

# Set up unsigned S3 client
s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED), region_name='eu-central-1')

bucket = 'sentinel-s2-l1c'
prefix = ''  # Example: Tile 20MPS on Jan 5, 2023

# List files
response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)

tiles = [
    {'utm_zone': '20', 'letter1': 'S', 'letter2': 'WD'},
    {'utm_zone': '19', 'letter1': 'S', 'letter2': 'VC'},
    {'utm_zone': '22', 'letter1': 'S', 'letter2': 'XD'}
]

dates = [
    {'year': '2023', 'month': '1', 'day': '5'},
    {'year': '2023', 'month': '6', 'day': '10'}
]


for tile in tiles:
    for date in dates:
        prefix = f"tiles/{tile['utm_zone']}/{tile['letter1']}/{tile['letter2']}/{date['year']}/{date['month']}/{date['day']}/0/"
        print(f"Processing tile {tile['utm_zone']}{tile['letter1']}{tile['letter2']} for {date['year']}-{date['month']}-{date['day']}")
        try:
            response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
            if response:
                print(f"Found {len(response['Contents'])} files in {prefix}")
                for obj in response['Contents']:
                    images.append({'key': obj['Key'], 'tile': f"{tile['utm_zone']}{tile['letter1']}{tile['letter2']}", 'date': f"{date['year']}-{date['month']}-{date['day']}"})
            else:
                print(f"No files found in {prefix}")
        except Exception as e:
            print(f"Error listing S3 objects for {prefix}: {str(e)}")

# Process Sentinel-2 images
for idx, image_info in enumerate(images):
    file_key = image_info['key']
    tile = image_info['tile']
    date = image_info['date']
    url = f"https://{bucket}.s3.eu-central-1.amazonaws.com/{file_key}"
    print(f"Processing Sentinel-2 image {idx+1}: {file_key} (Tile: {tile}, Date: {date})")
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to download {url}: Status {response.status_code}")
        continue
    img = Image.open(BytesIO(response.content))
    print(f"🔍 Original size: {img.width} x {img.height} = {img.width * img.height} pixels")
    img = resize_image(img)
    print(f"✅ Resized to: {img.width} x {img.height} = {img.width * img.height} pixels")
    if img.width * img.height > 89478485:
        print(f"❌ Still too large after resizing: {img.width * img.height}")
        continue
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
    data_url = f"data:image/png;base64,{base64_image}"
    nature = client.chat.completions.create(
        model="o4-mini-2025-04-16",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": data_url}},
                    {"type": "text",
                     "text": "Check out the article by nature about pre columbian earth builders settled along the entire southern rim of the amazon and ckeck if the image I provided somewhat matches with the information also find out the coordinates if you can. Also check if any new proofs of historical sites can be found with its reference"}
                ]
            }
        ]
    )
    print(nature.choices[0].message.content.strip())
    responsing = client.chat.completions.create(
        model="o4-mini-2025-04-16",
        messages=[
            {
                "role": "user",
                "content": [

                    {"type": "text",
                     "text": f"Do you think {nature}'s contents match with the article by science.org that More than 10,000 pre-Columbian earthworks are still hidden throughout Amazonia. If yes, list them. Also check if some new information is obtained or if a new proof of a historical site's information can be obtained"}

                ]
            }
        ]
    )
    articles.append("Nature Sentinel:" + nature.choices[0].message.content.strip())
    articles.append("Matches with Science.org: "+responsing.choices[0].message.content.strip())
    print(nature.choices[0].message.content.strip())
    print(responsing.choices[0].message.content.strip())
    response = client.chat.completions.create(
        model="o4-mini-2025-04-16",
        messages=[
            {
                "role": "user",
                "content": [
                        {"type": "image_url", "image_url": {"url": data_url}},
                        {"type": "text", "text": "Do you think this might be a historical site and where in the Amazon rainforests could this be? Try to predict approximate coordinates with latitudes and longitudes and also tell if it is a discovered site or not. Also check if any historical site's proof  could be obtained from the reference"}
                    ]
                }
            ]
        )

    result = response.choices[0].message.content.strip()
    responses.append("sentinel 2:"+result)
    print(result)
bounding_boxes = [
    {'south': -28.08, 'north': -28.00, 'west': -48.67, 'east': -48.60},
    {'south': -28.10, 'north': -28.02, 'west': -48.65, 'east': -48.58},
    {'south': -28.12, 'north': -28.04, 'west': -48.63, 'east': -48.56}
]


base_params = {
    'demtype': 'COP30',
    'outputFormat': 'GTiff',
    'API_Key': 'YOUR_API_KEY'
}
for i, bbox in enumerate(bounding_boxes):
    url = 'https://portal.opentopography.org/API/globaldem'
    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ Failed to fetch data for bounding box {i+1}: {response.status_code}")
        continue
    try:
        with rasterio.open(BytesIO(response.content)) as dataset:
            elevation = dataset.read(1)
            profile = dataset.profile
            norm = Normalize(vmin=np.min(elevation), vmax=np.max(elevation))
            normalized_data = norm(elevation)
            image_8bit = (normalized_data * 255).astype(np.uint8)
            colormap = plt.get_cmap('terrain')
            color_mapped_image = colormap(normalized_data)
            rgb_image = (color_mapped_image[:, :, :3] * 255).astype(np.uint8)
            filename = f"elevation_map_{i+1}.png"
            img = Image.fromarray(rgb_image)
            img = resize_image(img)
            if img.width * img.height > 89478485:
                print(f"❌ Still too large after resizing: {img.width * img.height}")
                continue
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)
            base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
            data_url = f"data:image/png;base64,{base64_image}"
            nature1 = client.chat.completions.create(
                model="o4-mini-2025-04-16",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": data_url}},
                            {"type": "text",
                             "text": "Check out the article by nature about pre columbian earth builders settled along the entire southern rim of the amazon and ckeck if the image I provided somewhat matches with the information also find out the coordinates if you can. Also check if any new proof of historical sites could be obtained"}
                        ]
                    }
                ]
            )
            responsing1 = client.chat.completions.create(
                model="o4-mini-2025-04-16",
                messages=[
                    {
                        "role": "user",
                        "content": [

                            {"type": "text",
                             "text": f"Do you think {nature1.choices[0].message.content.strip()}'s contents match with the article by science.org that More than 10,000 pre-Columbian earthworks are still hidden throughout Amazonia. If yes, list them. Check if any new proof of any historical site could be obtained"}

                        ]
                    }
                ]
            )
            articles.append("Nature COP30:" + nature1.choices[0].message.content.strip())
            articles.append("Nature 1 matches with science.org:" + responsing1.choices[0].message.content.strip())
            print(nature1.choices[0].message.content.strip())
            response = client.chat.completions.create(
                model="o4-mini-2025-04-16",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": data_url}},
                            {"type": "text",
                             "text": "Scan this for geometric shapes (rectangles, circles, straight ditches). Check if any proofs of a historical site is obtained"}
                        ]
                    }
                ]
            )
            print(response.choices[0].message.content.strip())
            cop30.append(response.choices[0].message.content.strip())
    except Exception as e:
        print(f"❌ Error processing bounding box {i+1}: {str(e)}")

responser = client.chat.completions.create(
    model="o4-mini-2025-04-16",
    messages=[
            {
                "role": "user",
                "content": [

                    {"type": "text", "text": f"Now refer to the books and articles:( the archaeology of the Upper Amazon, Complexity and Interaction of the Andean Tropical Forest which is edited by Ryan Clasby and Jason Nesbitt, ArcheoBlog on jqjacobs.net, Ethics in Archaeological Lidar. Journal of Computer Applications in Archaeology 3:1, pages 76-91, .G., Schaan, D.P., Robinson, M. et al. Pre-Columbian earth-builders settled along the entire southern rim of the Amazon, Denise Maria Cavalcante Gomes. Urban Archaeology in the Lower Amazon: Fieldwork Uncovering Large Pre-Colonial Villages in Santarém City, Brazil. Journal of Field Archaeology 0:0, pages 1-20, Jose Iriarte, Mark Robinson, Jonas de Souza, Antonia Damasceno, Franciele da Silva, Francisco Nakahara, Alceu Ranzi & Luiz Aragao. (2020) Geometry by Design: Contribution of Lidar to the Understanding of Settlement Patterns of the Mound Villages in SW Amazonia. Journal of Computer Applications in Archaeology 3:1, pages 151-169, Khan, S., Aragão, L., & Iriarte, J. (2017). A UAV–lidar system to map Amazonian rainforest and its ancient landscape transformations. International Journal of Remote Sensing, 38(8–10), 2313–2330, Prümers, H., Betancourt, C.J., Iriarte, J. et al. Lidar reveals pre-Hispanic low-density urbanism in the Bolivian Amazon. Nature 606, 325–328 (2022), Vinicius Peripato et al, (2023) More than 10,000 pre-Columbian earthworks are still hidden throughout Amazonia. Science 382:6666, pages 103-109, Fabien H. Wagner, Vinícius Peripato, Renato Kipnis, Sara L. Werdesheim, Ricardo Dalagnol, Luiz E.O.C. Aragão & Mayumi C. M. Hirye. (2022) Fast computation of digital terrain model anomalies based on LiDAR data for geoglyph detection in the Amazon. Remote Sensing Letters 13:9, pages 935-945, Robert S. Walker, Jeffrey R. Ferguson, Angelica Olmeda, Marcus J. Hamilton, Jim Elghammer & Briggs Buchanan. (2023) Predicting the geographic distribution of ancient Amazonian archaeological sites with machine learning. PeerJ 11, pages e15137, Per Stenborg, Denise Schaan, Camila G. Figueiredo, Contours of the Past: LiDAR Data Expands the Limits of Late Pre-Columbian Human Settlement in the Santarém Region, Lower Amazon, Journal of Field Archaeology, (2018) Vol. 43, No. 1, 44–57, Lost City of Z on archive.org, The Amazon and Madeira rivers : sketches and descriptions from the note-book of an explorer on loc.gov)  and see if {responses} or {cop30} or {nature} or {nature1} match with any context in the book also extract every sentence that mentions a river, compass direction, or distance travelled. Keep different columns for mathcing responses to the arrays and sentences extracted. Also give coordinates if possible. Check if any proof of a historical site is obtained."}


            ]
        }
    ]
)

articles.append(responser.choices[0].message.content.strip())
print(responser.choices[0].message.content.strip())
get = client.chat.completions.create(
    model="o4-mini-2025-04-16",
messages=[
            {
                "role": "user",
                "content": [

                    {"type": "text", "text":f"refer to all the data from nasa earth observatory, earth data.nasa.gov's NASA Shuttle Radar Topography Mission Global 1 arc second V003 and LBA-ECO LC-15 SRTM30 Digital Elevation Model Data and a Earth Observation Data Cubes for Brazil on Registry of Open Data for AWS and check if something like a archeological sites for amazon rainforest are there and also see if it matches with {articles}. Give both responses and tell me in plain English whether the surface patterns look man-made or natural. Include a 0–1 confidence."}


            ]
        }
    ]
)
responses.append(get)
print(get.choices[0].message.content.strip())
combination = client.chat.completions.create(
    model="o4-mini-2025-04-16",
    messages=[
        {
            "role":"user",
            "content":[
                {"type":"text","text":f"Check if {responses},{cop30} or {articles} or {images} images match any info or give the proofs of any historical site"}
            ]
        }
    ]
)
print(combination)
