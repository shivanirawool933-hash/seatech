# 🌊 AquaTrace

### Satellite-Based Oil Spill Detection and AIS Vessel Attribution System

AquaTrace is a maritime intelligence project designed to support oil spill detection and investigation by combining satellite imagery, geospatial analysis, and Automatic Identification System (AIS) vessel tracking data.

The project aims to identify potential oil slicks, visualize their geographic extent, analyze vessel trajectories, and rank candidate vessels for further investigation.

## 🎯 Problem Statement

Oil spills threaten marine ecosystems, coastal communities, and ocean environments. Investigating a spill requires analyzing satellite observations alongside vessel movements and environmental conditions.

AquaTrace aims to bring these data sources together in one platform to support maritime pollution monitoring and oil spill investigation.

## ✨ Key Features

- 🛰️ **Satellite Imagery Analysis:** Support for georeferenced imagery, including Sentinel-1 Synthetic Aperture Radar (SAR).
- 🛢️ **Oil Spill Detection:** Identify potential oil slicks from suitable satellite imagery.
- 🗺️ **GIS Visualization:** Display spill locations and geographic boundaries.
- 🚢 **AIS Data Integration:** Analyze historical vessel tracking data.
- 📍 **Vessel Trajectory Analysis:** Compare vessel movements with a spill's location and estimated time.
- 📊 **Candidate Vessel Ranking:** Use transparent scoring criteria to prioritize vessels for investigation.
- 🌊 **Drift Analysis:** Explore wind and ocean-current data to estimate possible spill origins.

*Feature availability depends on the implemented modules and connected datasets.*

## 🔄 Project Workflow

1. Upload georeferenced satellite imagery.
2. Analyze imagery for potential oil slicks.
3. Determine the spill's geographic location and boundaries.
4. Import historical AIS vessel data.
5. Correlate vessel trajectories with the spill's location and time window.
6. Rank candidate vessels using defined scoring criteria.
7. Visualize the findings to support further investigation.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| React | User interface |
| TypeScript | Type-safe application development |
| Vite | Frontend development and build tooling |
| Tailwind CSS | Responsive styling |
| Python | Backend processing, where implemented |
| GIS tools | Geospatial analysis and mapping |
| Sentinel-1 SAR | Satellite imagery source |
| AIS datasets | Historical vessel tracking |

## 🛰️ Data Sources

- **Satellite imagery:** Sentinel-1 SAR and other suitable Earth observation data.
- **AIS data:** [NOAA MarineCadastre AccessAIS](https://marinecadastre.gov/accessais/).
- **Environmental data:** Wind and ocean-current information for potential drift analysis.

## 🚀 Getting Started

### Prerequisites

- Git
- Node.js and npm
- Python, if running the backend

### Clone the Repository

```bash
git clone https://github.com/shivanirawool933-hash/seatech.git
cd seatech
```

### Run the Frontend

```bash
cd frontend
npm install
npm run dev
```

### Build the Frontend

```bash
npm run build
```

*These commands assume the frontend is in the `frontend` directory and the corresponding npm scripts are configured.*

For backend setup, install the dependencies listed in `backend/requirements.txt` and follow the backend configuration required by the project.

## 🌍 Potential Applications

- Maritime pollution monitoring
- Oil spill investigation support
- Historical vessel trajectory analysis
- Marine environmental protection
- Geospatial intelligence and research

## 🔮 Future Scope

- Improve satellite-based oil slick detection.
- Integrate additional Earth observation datasets.
- Enhance AIS trajectory correlation.
- Incorporate ocean-current and wind-driven drift modelling.
- Improve candidate ranking explainability.
- Validate results against documented oil spill events.

## ⚠️ Important Note

AquaTrace is intended to support oil spill investigation. A candidate vessel ranking is an investigative lead, not definitive proof that a vessel caused a spill.

## 👩‍💻 Author

**Shivani Rawool**

- GitHub: [@shivanirawool933-hash](https://github.com/shivanirawool933-hash)

## 📄 License

No license has been specified yet. Add an appropriate license if you intend to distribute the project under open-source terms.
