// Keep your imports the same
import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';
import '../models/satellite_type.dart';
import '../services/satellite_service.dart';
import 'satellite_visualization.dart';

class TrackSatellitesPage extends StatefulWidget {
  const TrackSatellitesPage({super.key});

  @override
  State<TrackSatellitesPage> createState() => _TrackSatellitesPageState();
}

class _TrackSatellitesPageState extends State<TrackSatellitesPage> {
  late VideoPlayerController _controller;

  List<SatelliteType> satelliteTypes = [];
  List<Satellite> availableSatellites = [];
  SatelliteType? selectedType;
  List<Satellite> selectedSatellites = [];
  int selectedNumberOfSatellites = 1;

  final List<int> satelliteNumbers = [1, 2, 3, 4, 5];
  String warningMessage = '';

  @override
  void initState() {
    super.initState();
    _controller = VideoPlayerController.asset("assets/videos/background.mp4")
      ..setLooping(true)
      ..initialize().then((_) {
        setState(() {
          _controller.play();
        });
      });

    fetchTypes();
  }

  Future<void> fetchTypes() async {
    try {
      final types = await SatelliteService.fetchSatelliteTypes();
      setState(() {
        satelliteTypes = types;
        if (types.isNotEmpty) {
          selectedType = types.first;
          fetchSatellites(selectedType!.name);
        }
      });
    } catch (e) {
      debugPrint("❌ Error loading satellite types: $e");
    }
  }

