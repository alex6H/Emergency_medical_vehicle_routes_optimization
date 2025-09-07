# Emergency medical vehicle routes optimization
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Language](https://img.shields.io/badge/Language-Python-green.svg)](https://www.python.org/)
[![GIS](https://img.shields.io/badge/GIS-OSRM%20%7C%20OpenStreetMap-orange.svg)](https://project-osrm.org/)
[![GitHub Views](https://komarev.com/ghpvc/?username=alex6H&repo=Emergency_medical_vehicle_routes_optimization&color=brightgreen&style=flat&label=Views)](https://github.com/alex6H/Emergency_medical_vehicle_routes_optimization)

Enhancing EMS response times through real-time data and intelligent routing.
Here is the final result of my Master's thesis in Information and Communication Technology at the [Université Libre de Bruxelles](https://www.ulb.be/fr/programme/ma-stic). 
**This work got the highest grade for the 2018-2019 academic year.**

## Thesis : 
_"Optimisation d’itinéraires des véhicules médicaux d’urgence à l’aide de données de position.
Application aux données du Service d’Incendie et Aide Médicale Urgente de Bruxelles-Capitale"_

_"Optimization of emergency medical vehicle routes using location data.
Application to data from the Brussels-Capital Fire and Emergency Medical Service"_

Author : Alexis Huart

**Link to thesis (in french) :** [Emergency Medical Vehicle Routes Optimization](https://github.com/alex6H/Emergency_medical_vehicle_routes_optimization/blob/main/HUART_Optimisation_itin%C3%A9raires_2019.pdf)

## Abstract : 
The patients survival rate out-of-hospital depends directly on how quickly emergency medical services (EMS) arrive. Therefore, the vehicle with the shortest estimated time of arrival (ETA) should be sent to the scene. This is a considerable challenge, particularly in urban areas where traffic congestion is significant and the road network complex. Currently, ETA is calculated on a theoretical basis. This work attempts to create a draft navigation system based on position data and therefore actual speeds. The aim is to identify the influence of traffic, improve ETA, enhance vehicle selection and route choice. The concept is applied to [Brussels fire and emergency medical service](https://be.brussels/en/about-region/structure-and-organisations/administrations-and-institutions-region/siamurbc/location-our-fire-stations) data. The average speeds of EMS vehicles are calculated and input into a navigation system. The experiment uses the Open Source RoutingMachine library for map matching and routing, as well as a Python script for error correction and speed calculation. The procedure and results are compared to the [Poulton study](https://arxiv.org/pdf/1812.03181), the only work to date using position data for EMS navigation. In Brussels, we observe that automobile congestion clearly modifies the average speed of EMS during peak hours. From the speed analysis, we obtain a draft of a functional navigation system, based on data with a realistic ETA.

## Research Problem
Current EMS dispatch systems calculate Estimated Time of Arrival (ETA) using theoretical speeds, which can be highly inaccurate in real-world traffic conditions. This project demonstrates how real-world vehicle tracking data can significantly improve:

- ⏱️ ETA Accuracy: More realistic arrival time predictions
- 🚗 Vehicle Selection: Better choice of which ambulance to dispatch
- 🗺️ Route Optimization: Improved path planning considering actual traffic conditions
- 📊 Traffic Impact Analysis: Understanding how congestion affects emergency response

## Key Findings

- **Proof of concept**: Demonstrated feasibility of a custom navigation model for emergency vehicles using historical GPS data, providing more accurate ETA predictions and vehicle selection than theoretical or conventional systems.
- **Key insights**:
  - Public navigation systems consistently overestimate EMS ETAs in urban settings.
  - Data quality (sampling interval, HDOP, azimuth) is critical for reliable map matching and speed estimation; SIAMU's lack of these attributes imposed limitations.
  - Average EMS speeds in Brussels: 44.5 km/h (ambulances), 54.5 km/h (medicalized vehicles), with clear congestion effects during peak hours.
  - Segment-level speed profiles enable dynamic, hourly weighting of the road network for EMS routing—an improvement over static approaches.
- **Limitations**:
  - Results affected by data gaps, lack of HDOP/azimuth, arbitrary thresholds (e.g., minimum 20 passes per segment).
  - Segments lacking empirical speed data revert to default routing values, potentially biasing ETA estimates.
  - The system is a research prototype; operational deployment would require further validation and refinement.

## Future Directions

- **Data enhancement**: Incorporate azimuth, HDOP, and more granular sampling to improve map matching and confidence.
- **Comparative studies**: Benchmark performance against other routing methods and integrate additional years of data for temporal modeling.
- **Isochrone analysis**: Use real travel times to delineate EMS service areas and identify underserved zones for resource allocation.
- **Sensor fusion**: Integrate multi-source positioning (WiFi, cellular, GNSS) to mitigate urban canyon effects and improve accuracy.
- **Operationalization**: Develop real-time updates using live traffic, incident, and weather data; enable embedded use in dispatch centers and vehicles.
- **Network effects**: Exploit V2X (vehicle-to-infrastructure) for dynamic traffic light prioritization and incident avoidance.
- **Machine learning**: Leverage predictive analytics for continuous ETA optimization, considering evolving road, traffic, and environmental conditions.

## Technology Stack

- **Routing engine**: [OSRM (Open Source Routing Machine)](https://project-osrm.org/)
- **Programming**: Python for data processing and error correction
- **Mapping data**: [OpenStreetMap (OSM)](https://www.openstreetmap.org/)
- **GIS processing**: Map matching and route calculation
- **Data source**: Brussels SIAMU vehicle tracking data

---

# Chapter Summaries

## Chapter 1: Introduction

**Motivations**
- Survival rates in critical emergencies depend directly on EMS response time, which is hindered by severe urban congestion in Brussels.
- Current Belgian EMS dispatch relies on theoretical travel times, ignoring real traffic conditions and leading to unreliable ETA predictions.
- Leveraging historical EMS vehicle data enables data-driven routing, yielding more accurate ETAs and optimal vehicle selection.

**Limits**
- This work is a proof of concept; it does not aim to deliver a production system or comprehensive velocity analysis.
- Only data from 2017 and two EMS vehicle types are used to ensure data quality and manageable processing.
- Analysis focuses on feasibility within the Brussels region, not broader generalization or real-time integration.

**Methodology**
- The thesis combines a theoretical review (EMS organization, routing theory, map matching) and a practical application to Brussels EMS data.
- Data is cleaned, filtered, and processed using OSRM and Python geospatial libraries to reconstruct and analyze routes.
- The system's ETA predictions and routing are compared against prior research (notably the [London Ambulance Service study](https://arxiv.org/pdf/1812.03181)).
      
## Chapter 2: Urban GNSS Positioning & Sensor Integration

- **GNSS Limitations:**  
  Details the impact of urban environments on GNSS accuracy, with frequent positional errors placing vehicles outside the road network.
- **Deduced Reckoning (DR) Sensors:**  
  Explains the role of gyroscopes and odometers in supplementing GNSS, providing continuity in GNSS-denied environments (e.g., tunnels), and correcting for drift and wheel circumference variations.
- **Alternative Positioning:**  
  Reviews mobile telephony and WiFi-based positioning, noting their utility in urban and indoor contexts, but highlighting their lower precision compared to GNSS.

## Chapter 3: Map Matching Principles & Network Quality

- **Map Matching (MM) Fundamentals:**  
  Defines MM as the process of aligning raw vehicle positions to road network segments, correcting navigation errors.
- **Network Data Quality:**  
  Emphasizes the importance of topological integrity and completeness in the road network, noting discrepancies between datasets (e.g., NavTech vs. Ordnance Survey) can affect MM accuracy.
- **Algorithmic Approaches:**  
  Categorizes MM algorithms into geometric, topological, probabilistic, and advanced techniques, with detailed discussion of point-to-point and point-to-curve matching.

## Chapter 4: Advanced Map Matching Algorithms

- **Hidden Markov Model (HMM) Approaches:**  
  Compares Hummel’s and Newson & Krumm’s HMM-based algorithms, focusing on their robustness to noisy, sparse GPS data and lack of azimuth information.
- **Empirical Validation:**  
  Summarizes validation using real-world GPS traces, demonstrating high accuracy up to 30-second intervals and 50-meter deviations.
- **Routing Fundamentals:**  
  Defines routing as the selection of optimal paths within a network, incorporating turn restrictions and mode-specific profiles.

## Chapter 5: Routing Algorithms

- **Algorithm Categories:**  
  Reviews hierarchical (Dijkstra’s), goal-directed (A*), and hybrid (Contraction Hierarchies) routing algorithms.
- **Dijkstra’s Algorithm:**  
  Describes its breadth-first search nature, memory efficiency, and scalability limitations.
- **A* Algorithm:**  
  Highlights heuristic integration for improved efficiency, serving as a foundation for advanced variants.
- **Contraction Hierarchies:**  
  Notes preprocessing and shortcut edge creation for rapid queries in large-scale networks.

## Chapter 6: Experimental Methodology & Data Sources

- **Speed Modeling:**  
  Details five speed calculation methods for road segments, enabling a hybrid model to minimize routing and ETA errors.
- **SIAMU Database:**  
  Describes the structure and content of the emergency vehicle dataset, including sensor integration and mission logs.
- **Workflow Overview:**  
  Outlines the experimental process: data cleaning, urgent phase extraction, map matching (OSRM/HMM), error correction, and segment-level speed estimation.

## Chapter 7: Technical Implementation

- **OSRM & Python Integration:**  
  Documents the use of OSRM (Contraction Hierarchies, HMM map matching) and Python (Shapely, GeoPandas, Numpy, Pandas) for geospatial data processing.
- **Database Schema:**  
  Details the SIAMU PostgreSQL database structure, including key tables for trips, positions, interventions, and vehicle inventory.
- **Hardware & Software Environment:**  
  Specifies system setup for reproducibility.

## Chapter 8: Geospatial Trajectory Analysis Workflow

- **Script Logic:**  
  Describes the main Python script for trajectory analysis, including library imports, GeoDataFrame construction, OSRM data retrieval, overlay and bearing corrections, route extraction, error handling, and database integration.
- **Validation Procedures:**  
  Details segment length and speed assignment, with rigorous error tolerance checks.

## Chapter 9: Error Correction Strategies

- **Custom Functions:**  
  Explains Python functions for overlay removal, bearing correction, duplicate segment elimination, roundabout loop detection, and bidirectional segment filtering.
- **Persistent Issues:**  
  Notes unresolved artifacts such as low speeds at mission start and occasional high-speed anomalies.
- **Illustrative Examples:**  
  Provides figures demonstrating error sources and correction effects.

## Chapter 10: Performance Evaluation & System Limitations

- **Validation Constraints:**  
  Discusses the lack of theoretical performance quantification, emphasizing the need for comparative practical trials.
- **Data-Driven System Challenges:**  
  Highlights limitations in discovering new network elements and the necessity for exploratory driving.
- **EMS Application:**  
  Justifies the need for custom predictive models over conventional navigation, referencing operations research literature.
- **Data Quality Assessment:**  
  Details the SIAMU data inventory, filtering procedures, and selection of OSRM/HMM for map matching.

## Chapter 11: Routing Profile Adaptation & Speed Analysis

- **Profile Modification:**  
  Describes adaptation of OSRM routing profiles for emergency scenarios and dynamic edge weighting.
- **Data Cleaning & Filtering:**  
  Summarizes post-matching error correction and trace filtering.
- **Speed Attribution:**  
  Presents segment-level speed calculations, temporal analysis, and dynamic weighting.
- **System Limitations:**  
  Notes reliance on arbitrary thresholds and default values, emphasizing the prototype’s proof-of-concept status.

---


## License

This project is licensed under the MIT License.
You are free to use, modify, and distribute this work, provided you include appropriate attribution.
Please cite this repository and the original thesis when using this code or methodology in your research or applications.

**Recommended Citation:**
Huart, A. (2019). Optimisation d'itinéraires des véhicules médicaux d'urgence à l'aide de données de position. 
Master's Thesis, Université Libre de Bruxelles. 
Available: https://github.com/alex6H/Emergency_medical_vehicle_routes_optimization

```
@mastersthesis{huart2019optimisation,
  author       = {Huart, Alexis},
  title        = {Optimisation d'itinéraires des véhicules médicaux d'urgence à l'aide de données de position},
  school       = {Université Libre de Bruxelles},
  year         = {2019},
  note         = {Master's Thesis},
  url          = {https://github.com/alex6H/Emergency_medical_vehicle_routes_optimization}
}
```

## Keywords : 
`Operations research`, `Intelligent transport systems`, `ITS`, `Service d’incendie et d’aide médicale urgente`, `SIAMU`,
`Estimated time of arrival`, `ETA`, `Emergency medical services`, `EMS`,
`Open source routing machine`, `OSRM`, `OpenStreetMap`, `OSM`, `Map matching`,
`Bruxelles`, `Brussels`, `Geographic Information Systems`, `GIS`, `Spatial analysis`,
`Routing algorithms`, `Shortest path`, `Traffic congestion`, `Real-time data`,
`GPS tracking`, `Trajectory analysis`, `Urban mobility`, `Emergency response`,
`Dispatch optimization`, `Healthcare logistics`, `Fleet management`, `Dynamic routing`,
`Contraction Hierarchies`, `Hidden Markov Model`, `HMM`, `Map-matching algorithms`,
`Travel time prediction`, `Navigation system`, `Data-driven decision making`,
`Public safety`, `Urban transport`, `Road network analysis`, `Geospatial data`,
`Python`, `PostgreSQL`, `Geopandas`, `Shapely`, `Data cleaning`,
`Transport modelling`, `Mobility data`, `Critical infrastructure`,
`Incident response`, `Location-based services`, `Vehicle tracking`, `Spatial database`
