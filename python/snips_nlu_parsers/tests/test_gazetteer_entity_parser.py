from __future__ import unicode_literals

import unittest
from builtins import str

from snips_nlu_parsers import GazetteerEntityParser
from snips_nlu_parsers.tests.utils import ROOT_DIR
from snips_nlu_parsers.utils import temp_dir

CUSTOM_PARSER_PATH = ROOT_DIR / "data" / "tests" / "custom_gazetteer_parser"


class TestGazetteerEntityParser(unittest.TestCase):
    def get_test_parser_config(self):
        return {
            "entity_parsers": [
                self.get_music_artist_entity_config(),
                self.get_music_track_entity_config(),
            ]
        }

    @staticmethod
    def get_music_track_entity_config():
        return {
            "entity_identifier": "music_track",
            "entity_parser": {
                "gazetteer": [
                    {
                        "raw_value": "what s my age again",
                        "resolved_value": "What's my age again"
                    }
                ],
                "threshold": 0.7,
                "n_gazetteer_stop_words": None,
                "additional_stop_words": None
            }
        }

    @staticmethod
    def get_music_artist_entity_config():
        return {
            "entity_identifier": "music_artist",
            "entity_parser": {
                "gazetteer": [
                    {
                        "raw_value": "the rolling stones",
                        "resolved_value": "The Rolling Stones"
                    },
                    {
                        "raw_value": "blink one eight two",
                        "resolved_value": "Blink 182"
                    }
                ],
                "threshold": 0.6,
                "n_gazetteer_stop_words": None,
                "additional_stop_words": None,
                "license_info": {
                    "filename": "LICENSE",
                    "content": "Some license content\nhere\n"
                }
            },
        }

    @staticmethod
    def get_ambiguous_music_artist_entity_config():
        return {
            "entity_identifier": "music_artist",
            "entity_parser": {
                "gazetteer": [
                    {
                        "raw_value": "the rolling stones",
                        "resolved_value": "The Rolling Stones"
                    },
                    {
                        "raw_value": "the crying stones",
                        "resolved_value": "The Crying Stones"
                    },
                    {
                        "raw_value": "the flying stones",
                        "resolved_value": "The Flying Stones"
                    },
                    {
                        "raw_value": "the loving stones",
                        "resolved_value": "The Loving Stones"
                    },
                ],
                "threshold": 0.6,
                "n_gazetteer_stop_words": None,
                "additional_stop_words": None,
            },
        }

    def test_should_parse_from_built_parser(self):
        # Given
        parser_config = self.get_test_parser_config()
        parser = GazetteerEntityParser.build(parser_config)

        # When
        res = parser.parse("I want to listen to the stones", None)

        # Then
        expected_result = [
            {
                "value": "the stones",
                "resolved_value": "The Rolling Stones",
                "alternative_resolved_values": [],
                "range": {"start": 20, "end": 30},
                "entity_identifier": "music_artist"
            }
        ]

        self.assertListEqual(expected_result, res)

    def test_should_parse_from_built_parser_with_scope(self):
        # Given
        parser_config = self.get_test_parser_config()
        parser = GazetteerEntityParser.build(parser_config)

        # When
        text = "I want to listen to what s my age again by blink one eight two"
        res_artist = parser.parse(text, ["music_artist"])
        res_track = parser.parse(text, ["music_track"])

        # Then
        expected_artist_result = [
            {
                "value": "blink one eight two",
                "resolved_value": "Blink 182",
                "alternative_resolved_values": [],
                "range": {"start": 43, "end": 62},
                "entity_identifier": "music_artist"
            }
        ]

        expected_track_result = [
            {
                "value": "what s my age again",
                "resolved_value": "What's my age again",
                "alternative_resolved_values": [],
                "range": {"start": 20, "end": 39},
                "entity_identifier": "music_track"
            }
        ]

        self.assertListEqual(expected_artist_result, res_artist)
        self.assertListEqual(expected_track_result, res_track)

    def test_should_parse_from_built_parser_with_max_alternatives(self):
        # Given
        parser_config = {
            "entity_parsers": [
                self.get_ambiguous_music_artist_entity_config()
            ]
        }
        parser = GazetteerEntityParser.build(parser_config)

        # When
        text = "Play me the stones"
        res = parser.parse(text, max_alternative_resolved_values=2)

        # Then
        expected_artist_result = [
            {
                "value": "the stones",
                "resolved_value": "The Rolling Stones",
                "alternative_resolved_values": [
                    "The Crying Stones",
                    "The Flying Stones"
                ],
                "range": {"start": 8, "end": 18},
                "entity_identifier": "music_artist"
            }
        ]

        expected_track_result = [
            {
                "value": "what s my age again",
                "resolved_value": "What's my age again",
                "range": {"start": 20, "end": 39},
                "entity_identifier": "music_track"
            }
        ]

        self.assertListEqual(expected_artist_result, res)

    def test_should_persist_parser(self):
        # Given
        parser_config = self.get_test_parser_config()
        parser = GazetteerEntityParser.build(parser_config)

        # When
        with temp_dir() as tmpdir:
            persisted_path = tmpdir / "persisted_gazetteer_parser"
            parser.persist(str(persisted_path))

            # Then
            license_path = persisted_path / "parser_1" / "LICENSE"
            self.assertTrue(license_path.exists(),
                            "Couldn't find license file")

            with license_path.open(encoding="utf8") as f:
                license_content = f.read()

            loaded_parser = GazetteerEntityParser.from_path(persisted_path)

        res = loaded_parser.parse("I want to listen to the stones", None)

        # Then
        expected_license_content = "Some license content\nhere\n"
        expected_result = [
            {
                "value": "the stones",
                "resolved_value": "The Rolling Stones",
                "alternative_resolved_values": [],
                "range": {"start": 20, "end": 30},
                "entity_identifier": "music_artist"
            }
        ]
        self.assertEqual(expected_license_content, license_content)
        self.assertListEqual(expected_result, res)

    def test_should_load_parser_from_path(self):
        # Given
        parser = GazetteerEntityParser.from_path(CUSTOM_PARSER_PATH)

        # When
        res = parser.parse("I want to listen to the stones", None)

        # Then
        expected_result = [
            {
                "value": "the stones",
                "resolved_value": "The Rolling Stones",
                "alternative_resolved_values": [],
                "range": {"start": 20, "end": 30},
                "entity_identifier": "music_artist"
            }
        ]

        self.assertListEqual(expected_result, res)

    def test_should_not_accept_bytes_in_text(self):
        # Given
        parser = GazetteerEntityParser.from_path(CUSTOM_PARSER_PATH)
        bytes_text = b"Raise to sixty"

        # When/Then
        with self.assertRaises(TypeError):
            parser.parse(bytes_text)

    def test_should_not_accept_bytes_in_scope(self):
        # Given
        scope = [b"snips/number", b"snips/datetime"]
        parser = GazetteerEntityParser.from_path(CUSTOM_PARSER_PATH)

        # When/Then
        with self.assertRaises(TypeError):
            parser.parse("Raise to sixty", scope)
