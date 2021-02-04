.. Image substitutions:
   ====================

.. |Plums| image:: /_static/plums.png
    :alt: Plums-Microlib
    :scale: 80%
    :align: bottom

.. |PlumsTiny| image:: /_static/plums.png
    :alt: Plums-Microlib
    :scale: 30%
    :align: bottom

.. |PlumsDark| image:: /_static/plums_dark.png
    :alt: Plums-Microlib
    :scale: 80%
    :align: bottom

.. |PlumsDarkTiny| image:: /_static/plums_dark.png
    :alt: Plums-Microlib
    :scale: 30%
    :align: bottom

.. |PlumsLogo| image:: /_static/plums_notext.png
    :alt: Plums-Microlib
    :scale: 80%
    :align: bottom

.. |PlumsLogoTiny| image:: /_static/plums_notext.png
    :alt: Plums-Microlib
    :scale: 30%
    :align: bottom

.. |PlumsLogoDark| image:: /_static/plums_notext_dark.png
    :alt: Plums-Microlib
    :scale: 80%
    :align: bottom

.. |PlumsLogoDarkTiny| image:: /_static/plums_notext_dark.png
    :alt: Plums-Microlib
    :scale: 30%
    :align: bottom

.. Classes substitutions for commons:
   ==================================

.. |Path| replace:: :class:`~plums.commons.Path`

.. |TileCollection| replace:: :class:`~plums.commons.TileCollection`
.. |Tile| replace:: :class:`~plums.commons.Tile`
.. |TileWrapper| replace:: :class:`~plums.commons.TileWrapper`

.. |DataPoint| replace:: :class:`~plums.commons.DataPoint`
.. |Annotation| replace:: :class:`~plums.commons.Annotation`

.. |RasterMask| replace:: :class:`~plums.commons.RasterMask`
.. |VectorMask| replace:: :class:`~plums.commons.VectorMask`
.. |MaskCollection| replace:: :class:`~plums.commons.MaskCollection`
.. |Mask| replace:: :class:`~plums.commons.Mask`

.. |RecordCollection| replace:: :class:`~plums.commons.RecordCollection`
.. |Record| replace:: :class:`~plums.commons.Record`

.. |GeoInterfaced| replace:: :class:`~plums.commons.data.GeoInterfaced`
.. |ArrayInterfaced| replace:: :class:`~plums.commons.data.ArrayInterfaced`
.. |PropertyContainer| replace:: :class:`~plums.commons.PropertyContainer`
.. |_Array| replace:: :class:`~plums.commons.data.base._Array`

.. |Taxonomy| replace:: :class:`~plums.commons.Taxonomy`
.. |Tree| replace:: :class:`~plums.commons.Tree`
.. |Label| replace:: :class:`~plums.commons.Label`

.. |TreeAccessorBase| replace:: :class:`~plums.commons.data.taxonomy.accessor.TreeAccessorBase`
.. |NameTreeAccessor| replace:: :class:`~plums.commons.data.taxonomy.accessor.NameTreeAccessor`
.. |IdTreeAccessor| replace:: :class:`~plums.commons.data.taxonomy.accessor.IdTreeAccessor`
.. |DefaultTreeAccessor| replace:: :class:`~plums.commons.data.taxonomy.accessor.DefaultTreeAccessor`

.. |TreeIteratorBase| replace:: :class:`~plums.commons.data.taxonomy.iterator.TreeIteratorBase`
.. |TopDownTreeIterator| replace:: :class:`~plums.commons.data.taxonomy.iterator.TopDownTreeIterator`
.. |BottomUpTreeIterator| replace:: :class:`~plums.commons.data.taxonomy.iterator.BottomUpTreeIterator`
.. |FloorTreeIterator| replace:: :class:`~plums.commons.data.taxonomy.iterator.FloorTreeIterator`
.. |TopDownDepthWiseTreeIterator| replace:: :class:`~plums.commons.data.taxonomy.iterator.TopDownDepthWiseTreeIterator`
.. |BottomUpDepthWiseTreeIterator| replace:: :class:`~plums.commons.data.taxonomy.iterator.BottomUpDepthWiseTreeIterator`
.. |DefaultTreeIterator| replace:: :class:`~plums.commons.data.taxonomy.iterator.DefaultTreeIterator`

.. Classes substitutions for dataflow:
   ==================================

.. |TileIO| replace:: :class:`~plums.dataflow.io.Tile`
.. |ptype| replace:: :class:`~plums.dataflow.io.ptype`
.. |dump| replace:: :class:`~plums.dataflow.io.json.dump`
.. |load| replace:: :class:`~plums.dataflow.io.json.load`

