import os
import shutil

import pytest
from appdirs import user_cache_dir

from plums.commons.path import Path

_tree_complex = {
    'metadata.csv': '',
    'tree.json': '',
    'data': {
        'images.json': '',
        'images': {
            'dataset_1': {
                'aoi_0': {
                    'labeled': {
                        'tile_00.jpg': '',
                        'tile_01.jpg': '',
                        'tile_02.jpg': '',
                        'tile_03.jpg': '',
                        'tile_04.jpg': '',
                        'tile_05.jpg': '',
                        'tile_06.jpg': '',
                        'tile_07.jpg': '',
                    },
                    'simulated': {
                        'tile_aa.jpg': '',
                        'tile_ab.jpg': '',
                        'tile_ac.jpg': '',
                        'tile_ad.jpg': '',
                        'tile_ae.jpg': '',
                        'tile_af.jpg': '',
                    }},
                'aoi_3': {
                    'labeled': {
                        'tile_8.jpg': '',
                        'tile_9.jpg': '',
                        'tile_10.jpg': '',
                        'tile_11.jpg': '',
                        'tile_12.jpg': '',
                        'tile_13.jpg': '',
                        'tile_14.jpg': '',
                        'tile_15.jpg': '',
                    },
                    'simulated': {
                        'tile_ba.jpg': '',
                        'tile_bb.jpg': '',
                        'tile_bc.jpg': '',
                        'tile_bd.jpg': '',
                        'tile_be.jpg': '',
                        'tile_bf.jpg': '',
                    }
                }
            },
            'dataset_0': {
                'labeled': {
                    'tile_20.jpg': '',
                    'tile_21.jpg': '',
                    'tile_22.jpg': '',
                    'tile_23.jpg': '',
                    'tile_24.jpg': '',
                    'tile_25.jpg': '',
                    'tile_26.jpg': '',
                    'tile_27.jpg': '',
                }
            },
            'dataset_3': {
                'tile_30.jpg': '',
                'tile_31.jpg': '',
                'tile_32.jpg': '',
                'tile_33.jpg': '',
                'tile_34.jpg': '',
                'added': {
                    'tile_ca.jpg': '',
                    'tile_cb.jpg': '',
                    'tile_cc.jpg': '',
                }
            }
        }
    }
}

_tree_pattern_loose = {
    'metadata.csv': '',
    'tree.json': '',
    'data': {
        'images.json': '',
        'images': {
            'dataset_1': {
                'aoi_0': {
                    'labeled': {
                        'tile_00.jpg': '',
                        'tile_01.jpg': '',
                        'tile_00.json': '',
                        'tile_01.geojson': '',
                    },
                    'simulated': {
                        'tile_00.jpg': '',
                        'tile_01.jpg': '',
                    }
                },
                'aoi_3': {
                    'labeled': {
                        'tile_00.jpg': '',
                        'tile_01.jpg': '',
                    },
                    'simulated': {
                        'tile_00.jpg': '',
                        'tile_01.jpg': '',
                    }
                }
            },
            'dataset_0': {
                'labeled': {
                    'prior': {
                        'tile_00.jpg': '',
                        'tile_01.jpg': '',
                    },
                    'posterior': {
                        'tile_00.jpg': '',
                        'tile_01.jpg': '',
                    }
                },
                'labels': {
                    'tile_00.json': '',
                    'tile_01.json': '',
                }
            }
        },
        'labels': {
            'dataset_1': {
                'aoi_0': {
                    'simulated': {
                        'tile_00.json': '',
                        'tile_01.json': '',
                    }
                },
                'aoi_3': {
                    'labeled': {
                        'tile_00.json': '',
                        'tile_01.json': '',
                    },
                    'simulated': {
                        'tile_00.json': '',
                        'tile_01.json': '',
                    }
                }
            },
            'dataset_0': {
                'labeled': {
                    'tile_00.json': '',
                    'tile_01.json': '',
                }
            }
        }
    }
}

_tree_pattern_strict = {
    'metadata.csv': '',
    'tree.json': '',
    'data': {
        'images.json': '',
        'images': {
            'dataset_1': {
                'aoi_0': {
                    'labeled': {
                        'tile_00.jpg': '',
                        'tile_01.jpg': '',
                    },
                    'simulated': {
                        'tile_00.jpg': '',
                        'tile_01.jpg': '',
                    }},
                'aoi_3': {
                    'labeled': {
                        'tile_00.jpg': '',
                        'tile_01.jpg': '',
                    },
                    'simulated': {
                        'tile_00.jpg': '',
                        'tile_01.jpg': '',
                    }
                }
            },
            'dataset_0': {
                'labeled': {
                    'tile_00.jpg': '',
                    'tile_01.jpg': '',
                },
                'labels': {
                    'tile_00.json': '',
                    'tile_01.json': '',
                }
            }
        },
        'labels': {
            'dataset_1': {
                'aoi_0': {
                    'labeled': {
                        'tile_00.json': '',
                        'tile_01.json': '',
                    },
                    'simulated': {
                        'tile_00.json': '',
                        'tile_01.json': '',
                    }},
                'aoi_3': {
                    'labeled': {
                        'tile_00.json': '',
                        'tile_01.json': '',
                    },
                    'simulated': {
                        'tile_00.json': '',
                        'tile_01.json': '',
                    }
                }
            },
            'dataset_0': {
                'labeled': {
                    'tile_00.json': '',
                    'tile_01.json': '',
                },
                'images': {
                    'tile_00.jpg': '',
                    'tile_01.jpg': '',
                }
            }
        },
    }
}

with open(str(Path(__file__)[:-1] / 'test_io' / 'test_tile' / '_data' / 'test_jpg.jpg'), 'rb') as f:
    _mona_lisa = f.read()

_feature_collection = """
{
  "type": "FeatureCollection",
  "features": [
    {
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              92.7,
              256
            ],
            [
              92.8,
              253.6
            ],
            [
              86,
              253.4
            ],
            [
              85.9,
              256
            ],
            [
              92.7,
              256
            ]
          ]
        ]
      },
      "type": "Feature",
      "properties": {
        "last_modifier_id": "35e372a9-6b76-40c6-a3d5-1ee7183c3dc7",
        "comment": null,
        "orientation": -178.522,
        "tags": [
          "tag",
          "class"
        ],
        "surface": 64.2146176930851,
        "kept_percentage": 0.09569366018406641,
        "image_id": "9ad5b20165e2873321bbc1f979c6669cdc451014",
        "dataset_id": "f16fff43-2535-4e34-afec-6404dcdcd545",
        "id": "record.6e73eff2-06f3-11ea-976a-b24c6cdc2bc0",
        "zone_id": "10187fa3-30df-4eb4-a1e9-6b1dcdc79951",
        "confidence": null,
        "angle": 2.16567500171822,
        "job_id": null,
        "created_at": "2019-11-14T15:28:38.813332",
        "modified_at": "2019-11-14T15:28:38.805320",
        "length": 15.8988469989003,
        "width": 4.06052237034644,
        "state": "ADDED",
        "record_id": "6e73eff2-06f3-11ea-976a-b2cdca212bc0",
        "image_2_id": null,
        "owner_id": "35e370a9-6b76-4ac6-a3d5-1eeb983c3dc7"
      }
    },
    {
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              0,
              0
            ],
            [
              0,
              256
            ],
            [
              256,
              256
            ],
            [
              256,
              0
            ],
            [
              0,
              0
            ]
          ]
        ]
      },
      "type": "Feature",
      "properties": {
        "kept_percentage": 1,
        "mask": true
      }
    }
  ]
}
""".encode('utf8')

