import requests
from osgeo import ogr, osr
import os
from typing import List, Dict, Any, Tuple

class OceanObs:
    BASE_URL = "https://dmigw.govcloud.dk/v2/oceanObs/collections"
    API_KEY = "01d3f954-0ee0-4235-ad92-dbd6898e3793"
    headers = {"X-Gravitee-Api-Key": API_KEY}

    def get_collections(self) -> Dict[str, Any]:
        """Fetch all available collections in the API."""
        response = requests.get(self.BASE_URL, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_items(self, collection_name: str, limit: int = 1000, offset: int = 0, **filters) -> Dict[str, Any]:
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

    def get_stationid(self, bbox: List[float]) -> List[str]:
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

    def get_active_stations_for_bbox(self, bbox: List[float]) -> List[Dict[str, Any]]:
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

    def get_station_observations(self, station_id: str, datetime_range: str) -> List[Dict[str, Any]]:
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

    def save_data_to_file(self, data: List[Dict[str, Any]], file_path: str, layer_name: str, spatial_ref: osr.SpatialReference, fields: List[Tuple[str, int, int]]) -> None:
        """Save data to a point layer file using GDAL."""
        ogr.RegisterAll()
        driver = ogr.GetDriverByName("GPKG")
        if driver is None:
            raise ValueError("GPKG driver is not available.")
        data_source = driver.CreateDataSource(file_path)
        if data_source is None:
            raise ValueError(f"Could not create file: {file_path}")
        layer = data_source.CreateLayer(layer_name, spatial_ref, ogr.wkbPoint)
        if layer is None:
            raise ValueError("Layer creation failed.")
        for field_name, field_type, field_width in fields:
            field = ogr.FieldDefn(field_name, field_type)
            if field_width:
                field.SetWidth(field_width)
            layer.CreateField(field)
        for item in data:
            lon, lat = item["geometry"]["coordinates"]
            point = ogr.Geometry(ogr.wkbPoint)
            point.AddPoint(lon, lat)
            feature = ogr.Feature(layer.GetLayerDefn())
            feature.SetGeometry(point)
            for field_name, _, _ in fields:
                feature_value = item["properties"].get(field_name)
                if feature_value is not None:
                    feature.SetField(str(field_name), feature_value)
            layer.CreateFeature(feature)
            feature.Destroy()
        data_source.Destroy()

    def retrieve_stations_data(self, bbox: List[float], datetime_range: str, output_directory: str) -> None:
        """Retrieve and save observations for all active stations to station-specific GeoPackage files."""
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
            file_path = os.path.join(output_directory, f"{station_id}.gpkg")
            fields = [
                ("created", ogr.OFTString, 50),
                ("observed", ogr.OFTString, 50),
                ("parameterId", ogr.OFTString, 50),
                ("qcStatus", ogr.OFTString, 20),
                ("stationId", ogr.OFTString, 20),
                ("value", ogr.OFTReal, None)
            ]
            self.save_data_to_file(observations, file_path, station_id, spatial_ref, fields)
            print(f"Data for station {station_id} saved to {file_path}")
