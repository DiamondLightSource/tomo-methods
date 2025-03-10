.. _method_remove_stripe_ti:

Remove stripes Titarenko
^^^^^^^^^^^^^^^^^^^^^^^^

**Description**

This stripe removal algorithm is developed by Dr. Sofya Titarenko and is a part of the module :doc:`../../api/httomolibgpu.prep.stripe` for data correction.
This filter works in the sinogram space to minimise stripes leading to `Ring Artifacts <https://radiopaedia.org/articles/ring-artifact-2?lang=gb>`_ in the reconstruction. See more about the filter in the original publication :cite:`titarenko2010analytical`.
The algorithm uses a priori information about the sinogram, such as its smoothness and symmetry.

**Where and how to use it:**

Stripe removal method is used for data pre-processing, i.e., before the reconstruction to remove the stripes present in the data. If the stripes are not removed,
this will lead to ring artefacts in the reconstruction and further problems with quantification and segmentation.

**What are the adjustable parameters:**

The important parameter here is :code:`beta` which is responsible for strength of the filter. Note that lower values increase the filter strength.

**Practical example:**

In this example we demonstrate how to apply Titarenko's stripe removal algorithm to the normalised projection data.

.. warning:: As with any pre-processing tool, one needs to be careful in applying stripe removal algorithm to data. Sub-optimal parameters can potentially lead to other artifacts introduced in the reconstruction.
.. list-table::


    * - .. figure:: ../../_static/auto_images_methods/data_stripes_added_sino.png

           Input (sinogram view) with the stripes added

      - .. figure:: ../../_static/auto_images_methods/data_stripes_added_proj.png

           Input (projection view) with the stripes added

    * - .. figure:: ../../_static/auto_images_methods/remove_stripe_ti_sino.png

           After applying remove stripes by Titarenko's stripe removal (sinogram)

      - .. figure:: ../../_static/auto_images_methods/remove_stripe_ti_proj.png

           After applying remove stripes by Titarenko's stripe removal (projection)

    * - .. figure:: ../../_static/auto_images_methods/remove_stripe_ti_res_sino.png

           Sinogram view of absolute residual between input and output

      - .. figure:: ../../_static/auto_images_methods/remove_stripe_ti_res_proj.png

           Projection view of absolute residual between input and output




