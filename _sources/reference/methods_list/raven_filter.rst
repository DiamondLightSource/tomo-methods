.. _method_raven_filter:

Raven filter
^^^^^^^^^^^^^

**Description**

Raven filter is a part of the module :doc:`../../api/httomolibgpu.prep.stripe` for data correction. Raven filter is based on a FFT filter applied in sinogram space to minimise stripes leading to `Ring Artifacts <https://radiopaedia.org/articles/ring-artifact-2?lang=gb>`_ in reconstruction. See more about the filter in the original publication :cite:`raven1998numerical`.

**Where and how to use it:**

Raven filter can be used in pre-processing, i.e., before the reconstruction to remove the stripes present in the data.

**What are the adjustable parameters:**

Most important parameters are :code:`uvalue` and :code:`nvalue` that define the shape of the filter, as well as, :code:`vvalue`, the number of rows to be applied to the filter.

**Practical example:**

In this example we demonstrate how to apply Raven filter to the normalised projection data.

.. warning:: As with any pre-processing tool, one needs to be careful in applying Raven filter to data. Sub-optimal parameters can potentially lead to other artifacts introduced in the reconstruction and blurring.
.. list-table::


    * - .. figure:: ../../_static/auto_images_methods/data_stripes_added_sino.png

           Input (sinogram view) with the stripes added

      - .. figure:: ../../_static/auto_images_methods/data_stripes_added_proj.png

           Input (projection view) with the stripes added

    * - .. figure:: ../../_static/auto_images_methods/raven_filter_sino.png

           After applying Raven filter (sinogram)

      - .. figure:: ../../_static/auto_images_methods/raven_filter_proj.png

           After applying Raven filter (projection)

    * - .. figure:: ../../_static/auto_images_methods/raven_filter_res_sino.png

           Sinogram view of absolute residual between input and output

      - .. figure:: ../../_static/auto_images_methods/raven_filter_res_proj.png

           Projection view of absolute residual between input and output




