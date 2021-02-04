from contextlib import contextmanager

import pytest
import yaml

from plums.commons.path import Path


@contextmanager
def does_not_raise():
    yield

#  'Checkpoint',
#  'Data',
#  'Default',
#  'DefaultTree',
#  'Initialisation',
#  'InitialisationPMF',
#  'InitialisationPath',
#  'Metadata',
#  'Model'


# Metadata -------------------------------------------------------------------------------------------------------------
__metadata__ = \
    {
        'format': {
            'version': '1.0.0',
            'producer': {
                'name': 'a_producer_name',
                'version': {
                    'format': 'py_pa',
                    'value': '1.0.0'
                }
            }
        },
        'model': {
            'name': 'my_model',
            'id': 'some_id',
            'configuration': {
                'path': 'my_config_file.yaml',
                'hash': 'd41d8cd98f00b204e9800998ecf8427e'  # Empty
            },
            'initialisation': {
                'pmf': {
                    'name': 'my_init_model',
                    'id': 'some_init_id',
                    'checkpoint': 6,
                    'path': 'data/initialisation'
                }
            },
            'training': {
                'status': 'finished',
                'start_epoch': 0,
                'start_time': 0,
                'latest_epoch': 10,
                'latest_time': 10,
                'end_epoch': 10,
                'end_time': 10,
                'latest': 6,
                'checkpoints': {
                    1: {
                        'epoch': 3,
                        'path': 'data/checkpoints/1.weight',
                        'hash': 'd41d8cd98f00b204e9800998ecf8427e'  # Empty
                    },
                    6: {
                        'epoch': 10,
                        'path': 'data/checkpoints/6.weight',
                        'hash': 'cfcd208495d565ef66e7dff9f98764da'  # Only a '0' inside
                    }
                }
            }
        }
    }


__metadata_empty__ = \
    {
        'format': {
            'version': '1.0.0',
            'producer': {
                'name': 'a_producer_name',
                'version': {
                    'format': 'py_pa',
                    'value': '1.0.0'
                }
            }
        },
        'model': {
            'name': 'my_model',
            'id': 'some_id',
            'configuration': {
                'path': 'my_config_file.yaml',
                'hash': 'd41d8cd98f00b204e9800998ecf8427e'  # Empty
            },
            'initialisation': {
                'pmf': {
                    'name': 'my_init_model',
                    'id': 'some_init_id',
                    'checkpoint': 6,
                    'path': 'data/initialisation'
                }
            },
            'training': {
                'status': 'pending',
                'start_epoch': None,
                'start_time': None,
                'latest_epoch': None,
                'latest_time': None,
                'end_epoch': None,
                'end_time': None,
                'latest': None,
                'checkpoints': {}
            }
        }
    }


__init_metadata_empty__ = \
    {
        'format': {
            'version': '1.0.0',
            'producer': {
                'name': 'a_producer_name',
                'version': {
                    'format': 'py_pa',
                    'value': '1.0.0'
                }
            }
        },
        'model': {
            'name': 'my_init_model',
            'id': 'some_init_id',
            'configuration': {
                'path': 'my_config_file.yaml',
                'hash': 'cfcd208495d565ef66e7dff9f98764da'  # Only a '0' inside
            },
            'initialisation': None,
            'training': {
                'status': 'finished',
                'start_epoch': 0,
                'start_time': 0,
                'latest_epoch': 10,
                'latest_time': 10,
                'end_epoch': 10,
                'end_time': 10,
                'latest': 6,
                'checkpoints': {
                    6: {
                        'epoch': 10,
                        'path': 'data/checkpoints/6.weight',
                        'hash': 'cfcd208495d565ef66e7dff9f98764da'  # Only a '0' inside
                    },
                    7: {
                        'epoch': 9,
                        'path': 'data/checkpoints/6.weight',
                        'hash': 'cfcd208495d565ef66e7dff9f98764da'  # Only a '0' inside
                    }
                }
            }
        }
    }


