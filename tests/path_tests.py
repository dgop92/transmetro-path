import json
import logging
import unittest

from core.commons import get_station_and_stops
from core.models import Coordinate, Method
from core.paths import SingleAlternativePathBuilder, get_json_from_tosomewhere_steps

logger = logging.getLogger(__name__)


class TestPath:

    path_builder_class = SingleAlternativePathBuilder

    def assert_step_method(self, step, method):
        self.assertEqual(step["through"]["method"], method)

    def assert_station_id(self, step, station_id):
        self.assertEqual(step["data"]["station_id"], station_id)

    def assert_route_id(self, step, transmetro_id):
        self.assertEqual(step["through"]["route_data"]["transmetro_id"], transmetro_id)

    def get_path_builder(self, start, final):
        stations_stops = get_station_and_stops(start, final)
        return self.path_builder_class(start, final, stations_stops)

    def get_json_representation(self, path):
        raw_json_repr = get_json_from_tosomewhere_steps(path)
        json_repr = json.loads(raw_json_repr)

        logger.debug("Path")
        logger.debug(json.dumps(json_repr, indent=2))
        return json_repr


class TestBasicPaths(unittest.TestCase, TestPath):
    def test_paths_between_start_stations_and_final_stations(self):

        # Esthercita to Buenos aires
        start = Coordinate(lon=-74.8026641, lat=10.9915344)
        final = Coordinate(lon=-74.800063, lat=10.9415782)

        path_builder = self.get_path_builder(start, final)
        paths = path_builder.get_paths_between_start_stations_and_final_stations()
        path = paths[0]

        json_repr = self.get_json_representation(path)

        self.assertEqual(len(path), 3)

        self.assert_step_method(json_repr[0], Method.WALK.value)
        self.assert_station_id(json_repr[0], 205)

        self.assert_step_method(json_repr[1], Method.TRONCAL.value)
        self.assert_station_id(json_repr[1], 104)

    def test_paths_between_start_stops_and_final_stations(self):

        # Uninorte to Pacho galan
        start = Coordinate(lon=-74.8497828, lat=11.0177671)
        final = Coordinate(lon=-74.799618, lat=10.9154516)

        path_builder = self.get_path_builder(start, final)
        paths = path_builder.get_paths_between_start_stops_and_final_stations()
        path = paths[0]

        json_repr = self.get_json_representation(path)

        self.assertEqual(len(path), 4)

        self.assert_step_method(json_repr[0], Method.WALK.value)

        self.assert_step_method(json_repr[1], Method.ALIMENTADOR.value)
        self.assert_route_id(json_repr[1], 37)
        self.assert_station_id(json_repr[1], 206)

        self.assert_step_method(json_repr[2], Method.TRONCAL.value)
        self.assert_route_id(json_repr[2], 6)
        self.assert_station_id(json_repr[2], 101)

    def test_paths_between_start_stations_and_final_stops(self):

        # Pacho galan To Uninorte
        start = Coordinate(lon=-74.799618, lat=10.9154516)
        final = Coordinate(lon=-74.8497828, lat=11.0177671)

        path_builder = self.get_path_builder(start, final)
        paths = path_builder.get_paths_between_start_stations_and_final_stops()
        path = paths[0]

        json_repr = self.get_json_representation(path)

        self.assertEqual(len(path), 4)

        self.assert_step_method(json_repr[0], Method.WALK.value)
        self.assert_station_id(json_repr[0], 101)

        self.assert_step_method(json_repr[1], Method.TRONCAL.value)
        self.assert_route_id(json_repr[1], 2)
        self.assert_station_id(json_repr[1], 206)

        self.assert_step_method(json_repr[2], Method.ALIMENTADOR.value)
        self.assert_route_id(json_repr[2], 37)

    def test_paths_between_start_stops_and_final_stops(self):

        # Uninorte to Ciudadela?
        start = Coordinate(lon=-74.8497828, lat=11.0177671)
        final = Coordinate(lon=-74.8059385, lat=10.9292644)

        path_builder = self.get_path_builder(start, final)
        paths = path_builder.get_paths_between_start_stops_and_final_stops()
        path = paths[0]

        json_repr = self.get_json_representation(path)

        self.assertEqual(len(path), 5)

        self.assert_step_method(json_repr[0], Method.WALK.value)

        self.assert_step_method(json_repr[1], Method.ALIMENTADOR.value)
        self.assert_route_id(json_repr[1], 37)
        self.assert_station_id(json_repr[1], 206)

        self.assert_step_method(json_repr[2], Method.TRONCAL.value)
        self.assert_route_id(json_repr[2], 6)
        self.assert_station_id(json_repr[2], 103)

        self.assert_step_method(json_repr[3], Method.ALIMENTADOR.value)
        self.assert_route_id(json_repr[3], 28)
