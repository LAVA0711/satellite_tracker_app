import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/satellite_type.dart';

class Satellite {
  final int id;
  final String name;
  final double latitude;
  final double? longitude;
  final double altitude;
  final double distanceFromEarth;
  final double distanceFromMoon;

  Satellite({
    required this.id,
    required this.name,
    required this.latitude,
    required this.longitude,
    required this.altitude,
    required this.distanceFromEarth,
    required this.distanceFromMoon,
  });

  factory Satellite.fromJson(Map<String, dynamic> json) {
    return Satellite(
      id: json['satellite_id'],
      name: json['name'],
      latitude: json['latitude'],
      longitude: json['longitude'],
      altitude: json['altitude'],
      distanceFromEarth: json['distance_from_earth'],
      distanceFromMoon: json['distance_from_moon'],
    );
  }

  String toJsonString() {
    return '''
      {
        "satellite_id": $id,
        "name": "$name",
        "latitude": $latitude,
        "longitude": $longitude,
        "altitude": $altitude,
        "distance_from_earth": $distanceFromEarth,
        "distance_from_moon": $distanceFromMoon
      }
    ''';
  }
}

class SatelliteService {
  static const String baseUrl = "https://your-backend-url.com";  // Replace with your actual backend URL

  // Fetch satellite types from MongoDB Atlas via your backend API
  static Future<List<SatelliteType>> fetchSatelliteTypes() async {
    final response = await http.get(Uri.parse('$baseUrl/satellite-types'));

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      final List types = data['categories'];
      return types.map((json) => SatelliteType.fromJson(json)).toList();
    } else {
      throw Exception("Failed to fetch satellite types");
    }
  }

  // Fetch satellites by category from MongoDB Atlas via your backend API
  static Future<List<Satellite>> fetchSatellitesByCategory(String categoryName) async {
    final response = await http.get(Uri.parse('$baseUrl/satellites/by-category/$categoryName'));

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      final List satellites = data['satellites'];
      return satellites.map((json) => Satellite.fromJson(json)).toList();
    } else {
      throw Exception("Failed to fetch satellites by category");
    }
  }

  // Fetch satellites above a specific location (latitude, longitude) from MongoDB Atlas via your backend API
  static Future<List<Satellite>> fetchSatellitesAbove(double lat, double lon) async {
    final url = Uri.parse('$baseUrl/satellites/above?lat=$lat&lon=$lon');
    final response = await http.get(url);

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      final List satellites = data['satellites'];
      return satellites.map((json) => Satellite.fromJson(json)).toList();
    } else {
      throw Exception("Failed to load satellites above location");
    }
  }
}