__init_metadata__ = \
    {
        'format': {
            'version': '1.0.0',
            'producer': {
                'name': 'a_producer_name',
                'version': {
                    'format': 'py_pa',
                    'value': '1.0.0'
                }
            }
        },
        'model': {
            'name': 'my_init_model',
            'id': 'some_init_id',
            'configuration': {
                'path': 'my_config_file.yaml',
                'hash': 'cfcd208495d565ef66e7dff9f98764da'  # Only a '0' inside
            },
            'initialisation': {
                'file': {
                    'name': 'my_init_file',
                    'path': 'data/initialisation/init.weight',
                    'hash': 'd41d8cd98f00b204e9800998ecf8427e'  # Empty
                }
            },
            'training': {
                'status': 'finished',
                'start_epoch': 0,
                'start_time': 0,
                'latest_epoch': 10,
                'latest_time': 10,
                'end_epoch': 10,
                'end_time': 10,
                'latest': 6,
                'checkpoints': {
                    6: {
                        'epoch': 10,
                        'path': 'data/checkpoints/6.weight',
                        'hash': 'cfcd208495d565ef66e7dff9f98764da'  # Only a '0' inside
                    },
                    7: {
                        'epoch': 9,
                        'path': 'data/checkpoints/6.weight',
                        'hash': 'cfcd208495d565ef66e7dff9f98764da'  # Only a '0' inside
                    }
                }
            }
        }
    }


__init_metadata_invalid__ = \
    {
        'format': {
            'version': '1.0.0',
            'producer': {
                'name': 'a_producer_name',
                'version': {
                    'format': 'py_pa',
                    'value': '1.0.0'
                }
            }
        },
        'model': {
            'name': 'my_init_model',
            'id': 'some_init_id',
            'configuration': {
                'path': 'my_config_file.yaml',
                'hash': 'cfcd208495d565ef66e7dff9f98764da'  # Only a '0' inside
            },
            'initialisation': {
                'file': {
                    'name': 'my_init_file',
                    'path': 'data/initialisation/init.weight',
                    'hash': 'd41d8cd98f00b204e9800998ecf8427e'  # Empty
                }
            },
            'training': {
                'status': 'finished',
                'start_epoch': 0,
                'start_time': 0,
                'latest_epoch': 10,
                'latest_time': 10,
                'end_epoch': 10,
                'end_time': 10,
                'latest': 10,
                'checkpoints': {
                    10: {  # Invalid (main init ref is not 10 but 6)
                        'epoch': 10,
                        'path': 'data/checkpoints/6.weight',
                        'hash': 'cfcd208495d565ef66e7dff9f98764da'  # Only a '0' inside
                    },
                    7: {
                        'epoch': 9,
                        'path': 'data/checkpoints/6.weight',
                        'hash': 'cfcd208495d565ef66e7dff9f98764da'  # Only a '0' inside
                    }
                }
            }
        }
    }

# Valid trees ----------------------------------------------------------------------------------------------------------
_valid_tree_empty = {
    'metadata.yaml': yaml.safe_dump(__metadata_empty__),
    'my_config_file.yaml': '',
    'data': {
        'build_parameters.yaml': '',
        'checkpoints': {},
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata_empty__),
            'my_config_file.yaml': '0',
            'data': {
                'build_parameters.yaml': '',
                'initialisation': {}
            }
        }
    }
}

