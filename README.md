# ![PLUMS](docs/source/_static/plums.png)

**PL**aygroundML **U**nified **M**icrolib **S**et : The **Playground ML** python *toolbox* package

[![pyversions](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8%20%7C%203.9-informational)](https://github.com/airbusgeo/playground-plums)
[![License](https://img.shields.io/badge/License-MIT-green)](https://choosealicense.com/licenses/mit/)


The Plums library set aims to defined a common set of packages to be used by people involved in thePlaygroundML team.

Those packages puropose is to set a unique baseline to help make the code base more unified and avoid countless reimplementation of the same tools which in turns make people waste time and make the code base herd to understand,
debug and reuse.

Installation is simple with *PyPI* repository:

```bash
pip install plums
```

[TODO]
More information on installation can be found in the [Getting Started](https://playground-plums.readthedocs.io/en/latest/content/getting_started.html) section of the documentation.

Documentation and tests specific dependencies can be installed with the ``docs`` and ``tests`` extra keywords respectively.

## Packages

### Commons

The Plums **commons** package aims to offer a set of lightweight highly
reusable classes and utilities for all other packages.

To import do:

```python
import plums.commons
```

### Plot

The Plums **plot** package aims to offer a set of lightweight highly
reusable classes and utilities for visualizing detection and segmentation
results.

To import do:

```python
import plums.plot
```

### Model

The Plums **model** package aims to offer a framework-agnostic model
format specification (the **P**lums **M**odel **F**ormat) along with its
python representation and helper implementation to ease integration into
producer and consumer codebases.

To import do:

```python
import plums.model
```

### Dataflow

**I/O** operations and efficient *dataset* iteration and indexing
handling.

To import do:

```python
import plums.dataflow
```

-------------------------------------------------------------------

## Objectives

### Dataflow

Dataflow elements to speedup future developements: e.g. `Dataset` classes, `Sampler` and/or `Dataloader` (?) and handle augmentation (`imgaug`, `albumentation`, `pure numpy` ?)

* Python representation of data elements (e.g. `Annotation`, `Feature`, `Image`, `Datapoint`...)
* `Dataset` classes for playground datasets
* `TranformedDataset`-like classes to manipulate, combine and transform (e.g. augmentations) datasets in an online fashion
* `Sampler` and `BatchSampler` classes to port PyTorch functionalities into Keras and build upon them

### Data-preparation

* Loop through datasets in a multi-threaded or multi-processed fashion
* Some convenient data-preparation functions such as image transformations or annotations refinement
* Some convenient statistic and analysis tools

### Visualisation

* Plot annotation on image
* Handle single image and image grids
* Plot differentials and/or superposition of annotations on same images
* Handle multiple color code mode, e.g.:
	* By label
	* By confidence
	* By size
	* By type (in differential plotting)
	* And possibly combination of examples above (e.g. Color by label and shades by confidence)

### Model Format (UMF like ?)

* Python representation of a model and its format components
* IO functionalities, e.g.:
	* Save a model (as collect disparate resources into a coherent model directory w/ metadata)
	* Load a model (as create a Python model representation w/ metadata from a model directory)
	* Verify an existing model directory
	* Copy and/or prune a model