_taxonomy = """
{
  "tag": {
    "class": {}
    }
}
""".encode('utf8')

_taxonomy_conflict = """
{
  "tags": {
    "class": {}
    }
}
""".encode('utf8')


_dataset_1_summary = """
{
  "targetZoom": 18,
  "datasetName": "Test PGML 1",
  "imageIds": [
    ["f9525e3bfbd081cd545261b3b5414eb88f689005",
     "75ad128196254e711ef7c9b129d1c59153098b18"],
    ["S2B_MSIL1C_20200212T025609_N0209_R003_T47DMH_20200212T054548",
     "088dbf07-2879-4b23-af06-b3f4189fcae6"]
  ],
  "zoneIds": [
    "fa719db8-31e9-49d1-9344-d4608ef6417e",
    "b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7"
  ],
  "creationDate": "2021-12-31T23:59:59.676066",
  "datasetId": "63d0da07-0a4b-4ffd-844f-af75c02288e0"
}
""".encode('utf8')


_dataset_2_summary = """
{
  "targetZoom": 14,
  "datasetName": "Test PGML 2",
  "imageIds": [
    ["d51636c2-e94d-422c-a034-82e4ff8fa7aa"],
    ["4e15b4a3-ee52-4382-b8a8-7d492fb1a6ed",
     "5562b632-72c3-4c21-b24e-e0536d8b20c8"]
  ],
  "zoneIds": [
    "c3e8b68b-f862-41bd-848c-6e2df28e4dd8",
    "2411dbb6-e7bf-41fd-8898-83325a9c6e5a"
  ],
  "creationDate": "2021-12-31T23:59:59.676066",
  "datasetId": "1af6c4c5-278d-40ae-9e32-dc8192f8402a"
}
""".encode('utf8')


_tree_playground = {
    '63d0da07-0a4b-4ffd-844f-af75c02288e0': {
        'taxonomy.json': _taxonomy,
        'dataset_summary.json': _dataset_1_summary,
        'samples': {
            'fa719db8-31e9-49d1-9344-d4608ef6417e': {
                'f9525e3bfbd081cd545261b3b5414eb88f689005': {  # Pleiades
                    '7c47df1097b349278c052e93e1d1903a.jpg': _mona_lisa
                },
                '75ad128196254e711ef7c9b129d1c59153098b18': {  # Spot
                    '7c47df1097b349278c052e93e1d1903a.jpg': _mona_lisa
                },
            },
            'b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7': {
                'S2B_MSIL1C_20200212T025609_N0209_R003_T47DMH_20200212T054548': {  # Sentinel-2
                    '453e41d218e071ccfb2d1c99ce23906a.jpg': _mona_lisa,
                    '453e41d218e071ccfb2d1c99ce23906a.jgw': '',
                },
                '088dbf07-2879-4b23-af06-b3f4189fcae6': {  # AERIAL
                    '0cc175b9c0f1b6a831c399e269772661.jpg': _mona_lisa
                },
            },
            # ---------------------------------------------- Out -------------------------------------------------------
            '99aa890e-4d9a-11ea-92ec-a0481c91ddca': {  # uuid-1
                'S2B_MSIL1C_20200212T025609_N0209_R003_T47DMH_20200212T054548': {  # Sentinel-2
                    '453e41d218e071ccfb2d1c99ce23906a.jpg': _mona_lisa,
                    '453e41d218e071ccfb2d1c99ce23906a.jgw': '',
                },
                '088dbf07-2879-4b23-af06-b3f4189fcae6': {  # AERIAL
                    '0cc175b9c0f1b6a831c399e269772661.jpg': _mona_lisa
                },
            },
            '732af79d-f68d-393b-b2f8-9239bcd62a27': {  # uuid-3
                'f9525e3bfbd081cd545261b3b5414eb88f689005': {  # Pleiades
                    '7c47df1097b349278c052e93e1d1903a.jpg': _mona_lisa
                },
                '75ad128196254e711ef7c9b129d1c59153098b18': {  # Spot
                    '88aff0a92b21b86460bfd4474ab1626a.jpg': _mona_lisa
                },
            },
            'f9a071b2-7c2d-5987-b251-f386a554e28a': {  # uuid-5
                'S2B_MSIL1C_20200212T025609_N0209_R003_T47DMH_20200212T054548': {  # Sentinel-2
                    '453e41d218e071ccfb2d1c99ce23906a.jpg': _mona_lisa,
                    '453e41d218e071ccfb2d1c99ce23906a.jgw': '',
                },
            }
        },  # ----------------------------------------------------------------------------------------------------------
        'labels': {
            'fa719db8-31e9-49d1-9344-d4608ef6417e': {
                '7c47df1097b349278c052e93e1d1903a.json': _feature_collection
            },
            'b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7': {
                '453e41d218e071ccfb2d1c99ce23906a.json': _feature_collection,
                '0cc175b9c0f1b6a831c399e269772661.json': _feature_collection
            },
            # ---------------------------------------------- Out -------------------------------------------------------
            '99aa890e-4d9a-11ea-92ec-a0481c91ddca': {},  # uuid-1
            '732af79d-f68d-393b-b2f8-9239bcd62a27': {  # uuid-3
                '7c47df1097b349278c052e93e1d1903a.json': _feature_collection,
                '88aff0a92b21b86460bfd4474ab1626a.json': _feature_collection
            },
            'f9a071b2-7c2d-5987-b251-f386a554e28a': {  # uuid-5
                '453e41d218e071ccfb2d1c99ce23906a.json': _feature_collection,
            }
        },  # ----------------------------------------------------------------------------------------------------------
    },
    '1af6c4c5-278d-40ae-9e32-dc8192f8402a': {
        'taxonomy.json': _taxonomy,
        'dataset_summary.json': _dataset_2_summary,
        'samples': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                'd51636c2-e94d-422c-a034-82e4ff8fa7aa': {  # Deimos-2
                    '92eb5ffee6ae2fec3ad71c777531578f': '',
                    '92eb5ffee6ae2fec3ad71c777531578b.jpg': _mona_lisa
                },
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '4e15b4a3-ee52-4382-b8a8-7d492fb1a6ed': {  # Vision1
                    '04a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                },
                '5562b632-72c3-4c21-b24e-e0536d8b20c8': {  # TerraSAR-X
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa
                },
            }
        },
        'labels': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                '92eb5ffee6ae2fec3ad71c777531578f': '',
                '92eb5ffee6ae2fec3ad71c777531578b.json': _feature_collection
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '04a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '4a8a08f09d37b73795649038408b5f33.json': _feature_collection
            }
        }
    },
    # --------------------------------------------------- Out ----------------------------------------------------------
    'd53187c6-4d99-11ea-92ec-a0481c91ddca': {  # uuid-1
        'taxonomy.json': _taxonomy_conflict,
        'samples': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                'd51636c2-e94d-422c-a034-82e4ff8fa7aa': {  # Deimos-2
                    '92eb5ffee6ae2fec3ad71c777531578f': '',
                    '92eb5ffee6ae2fec3ad71c777531578b.jpg': _mona_lisa
                },
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '4e15b4a3-ee52-4382-b8a8-7d492fb1a6ed': {  # Vision1
                    '04a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                },
                '5562b632-72c3-4c21-b24e-e0536d8b20c8': {  # TerraSAR-X
                    '8277e0910d750195b448797616e091ad.jpg': _mona_lisa
                }
            }
        },
        'labels': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                '92eb5ffee6ae2fec3ad71c777531578f': '',
                '92eb5ffee6ae2fec3ad71c777531578b.json': _feature_collection
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '04a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '4a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '8277e0910d750195b448797616e091ad.json': _feature_collection
            }
        }
    },
    'bb959eb8-692f-3225-9506-e885ac3770bf': {  # uuid-3
        'samples': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                'd51636c2-e94d-422c-a034-82e4ff8fa7aa': {  # Deimos-2
                    '92eb5ffee6ae2fec3ad71c777531578f': '',
                    '92eb5ffee6ae2fec3ad71c777531578b.jpg': _mona_lisa
                },
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '4e15b4a3-ee52-4382-b8a8-7d492fb1a6ed': {  # Vision1
                    '04a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                },
                '5562b632-72c3-4c21-b24e-e0536d8b20c8': {  # TerraSAR-X
                    '8277e0910d750195b448797616e091ad.jpg': _mona_lisa
                },
            }
        }
    },
    '6e9a3589-d6c8-534e-ada1-b769aeec2fe2': {  # uuid-5
        'samples': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                'd51636c2-e94d-422c-a034-82e4ff8fa7aa': {  # Deimos-2
                    '92eb5ffee6ae2fec3ad71c777531578f': '',
                    '92eb5ffee6ae2fec3ad71c777531578b.jpg': _mona_lisa
                },
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '4e15b4a3-ee52-4382-b8a8-7d492fb1a6ed': {  # Vision1
                    '04a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                },
                '5562b632-72c3-4c21-b24e-e0536d8b20c8': {  # TerraSAR-X
                    '8277e0910d750195b448797616e091ad.jpg': _mona_lisa
                },
            }
        },
        'labels': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                '92eb5ffee6ae2fec3ad71c777531578f': '',
                '92eb5ffee6ae2fec3ad71c777531578b.json': _feature_collection
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '04a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '4a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '8277e0910d750195b448797616e091ad.json': _feature_collection
            }
        }
    },
    # ------------------------------------------------------------------------------------------------------------------
}