_valid_tree = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    'data': {
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0'
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',
            'data': {
                'build_parameters.yaml': '',
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}


_valid_tree_extra = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    # Extras ----------
    'some_file': 'some_content',
    'some_dir': {
        'some_enclosed_file': 'some_content',
        'some_enclosed_dir': {
            'some_content': 'in_some_file'
        }
    },
    # -----------------
    'data': {
        # Extras ----------
        'some_file': 'some_content',
        'some_dir': {
            'some_enclosed_file': 'some_content',
            'some_enclosed_dir': {
                'some_content': 'in_some_file'
            }
        },
        # -----------------
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0',
            # Extras ----------
            '10.weight': '150'
            # -----------------
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',
            'data': {
                # Extras ----------
                'some_file': 'some_content',
                'some_dir': {
                    'some_enclosed_file': 'some_content',
                    'some_enclosed_dir': {
                        'some_content': 'in_some_file'
                    }
                },
                # -----------------
                'build_parameters.yaml': '',
                # Extras ----------
                'checkpoints': {
                    '10.weight': '5',
                },
                # -----------------
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}

# Invalid trees --------------------------------------------------------------------------------------------------------
# > Invalid (discrepancy issue) ---------------------------------------------------------------------------------------
_invalid_tree_discrepancy_0 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    'data': {
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': ''  # Invalid
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata_invalid__),
            'my_config_file.yaml': '0',
            'data': {
                'build_parameters.yaml': '',
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}

_invalid_tree_discrepancy_1 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    'data': {
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': ''  # Invalid
        },
        'initialisation': {
            'init.weight': ''
        }
    }
}

_invalid_tree_discrepancy_2 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    'data': {
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0'
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',
            'data': {
                'build_parameters.yaml': '',
                'initialisation': {   # Invalid
                    'metadata.yaml': yaml.safe_dump(__init_metadata__),
                    'my_config_file.yaml': '0',
                    'data': {
                        'build_parameters.yaml': '',
                        'initialisation': {
                            'init.weight': ''
                        }
                    }
                }
            }
        }
    }
}

