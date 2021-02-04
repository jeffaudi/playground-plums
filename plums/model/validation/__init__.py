from plums.commons.path import Path
from plums.model.validation.structure import Model
from plums.model.validation.metadata import Metadata
from plums.model.validation.utils.dict_from_tree import make_dict_structure_from_tree


def validate(path, strict=False, verbose=False, **kwargs):
    """Validate a **PMF** model location and return offending files or directories.

    Args:
        path (Pathlike): A |Path| to a model saved in a **PMF** format.
        strict (bool): Whether to perform strict validation (see |ModelTree|).
        verbose (bool): Optional. Default to ``False``. Toggle verbose offence reporting.
        **kwargs (Any): Additional arguments are passed to the |ModelTree| validator.

    Returns:
        dict: A parsed PMF model metadata structure if the model is valid.

    """
    validator = Model(strict=strict, verbose=verbose, **kwargs)

    path = Path(path)
    tree = make_dict_structure_from_tree(path)

    tree = validator.validate(tree)
    return tree['metadata.yaml']