.. |Channel| replace:: :class:`~plums.dataflow.io.tile._format.channel.Channel`
.. |RGB| replace:: :class:`~plums.dataflow.io.RGB`
.. |RGBA| replace:: :class:`~plums.dataflow.io.RGBA`
.. |BGR| replace:: :class:`~plums.dataflow.io.BGR`
.. |BGRA| replace:: :class:`~plums.dataflow.io.BGRA`
.. |GREY| replace:: :class:`~plums.dataflow.io.GREY`

.. |Dataset| replace:: :class:`~plums.dataflow.dataset.Dataset`
.. |SizedDataset| replace:: :class:`~plums.dataflow.dataset.SizedDataset`
.. |Subset| replace:: :class:`~plums.dataflow.dataset.Subset`
.. |ConcatDataset| replace:: :class:`~plums.dataflow.dataset.ConcatDataset`
.. |PatternDataset| replace:: :class:`~plums.dataflow.dataset.PatternDataset`
.. |PlaygroundDataset| replace:: :class:`~plums.dataflow.dataset.PlaygroundDataset`
.. |TileDriver| replace:: :class:`~plums.dataflow.dataset.playground.TileDriver`
.. |AnnotationDriver| replace:: :class:`~plums.dataflow.dataset.playground.AnnotationDriver`
.. |TaxonomyReader| replace:: :class:`~plums.dataflow.dataset.playground.TaxonomyReader`

.. Classes substitutions for model:
   ===============================

.. |validate| replace:: :func:`~plums.model.validation.validate`

.. |md5_checksum| replace:: :func:`~plums.model.validation.utils.checksum.md5_checksum`
.. |make_dict_structure_from_tree| replace:: :func:`~plums.model.validation.utils.dict_from_tree.make_dict_structure_from_tree`
.. |is_pathname_valid| replace:: :func:`~plums.model.validation.utils.validate_path.is_pathname_valid`

.. |SchemaComponent| replace:: :class:`~plums.model.validation.schema_core.SchemaComponent`
.. |Default| replace:: :class:`~plums.model.validation.schema_core.Default`
.. |PathSchema| replace:: :class:`~plums.model.validation.schema_core.Path`
.. |MD5Checksum| replace:: :class:`~plums.model.validation.schema_core.MD5Checksum`

.. |MetadataComponent| replace:: :class:`~plums.model.validation.metadata.MetadataComponent`
.. |DefaultMetadata| replace:: :class:`~plums.model.validation.metadata.DefaultMetadata`
.. |ProducerVersionSchema| replace:: :class:`~plums.model.validation.metadata.ProducerVersion`
.. |ProducerSchema| replace:: :class:`~plums.model.validation.metadata.Producer`
.. |FormatSchema| replace:: :class:`~plums.model.validation.metadata.Format`
.. |CheckpointSchema| replace:: :class:`~plums.model.validation.metadata.Checkpoint`
.. |TrainingSchema| replace:: :class:`~plums.model.validation.metadata.Training`
.. |ConfigurationSchema| replace:: :class:`~plums.model.validation.metadata.Configuration`
.. |InitialisationPathSchema| replace:: :class:`~plums.model.validation.metadata.InitialisationPath`
.. |InitialisationPMFSchema| replace:: :class:`~plums.model.validation.metadata.InitialisationPMF`
.. |InitialisationSchema| replace:: :class:`~plums.model.validation.metadata.Initialisation`
.. |ModelSchema| replace:: :class:`~plums.model.validation.metadata.Model`
.. |MetadataSchema| replace:: :class:`~plums.model.validation.metadata.Metadata`

.. |TreeComponent| replace:: :class:`~plums.model.validation.structure.TreeComponent`
.. |DefaultTree| replace:: :class:`~plums.model.validation.structure.DefaultTree`
.. |MetadataTree| replace:: :class:`~plums.model.validation.structure.Metadata`

.. |DataTree| replace:: :class:`~plums.model.validation.structure.Data`
.. |CheckpointTree| replace:: :class:`~plums.model.validation.structure.Checkpoint`
.. |InitialisationTree| replace:: :class:`~plums.model.validation.structure.Initialisation`
.. |InitialisationPMFTree| replace:: :class:`~plums.model.validation.structure.InitialisationPMF`
.. |InitialisationPathTree| replace:: :class:`~plums.model.validation.structure.InitialisationPath`
.. |ModelTree| replace:: :class:`~plums.model.validation.structure.Model`
.. |PathTree| replace:: :class:`~plums.model.validation.structure.Path`

