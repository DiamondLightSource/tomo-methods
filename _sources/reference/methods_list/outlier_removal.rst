.. _method_outlier_removal:

Outliers removal filter
^^^^^^^^^^^^^^^^^^^^^^^

**Description**

Also called as a **dezinger**. Outliers removal filter is a part of the module :doc:`../../api/httomolibgpu.misc.corr` for data correction. 
This method seeks the pixels/voxels that do not fit normally distributed data and replace them by using the :ref:`method_median_filter`. Essentially, dezinger is 
a spatially variant median filter. The user needs to set the threshold parameter, based on which the filter will remove the outliers that are **above** 
the chosen threshold. See the :code:`dif` parameter of the :code:`remove_outlier` method. 
Mathematically, one can express the dezinger as: 

.. math::

   f \in \mathrm{R}^{N}: \textit{input}
   
   g \in \mathrm{R}^{N}: \textit{output}

   \hat{f}_{i} = \textit{median}(f_{j}), \textrm{where} \ j \in \mathrm{N}_{i}

   g_{i} = \hat{f}_{i} \  \textrm{if} \ | f_{i} - \hat{f}_{i} | \geq \sigma.

Where :math:`\sigma` is the threshold parameter and :math:`\mathrm{N}_{i}` is the symmetric neighbourhood (e.g. 3 x 3) of the pixel :math:`j`.

.. note:: Increasing the threshold value leads to the filter being more selective and decreasing the value makes it more like the normal median filter. 
  
**Where and how to use it:**

Outliers removal filter should be used in situations when the data (projections or sinograms) contains pixels/voxels that do not belong to the surrounding area. 
Usually, it looks like a `salt-and-pepper <https://en.wikipedia.org/wiki/Salt-and-pepper_noise>`_ noise or speckle-type noise, see Practical example bellow. In tomography, such
noise can be present because of the scattered X-rays and the quicker way to establish the need for the filter is to investigate the raw data visually. When removing
the outliers, it is preferable to avoid any modification of the data, therefore some experimentation with the :math:`\sigma` parameter might needed. 

**What are the adjustable parameters:**

* :code:`kernel_size` defines the neighborhood size, see :math:`\mathrm{N}_{i}` in the equations above. For instance, for 2D image :code:`kernel_size = 3` defines the neighborhood of 3 by 3 pixels (one needs to use only odd numbers). Increasing :code:`kernel_size` results in more smoothing applied, it is recommended to use the higher values when the clusters of pixels are large. As a rule of thumb, keeping :code:`kernel_size` within 7-11 range is a good trade-off. The limit is set to 13 currently.

* :code:`dif` defines the threshold above which the value in the pixel is considered to be too high/low. Some empirical testing is usually required to establish the best trade-off. 


**Practical example:**

In this example we demonstrate how the outliers, visible in sinogram and projection spaces can be removed from the data.

.. list-table:: 


    * - .. figure:: ../../_static/auto_images_methods/remove_outlier_input_sino.png

           Input (sinogram view) with a stripe of outliers in the middle of the image. 

      - .. figure:: ../../_static/auto_images_methods/remove_outlier_input_proj.png

           Input (projection view) with some outliers in the left part of the image.

    * - .. figure:: ../../_static/auto_images_methods/remove_outlier_sino.png

           After applying outliers removal (sinogram)

      - .. figure:: ../../_static/auto_images_methods/remove_outlier_proj.png

           After applying outliers removal (projection)

    * - .. figure:: ../../_static/auto_images_methods/remove_outlier_res_sino.png

           Sinogram view of absolute residual between input and output. Note that the residual contains only removed outliers, we want to avoid smoothing the data.

      - .. figure:: ../../_static/auto_images_methods/remove_outlier_res_proj.png

           Projection view of absolute residual between input and output. Note that the residual contains only removed outliers, we want to avoid smoothing the data.
