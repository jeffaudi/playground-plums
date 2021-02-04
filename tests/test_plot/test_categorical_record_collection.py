from playground_plums.commons import RecordCollection, Record
from playground_plums.plot.engine.color_engine import CategoricalRecordCollection


class TestRecord:
    def test_record_collection(self):
        import geojson
        r = Record([0, 1, 2], ('car', 'road vehicle'), some_property='some property', another_property=45)
        r2 = Record([[[0, 0], [0, 1], [1, 1], [0, 0]]], ('car', 'road vehicle'),
                    some_property='some property', another_property=42)
        r3 = Record([[[0, 0], [0, 1], [1, 1], [0, 0]]], ('car', 'road vehicle'),
                    some_property='some properties', another_property=42)

        rc = RecordCollection(r, r2)

        crc_frc = CategoricalRecordCollection.from_record_collection('another_property', rc)
        crc = CategoricalRecordCollection('another_property', r, r2)

        assert len(crc) == 2
        assert len(crc_frc) == 2

        assert crc[1] == r2
        assert crc_frc[1] == r2

        assert crc[1, 0] == r2
        assert crc_frc[1, 0] == r2

        crc[1, 0] = r3
        crc_frc[1, 0] = r3
        assert crc[1, 0] == r3
        assert crc_frc[1, 0] == r3

        assert crc.loc[42, 0] == r3
        assert crc_frc.loc[42, 0] == r3

        crc.loc[42, 0] = r2
        crc_frc.loc[42, 0] = r2
        assert crc.loc[42, 0] == r2
        assert crc_frc.loc[42, 0] == r2

        assert geojson.dumps(crc, sort_keys=True) == '{"features": [' \
                                                     '{"geometry": {"coordinates": [0, 1, 2], "type": "Point"}, ' \
                                                     '"properties": {"another_property": 45, ' \
                                                     '"category": ["car", "road vehicle"], ' \
                                                     '"confidence": null, "some_property": "some property"}, ' \
                                                     '"type": "Feature"}, ' \
                                                     '{"geometry": {"coordinates": ' \
                                                     '[[[0, 0], [0, 1], [1, 1], [0, 0]]], ' \
                                                     '"type": "Polygon"}, ' \
                                                     '"properties": {"another_property": 42, ' \
                                                     '"category": ["car", "road vehicle"], ' \
                                                     '"confidence": null, ' \
                                                     '"some_property": "some property"}, "type": "Feature"}], ' \
                                                     '"type": "FeatureCollection"}'

        assert geojson.dumps(crc_frc, sort_keys=True) == '{"features": [' \
                                                         '{"geometry": {"coordinates": [0, 1, 2], "type": "Point"}, ' \
                                                         '"properties": {"another_property": 45, ' \
                                                         '"category": ["car", "road vehicle"], ' \
                                                         '"confidence": null, "some_property": "some property"}, ' \
                                                         '"type": "Feature"}, ' \
                                                         '{"geometry": {"coordinates": ' \
                                                         '[[[0, 0], [0, 1], [1, 1], [0, 0]]], ' \
                                                         '"type": "Polygon"}, ' \
                                                         '"properties": {"another_property": 42, ' \
                                                         '"category": ["car", "road vehicle"], ' \
                                                         '"confidence": null, ' \
                                                         '"some_property": "some property"}, "type": "Feature"}], ' \
                                                         '"type": "FeatureCollection"}'