_tree_playground_summary_missing_image = {
    '63d0da07-0a4b-4ffd-844f-af75c02288e0': {
        'taxonomy.json': _taxonomy,
        'dataset_summary.json': _dataset_1_summary,
        'samples': {
            'fa719db8-31e9-49d1-9344-d4608ef6417e': {
                'f9525e3bfbd081cd545261b3b5414eb88f689005': {  # Pleiades
                    '7c47df1097b349278c052e93e1d1903a.jpg': _mona_lisa
                },
                '75ad128196254e711ef7c9b129d1c59153098b18': {  # Spot
                    '7c47df1097b349278c052e93e1d1903a.jpg': _mona_lisa
                },
                '75ad128156ef4e711ef7c9b129d1c59153098b18': {  # Spot -> Missing from summary
                    '7c47df10ef5649278c052e93e1d1903a.jpg': _mona_lisa
                },
            },
            'b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7': {
                'S2B_MSIL1C_20200212T025609_N0209_R003_T47DMH_20200212T054548': {  # Sentinel-2
                    '453e41d218e071ccfb2d1c99ce23906a.jpg': _mona_lisa,
                    '453e41d218e071ccfb2d1c99ce23906a.jgw': '',
                },
                '088dbf07-2879-4b23-af06-b3f4189fcae6': {  # AERIAL
                    '0cc175b9c0f1b6a831c399e269772661.jpg': _mona_lisa
                },
            },
            # ---------------------------------------------- Out -------------------------------------------------------
            '99aa890e-4d9a-11ea-92ec-a0481c91ddca': {  # uuid-1
                'S2B_MSIL1C_20200212T025609_N0209_R003_T47DMH_20200212T054548': {  # Sentinel-2
                    '453e41d218e071ccfb2d1c99ce23906a.jpg': _mona_lisa,
                    '453e41d218e071ccfb2d1c99ce23906a.jgw': '',
                },
                '088dbf07-2879-4b23-af06-b3f4189fcae6': {  # AERIAL
                    '0cc175b9c0f1b6a831c399e269772661.jpg': _mona_lisa
                },
            },
            '732af79d-f68d-393b-b2f8-9239bcd62a27': {  # uuid-3
                'f9525e3bfbd081cd545261b3b5414eb88f689005': {  # Pleiades
                    '7c47df1097b349278c052e93e1d1903a.jpg': _mona_lisa
                },
                '75ad128196254e711ef7c9b129d1c59153098b18': {  # Spot
                    '88aff0a92b21b86460bfd4474ab1626a.jpg': _mona_lisa
                },
            },
            'f9a071b2-7c2d-5987-b251-f386a554e28a': {  # uuid-5
                'S2B_MSIL1C_20200212T025609_N0209_R003_T47DMH_20200212T054548': {  # Sentinel-2
                    '453e41d218e071ccfb2d1c99ce23906a.jpg': _mona_lisa,
                    '453e41d218e071ccfb2d1c99ce23906a.jgw': '',
                },
            }
        },  # ----------------------------------------------------------------------------------------------------------
        'labels': {
            'fa719db8-31e9-49d1-9344-d4608ef6417e': {
                '7c47df1097b349278c052e93e1d1903a.json': _feature_collection,
                '7c47df10ef5649278c052e93e1d1903a.json': _feature_collection  # -> Missing from summary
            },
            'b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7': {
                '453e41d218e071ccfb2d1c99ce23906a.json': _feature_collection,
                '0cc175b9c0f1b6a831c399e269772661.json': _feature_collection
            },
            # ---------------------------------------------- Out -------------------------------------------------------
            '99aa890e-4d9a-11ea-92ec-a0481c91ddca': {},  # uuid-1
            '732af79d-f68d-393b-b2f8-9239bcd62a27': {  # uuid-3
                '7c47df1097b349278c052e93e1d1903a.json': _feature_collection,
                '88aff0a92b21b86460bfd4474ab1626a.json': _feature_collection
            },
            'f9a071b2-7c2d-5987-b251-f386a554e28a': {  # uuid-5
                '453e41d218e071ccfb2d1c99ce23906a.json': _feature_collection,
            }
        },  # ----------------------------------------------------------------------------------------------------------
    },
    '1af6c4c5-278d-40ae-9e32-dc8192f8402a': {
        'taxonomy.json': _taxonomy,
        'dataset_summary.json': _dataset_2_summary,
        'samples': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                'd51636c2-e94d-422c-a034-82e4ff8fa7aa': {  # Deimos-2
                    '92eb5ffee6ae2fec3ad71c777531578f': '',
                    '92eb5ffee6ae2fec3ad71c777531578b.jpg': _mona_lisa
                },
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '4e15b4a3-ee52-4382-b8a8-7d492fb1a6ed': {  # Vision1
                    '04a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                },
                '5562b632-72c3-4c21-b24e-e0536d8b20c8': {  # TerraSAR-X
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa
                },
            }
        },
        'labels': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                '92eb5ffee6ae2fec3ad71c777531578f': '',
                '92eb5ffee6ae2fec3ad71c777531578b.json': _feature_collection
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '04a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '4a8a08f09d37b73795649038408b5f33.json': _feature_collection
            }
        }
    },
    # --------------------------------------------------- Out ----------------------------------------------------------
    'd53187c6-4d99-11ea-92ec-a0481c91ddca': {  # uuid-1
        'taxonomy.json': _taxonomy_conflict,
        'samples': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                'd51636c2-e94d-422c-a034-82e4ff8fa7aa': {  # Deimos-2
                    '92eb5ffee6ae2fec3ad71c777531578f': '',
                    '92eb5ffee6ae2fec3ad71c777531578b.jpg': _mona_lisa
                },
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '4e15b4a3-ee52-4382-b8a8-7d492fb1a6ed': {  # Vision1
                    '04a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                },
                '5562b632-72c3-4c21-b24e-e0536d8b20c8': {  # TerraSAR-X
                    '8277e0910d750195b448797616e091ad.jpg': _mona_lisa
                }
            }
        },
        'labels': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                '92eb5ffee6ae2fec3ad71c777531578f': '',
                '92eb5ffee6ae2fec3ad71c777531578b.json': _feature_collection
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '04a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '4a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '8277e0910d750195b448797616e091ad.json': _feature_collection
            }
        }
    },
    'bb959eb8-692f-3225-9506-e885ac3770bf': {  # uuid-3
        'samples': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                'd51636c2-e94d-422c-a034-82e4ff8fa7aa': {  # Deimos-2
                    '92eb5ffee6ae2fec3ad71c777531578f': '',
                    '92eb5ffee6ae2fec3ad71c777531578b.jpg': _mona_lisa
                },
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '4e15b4a3-ee52-4382-b8a8-7d492fb1a6ed': {  # Vision1
                    '04a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                },
                '5562b632-72c3-4c21-b24e-e0536d8b20c8': {  # TerraSAR-X
                    '8277e0910d750195b448797616e091ad.jpg': _mona_lisa
                },
            }
        }
    },
    '6e9a3589-d6c8-534e-ada1-b769aeec2fe2': {  # uuid-5
        'samples': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                'd51636c2-e94d-422c-a034-82e4ff8fa7aa': {  # Deimos-2
                    '92eb5ffee6ae2fec3ad71c777531578f': '',
                    '92eb5ffee6ae2fec3ad71c777531578b.jpg': _mona_lisa
                },
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '4e15b4a3-ee52-4382-b8a8-7d492fb1a6ed': {  # Vision1
                    '04a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                },
                '5562b632-72c3-4c21-b24e-e0536d8b20c8': {  # TerraSAR-X
                    '8277e0910d750195b448797616e091ad.jpg': _mona_lisa
                },
            }
        },
        'labels': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                '92eb5ffee6ae2fec3ad71c777531578f': '',
                '92eb5ffee6ae2fec3ad71c777531578b.json': _feature_collection
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '04a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '4a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '8277e0910d750195b448797616e091ad.json': _feature_collection
            }
        }
    },
    # ------------------------------------------------------------------------------------------------------------------
}


