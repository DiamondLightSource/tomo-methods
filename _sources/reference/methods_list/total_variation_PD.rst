.. _method_total_variation_PD:

Total Variation denoising (PD)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Description**

`Total variation (TV) denoising <https://en.wikipedia.org/wiki/Total_variation_denoising>`_ using Primal-Dual optimisation strategy :cite:`chan1999nonlinear` is more advanced
method compared to :ref:`method_total_variation_ROF` which uses smoothed version of the TV-norm :cite:`rudin1992nonlinear`.

From the user perspective this model usually leads to true piecewise-constant images with a better contrast.

.. list-table::


    * - .. figure:: ../../_static/figures/FBP.png

           The noisy image

      - .. figure:: ../../_static/figures/SB.png

           Recovery using PD-TV denoising

      - .. figure:: ../../_static/figures/SB_zoom.png

           Zoomed to PD-TV denoised image

Mathematically speaking, the optimisation problem involving the exact TV-norm needs to be solved, where TV norm is defined as:

.. math::

     \mathbf{x} \in \mathrm{R}^{m \times n}: \textit{input}

     \mathbf{u} \in \mathrm{R}^{m \times n}: \textit{output}

     g(\mathbf{x}) = \lambda\| \nabla \mathbf{x} \| : \textit{TV-functional}

The authors used a trick to avoid singularity in the TV-norm derivative by *introducing an additional variable for the
flux quantity appearing in the gradient of the objective function, which can be interpreted as the normal vector to the level sets of the image* :math:`x`.

More information about different denoising models, including TV-models can be found in this paper :cite:`kazantsev2019ccpi`.

**Where and how to use it:**

Use it when the noise in the reconstructed image/volume needs to be removed. The TV-denoising should work better than :ref:`method_median_filter` and introduce less undesirable smoothing and features distortion/disappearance. Also the contrast improvement is expected.

.. note:: Applying denoising after the reconstruction is different to employ that kind of smoothing as a regularisation within an iterative method. Use the latter when the projection data is undersampled and of poor quality (many artefacts, distortions, etc.). In that case, just denoising, might be not very effective.

**What are the adjustable parameters:**

* :code:`regularisation_parameter` Is the most important parameter as it controls the level of smoothing of the image. Larger values lead to more smoothing, which can lead to undesirable oversmoothing.

* :code:`iterations` Algorithm iterations. You will also need a significant number of iteration for this optimisation scheme. It is recommended to keep the number of iterations between 500 and 2000 iterations.

* :code:`isotropic` Choose between the preference of the smoothing dimension of the TV norm, isotropic (True) or anisotropic (False). Defaults to isotropic.

* :code:`nonnegativity` Enables non-negativity in iterations which can lead to better contrast. Disabled by default.

* :code:`lipschitz_const` This parameter controls the stability of convergence. Defaults to 8, which should satisfy the condition.