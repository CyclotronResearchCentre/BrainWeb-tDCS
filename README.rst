=============
BrainWeb tDCS
=============

This repository contains the final stage of our data analyses.
While it does not provide full access to the previous stages (mostly due to the fact that the whole workflow generated several dozens of TB of data), it contains all the records required to run the notebooks.

Repository map
--------------

- The `code/` directory contains both a local `brainweb_tdcs` python package and the files required to run the Nextflow pipeline.
- The `envs/` directory contains the Conda environment configuration used to run the notebooks.
- The `notebooks/` directory contains the Jupyter notebooks used to produce the final results.

How to
------

Here are the general steps to run the notebooks. You can runn them manually one-by-one or use an automation tool such as Papermill.

1. Clone this repository.
2. `cd` into the project directory.
3. Build the Conda environment using `conda env create -f envs/env.yaml`.
4. Activate the Conda environment using `conda activate brainweb-tdcs-analysis`.
5. Run Jupyter lab using `python -m jupyter lab`.
6. Choose a notebook in the `notebooks/` directory.
7. Set the value of `experiment_id` to a value between 0 and 5 (see below the corresponding experiments) and `use_gpr` to `True` if you want to compute the results for the truncated normal distributions or to `False` if you want to use the uniform distributions.
8. Run the notebook.

The experiment IDs from 0 to 5 correspond to :

0. C3-C4 (MC)
1. C3-Fp2 (MC)
2. F3-F4 (dlPFC)
3. F3-Fp2 (dlPFC)
4. F7-F8 (vmPFC)
5. P3-P4 (IPS)

License
-------

Copyright (C) 2022 [GIGA CRC In-Vivo Imaging](https://www.gigacrc.uliege.be/), Liège, Belgium

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

For more information, refer to [the full license](LICENSE.md).