_tree_playground_summary_missing_zone = {
    '63d0da07-0a4b-4ffd-844f-af75c02288e0': {
        'taxonomy.json': _taxonomy,
        'dataset_summary.json': _dataset_1_summary,
        'samples': {
            'fa719db8-31e9-49d1-9344-d4608ef6417e': {
                'f9525e3bfbd081cd545261b3b5414eb88f689005': {  # Pleiades
                    '7c47df1097b349278c052e93e1d1903a.jpg': _mona_lisa
                },
                '75ad128196254e711ef7c9b129d1c59153098b18': {  # Spot
                    '7c47df1097b349278c052e93e1d1903a.jpg': _mona_lisa
                },
            },
            'b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7': {
                'S2B_MSIL1C_20200212T025609_N0209_R003_T47DMH_20200212T054548': {  # Sentinel-2
                    '453e41d218e071ccfb2d1c99ce23906a.jpg': _mona_lisa,
                    '453e41d218e071ccfb2d1c99ce23906a.jgw': '',
                },
                '088dbf07-2879-4b23-af06-b3f4189fcae6': {  # AERIAL
                    '0cc175b9c0f1b6a831c399e269772661.jpg': _mona_lisa
                },
            },
            # ---------------------------------------------- Out -------------------------------------------------------
            '99aa890e-4d9a-11ea-92ec-a0481c91ddca': {  # uuid-1
                'S2B_MSIL1C_20200212T025609_N0209_R003_T47DMH_20200212T054548': {  # Sentinel-2
                    '453e41d218e071ccfb2d1c99ce23906a.jpg': _mona_lisa,
                    '453e41d218e071ccfb2d1c99ce23906a.jgw': '',
                },
                '088dbf07-2879-4b23-af06-b3f4189fcae6': {  # AERIAL
                    '0cc175b9c0f1b6a831c399e269772661.jpg': _mona_lisa
                },
            },
            '732af79d-f68d-393b-b2f8-9239bcd62a27': {  # uuid-3
                'f9525e3bfbd081cd545261b3b5414eb88f689005': {  # Pleiades
                    '7c47df1097b349278c052e93e1d1903a.jpg': _mona_lisa
                },
                '75ad128196254e711ef7c9b129d1c59153098b18': {  # Spot
                    '88aff0a92b21b86460bfd4474ab1626a.jpg': _mona_lisa
                },
            },
            'f9a071b2-7c2d-5987-b251-f386a554e28a': {  # uuid-5
                'S2B_MSIL1C_20200212T025609_N0209_R003_T47DMH_20200212T054548': {  # Sentinel-2
                    '453e41d218e071ccfb2d1c99ce23906a.jpg': _mona_lisa,
                    '453e41d218e071ccfb2d1c99ce23906a.jgw': '',
                },
            }
        },  # ----------------------------------------------------------------------------------------------------------
        'labels': {
            'fa719db8-31e9-49d1-9344-d4608ef6417e': {
                '7c47df1097b349278c052e93e1d1903a.json': _feature_collection
            },
            'b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7': {
                '453e41d218e071ccfb2d1c99ce23906a.json': _feature_collection,
                '0cc175b9c0f1b6a831c399e269772661.json': _feature_collection
            },
            # ---------------------------------------------- Out -------------------------------------------------------
            '99aa890e-4d9a-11ea-92ec-a0481c91ddca': {},  # uuid-1
            '732af79d-f68d-393b-b2f8-9239bcd62a27': {  # uuid-3
                '7c47df1097b349278c052e93e1d1903a.json': _feature_collection,
                '88aff0a92b21b86460bfd4474ab1626a.json': _feature_collection
            },
            'f9a071b2-7c2d-5987-b251-f386a554e28a': {  # uuid-5
                '453e41d218e071ccfb2d1c99ce23906a.json': _feature_collection,
            }
        },  # ----------------------------------------------------------------------------------------------------------
    },
    '1af6c4c5-278d-40ae-9e32-dc8192f8402a': {
        'taxonomy.json': _taxonomy,
        'dataset_summary.json': _dataset_2_summary,
        'samples': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                'd51636c2-e94d-422c-a034-82e4ff8fa7aa': {  # Deimos-2
                    '92eb5ffee6ae2fec3ad71c777531578f': '',
                    '92eb5ffee6ae2fec3ad71c777531578b.jpg': _mona_lisa
                },
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '4e15b4a3-ee52-4382-b8a8-7d492fb1a6ed': {  # Vision1
                    '04a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                },
                '5562b632-72c3-4c21-b24e-e0536d8b20c8': {  # TerraSAR-X
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa
                },
            },
            '2411ef56-e7bf-41fd-8898-83325a9c6e5a': {  # -> Missing from summary
                '4e1ef5a3-ee52-4382-b8a8-7d492fb1a6ed': {  # Vision1
                    '4a8a08f0ef56b73795649038408b5f33.jpg': _mona_lisa,
                },
            }
        },
        'labels': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                '92eb5ffee6ae2fec3ad71c777531578f': '',
                '92eb5ffee6ae2fec3ad71c777531578b.json': _feature_collection
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '04a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '4a8a08f09d37b73795649038408b5f33.json': _feature_collection
            },
            '2411ef56-e7bf-41fd-8898-83325a9c6e5a': {  # -> Missing from summary
                '4a8a08f0ef56b73795649038408b5f33.json': _feature_collection,
            }
        }
    },
    # --------------------------------------------------- Out ----------------------------------------------------------
    'd53187c6-4d99-11ea-92ec-a0481c91ddca': {  # uuid-1
        'taxonomy.json': _taxonomy_conflict,
        'samples': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                'd51636c2-e94d-422c-a034-82e4ff8fa7aa': {  # Deimos-2
                    '92eb5ffee6ae2fec3ad71c777531578f': '',
                    '92eb5ffee6ae2fec3ad71c777531578b.jpg': _mona_lisa
                },
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '4e15b4a3-ee52-4382-b8a8-7d492fb1a6ed': {  # Vision1
                    '04a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                },
                '5562b632-72c3-4c21-b24e-e0536d8b20c8': {  # TerraSAR-X
                    '8277e0910d750195b448797616e091ad.jpg': _mona_lisa
                }
            }
        },
        'labels': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                '92eb5ffee6ae2fec3ad71c777531578f': '',
                '92eb5ffee6ae2fec3ad71c777531578b.json': _feature_collection
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '04a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '4a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '8277e0910d750195b448797616e091ad.json': _feature_collection
            }
        }
    },
    'bb959eb8-692f-3225-9506-e885ac3770bf': {  # uuid-3
        'samples': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                'd51636c2-e94d-422c-a034-82e4ff8fa7aa': {  # Deimos-2
                    '92eb5ffee6ae2fec3ad71c777531578f': '',
                    '92eb5ffee6ae2fec3ad71c777531578b.jpg': _mona_lisa
                },
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '4e15b4a3-ee52-4382-b8a8-7d492fb1a6ed': {  # Vision1
                    '04a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                },
                '5562b632-72c3-4c21-b24e-e0536d8b20c8': {  # TerraSAR-X
                    '8277e0910d750195b448797616e091ad.jpg': _mona_lisa
                },
            }
        }
    },
    '6e9a3589-d6c8-534e-ada1-b769aeec2fe2': {  # uuid-5
        'samples': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                'd51636c2-e94d-422c-a034-82e4ff8fa7aa': {  # Deimos-2
                    '92eb5ffee6ae2fec3ad71c777531578f': '',
                    '92eb5ffee6ae2fec3ad71c777531578b.jpg': _mona_lisa
                },
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '4e15b4a3-ee52-4382-b8a8-7d492fb1a6ed': {  # Vision1
                    '04a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                },
                '5562b632-72c3-4c21-b24e-e0536d8b20c8': {  # TerraSAR-X
                    '8277e0910d750195b448797616e091ad.jpg': _mona_lisa
                },
            }
        },
        'labels': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                '92eb5ffee6ae2fec3ad71c777531578f': '',
                '92eb5ffee6ae2fec3ad71c777531578b.json': _feature_collection
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '04a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '4a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '8277e0910d750195b448797616e091ad.json': _feature_collection
            }
        }
    },
    # ------------------------------------------------------------------------------------------------------------------
}


