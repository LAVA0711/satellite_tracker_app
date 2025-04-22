import 'package:flutter/material.dart';
import 'package:ar_flutter_plugin/ar_flutter_plugin.dart';
import 'package:ar_flutter_plugin/datatypes/node_types.dart';
import 'package:ar_flutter_plugin/models/ar_node.dart';
import 'package:ar_flutter_plugin/managers/ar_anchor_manager.dart';
import 'package:ar_flutter_plugin/managers/ar_location_manager.dart';
import 'package:ar_flutter_plugin/managers/ar_object_manager.dart';
import 'package:ar_flutter_plugin/managers/ar_session_manager.dart';
import 'package:vector_math/vector_math_64.dart' show Vector3, Vector4;
import 'package:geolocator/geolocator.dart';
import 'services/satellite_service.dart';

class AugmentedRealityPage extends StatefulWidget {
  const AugmentedRealityPage({super.key});

  @override
  State<AugmentedRealityPage> createState() => _AugmentedRealityPageState();
}

class _AugmentedRealityPageState extends State<AugmentedRealityPage> {
  late ARSessionManager arSessionManager;
  late ARObjectManager arObjectManager;
  bool _noSatellitesFound = false;
  bool _satelliteAdded = false;

  @override
  void initState() {
    super.initState();
    _startSatelliteTimeout();
  }

  void _startSatelliteTimeout() {
    Future.delayed(const Duration(seconds: 15), () {
      if (!_satelliteAdded) {
        setState(() {
          _noSatellitesFound = true;
        });
      }
    });
  }

  @override
  void dispose() {
    arSessionManager.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        children: [
          ARView(onARViewCreated: onARViewCreated),
          if (!_satelliteAdded && !_noSatellitesFound)
            Positioned(
              bottom: 80,
              left: 0,
              right: 0,
              child: Center(
                child: Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: Colors.black87,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Text(
                    "⚠️ Hold your phone towards sky...!!!",
                    style: TextStyle(color: Colors.white, fontSize: 16),
                  ),
                ),
              ),
            ),
          if (_noSatellitesFound)
            Positioned.fill(
              child: Container(
                color: Colors.black87,
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Text(
                      "No satellites found above your location",
                      style: TextStyle(color: Colors.white, fontSize: 18),
                    ),
                    const SizedBox(height: 20),
                    ElevatedButton(
                      onPressed: () {
                        Navigator.of(context).pop();
                      },
                      child: const Text("Go to Home Page"),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }

  void onARViewCreated(
      ARSessionManager sessionManager,
      ARObjectManager objectManager,
      ARAnchorManager anchorManager,
      ARLocationManager locationManager,
      ) {
    arSessionManager = sessionManager;
    arObjectManager = objectManager;

    arSessionManager.onInitialize(
      showFeaturePoints: false,
      showPlanes: false,
      showWorldOrigin: false,
      handleTaps: false,
    );

    arObjectManager.onInitialize();

    _getCurrentLocation().then((position) {
      debugPrint("📍 Location: ${position.latitude}, ${position.longitude}");
      addSatelliteModels(position.latitude, position.longitude);
    }).catchError((e) {
      debugPrint("❌ Location error: $e");
    });
  }

  Future<void> addSatelliteModels(double userLat, double userLon) async {
    try {
      List<Satellite> satellites =
      await SatelliteService.fetchSatellitesAbove(userLat, userLon);

      if (satellites.isEmpty) return;

      for (Satellite satellite in satellites.take(5)) {
        double latDiff = satellite.latitude - userLat;
        double lonDiff = satellite.longitude - userLon;

        double posScale = 50.0;

        final node = ARNode(
          type: NodeType.localGLTF2,
          uri: "assets/models/Basic_Satellite.gltf",
          scale: Vector3(0.4, 0.4, 0.4),
          position: Vector3(lonDiff * posScale, 0.0, -(latDiff * posScale)),
          rotation: Vector4(0.0, 1.0, 0.0, 0.0),
        );

        bool? didAdd = await arObjectManager.addNode(node);
        if (didAdd == true) {
          setState(() {
            _satelliteAdded = true;
          });
        }
      }
    } catch (e) {
      debugPrint("❌ Error adding satellite: $e");
    }
  }

  Future<Position> _getCurrentLocation() async {
    bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) throw Exception("Location services are disabled.");

    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        throw Exception("Location permission denied.");
      }
    }

    if (permission == LocationPermission.deniedForever) {
      throw Exception("Location permission permanently denied.");
    }

    return await Geolocator.getCurrentPosition(
      desiredAccuracy: LocationAccuracy.high,
    );
  }
}