.. |Model| replace:: :class:`~plums.model.model.Model`

.. |initialisation| replace:: :class:`~plums.model.model.initialisation`
.. |Training| replace:: :class:`~plums.model.components.components.Training`
.. |Producer| replace:: :class:`~plums.model.components.components.Producer`
.. |CheckpointCollection| replace:: :class:`~plums.model.components.components.CheckpointCollection`
.. |TrainingStatus| replace:: :class:`~plums.model.components.utils.TrainingStatus`
.. |Checkpoint| replace:: :class:`~plums.model.components.utils.Checkpoint`
.. |ProducerVersion| replace:: :class:`~plums.model.components.version.Version`
.. |PyPaVersion| replace:: :class:`~plums.model.components.version.PyPA`

.. |version| replace:: :class:`~plums.model.components.version.version`
.. |register| replace:: :class:`~plums.model.components.version.register`
.. |is_duplicate| replace:: :class:`~plums.model.components.utils.is_duplicate`
.. |copy| replace:: :class:`~plums.model.components.utils.copy`
.. |rmtree| replace:: :class:`~plums.model.components.utils.rmtree`

.. Classes substitutions for plot:
   ==============================

.. |Draw| replace:: :class:`~plums.plot.engine.painter.Draw`
.. |TagPainter| replace:: :class:`~plums.plot.engine.painter.TagPainter`
.. |Geometry| replace:: :class:`~plums.plot.engine.painter.Geometry`
.. |Painter| replace:: :class:`~plums.plot.engine.Painter`
.. |PainterBase| replace:: :class:`~plums.plot.engine.painter.PainterBase`
.. |Position| replace:: :class:`~plums.plot.engine.painter.Position`

.. |LegendPainter| replace:: :class:`~plums.plot.engine.legend_painter.LegendPainter`

.. |Compositor| replace:: :class:`~plums.plot.engine.Compositor`

.. |SimpleImagePositionGenerator| replace:: :class:`~plums.plot.engine.position_generator.SimpleImagePositionGenerator`
.. |LayoutImagePositionGenerator| replace:: :class:`~plums.plot.engine.position_generator.LayoutImagePositionGenerator`
.. |AdaptiveImagePositionGenerator| replace:: :class:`~plums.plot.engine.position_generator.AdaptiveImagePositionGenerator`

.. |Color| replace:: :class:`~plums.plot.engine.Color`
.. |ColorMap| replace:: :class:`~plums.plot.engine.ColorMap`
.. |ContinuousColorMap| replace:: :class:`~plums.plot.engine.ContinuousColorMap`
.. |DiscreteColorMap| replace:: :class:`~plums.plot.engine.DiscreteColorMap`
.. |CategoricalColorMap| replace:: :class:`~plums.plot.engine.CategoricalColorMap`
.. |KeyPointsColorMap| replace:: :class:`~plums.plot.engine.KeyPointsColorMap`
.. |CircularColorMap| replace:: :class:`~plums.plot.engine.CircularColorMap`
.. |SemiCircularColorMap| replace:: :class:`~plums.plot.engine.SemiCircularColorMap`
.. |LightnessColorMap| replace:: :class:`~plums.plot.engine.LightnessColorMap`

.. |Labels| replace:: :class:`~plums.plot.Labels`
.. |Confidence| replace:: :class:`~plums.plot.Confidence`
.. |Area| replace:: :class:`~plums.plot.Area`
.. |Descriptor| replace:: :class:`~plums.plot.engine.Descriptor`
.. |CategoricalDescriptor| replace:: :class:`~plums.plot.CategoricalDescriptor`
.. |ContinuousDescriptor| replace:: :class:`~plums.plot.ContinuousDescriptor`
.. |IntervalDescriptor| replace:: :class:`~plums.plot.IntervalDescriptor`
.. |ColorEngine| replace:: :class:`~plums.plot.engine.color_engine.ColorEngine`
.. |ByCategoryDescriptor| replace:: :class:`~plums.plot.engine.color_engine.ByCategoryDescriptor`
.. |CategoricalRecordCollection| replace:: :class:`~plums.plot.engine.color_engine.CategoricalRecordCollection`

.. |Orchestrator| replace:: :class:`~plums.plot.engine.Orchestrator`

.. |Plot| replace:: :class:`~plums.plot.Plot`
.. |PairPlot| replace:: :class:`~plums.plot.PairPlot`
.. |StandardPlot| replace:: :class:`~plums.plot.StandardPlot`