_tree_playground_summary_missing_dataset = {
    '63d0da07-0a4b-4ffd-844f-af75c02288e0': {
        'taxonomy.json': _taxonomy,
        'dataset_summary.json': _dataset_1_summary,
        'samples': {
            'fa719db8-31e9-49d1-9344-d4608ef6417e': {
                'f9525e3bfbd081cd545261b3b5414eb88f689005': {  # Pleiades
                    '7c47df1097b349278c052e93e1d1903a.jpg': _mona_lisa
                },
                '75ad128196254e711ef7c9b129d1c59153098b18': {  # Spot
                    '7c47df1097b349278c052e93e1d1903a.jpg': _mona_lisa
                },
            },
            'b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7': {
                'S2B_MSIL1C_20200212T025609_N0209_R003_T47DMH_20200212T054548': {  # Sentinel-2
                    '453e41d218e071ccfb2d1c99ce23906a.jpg': _mona_lisa,
                    '453e41d218e071ccfb2d1c99ce23906a.jgw': '',
                },
                '088dbf07-2879-4b23-af06-b3f4189fcae6': {  # AERIAL
                    '0cc175b9c0f1b6a831c399e269772661.jpg': _mona_lisa
                },
            },
            # ---------------------------------------------- Out -------------------------------------------------------
            '99aa890e-4d9a-11ea-92ec-a0481c91ddca': {  # uuid-1
                'S2B_MSIL1C_20200212T025609_N0209_R003_T47DMH_20200212T054548': {  # Sentinel-2
                    '453e41d218e071ccfb2d1c99ce23906a.jpg': _mona_lisa,
                    '453e41d218e071ccfb2d1c99ce23906a.jgw': '',
                },
                '088dbf07-2879-4b23-af06-b3f4189fcae6': {  # AERIAL
                    '0cc175b9c0f1b6a831c399e269772661.jpg': _mona_lisa
                },
            },
            '732af79d-f68d-393b-b2f8-9239bcd62a27': {  # uuid-3
                'f9525e3bfbd081cd545261b3b5414eb88f689005': {  # Pleiades
                    '7c47df1097b349278c052e93e1d1903a.jpg': _mona_lisa
                },
                '75ad128196254e711ef7c9b129d1c59153098b18': {  # Spot
                    '88aff0a92b21b86460bfd4474ab1626a.jpg': _mona_lisa
                },
            },
            'f9a071b2-7c2d-5987-b251-f386a554e28a': {  # uuid-5
                'S2B_MSIL1C_20200212T025609_N0209_R003_T47DMH_20200212T054548': {  # Sentinel-2
                    '453e41d218e071ccfb2d1c99ce23906a.jpg': _mona_lisa,
                    '453e41d218e071ccfb2d1c99ce23906a.jgw': '',
                },
            }
        },  # ----------------------------------------------------------------------------------------------------------
        'labels': {
            'fa719db8-31e9-49d1-9344-d4608ef6417e': {
                '7c47df1097b349278c052e93e1d1903a.json': _feature_collection
            },
            'b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7': {
                '453e41d218e071ccfb2d1c99ce23906a.json': _feature_collection,
                '0cc175b9c0f1b6a831c399e269772661.json': _feature_collection
            },
            # ---------------------------------------------- Out -------------------------------------------------------
            '99aa890e-4d9a-11ea-92ec-a0481c91ddca': {},  # uuid-1
            '732af79d-f68d-393b-b2f8-9239bcd62a27': {  # uuid-3
                '7c47df1097b349278c052e93e1d1903a.json': _feature_collection,
                '88aff0a92b21b86460bfd4474ab1626a.json': _feature_collection
            },
            'f9a071b2-7c2d-5987-b251-f386a554e28a': {  # uuid-5
                '453e41d218e071ccfb2d1c99ce23906a.json': _feature_collection,
            }
        },  # ----------------------------------------------------------------------------------------------------------
    },
    '1af6c4c5-278d-40ae-9e32-dc8192f8402a': {
        'taxonomy.json': _taxonomy,
        'samples': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                'd51636c2-e94d-422c-a034-82e4ff8fa7aa': {  # Deimos-2
                    '92eb5ffee6ae2fec3ad71c777531578f': '',
                    '92eb5ffee6ae2fec3ad71c777531578b.jpg': _mona_lisa
                },
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '4e15b4a3-ee52-4382-b8a8-7d492fb1a6ed': {  # Vision1
                    '04a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                },
                '5562b632-72c3-4c21-b24e-e0536d8b20c8': {  # TerraSAR-X
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa
                },
            }
        },
        'labels': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                '92eb5ffee6ae2fec3ad71c777531578f': '',
                '92eb5ffee6ae2fec3ad71c777531578b.json': _feature_collection
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '04a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '4a8a08f09d37b73795649038408b5f33.json': _feature_collection
            }
        }
    },
    # --------------------------------------------------- Out ----------------------------------------------------------
    'd53187c6-4d99-11ea-92ec-a0481c91ddca': {  # uuid-1
        'taxonomy.json': _taxonomy_conflict,
        'samples': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                'd51636c2-e94d-422c-a034-82e4ff8fa7aa': {  # Deimos-2
                    '92eb5ffee6ae2fec3ad71c777531578f': '',
                    '92eb5ffee6ae2fec3ad71c777531578b.jpg': _mona_lisa
                },
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '4e15b4a3-ee52-4382-b8a8-7d492fb1a6ed': {  # Vision1
                    '04a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                },
                '5562b632-72c3-4c21-b24e-e0536d8b20c8': {  # TerraSAR-X
                    '8277e0910d750195b448797616e091ad.jpg': _mona_lisa
                }
            }
        },
        'labels': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                '92eb5ffee6ae2fec3ad71c777531578f': '',
                '92eb5ffee6ae2fec3ad71c777531578b.json': _feature_collection
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '04a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '4a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '8277e0910d750195b448797616e091ad.json': _feature_collection
            }
        }
    },
    'bb959eb8-692f-3225-9506-e885ac3770bf': {  # uuid-3
        'samples': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                'd51636c2-e94d-422c-a034-82e4ff8fa7aa': {  # Deimos-2
                    '92eb5ffee6ae2fec3ad71c777531578f': '',
                    '92eb5ffee6ae2fec3ad71c777531578b.jpg': _mona_lisa
                },
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '4e15b4a3-ee52-4382-b8a8-7d492fb1a6ed': {  # Vision1
                    '04a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                },
                '5562b632-72c3-4c21-b24e-e0536d8b20c8': {  # TerraSAR-X
                    '8277e0910d750195b448797616e091ad.jpg': _mona_lisa
                },
            }
        }
    },
    '6e9a3589-d6c8-534e-ada1-b769aeec2fe2': {  # uuid-5
        'samples': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                'd51636c2-e94d-422c-a034-82e4ff8fa7aa': {  # Deimos-2
                    '92eb5ffee6ae2fec3ad71c777531578f': '',
                    '92eb5ffee6ae2fec3ad71c777531578b.jpg': _mona_lisa
                },
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '4e15b4a3-ee52-4382-b8a8-7d492fb1a6ed': {  # Vision1
                    '04a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                },
                '5562b632-72c3-4c21-b24e-e0536d8b20c8': {  # TerraSAR-X
                    '8277e0910d750195b448797616e091ad.jpg': _mona_lisa
                },
            }
        },
        'labels': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                '92eb5ffee6ae2fec3ad71c777531578f': '',
                '92eb5ffee6ae2fec3ad71c777531578b.json': _feature_collection
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '04a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '4a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '8277e0910d750195b448797616e091ad.json': _feature_collection
            }
        }
    },
    # ------------------------------------------------------------------------------------------------------------------
}