  Future<void> fetchSatellites(String categoryName) async {
    if (selectedType == null) return;
    try {
      final satellites = await SatelliteService.fetchSatellitesByCategory(categoryName);
      satellites.sort((a, b) => a.name.compareTo(b.name));
      setState(() {
        availableSatellites = satellites;
        if (satellites.isNotEmpty) {
          selectedSatellites = satellites.take(selectedNumberOfSatellites).toList();
        }
      });
    } catch (e) {
      debugPrint("❌ Error loading satellites: $e");
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void handleTrack() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => SatelliteVisualizationPage(satellites: selectedSatellites),
      ),
    );
  }

  void handleSatelliteSelection(Satellite satellite) {
    if (selectedSatellites.contains(satellite)) {
      setState(() {
        selectedSatellites.remove(satellite);
        warningMessage = '';
      });
    } else {
      if (selectedSatellites.length < selectedNumberOfSatellites) {
        setState(() {
          selectedSatellites.add(satellite);
          warningMessage = '';
        });
      } else {
        setState(() {
          warningMessage = "You can only select up to $selectedNumberOfSatellites satellites.";
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          if (_controller.value.isInitialized)
            Positioned.fill(
              child: FittedBox(
                fit: BoxFit.cover,
                child: SizedBox(
                  width: _controller.value.size.width,
                  height: _controller.value.size.height,
                  child: VideoPlayer(_controller),
                ),
              ),
            ),
          Positioned.fill(child: Container(color: Colors.black.withOpacity(0.4))),
          Center(
            child: Container(
              width: 420,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                boxShadow: [
                  BoxShadow(color: Colors.black.withOpacity(0.2), blurRadius: 10, spreadRadius: 2)
                ],
              ),
              child: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Row(
                      children: [
                        IconButton(
                          icon: const Icon(Icons.arrow_back),
                          onPressed: () => Navigator.pop(context),
                        ),
                        const Text("Track Satellites", style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                      ],
                    ),
                    const SizedBox(height: 15),
                    buildDropdownRow(
                      "Satellite Type",
                      satelliteTypes,
                      selectedType,
                          (value) {
                        setState(() {
                          selectedType = value;
                          selectedSatellites.clear();
                          warningMessage = '';
                          if (selectedType != null) {
                            fetchSatellites(selectedType!.name);
                          }
                        });
                      },
                    ),
                    const SizedBox(height: 10),
                    buildDropdownRow(
                      "Number of Satellites",
                      satelliteNumbers,
                      selectedNumberOfSatellites,
                          (value) {
                        setState(() {
                          selectedNumberOfSatellites = value as int;
                          selectedSatellites.clear();
                          warningMessage = '';
                        });
                      },
                    ),
                    const SizedBox(height: 10),
                    Row(
                      children: [
                        const Expanded(
                          flex: 4,
                          child: Text("Satellites", style: TextStyle(fontSize: 14)),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          flex: 6,
                          child: DropdownButtonFormField<Satellite>(
                            hint: const Text("Select Satellite", style: TextStyle(fontSize: 12)),
                            value: null,
                            items: availableSatellites
                                .where((sat) => !selectedSatellites.contains(sat))
                                .map((sat) => DropdownMenuItem<Satellite>(
                              value: sat,
                              child: Text(sat.name, style: const TextStyle(fontSize: 13)),
                            ))
                                .toList(),
                            onChanged: (Satellite? value) {
                              if (value != null) {
                                handleSatelliteSelection(value);
                              }
                            },
                            decoration: InputDecoration(
                              filled: true,
                              fillColor: Colors.white,
                              contentPadding: const EdgeInsets.symmetric(vertical: 6, horizontal: 10),
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(8),
                                borderSide: const BorderSide(color: Colors.black),
                              ),
                              enabledBorder: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(8),
                                borderSide: const BorderSide(color: Colors.black),
                              ),
                              focusedBorder: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(8),
                                borderSide: const BorderSide(color: Colors.blue),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    Align(
                      alignment: Alignment.centerLeft,
                      child: Wrap(
                        spacing: 8,
                        runSpacing: 4,
                        children: selectedSatellites.map((satellite) {
                          return Chip(
                            label: Text(satellite.name, style: const TextStyle(fontSize: 12)),
                            deleteIcon: const Icon(Icons.close, size: 18),
                            onDeleted: () => handleSatelliteSelection(satellite),
                            backgroundColor: Colors.blue.shade100,
                          );
                        }).toList(),
                      ),
                    ),
                    const SizedBox(height: 10),
                    ConstrainedBox(
                      constraints: const BoxConstraints(maxHeight: 200),
                      child: SingleChildScrollView(
                        child: buildSatelliteSelectionRow(),
                      ),
                    ),
                    if (warningMessage.isNotEmpty) ...[
                      const SizedBox(height: 10),
                      Text(warningMessage, style: const TextStyle(color: Colors.red, fontSize: 13)),
                    ],
                    const SizedBox(height: 15),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.black,
                          padding: const EdgeInsets.symmetric(vertical: 10),
                        ),
                        onPressed: handleTrack,
                        child: const Text("Track", style: TextStyle(fontSize: 16, color: Colors.white)),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          )
        ],
      ),
    );
  }

  Widget buildDropdownRow<T>(
      String label,
      List<T> items,
      T? selectedValue,
      Function(T?) onChanged,
      ) {
    return Row(
      children: [
        Expanded(flex: 4, child: Text(label, style: const TextStyle(fontSize: 14))),
        const SizedBox(width: 10),
        Expanded(
          flex: 6,
          child: DropdownButtonFormField<T>(
            value: selectedValue,
            hint: Text("Select $label", style: const TextStyle(fontSize: 12)),
            items: items.map((item) {
              return DropdownMenuItem<T>(
                value: item,
                child: Text(
                  item is SatelliteType ? item.name : item.toString(),
                  style: const TextStyle(fontSize: 13),
                ),
              );
            }).toList(),
            onChanged: (value) {
              if (value != null) {
                onChanged(value);
              }
            },
            isExpanded: true,
            decoration: InputDecoration(
              filled: true,
              fillColor: Colors.white,
              contentPadding: const EdgeInsets.symmetric(vertical: 6, horizontal: 10),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: const BorderSide(color: Colors.black),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: const BorderSide(color: Colors.black),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: const BorderSide(color: Colors.blue),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget buildSatelliteSelectionRow() {
    return Column(
      children: availableSatellites.map((satellite) {
        final isSelected = selectedSatellites.contains(satellite);
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 3.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(child: Text(satellite.name, style: const TextStyle(fontSize: 13))),
              const SizedBox(width: 10),
              InkWell(
                onTap: () => handleSatelliteSelection(satellite),
                child: Container(
                  padding: const EdgeInsets.symmetric(vertical: 5, horizontal: 10),
                  decoration: BoxDecoration(
                    color: isSelected ? Colors.green : Colors.grey[200],
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        isSelected ? "Selected" : "Select",
                        style: TextStyle(
                          fontSize: 11,
                          color: isSelected ? Colors.white : Colors.black,
                        ),
                      ),
                      if (isSelected)
                        const Padding(
                          padding: EdgeInsets.only(left: 6),
                          child: Icon(Icons.check, size: 14, color: Colors.white),
                        ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }
}
