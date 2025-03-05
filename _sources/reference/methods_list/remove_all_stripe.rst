.. _method_remove_all_stripe:

Remove stripes combo
^^^^^^^^^^^^^^^^^^^^

**Description**

This stripe removal algorithm is developed by Dr. Nghia Vo and is a part of the module :doc:`../../api/httomolibgpu.prep.stripe` for data correction.
This filter works in the sinogram space to minimise stripes leading to `Ring Artifacts <https://radiopaedia.org/articles/ring-artifact-2?lang=gb>`_ in the reconstruction. See more about the filter in the original publication :cite:`vo2018superior`.
Also more information about the method can be found on the author's software `Sarepy <https://sarepy.readthedocs.io/>`_.

Remove stripes combination uses four algorithms applied sequentially to the data in order to remove different types of stripe artefacts as presented in the paper :cite:`vo2018superior`.

**Where and how to use it:**

Remove stripes combination should be applied when different types of stripe artefacts present in the data (e.g. small or large or partial stripes). It is useful to have a look at this
`classification <https://sarepy.readthedocs.io/toc/section2.html>`_ of different ring/stripe artefacts beforehand. The method can be used blindly, however,
applying multiple pre-processing algorithms can distort the data, resulting in artefacts in the reconstruction. Meaning that if there are not to many stripes in the data and the method is still applied,
could result in suboptimal reconstructions.

**What are the adjustable parameters:**

As this method based on multiple algorithms, including :ref:`method_remove_stripe_based_sorting`, it has a number of free parameters.
The :code:`snr` parameter is used to detect and remove large stripes. The associated to that method parameter :code:`la_size` is used to remove
large stripes, also by means of sorting. Parameter :code:`sm_size` defines the size of the median filter when sorting is performed to remove
thinner stripes.

**Practical example:**

In this example we demonstrate how to apply remove stripes combo algorithm to the normalised projection data.

.. warning:: As with any pre-processing tool, one needs to be careful in applying stripe removal algorithm to data. Sub-optimal parameters can potentially lead to other artifacts introduced in the reconstruction.
.. list-table::


    * - .. figure:: ../../_static/auto_images_methods/data_stripes_added_sino.png

           Input (sinogram view) with the stripes added

      - .. figure:: ../../_static/auto_images_methods/data_stripes_added_proj.png

           Input (projection view) with the stripes added

    * - .. figure:: ../../_static/auto_images_methods/remove_all_stripe_sino.png

           After applying remove stripes combo (sinogram)

      - .. figure:: ../../_static/auto_images_methods/remove_all_stripe_proj.png

           After applying remove stripes combo (projection)

    * - .. figure:: ../../_static/auto_images_methods/remove_all_stripe_res_sino.png

           Sinogram view of absolute residual between input and output

      - .. figure:: ../../_static/auto_images_methods/remove_all_stripe_res_proj.png

           Projection view of absolute residual between input and output




