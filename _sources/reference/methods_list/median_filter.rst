.. _method_median_filter:

Median filter
^^^^^^^^^^^^^

**Description**

Median filter is a part of the module :doc:`../../api/httomolibgpu.misc.corr` for data correction. Median filter is a non-linear noise removing technique with 
edge-preserving properties, see more on it `here <https://en.wikipedia.org/wiki/Median_filter>`_.  Mathematically, one can express the median filter as: 

.. math::

   f \in \mathrm{R}^{N}: \textit{input}
   
   g \in \mathrm{R}^{N}: \textit{output}

   g_{i} = \textit{median}(f_{j}), \textrm{where} \ j \in \mathrm{N}_{i}


Where :math:`\mathrm{N}_{i}` is the symmetric neighbourhood (e.g. 3 x 3) of the pixel :math:`j`.


**Where and how to use it:**

Median filter can be used in post-processing, e.g., after the reconstruction to remove the noise and prepare the image for further analysis. Applying edge-preserving noise correction
can simplify segmentation. 

**What are the adjustable parameters:**

* :code:`kernel_size` defines the neighborhood size, see :math:`\mathrm{N}_{i}` in the equations above. For instance, for 2D image :code:`kernel_size = 3` defines the neighborhood of 3 by 3 pixels (one needs to use only odd numbers). Increasing :code:`kernel_size` results in more smoothing applied, it is recommended to use the higher values when the level of noise is high. As a rule of thumb, keeping :code:`kernel_size` within 3-5 range is a good trade-off to avoid destroying important data features. 

**Practical example:**

In this example we demonstrate how to apply median filter to projection data to demonstrate its noise removing properties. 

.. warning:: It is not recommended to apply median filter to projection data as any modification of the data itself can result in further problems, e.g., the loss of the resolution and the presence of artifacts in the reconstruction step.

.. list-table:: 


    * - .. figure:: ../../_static/auto_images_methods/normalisation_sino.png

           Input (sinogram view)

      - .. figure:: ../../_static/auto_images_methods/normalisation_proj.png

           Input (projection view)

    * - .. figure:: ../../_static/auto_images_methods/median_filter_sino.png

           After applying median filter (sinogram)

      - .. figure:: ../../_static/auto_images_methods/median_filter_proj.png

           After applying median filter (projection)

    * - .. figure:: ../../_static/auto_images_methods/median_filter_res_sino.png

           Sinogram view of absolute residual between input and output

      - .. figure:: ../../_static/auto_images_methods/median_filter_res_proj.png

           Projection view of absolute residual between input and output

    

    