_tree_playground_summary_missing_summaries = {
    '63d0da07-0a4b-4ffd-844f-af75c02288e0': {
        'taxonomy.json': _taxonomy,
        'samples': {
            'fa719db8-31e9-49d1-9344-d4608ef6417e': {
                'f9525e3bfbd081cd545261b3b5414eb88f689005': {  # Pleiades
                    '7c47df1097b349278c052e93e1d1903a.jpg': _mona_lisa
                },
                '75ad128196254e711ef7c9b129d1c59153098b18': {  # Spot
                    '7c47df1097b349278c052e93e1d1903a.jpg': _mona_lisa
                },
            },
            'b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7': {
                'S2B_MSIL1C_20200212T025609_N0209_R003_T47DMH_20200212T054548': {  # Sentinel-2
                    '453e41d218e071ccfb2d1c99ce23906a.jpg': _mona_lisa,
                    '453e41d218e071ccfb2d1c99ce23906a.jgw': '',
                },
                '088dbf07-2879-4b23-af06-b3f4189fcae6': {  # AERIAL
                    '0cc175b9c0f1b6a831c399e269772661.jpg': _mona_lisa
                },
            },
            # ---------------------------------------------- Out -------------------------------------------------------
            '99aa890e-4d9a-11ea-92ec-a0481c91ddca': {  # uuid-1
                'S2B_MSIL1C_20200212T025609_N0209_R003_T47DMH_20200212T054548': {  # Sentinel-2
                    '453e41d218e071ccfb2d1c99ce23906a.jpg': _mona_lisa,
                    '453e41d218e071ccfb2d1c99ce23906a.jgw': '',
                },
                '088dbf07-2879-4b23-af06-b3f4189fcae6': {  # AERIAL
                    '0cc175b9c0f1b6a831c399e269772661.jpg': _mona_lisa
                },
            },
            '732af79d-f68d-393b-b2f8-9239bcd62a27': {  # uuid-3
                'f9525e3bfbd081cd545261b3b5414eb88f689005': {  # Pleiades
                    '7c47df1097b349278c052e93e1d1903a.jpg': _mona_lisa
                },
                '75ad128196254e711ef7c9b129d1c59153098b18': {  # Spot
                    '88aff0a92b21b86460bfd4474ab1626a.jpg': _mona_lisa
                },
            },
            'f9a071b2-7c2d-5987-b251-f386a554e28a': {  # uuid-5
                'S2B_MSIL1C_20200212T025609_N0209_R003_T47DMH_20200212T054548': {  # Sentinel-2
                    '453e41d218e071ccfb2d1c99ce23906a.jpg': _mona_lisa,
                    '453e41d218e071ccfb2d1c99ce23906a.jgw': '',
                },
            }
        },  # ----------------------------------------------------------------------------------------------------------
        'labels': {
            'fa719db8-31e9-49d1-9344-d4608ef6417e': {
                '7c47df1097b349278c052e93e1d1903a.json': _feature_collection
            },
            'b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7': {
                '453e41d218e071ccfb2d1c99ce23906a.json': _feature_collection,
                '0cc175b9c0f1b6a831c399e269772661.json': _feature_collection
            },
            # ---------------------------------------------- Out -------------------------------------------------------
            '99aa890e-4d9a-11ea-92ec-a0481c91ddca': {},  # uuid-1
            '732af79d-f68d-393b-b2f8-9239bcd62a27': {  # uuid-3
                '7c47df1097b349278c052e93e1d1903a.json': _feature_collection,
                '88aff0a92b21b86460bfd4474ab1626a.json': _feature_collection
            },
            'f9a071b2-7c2d-5987-b251-f386a554e28a': {  # uuid-5
                '453e41d218e071ccfb2d1c99ce23906a.json': _feature_collection,
            }
        },  # ----------------------------------------------------------------------------------------------------------
    },
    '1af6c4c5-278d-40ae-9e32-dc8192f8402a': {
        'taxonomy.json': _taxonomy,
        'samples': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                'd51636c2-e94d-422c-a034-82e4ff8fa7aa': {  # Deimos-2
                    '92eb5ffee6ae2fec3ad71c777531578f': '',
                    '92eb5ffee6ae2fec3ad71c777531578b.jpg': _mona_lisa
                },
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '4e15b4a3-ee52-4382-b8a8-7d492fb1a6ed': {  # Vision1
                    '04a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                },
                '5562b632-72c3-4c21-b24e-e0536d8b20c8': {  # TerraSAR-X
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa
                },
            }
        },
        'labels': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                '92eb5ffee6ae2fec3ad71c777531578f': '',
                '92eb5ffee6ae2fec3ad71c777531578b.json': _feature_collection
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '04a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '4a8a08f09d37b73795649038408b5f33.json': _feature_collection
            }
        }
    },
    # --------------------------------------------------- Out ----------------------------------------------------------
    'd53187c6-4d99-11ea-92ec-a0481c91ddca': {  # uuid-1
        'taxonomy.json': _taxonomy_conflict,
        'samples': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                'd51636c2-e94d-422c-a034-82e4ff8fa7aa': {  # Deimos-2
                    '92eb5ffee6ae2fec3ad71c777531578f': '',
                    '92eb5ffee6ae2fec3ad71c777531578b.jpg': _mona_lisa
                },
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '4e15b4a3-ee52-4382-b8a8-7d492fb1a6ed': {  # Vision1
                    '04a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                },
                '5562b632-72c3-4c21-b24e-e0536d8b20c8': {  # TerraSAR-X
                    '8277e0910d750195b448797616e091ad.jpg': _mona_lisa
                }
            }
        },
        'labels': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                '92eb5ffee6ae2fec3ad71c777531578f': '',
                '92eb5ffee6ae2fec3ad71c777531578b.json': _feature_collection
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '04a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '4a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '8277e0910d750195b448797616e091ad.json': _feature_collection
            }
        }
    },
    'bb959eb8-692f-3225-9506-e885ac3770bf': {  # uuid-3
        'samples': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                'd51636c2-e94d-422c-a034-82e4ff8fa7aa': {  # Deimos-2
                    '92eb5ffee6ae2fec3ad71c777531578f': '',
                    '92eb5ffee6ae2fec3ad71c777531578b.jpg': _mona_lisa
                },
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '4e15b4a3-ee52-4382-b8a8-7d492fb1a6ed': {  # Vision1
                    '04a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                },
                '5562b632-72c3-4c21-b24e-e0536d8b20c8': {  # TerraSAR-X
                    '8277e0910d750195b448797616e091ad.jpg': _mona_lisa
                },
            }
        }
    },
    '6e9a3589-d6c8-534e-ada1-b769aeec2fe2': {  # uuid-5
        'samples': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                'd51636c2-e94d-422c-a034-82e4ff8fa7aa': {  # Deimos-2
                    '92eb5ffee6ae2fec3ad71c777531578f': '',
                    '92eb5ffee6ae2fec3ad71c777531578b.jpg': _mona_lisa
                },
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '4e15b4a3-ee52-4382-b8a8-7d492fb1a6ed': {  # Vision1
                    '04a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                },
                '5562b632-72c3-4c21-b24e-e0536d8b20c8': {  # TerraSAR-X
                    '8277e0910d750195b448797616e091ad.jpg': _mona_lisa
                },
            }
        },
        'labels': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                '92eb5ffee6ae2fec3ad71c777531578f': '',
                '92eb5ffee6ae2fec3ad71c777531578b.json': _feature_collection
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '04a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '4a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '8277e0910d750195b448797616e091ad.json': _feature_collection
            }
        }
    },
    # ------------------------------------------------------------------------------------------------------------------
}

