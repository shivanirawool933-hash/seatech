from typing import List, Dict, Any
from app.schemas.dto import VesselCandidateScore, FeatureScoreBreakdown, RankingWeights
import logging

logger = logging.getLogger(__name__)

class TransparentVesselScoringEngine:
    """
    Transparent 5-factor scoring engine for vessel attribution:
    1. Distance score (30%)
    2. Time correlation score (25%)
    3. Trajectory proximity score (25%)
    4. Course / direction consistency (10%)
    5. Behavioral anomaly score (10%)
    
    IMPORTANT: Outputs strictly non-definitive analytical wording (e.g. "Most likely candidate", "Potential source vessel").
    """
    @staticmethod
    def rank_vessels(
        features_list: List[Dict[str, Any]],
        weights: RankingWeights = RankingWeights()
    ) -> List[VesselCandidateScore]:
        
        candidates: List[VesselCandidateScore] = []

        for feat in features_list:
            min_dist_origin = feat["min_dist_origin_km"]
            min_dist_spill = feat["min_dist_spill_km"]
            time_delta_h = feat["min_time_delta_hours"]
            closest_point = feat["closest_point"]

            # 1. Distance Score: Exponential decay from 0 to 50 km
            distance_score = max(0.0, 100.0 * (1.0 - (min_dist_origin / 50.0)**0.8))

            # 2. Time Score: Decay over 12 hour window
            time_score = max(0.0, 100.0 * (1.0 - (time_delta_h / 12.0)))

            # 3. Trajectory Proximity Score: Direct spill intersection gives 100%
            trajectory_score = max(0.0, 100.0 * (1.0 - (min_dist_spill / 25.0)))

            # 4. Course / Direction Score: Speed over ground analysis (high speed or sudden vessel stop near origin)
            sog = closest_point.sog if closest_point and closest_point.sog is not None else 10.0
            if sog < 2.0:
                course_score = 90.0 # Slow vessel / possible discharge activity
            elif 8.0 <= sog <= 16.0:
                course_score = 75.0 # Transit vessel
            else:
                course_score = 60.0

            # 5. Behavioral Anomaly Score: Tanker/Cargo types near origin with low speed get higher anomaly flags
            vtype = str(feat.get("vessel_type", "")).lower()
            if ("tanker" in vtype or "cargo" in vtype) and min_dist_origin < 10.0:
                anomaly_score = 88.0
            else:
                anomaly_score = 50.0

            # Compute weighted composite score
            w_dist = weights.distance_weight
            w_time = weights.time_weight
            w_traj = weights.trajectory_weight
            w_course = weights.course_weight
            w_anom = weights.anomaly_weight

            total_weight = w_dist + w_time + w_traj + w_course + w_anom
            if total_weight <= 0:
                total_weight = 1.0

            composite = (
                distance_score * w_dist +
                time_score * w_time +
                trajectory_score * w_traj +
                course_score * w_course +
                anomaly_score * w_anom
            ) / total_weight

            # Build evidence trail
            reasons = []
            if min_dist_origin < 5.0:
                reasons.append(f"Vessel passed within {min_dist_origin:.1f} km of estimated spill origin point.")
            else:
                reasons.append(f"Vessel closest point of approach was {min_dist_origin:.1f} km from estimated origin.")

            if time_delta_h < 2.0:
                reasons.append(f"High temporal correlation: vessel observed within {time_delta_h:.1f} hours of estimated spill creation.")
            else:
                reasons.append(f"Temporal offset: {time_delta_h:.1f} hours from estimated origin time.")

            if sog < 3.0:
                reasons.append(f"Low Speed Over Ground detected ({sog:.1f} knots) near spill location.")

            if "tanker" in vtype or "cargo" in vtype:
                reasons.append(f"High capacity vessel type ({feat.get('vessel_type')}) with potential discharge capability.")

            # Assign candidate status & confidence (Strict non-definitive language)
            if composite >= 75.0:
                status = "Most likely candidate"
                confidence = "High"
            elif composite >= 50.0:
                status = "Potential source vessel"
                confidence = "Medium"
            else:
                status = "Low probability candidate"
                confidence = "Low"

            candidates.append(VesselCandidateScore(
                vessel_name=feat["vessel_name"],
                mmsi=feat["mmsi"],
                imo=feat["imo"],
                vessel_type=feat["vessel_type"],
                composite_score=round(composite, 1),
                feature_scores=FeatureScoreBreakdown(
                    distance_score=round(distance_score, 1),
                    time_score=round(time_score, 1),
                    trajectory_score=round(trajectory_score, 1),
                    course_score=round(course_score, 1),
                    anomaly_score=round(anomaly_score, 1)
                ),
                min_distance_to_spill_km=round(min_dist_spill, 2),
                min_distance_to_origin_km=round(min_dist_origin, 2),
                time_delta_hours=round(time_delta_h, 1),
                evidence_reasons=reasons,
                candidate_status=status,
                confidence_level=confidence
            ))

        # Sort candidates descending by composite score
        candidates.sort(key=lambda c: c.composite_score, reverse=True)
        return candidates
