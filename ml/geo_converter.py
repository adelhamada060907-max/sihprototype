"""
AquaGuard AI - Geospatial Coordinate Converter
Converts side-scan sonar image pixel bounding boxes and slant ranges into
real-world WGS84 Geographic Coordinates (Latitude, Longitude, Target Depth).
"""

import math
from datetime import datetime

class SonarGeoConverter:
    """
    Geospatial translator converting pixel offsets in side-scan sonar imagery to
    georeferenced WGS84 Latitude and Longitude coordinates.
    """
    EARTH_RADIUS_METERS = 6378137.0 # WGS84 Equatorial Radius

    @staticmethod
    def calculate_target_gps(vessel_lat: float, vessel_lon: float, vessel_heading_deg: float,
                             across_track_m: float, along_track_m: float) -> tuple:
        """
        Calculates exact target latitude and longitude given vessel position,
        heading angle, and starboard/port across-track & along-track offsets in meters.
        """
        # Convert heading to radians (0 deg = North, 90 deg = East)
        heading_rad = math.radians(vessel_heading_deg)
        
        # Calculate total offset distance and azimuth bearing
        # across_track > 0 is Starboard (Right), < 0 is Port (Left)
        azimuth_rad = heading_rad + math.atan2(across_track_m, along_track_m)
        distance_m = math.sqrt(across_track_m**2 + along_track_m**2)
        
        # Angular distance in radians
        delta = distance_m / SonarGeoConverter.EARTH_RADIUS_METERS
        
        lat1 = math.radians(vessel_lat)
        lon1 = math.radians(vessel_lon)
        
        # Haversine / Direct Spherical formula
        lat2 = math.asin(math.sin(lat1) * math.cos(delta) +
                         math.cos(lat1) * math.sin(delta) * math.cos(azimuth_rad))
        
        lon2 = lon1 + math.atan2(math.sin(azimuth_rad) * math.sin(delta) * math.cos(lat1),
                                 math.cos(delta) - math.sin(lat1) * math.sin(lat2))
        
        target_lat = math.degrees(lat2)
        target_lon = math.degrees(lon2)
        
        return round(target_lat, 6), round(target_lon, 6)

    def convert_bbox_to_georeference(self, bbox_norm: list, telemetry: dict, img_width=640, img_height=640) -> dict:
        """
        Maps normalized bounding box center (x_center, y_center) to real-world position.
        telemetry dict contains:
            - latitude
            - longitude
            - depth_meters
            - sonar_heading_deg
            - range_resolution_m (optional, default 0.1 m/px)
        """
        vessel_lat = float(telemetry.get("latitude", 15.4989))
        vessel_lon = float(telemetry.get("longitude", 73.8278))
        vessel_heading = float(telemetry.get("sonar_heading_deg", 45.0))
        vessel_depth = float(telemetry.get("depth_meters", 20.0))
        m_per_pixel = float(telemetry.get("range_resolution_m", 0.1))
        
        x_center_norm, y_center_norm, _, _ = bbox_norm
        
        # Pixel coordinates
        px_x = x_center_norm * img_width
        px_y = y_center_norm * img_height
        
        # Center nadir gap position (vessel ground track line)
        nadir_x = img_width / 2.0
        nadir_y = img_height / 2.0
        
        # Across-track offset (positive = Starboard/Right, negative = Port/Left)
        across_track_m = (px_x - nadir_x) * m_per_pixel
        
        # Along-track offset (positive = Forward along tow track, negative = Aft)
        along_track_m = (nadir_y - px_y) * m_per_pixel
        
        target_lat, target_lon = self.calculate_target_gps(
            vessel_lat, vessel_lon, vessel_heading, across_track_m, along_track_m
        )
        
        # Estimate seabed target depth (slight slant-range variation)
        slant_range_m = math.sqrt(across_track_m**2 + vessel_depth**2)
        target_depth_m = round(min(100.0, max(1.0, slant_range_m)), 2)
        
        return {
            "latitude": target_lat,
            "longitude": target_lon,
            "depth_meters": target_depth_m,
            "across_track_m": round(across_track_m, 2),
            "along_track_m": round(along_track_m, 2),
            "timestamp": telemetry.get("timestamp", datetime.utcnow().isoformat() + "Z")
        }


# Quick test interface
if __name__ == "__main__":
    converter = SonarGeoConverter()
    telemetry_example = {
        "latitude": 15.4989,
        "longitude": 73.8278,
        "depth_meters": 25.0,
        "sonar_heading_deg": 90.0,
        "timestamp": "2026-09-06T00:00:00Z"
    }
    geo_res = converter.convert_bbox_to_georeference([0.7, 0.4, 0.1, 0.1], telemetry_example)
    print(f"[AquaGuard GeoConverter] Output target coordinates: Lat={geo_res['latitude']}, Lon={geo_res['longitude']}, Depth={geo_res['depth_meters']}m")