_tree_playground_conflict = {
    '63d0da07-0a4b-4ffd-844f-af75c02288e0': {
        'taxonomy.json': _taxonomy,
        'samples': {
            'fa719db8-31e9-49d1-9344-d4608ef6417e': {
                'f9525e3bfbd081cd545261b3b5414eb88f689005': {  # Pleiades
                    '7c47df1097b349278c052e93e1d1903a.jpg': _mona_lisa
                },
                '75ad128196254e711ef7c9b129d1c59153098b18': {  # Spot
                    '7c47df1097b349278c052e93e1d1903a.jpg': _mona_lisa
                },
            },
            'b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7': {
                'S2B_MSIL1C_20200212T025609_N0209_R003_T47DMH_20200212T054548': {  # Sentinel-2
                    '453e41d218e071ccfb2d1c99ce23906a.jpg': _mona_lisa,
                    '453e41d218e071ccfb2d1c99ce23906a.jgw': '',
                },
                '088dbf07-2879-4b23-af06-b3f4189fcae6': {  # AERIAL
                    '0cc175b9c0f1b6a831c399e269772661.jpg': _mona_lisa
                },
            },
            # ---------------------------------------------- Out -------------------------------------------------------
            '99aa890e-4d9a-11ea-92ec-a0481c91ddca': {  # uuid-1
                'S2B_MSIL1C_20200212T025609_N0209_R003_T47DMH_20200212T054548': {  # Sentinel-2
                    '453e41d218e071ccfb2d1c99ce23906a.jpg': _mona_lisa,
                    '453e41d218e071ccfb2d1c99ce23906a.jgw': '',
                },
                '088dbf07-2879-4b23-af06-b3f4189fcae6': {  # AERIAL
                    '0cc175b9c0f1b6a831c399e269772661.jpg': _mona_lisa
                },
            },
            '732af79d-f68d-393b-b2f8-9239bcd62a27': {  # uuid-3
                'f9525e3bfbd081cd545261b3b5414eb88f689005': {  # Pleiades
                    '7c47df1097b349278c052e93e1d1903a.jpg': _mona_lisa
                },
                '75ad128196254e711ef7c9b129d1c59153098b18': {  # Spot
                    '88aff0a92b21b86460bfd4474ab1626a.jpg': _mona_lisa
                },
            },
            'f9a071b2-7c2d-5987-b251-f386a554e28a': {  # uuid-5
                'S2B_MSIL1C_20200212T025609_N0209_R003_T47DMH_20200212T054548': {  # Sentinel-2
                    '453e41d218e071ccfb2d1c99ce23906a.jpg': _mona_lisa,
                    '453e41d218e071ccfb2d1c99ce23906a.jgw': '',
                },
            }
        },  # ----------------------------------------------------------------------------------------------------------
        'labels': {
            'fa719db8-31e9-49d1-9344-d4608ef6417e': {
                '7c47df1097b349278c052e93e1d1903a.json': _feature_collection
            },
            'b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7': {
                '453e41d218e071ccfb2d1c99ce23906a.json': _feature_collection,
                '0cc175b9c0f1b6a831c399e269772661.json': _feature_collection
            },
            # ---------------------------------------------- Out -------------------------------------------------------
            '99aa890e-4d9a-11ea-92ec-a0481c91ddca': {},  # uuid-1
            '732af79d-f68d-393b-b2f8-9239bcd62a27': {  # uuid-3
                '7c47df1097b349278c052e93e1d1903a.json': _feature_collection,
                '88aff0a92b21b86460bfd4474ab1626a.json': _feature_collection
            },
            'f9a071b2-7c2d-5987-b251-f386a554e28a': {  # uuid-5
                '453e41d218e071ccfb2d1c99ce23906a.json': _feature_collection,
            }
        },  # ----------------------------------------------------------------------------------------------------------
    },
    '1af6c4c5-278d-40ae-9e32-dc8192f8402a': {
        'taxonomy.json': _taxonomy_conflict,
        'samples': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                'd51636c2-e94d-422c-a034-82e4ff8fa7aa': {  # Deimos-2
                    '92eb5ffee6ae2fec3ad71c777531578f': '',
                    '92eb5ffee6ae2fec3ad71c777531578b.jpg': _mona_lisa
                },
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '4e15b4a3-ee52-4382-b8a8-7d492fb1a6ed': {  # Vision1
                    '04a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                },
                '5562b632-72c3-4c21-b24e-e0536d8b20c8': {  # TerraSAR-X
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa
                },
            }
        },
        'labels': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                '92eb5ffee6ae2fec3ad71c777531578f': '',
                '92eb5ffee6ae2fec3ad71c777531578b.json': _feature_collection
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '04a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '4a8a08f09d37b73795649038408b5f33.json': _feature_collection
            }
        }
    },
    # --------------------------------------------------- Out ----------------------------------------------------------
    'd53187c6-4d99-11ea-92ec-a0481c91ddca': {  # uuid-1
        'taxonomy.json': _taxonomy_conflict,
        'samples': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                'd51636c2-e94d-422c-a034-82e4ff8fa7aa': {  # Deimos-2
                    '92eb5ffee6ae2fec3ad71c777531578f': '',
                    '92eb5ffee6ae2fec3ad71c777531578b.jpg': _mona_lisa
                },
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '4e15b4a3-ee52-4382-b8a8-7d492fb1a6ed': {  # Vision1
                    '04a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                },
                '5562b632-72c3-4c21-b24e-e0536d8b20c8': {  # TerraSAR-X
                    '8277e0910d750195b448797616e091ad.jpg': _mona_lisa
                }
            }
        },
        'labels': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                '92eb5ffee6ae2fec3ad71c777531578f': '',
                '92eb5ffee6ae2fec3ad71c777531578b.json': _feature_collection
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '04a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '4a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '8277e0910d750195b448797616e091ad.json': _feature_collection
            }
        }
    },
    'bb959eb8-692f-3225-9506-e885ac3770bf': {  # uuid-3
        'samples': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                'd51636c2-e94d-422c-a034-82e4ff8fa7aa': {  # Deimos-2
                    '92eb5ffee6ae2fec3ad71c777531578f': '',
                    '92eb5ffee6ae2fec3ad71c777531578b.jpg': _mona_lisa
                },
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '4e15b4a3-ee52-4382-b8a8-7d492fb1a6ed': {  # Vision1
                    '04a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                },
                '5562b632-72c3-4c21-b24e-e0536d8b20c8': {  # TerraSAR-X
                    '8277e0910d750195b448797616e091ad.jpg': _mona_lisa
                },
            }
        }
    },
    '6e9a3589-d6c8-534e-ada1-b769aeec2fe2': {  # uuid-5
        'samples': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                'd51636c2-e94d-422c-a034-82e4ff8fa7aa': {  # Deimos-2
                    '92eb5ffee6ae2fec3ad71c777531578f': '',
                    '92eb5ffee6ae2fec3ad71c777531578b.jpg': _mona_lisa
                },
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '4e15b4a3-ee52-4382-b8a8-7d492fb1a6ed': {  # Vision1
                    '04a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                    '4a8a08f09d37b73795649038408b5f33.jpg': _mona_lisa,
                },
                '5562b632-72c3-4c21-b24e-e0536d8b20c8': {  # TerraSAR-X
                    '8277e0910d750195b448797616e091ad.jpg': _mona_lisa
                },
            }
        },
        'labels': {
            'c3e8b68b-f862-41bd-848c-6e2df28e4dd8': {
                '92eb5ffee6ae2fec3ad71c777531578f': '',
                '92eb5ffee6ae2fec3ad71c777531578b.json': _feature_collection
            },
            '2411dbb6-e7bf-41fd-8898-83325a9c6e5a': {
                '04a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '4a8a08f09d37b73795649038408b5f33.json': _feature_collection,
                '8277e0910d750195b448797616e091ad.json': _feature_collection
            }
        }
    },
    # ------------------------------------------------------------------------------------------------------------------
}


