import os
import sys
import pandas as pd

# Add app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.ais.trajectory import AISTrajectoryProcessor

def test_marinecadastre_ingestion():
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/sample_marinecadastre_ais.csv"))
    print(f"Testing NOAA MarineCadastre AIS ingestion from: {data_path}")
    
    df = pd.read_csv(data_path)
    trajectories = AISTrajectoryProcessor.process_csv(df)
    
    print(f"\nSuccessfully reconstructed {len(trajectories)} MarineCadastre vessel trajectories!")
    
    for traj in trajectories:
        print(f"\nVessel: {traj.vessel_name}")
        print(f"  MMSI: {traj.mmsi} | IMO: {traj.imo}")
        print(f"  Type: {traj.vessel_type}")
        print(f"  Points: {len(traj.positions)} | Distance: {traj.total_distance_km} km")
        print(f"  Latest Position: {traj.positions[-1].latitude}°N, {traj.positions[-1].longitude}°E | SOG: {traj.positions[-1].sog} kts")

if __name__ == "__main__":
    test_marinecadastre_ingestion()
