.. _method_total_variation_ROF:

Total Variation denoising (ROF)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Description**

`Total variation (TV) denoising <https://en.wikipedia.org/wiki/Total_variation_denoising>`_ using Rudin-Osher-Fatemi (ROF) model :cite:`rudin1992nonlinear` is a seminal work that proposed edge-preserving image smoothing in 1992.
As opposed to the Gaussian smoothing, where the edges of features are not preserved, this has revolutionised the field of image recovery. The TV
denoising has become a widely-accepted way to denoise images/volumes, while preserving important features in them.
The resulting denoised images are piecewise-constant or cartoon-like.

.. list-table::


    * - .. figure:: ../../_static/figures/FBP.png

           The noisy image

      - .. figure:: ../../_static/figures/ROF.png

           Recovery using ROF-TV denoising

      - .. figure:: ../../_static/figures/ROF_zoom.png

           Zoomed to ROF-TV denoised image

Mathematically speaking, the optimisation problem involving TV-norm needs to be solved, where TV norm is defined as:

.. math::

     \mathbf{x} \in \mathrm{R}^{m \times n}: \textit{input}

     \mathbf{u} \in \mathrm{R}^{m \times n}: \textit{output}

     g(\mathbf{x}) = \lambda\|\nabla \mathbf{x} \|_{\epsilon} : \textit{TV-functional}

The authors used partial differential equations explicit model to minimise the functional above with the help of a small constant (:math:`\epsilon = 1\mathrm{e}{-12}`) to avoid singularity in the derivative.
Because of that constant, the recovery using ROF-TV does not result in pure piecewise-constant solution. However, depending on the data, this might be even the desirable feature. More information
about different denoising models, including TV-models can be found in this paper :cite:`kazantsev2019ccpi`.

**Where and how to use it:**

Use it when the noise in the reconstructed image/volume needs to be removed. The TV-denoising should work better than :ref:`method_median_filter` and introduce less undesirable smoothing and features distortion/disappearance. Also the contrast improvement is expected.

.. note:: Applying denoising after the reconstruction is different to employ that kind of smoothing as a regularisation within an iterative method. Use the latter when the projection data is undersampled and of poor quality (many artefacts, distortions, etc.). In that case, just denoising, might be not very effective.

**What are the adjustable parameters:**

* :code:`regularisation_parameter` Is the most important parameter as it controls the level of smoothing of the image. Larger values lead to more smoothing, which can lead to undesirable oversmoothing.

* :code:`iterations` Algorithm iterations. You will need a significant number of iteration to run in order to see the change in the image. It is recommended to keep this number between 1000 and 5000 iterations.

* :code:`time_marching_parameter` This parameter ensures the stability of iterations and needs to be small. If you notice unusual artefacts in the denoised image, reduce the value of the parameter. We suggest to keep it 0.001 or smaller.