# > Strict invalid (content issue) -------------------------------------------------------------------------------------
_invalid_tree_content_0 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    'data': {
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': ''  # Invalid
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',
            'data': {
                'build_parameters.yaml': '',
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}

_invalid_tree_content_1 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    'data': {
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '0',  # Invalid
            '6.weight': '0'
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',
            'data': {
                'build_parameters.yaml': '',
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}

_invalid_tree_content_2 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '0',  # Invalid
    'data': {
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0'
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',
            'data': {
                'build_parameters.yaml': '',
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}

_invalid_tree_content_3 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    'data': {
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0'
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '',  # Invalid
            'data': {
                'build_parameters.yaml': '',
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}

_invalid_tree_content_4 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    'data': {
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0'
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',
            'data': {
                'build_parameters.yaml': '',
                'initialisation': {
                    'init.weight': '0'  # Invalid
                }
            }
        }
    }
}

# > Invalid (content issue) -------------------------------------------------------------------------------------

_invalid_tree_content_5 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    'data': {
        'build_parameters.yaml': '',
        'checkpoints': {
            '10.weight': '',  # Invalid
            '6.weight': '0'
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',
            'data': {
                'build_parameters.yaml': '',
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}

_invalid_tree_content_6 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file_0.yaml': '',  # Invalid
    'data': {
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0'
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',
            'data': {
                'build_parameters.yaml': '',
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}

_invalid_tree_content_7 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    'data': {
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0'
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file_0.yaml': '0',  # Invalid
            'data': {
                'build_parameters.yaml': '',
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}

_invalid_tree_content_8 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    'data': {
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0'
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',
            'data': {
                'build_parameters.yaml': '',
                'initialisation': {
                    'init_0.weight': ''  # Invalid
                }
            }
        }
    }
}

_invalid_tree_content_9 = {
    'metadata.yml': yaml.safe_dump(__metadata__),  # Invalid
    'my_config_file.yaml': '',
    'data': {
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0'
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',
            'data': {
                'build_parameters.yaml': '',
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}

_invalid_tree_content_10 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    'data': {
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0'
        },
        'initialisation': {
            'metadata.yml': yaml.safe_dump(__init_metadata__),  # Invalid
            'my_config_file.yaml': '0',
            'data': {
                'build_parameters.yaml': '',
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}

_invalid_tree_content_11 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    'data': {
        'build_parameters.yml': '',  # Invalid
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0'
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',
            'data': {
                'build_parameters.yaml': '',
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}

_invalid_tree_content_12 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    'data': {
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0'
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',
            'data': {
                'build_parameters.yml': '',  # Invalid
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}


# > Invalid (missing issue) --------------------------------------------------------------------------------------------
_invalid_tree_missing_0 = {  # Issue
    'my_config_file.yaml': '',
    'data': {
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0'
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',
            'data': {
                'build_parameters.yaml': '',
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}
_invalid_tree_extra_missing_0 = {  # Issue
    'my_config_file.yaml': '',
    # Extras ----------
    'some_file': 'some_content',
    'some_dir': {
        'some_enclosed_file': 'some_content',
        'some_enclosed_dir': {
            'some_content': 'in_some_file'
        }
    },
    # -----------------
    'data': {
        # Extras ----------
        'some_file': 'some_content',
        'some_dir': {
            'some_enclosed_file': 'some_content',
            'some_enclosed_dir': {
                'some_content': 'in_some_file'
            }
        },
        # -----------------
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0',
            # Extras ----------
            '10.weight': '150'
            # -----------------
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',
            'data': {
                # Extras ----------
                'some_file': 'some_content',
                'some_dir': {
                    'some_enclosed_file': 'some_content',
                    'some_enclosed_dir': {
                        'some_content': 'in_some_file'
                    }
                },
                # -----------------
                'build_parameters.yaml': '',
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}

_invalid_tree_missing_1 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),  # Issue
    'data': {
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0'
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',
            'data': {
                'build_parameters.yaml': '',
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}
_invalid_tree_extra_missing_1 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),  # Issue
    # Extras ----------
    'some_file': 'some_content',
    'some_dir': {
        'some_enclosed_file': 'some_content',
        'some_enclosed_dir': {
            'some_content': 'in_some_file'
        }
    },
    # -----------------
    'data': {
        # Extras ----------
        'some_file': 'some_content',
        'some_dir': {
            'some_enclosed_file': 'some_content',
            'some_enclosed_dir': {
                'some_content': 'in_some_file'
            }
        },
        # -----------------
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0',
            # Extras ----------
            '10.weight': '150'
            # -----------------
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',
            'data': {
                # Extras ----------
                'some_file': 'some_content',
                'some_dir': {
                    'some_enclosed_file': 'some_content',
                    'some_enclosed_dir': {
                        'some_content': 'in_some_file'
                    }
                },
                # -----------------
                'build_parameters.yaml': '',
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}

_invalid_tree_missing_2 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',  # Issue
}
_invalid_tree_extra_missing_2 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    # Extras ----------
    'some_file': 'some_content',
    'some_dir': {
        'some_enclosed_file': 'some_content',
        'some_enclosed_dir': {
            'some_content': 'in_some_file'
        }
    },
    # -----------------  # Issue
}

_invalid_tree_missing_3 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    'data': {  # Issue
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0'
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',
            'data': {
                'build_parameters.yaml': '',
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}
_invalid_tree_extra_missing_3 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    # Extras ----------
    'some_file': 'some_content',
    'some_dir': {
        'some_enclosed_file': 'some_content',
        'some_enclosed_dir': {
            'some_content': 'in_some_file'
        }
    },
    # -----------------
    'data': {
        # Extras ----------
        'some_file': 'some_content',
        'some_dir': {
            'some_enclosed_file': 'some_content',
            'some_enclosed_dir': {
                'some_content': 'in_some_file'
            }
        },
        # -----------------  # Issue
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0',
            # Extras ----------
            '10.weight': '150'
            # -----------------
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',
            'data': {
                # Extras ----------
                'some_file': 'some_content',
                'some_dir': {
                    'some_enclosed_file': 'some_content',
                    'some_enclosed_dir': {
                        'some_content': 'in_some_file'
                    }
                },
                # -----------------
                'build_parameters.yaml': '',
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}

_invalid_tree_missing_4 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    'data': {
        'build_parameters.yaml': '',  # Issue
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',
            'data': {
                'build_parameters.yaml': '',
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}
_invalid_tree_extra_missing_4 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    # Extras ----------
    'some_file': 'some_content',
    'some_dir': {
        'some_enclosed_file': 'some_content',
        'some_enclosed_dir': {
            'some_content': 'in_some_file'
        }
    },
    # -----------------
    'data': {
        # Extras ----------
        'some_file': 'some_content',
        'some_dir': {
            'some_enclosed_file': 'some_content',
            'some_enclosed_dir': {
                'some_content': 'in_some_file'
            }
        },
        # -----------------
        'build_parameters.yaml': '',  # Issue
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',
            'data': {
                # Extras ----------
                'some_file': 'some_content',
                'some_dir': {
                    'some_enclosed_file': 'some_content',
                    'some_enclosed_dir': {
                        'some_content': 'in_some_file'
                    }
                },
                # -----------------
                'build_parameters.yaml': '',
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}

_invalid_tree_missing_5 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    'data': {
        'build_parameters.yaml': '',
        'checkpoints': {  # Issue
            '6.weight': '0'
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',
            'data': {
                'build_parameters.yaml': '',
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}
_invalid_tree_extra_missing_5 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    # Extras ----------
    'some_file': 'some_content',
    'some_dir': {
        'some_enclosed_file': 'some_content',
        'some_enclosed_dir': {
            'some_content': 'in_some_file'
        }
    },
    # -----------------
    'data': {
        # Extras ----------
        'some_file': 'some_content',
        'some_dir': {
            'some_enclosed_file': 'some_content',
            'some_enclosed_dir': {
                'some_content': 'in_some_file'
            }
        },
        # -----------------
        'build_parameters.yaml': '',
        'checkpoints': {  # Issue
            '6.weight': '0',
            # Extras ----------
            '10.weight': '150'
            # -----------------
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',
            'data': {
                # Extras ----------
                'some_file': 'some_content',
                'some_dir': {
                    'some_enclosed_file': 'some_content',
                    'some_enclosed_dir': {
                        'some_content': 'in_some_file'
                    }
                },
                # -----------------
                'build_parameters.yaml': '',
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}

_invalid_tree_missing_6 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    'data': {
        'build_parameters.yaml': '',  # Issue
    }
}
_invalid_tree_extra_missing_6 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    # Extras ----------
    'some_file': 'some_content',
    'some_dir': {
        'some_enclosed_file': 'some_content',
        'some_enclosed_dir': {
            'some_content': 'in_some_file'
        }
    },
    # -----------------
    'data': {
        # Extras ----------
        'some_file': 'some_content',
        'some_dir': {
            'some_enclosed_file': 'some_content',
            'some_enclosed_dir': {
                'some_content': 'in_some_file'
            }
        },
        # -----------------
        'build_parameters.yaml': '',  # Issue
    }
}

_invalid_tree_missing_7 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    'data': {
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0'
        },
        'initialisation': {  # Issue
            'my_config_file.yaml': '0',
            'data': {
                'build_parameters.yaml': '',
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}
_invalid_tree_extra_missing_7 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    # Extras ----------
    'some_file': 'some_content',
    'some_dir': {
        'some_enclosed_file': 'some_content',
        'some_enclosed_dir': {
            'some_content': 'in_some_file'
        }
    },
    # -----------------
    'data': {
        # Extras ----------
        'some_file': 'some_content',
        'some_dir': {
            'some_enclosed_file': 'some_content',
            'some_enclosed_dir': {
                'some_content': 'in_some_file'
            }
        },
        # -----------------
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0',
            # Extras ----------
            '10.weight': '150'
            # -----------------
        },
        'initialisation': {  # Issue
            'my_config_file.yaml': '0',
            'data': {
                # Extras ----------
                'some_file': 'some_content',
                'some_dir': {
                    'some_enclosed_file': 'some_content',
                    'some_enclosed_dir': {
                        'some_content': 'in_some_file'
                    }
                },
                # -----------------
                'build_parameters.yaml': '',
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}

_invalid_tree_missing_8 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    'data': {
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0'
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),  # Issue
            'data': {
                'build_parameters.yaml': '',
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}
_invalid_tree_extra_missing_8 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    # Extras ----------
    'some_file': 'some_content',
    'some_dir': {
        'some_enclosed_file': 'some_content',
        'some_enclosed_dir': {
            'some_content': 'in_some_file'
        }
    },
    # -----------------
    'data': {
        # Extras ----------
        'some_file': 'some_content',
        'some_dir': {
            'some_enclosed_file': 'some_content',
            'some_enclosed_dir': {
                'some_content': 'in_some_file'
            }
        },
        # -----------------
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0',
            # Extras ----------
            '10.weight': '150'
            # -----------------
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),  # Issue
            'data': {
                # Extras ----------
                'some_file': 'some_content',
                'some_dir': {
                    'some_enclosed_file': 'some_content',
                    'some_enclosed_dir': {
                        'some_content': 'in_some_file'
                    }
                },
                # -----------------
                'build_parameters.yaml': '',
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}

_invalid_tree_missing_9 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    'data': {
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0'
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',  # Issue
        }
    }
}
_invalid_tree_extra_missing_9 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    # Extras ----------
    'some_file': 'some_content',
    'some_dir': {
        'some_enclosed_file': 'some_content',
        'some_enclosed_dir': {
            'some_content': 'in_some_file'
        }
    },
    # -----------------
    'data': {
        # Extras ----------
        'some_file': 'some_content',
        'some_dir': {
            'some_enclosed_file': 'some_content',
            'some_enclosed_dir': {
                'some_content': 'in_some_file'
            }
        },
        # -----------------
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0',
            # Extras ----------
            '10.weight': '150'
            # -----------------
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',  # Issue
        }
    }
}

_invalid_tree_missing_10 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    'data': {
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0'
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',
            'data': {  # Issue
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}
_invalid_tree_extra_missing_10 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    # Extras ----------
    'some_file': 'some_content',
    'some_dir': {
        'some_enclosed_file': 'some_content',
        'some_enclosed_dir': {
            'some_content': 'in_some_file'
        }
    },
    # -----------------
    'data': {
        # Extras ----------
        'some_file': 'some_content',
        'some_dir': {
            'some_enclosed_file': 'some_content',
            'some_enclosed_dir': {
                'some_content': 'in_some_file'
            }
        },
        # -----------------
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0',
            # Extras ----------
            '10.weight': '150'
            # -----------------
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',
            'data': {
                # Extras ----------
                'some_file': 'some_content',
                'some_dir': {
                    'some_enclosed_file': 'some_content',
                    'some_enclosed_dir': {
                        'some_content': 'in_some_file'
                    }
                },
                # -----------------  # Issue
                'initialisation': {
                    'init.weight': ''
                }
            }
        }
    }
}

_invalid_tree_missing_11 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    'data': {
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0'
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',
            'data': {
                'build_parameters.yaml': '',  # Issue
            }
        }
    }
}
_invalid_tree_extra_missing_11 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    # Extras ----------
    'some_file': 'some_content',
    'some_dir': {
        'some_enclosed_file': 'some_content',
        'some_enclosed_dir': {
            'some_content': 'in_some_file'
        }
    },
    # -----------------
    'data': {
        # Extras ----------
        'some_file': 'some_content',
        'some_dir': {
            'some_enclosed_file': 'some_content',
            'some_enclosed_dir': {
                'some_content': 'in_some_file'
            }
        },
        # -----------------
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0',
            # Extras ----------
            '10.weight': '150'
            # -----------------
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',
            'data': {
                # Extras ----------
                'some_file': 'some_content',
                'some_dir': {
                    'some_enclosed_file': 'some_content',
                    'some_enclosed_dir': {
                        'some_content': 'in_some_file'
                    }
                },
                # -----------------
                'build_parameters.yaml': '',  # Issue
            }
        }
    }
}

_invalid_tree_missing_12 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    'data': {
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0'
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',
            'data': {
                'build_parameters.yaml': '',
                'initialisation': {  # Issue
                }
            }
        }
    }
}
_invalid_tree_extra_missing_12 = {
    'metadata.yaml': yaml.safe_dump(__metadata__),
    'my_config_file.yaml': '',
    # Extras ----------
    'some_file': 'some_content',
    'some_dir': {
        'some_enclosed_file': 'some_content',
        'some_enclosed_dir': {
            'some_content': 'in_some_file'
        }
    },
    # -----------------
    'data': {
        # Extras ----------
        'some_file': 'some_content',
        'some_dir': {
            'some_enclosed_file': 'some_content',
            'some_enclosed_dir': {
                'some_content': 'in_some_file'
            }
        },
        # -----------------
        'build_parameters.yaml': '',
        'checkpoints': {
            '1.weight': '',
            '6.weight': '0',
            # Extras ----------
            '10.weight': '150'
            # -----------------
        },
        'initialisation': {
            'metadata.yaml': yaml.safe_dump(__init_metadata__),
            'my_config_file.yaml': '0',
            'data': {
                # Extras ----------
                'some_file': 'some_content',
                'some_dir': {
                    'some_enclosed_file': 'some_content',
                    'some_enclosed_dir': {
                        'some_content': 'in_some_file'
                    }
                },
                # -----------------
                'build_parameters.yaml': '',
                'initialisation': {  # Issue
                }
            }
        }
    }
}


def _make_invalid_params():
    p = tuple(entry[1:].replace('_', '-') for entry in globals()
              if '_invalid_tree_' in entry and not
              ('_invalid_tree_content_' in entry and entry.split('_')[-1] in ['0', '1', '2', '3', '4']))
    return sorted(p)


def _make_invalid_params_strict():
    p = tuple(entry[1:].replace('_', '-') for entry in globals()
              if '_invalid_tree_content_' in entry and entry.split('_')[-1] in ['0', '1', '2', '3', '4'])
    return sorted(p)


def _parse_param(param):
    return globals()['_{}'.format(param.replace('-', '_'))]


def _make_tree_level_from_dict(root, tree):
    pointer = Path(root)
    for name, value in tree.items():
        if isinstance(value, dict):
            (pointer / name).mkdir(exist_ok=True)
            _make_tree_level_from_dict(pointer / name, value)
        else:
            with open(str(pointer / name), 'w') as f:
                f.write(value)


@pytest.fixture()
def valid_tree_empty(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp('valid_tree_empty')
    _make_tree_level_from_dict(tmp_path, _valid_tree_empty)
    return Path(tmp_path)


@pytest.fixture()
def valid_tree(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp('valid_tree')
    _make_tree_level_from_dict(tmp_path, _valid_tree)
    return Path(tmp_path)


@pytest.fixture()
def valid_tree_extra(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp('valid_tree_extra')
    _make_tree_level_from_dict(tmp_path, _valid_tree_extra)
    return Path(tmp_path)


@pytest.fixture(params=_make_invalid_params())
def invalid_tree(request, tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp('invalid_tree')
    tree = _parse_param(request.param)
    _make_tree_level_from_dict(tmp_path, tree)
    return Path(tmp_path)


@pytest.fixture(params=_make_invalid_params_strict())
def invalid_tree_strict(request, tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp('invalid_tree_strict')
    tree = _parse_param(request.param)
    _make_tree_level_from_dict(tmp_path, tree)
    return Path(tmp_path)


@pytest.fixture(params=_make_invalid_params())
def invalid_tree_with_name(request, tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp('invalid_tree_with_name')
    tree = _parse_param(request.param)
    _make_tree_level_from_dict(tmp_path, tree)
    return request.param, Path(tmp_path)