def _make_tree_level_from_dict(root, tree):
    pointer = Path(root)
    for name, value in tree.items():
        if isinstance(value, dict):
            (pointer / name).mkdir(exist_ok=True)
            _make_tree_level_from_dict(pointer / name, value)
        else:
            with open(str(pointer / name), 'wb') as f:
                if isinstance(value, str):
                    value = value.encode('utf8')
                f.write(value)


def _make_tree_path_list_from_dict(root, tree):
    pointer = Path(root)
    for name, value in tree.items():
        if isinstance(value, dict):
            yield from _make_tree_path_list_from_dict(pointer / name, value)
        else:
            yield pointer / name


def _clean_up(path):
    for root, dirs, files in path.walk():
        for f in files:
            os.unlink(str(root / f))
        for d in dirs:
            shutil.rmtree(str(root / d))


@pytest.fixture()
def json_feature_collection():
    return _feature_collection.decode('utf8')


@pytest.fixture(scope="session", autouse=True)
def cache():
    cache_dir = Path(user_cache_dir('plums')) / 'pattern'
    _clean_up(cache_dir)
    yield
    _clean_up(cache_dir)


@pytest.fixture(scope='session')
def complex_tree(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp('complex_tree')
    _make_tree_level_from_dict(tmp_path, _tree_complex)
    return Path(tmp_path), list(_make_tree_path_list_from_dict(tmp_path, _tree_complex))


@pytest.fixture(scope='session')
def loose_pattern_tree(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp('loose_pattern_tree')
    _make_tree_level_from_dict(tmp_path, _tree_pattern_loose)
    return Path(tmp_path), list(_make_tree_path_list_from_dict(tmp_path, _tree_pattern_loose))


@pytest.fixture(scope='session')
def strict_pattern_tree(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp('strict_pattern_tree')
    _make_tree_level_from_dict(tmp_path, _tree_pattern_strict)
    return Path(tmp_path), list(_make_tree_path_list_from_dict(tmp_path, _tree_pattern_strict))


@pytest.fixture(scope='session')
def playground_tree(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp('playground_tree')
    _make_tree_level_from_dict(tmp_path, _tree_playground)
    return Path(tmp_path), list(_make_tree_path_list_from_dict(tmp_path, _tree_playground))


@pytest.fixture(scope='session')
def playground_tree_conflict(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp('playground_tree_conflict')
    _make_tree_level_from_dict(tmp_path, _tree_playground_conflict)
    return Path(tmp_path), list(_make_tree_path_list_from_dict(tmp_path, _tree_playground_conflict))


@pytest.fixture(scope='session')
def playground_tree_summary_missing_image(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp('playground_tree_summary_missing_image')
    _make_tree_level_from_dict(tmp_path, _tree_playground_summary_missing_image)
    return Path(tmp_path), list(_make_tree_path_list_from_dict(tmp_path, _tree_playground_summary_missing_image))


@pytest.fixture(scope='session')
def playground_tree_summary_missing_zone(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp('playground_tree_summary_missing_zone')
    _make_tree_level_from_dict(tmp_path, _tree_playground_summary_missing_zone)
    return Path(tmp_path), list(_make_tree_path_list_from_dict(tmp_path, _tree_playground_summary_missing_zone))


@pytest.fixture(scope='session')
def playground_tree_summary_missing_dataset(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp('playground_tree_summary_missing_dataset')
    _make_tree_level_from_dict(tmp_path, _tree_playground_summary_missing_dataset)
    return Path(tmp_path), list(_make_tree_path_list_from_dict(tmp_path, _tree_playground_summary_missing_dataset))


@pytest.fixture(scope='session')
def playground_tree_summary_missing_summaries(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp('playground_tree_summary_missing_summaries')
    _make_tree_level_from_dict(tmp_path, _tree_playground_summary_missing_summaries)
    return Path(tmp_path), list(_make_tree_path_list_from_dict(tmp_path, _tree_playground_summary_missing_summaries))
