import 'package:flutter/foundation.dart'; // For kIsWeb
import 'package:flutter/material.dart';
import 'package:webview_windows/webview_windows.dart' as win;
import 'package:webview_flutter/webview_flutter.dart' as android;
import 'dart:io' show Platform;
import '../services/satellite_service.dart';

class SatelliteVisualizationPage extends StatefulWidget {
  final List<Satellite> satellites;

  const SatelliteVisualizationPage({super.key, required this.satellites});

  @override
  State<SatelliteVisualizationPage> createState() => _SatelliteVisualizationPageState();
}

class _SatelliteVisualizationPageState extends State<SatelliteVisualizationPage> {
  late int currentIndex;
  final win.WebviewController windowsController = win.WebviewController();
  android.WebViewController? androidController;

  bool get isWindows {
    try {
      return !kIsWeb && Platform.isWindows;
    } catch (_) {
      return false;
    }
  }

  bool get isAndroid {
    try {
      return !kIsWeb && Platform.isAndroid;
    } catch (_) {
      return false;
    }
  }

  @override
  void initState() {
    super.initState();
    currentIndex = 0;

    // Initialize WebView for the platform
    if (isWindows) {
      _initWindowsWebView();
    } else if (isAndroid) {
      _initAndroidWebView();
    }
  }

  Future<void> _initWindowsWebView() async {
    await windowsController.initialize();
    await windowsController.loadUrl(Uri.file('assets/html/cesium_view.html').toString());
    setState(() {});
  }

  Future<void> _initAndroidWebView() async {
    androidController = android.WebViewController()
      ..setJavaScriptMode(android.JavaScriptMode.unrestricted)
      ..loadFlutterAsset('assets/html/cesium_view.html');
    setState(() {});
  }

  Widget _buildWebView() {
    if (isWindows) {
      return SizedBox(
        height: 400,
        child: win.Webview(windowsController),
      );
    } else if (isAndroid) {
      return SizedBox(
        height: 400,
        child: androidController == null
            ? const Center(child: CircularProgressIndicator())
            : android.WebViewWidget(controller: androidController!),
      );
    } else if (kIsWeb) {
      return const SizedBox(
        height: 400,
        child: Center(child: Text('3D Visualization not supported on Flutter Web.')),
      );
    } else {
      return const SizedBox(
        height: 400,
        child: Center(child: Text('Unsupported platform.')),
      );
    }
  }

  Widget _buildSatelliteCard(Satellite satellite) {
    return Padding(
      padding: const EdgeInsets.all(12.0),
      child: Card(
        elevation: 4,
        shape: RoundedRectangleBorder(
          side: BorderSide(color: Colors.green, width: 2),
          borderRadius: BorderRadius.circular(15),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(satellite.name, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
              const SizedBox(height: 10),
              Text("Latitude: ${satellite.latitude}"),
              Text("Longitude: ${satellite.longitude}"),
              Text("Altitude: ${satellite.altitude} km"),
              Text("Distance from Earth: ${satellite.distanceFromEarth} km"),
              Text("Distance from Moon: ${satellite.distanceFromMoon} km"),
            ],
          ),
        ),
      ),
    );
  }

  void _highlightSatellite(Satellite satellite) {
    String satelliteJson = satellite.toJsonString();

    if (isWindows) {
      windowsController.executeScript('highlightSatellite($satelliteJson);');
    } else if (isAndroid) {
      androidController?.runJavaScript('highlightSatellite($satelliteJson);');
    }
    // No need to run on Web since WebView not supported
  }

  @override
  Widget build(BuildContext context) {
    final satellites = widget.satellites;

    return Scaffold(
      appBar: AppBar(title: const Text("Satellite 3D Visualization")),
      body: Column(
        children: [
          _buildWebView(),
          Expanded(
            child: PageView.builder(
              itemCount: satellites.length,
              onPageChanged: (index) {
                setState(() {
                  currentIndex = index;
                  _highlightSatellite(satellites[currentIndex]);
                });
              },
              controller: PageController(viewportFraction: 0.9),
              itemBuilder: (context, index) => _buildSatelliteCard(satellites[index]),
            ),
          ),
        ],
      ),
    );
  }
}
