import logging
from typing import Dict, List

from config.constants import STOP_DIFFERENCE
from core.models import Coordinate
from core.queries import get_nearby_group_stops, get_nearby_stations
from core.utils import flatten

logger = logging.getLogger(__name__)


def get_best_stops(stops: List[dict], from_start_node: bool = True) -> list:

    if not stops:
        return []

    best_stops = []

    stops_sorted_by_dist = sorted(stops, key=lambda s: s["distance"])
    best_distance_stop = stops_sorted_by_dist.pop(0)
    best_stops.append(best_distance_stop)

    # it can be amount_to_arrive or a stop sequence depending on the point
    time_key = "amount_to_arrive" if from_start_node else "stop_sequence"
    best_time_stop = min(stops, key=lambda s: s[time_key])

    diff_stop_sequence = abs(
        int(best_distance_stop[time_key]) - int(best_time_stop[time_key])
    )

    if diff_stop_sequence > STOP_DIFFERENCE:
        best_stops.append(best_time_stop)

    return best_stops


def get_station_and_stops(
    start: Coordinate, final: Coordinate
) -> Dict[str, List[dict]]:

    # start
    logging.info("Retrieve start stations and stops")
    start_stations = get_nearby_stations(start)
    start_group_stops = get_nearby_group_stops(start)
    best_start_stops = flatten(
        map(lambda stops_group: get_best_stops(stops_group), start_group_stops)
    )

    # final
    logging.info("Retrieve final stations and stops")
    final_stations = get_nearby_stations(final)
    final_group_stops = get_nearby_group_stops(final)
    best_final_stops = flatten(
        map(
            lambda stops_group: get_best_stops(stops_group, from_start_node=False),
            final_group_stops,
        )
    )

    return {
        "start_stations": start_stations,
        "start_stops": best_start_stops,
        "final_stations": final_stations,
        "final_stops": best_final_stops,
    }
