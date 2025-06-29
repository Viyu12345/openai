# Amazon's Ancient Ruins

The **Amazons' Ancient Ruins** is a powerful AI + satellite data pipeline designed to detect potential ancient human settlements in the Amazon rainforest. This project combines Sentinel-2 imagery, texts, and spatial data analysis with cutting-edge AI tools to identify regions with archaeological significance. You can check thenew1.py to see how I got the results and proofs of historical sites which I have listed on my /train page. The results got from thenew1.py have been cleared from unwanted words and then displayed on the /train page.



## Project Goals

- Identify potential archaeological sites in the Amazon basin.
- Combine multispectral satellite data (Sentinel-2) with archaeological literature.
- Leverage AI (OpenAI models) to detect anomalies and generate reproducible coordinates.
- Support archaeological discovery efforts using remote sensing and LLM-powered inference.



## Data Sources

- **Sentinel-2 Satellite Imagery** (via AWS S3 / STAC API)
- **NASA Global Datasets** (e.g., elevation, canopy cover)
- **OpenTopography LIDAR Data**
- **COP30 Regional Models** (carbon and land use)
- **Historical Archaeological Reports & Papers**



## Technologies Used

- Python 3.10+
- `rasterio`, `matplotlib`, `numpy` for geospatial and image processing
- `pystac-client`, `boto3` for Sentinel-2 data access
- `shapely`, `pyproj`, `utm` for coordinate transformations
- OpenAI o4-mini for anomaly detection and site hypothesis generation



## How It Works

1. **Region Selection**  
   Define a bounding box (e.g., Acre, Bolivia) and retrieve satellite imagery tiles.

2. **Data Extraction**  
   Extract Sentinel-2 bands (e.g., B8, B4, B3, B2) and preprocess images.

3. **Feature Analysis**  
   Compute vegetation indices (NDVI), elevation models, and terrain anomalies.

4. **Text Analysis**  
   Parse archaeological texts for mentions of distances, rivers, coordinates, and cultural indicators.

5. **Anomaly Detection**  
   Use AI to cross-reference physical anomalies with historical clues and generate predicted coordinates.

6. **Visualization**  
   Plot NDVI maps, elevation slices, and potential site markers on maps.



## 📖 Citation / Acknowledgements

Inspired by decades of research on pre-Columbian civilizations in the Amazon. Thanks to:

- NASA Earth Data
- OpenTopography
- Copernicus Sentinel Program
- Archaeological literature (Fawcett, Roosevelt, etc.)
