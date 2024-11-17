import requests
from osgeo import ogr, osr
import os

class OceanObs:
    BASE_URL = "https://dmigw.govcloud.dk/v2/oceanObs/collections"
    API_KEY = "01d3f954-0ee0-4235-ad92-dbd6898e3793"
    headers = {"X-Gravitee-Api-Key": API_KEY}

    def get_collections(self):
        """Fetch all available collections in the API."""
        response = requests.get(self.BASE_URL, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_items(self, collection_name, limit=1000, offset=0, **filters):
        """Fetch items from a specified collection with optional filters."""
        url = f"{self.BASE_URL}/{collection_name}/items"
        params = {
            "limit": limit,
            "offset": offset,
            "api-key": self.API_KEY
        }
        params.update(filters)
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_stationid(self, bbox):
        """Fetch station IDs based on a bounding box."""
        url = f"{self.BASE_URL}/station/items"
        params = {
            "bbox": f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
            "api-key": self.API_KEY
        }
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            data = response.json()
            station_ids = [item["properties"]["stationId"] for item in data.get("features", [])]
            return station_ids
        else:
            response.raise_for_status()

    def get_active_stations_for_bbox(self, bbox):
        """Fetch all active stations within a specified bounding box."""
        url = f"{self.BASE_URL}/station/items"
        params = {
            "status": "Active",
            "bbox": f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
            "api-key": self.API_KEY
        }
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json().get("features", [])
        else:
            response.raise_for_status()

    def save_stations_to_file(self, bbox, file_path):
        """Save active stations within a bounding box to a point layer file using GDAL."""
        active_stations = self.get_active_stations_for_bbox(bbox)
        ogr.RegisterAll()
        driver = ogr.GetDriverByName("ESRI Shapefile")
        if driver is None:
            raise ValueError("ESRI Shapefile driver is not available.")
        data_source = driver.CreateDataSource(file_path)
        if data_source is None:
            raise ValueError(f"Could not create file: {file_path}")
        spatial_ref = osr.SpatialReference()
        spatial_ref.ImportFromEPSG(4326)
        layer = data_source.CreateLayer("active_stations", spatial_ref, ogr.wkbPoint)
        if layer is None:
            raise ValueError("Layer creation failed.")
        field_station_id = ogr.FieldDefn("stationId", ogr.OFTString)
        field_station_id.SetWidth(50)
        layer.CreateField(field_station_id)
        field_name = ogr.FieldDefn("name", ogr.OFTString)
        field_name.SetWidth(100)
        layer.CreateField(field_name)
        for station in active_stations:
            lon, lat = station["geometry"]["coordinates"]
            station_id = station["properties"]["stationId"]
            name = station["properties"].get("name", "Unknown")
            point = ogr.Geometry(ogr.wkbPoint)
            point.AddPoint(lon, lat)
            feature = ogr.Feature(layer.GetLayerDefn())
            feature.SetGeometry(point)
            feature.SetField("stationId", station_id)
            feature.SetField("name", name)
            layer.CreateFeature(feature)
            feature.Destroy()
        data_source.Destroy()

    # New method to get observations for a station
    def get_station_observations(self, station_id, datetime_range):
        """Fetch observations for a given station within a specified time window."""
        url = f"{self.BASE_URL}/observation/items"
        params = {
            "stationId": station_id,
            "datetime": datetime_range,
            "api-key": self.API_KEY
        }
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json().get("features", [])
        else:
            response.raise_for_status()

    # New method to save observations for each station to separate shapefiles
    def save_observations_to_station_files(self, bbox, datetime_range, output_directory):
        """Retrieve and save observations for all active stations to station-specific shapefiles."""
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        active_stations = self.get_active_stations_for_bbox(bbox)
        spatial_ref = osr.SpatialReference()
        spatial_ref.ImportFromEPSG(4326)
        for station in active_stations:
            station_id = station["properties"]["stationId"]
            name = station["properties"].get("name", "Unknown")
            print(f"Fetching data for station {station_id} ({name})...")
            observations = self.get_station_observations(station_id, datetime_range)
            if not observations:
                print(f"No observations found for station {station_id} in the specified time window.")
                continue
            file_path = os.path.join(output_directory, f"{station_id}.shp")
            driver = ogr.GetDriverByName("ESRI Shapefile")
            data_source = driver.CreateDataSource(file_path)
            layer = data_source.CreateLayer(station_id, spatial_ref, ogr.wkbPoint)
            field_time = ogr.FieldDefn("datetime", ogr.OFTString)
            field_time.SetWidth(25)
            layer.CreateField(field_time)
            field_param = ogr.FieldDefn("parameter", ogr.OFTString)
            field_param.SetWidth(50)
            layer.CreateField(field_param)
            field_value = ogr.FieldDefn("value", ogr.OFTReal)
            layer.CreateField(field_value)
            for observation in observations:
                lon, lat = observation["geometry"]["coordinates"]
                datetime = observation["properties"]["observed"]
                parameter = observation["properties"].get("parameterId", "Unknown")
                value = observation["properties"].get("value", 0.0)
                point = ogr.Geometry(ogr.wkbPoint)
                point.AddPoint(lon, lat)
                feature = ogr.Feature(layer.GetLayerDefn())
                feature.SetGeometry(point)
                feature.SetField("datetime", datetime)
                feature.SetField("parameter", parameter)
                feature.SetField("value", value)
                layer.CreateFeature(feature)
                feature.Destroy()
            data_source.Destroy()
            print(f"Data for station {station_id} saved to {file_path}")