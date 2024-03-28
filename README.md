# Parametric FFF-printable turnbuckle
This project allows you to create FFF-printable (3D-printable) model of a turnbuckle made of body and eye end fittings. You can parametrize many properties, including thread diameter, take-up length, eye diameter and others.

## Quick start
The link "launch binder" will take you to a Jupyter notebook environment prepared for building your turnbuckle model. Once there, follow the instructions on how to start the build process and download the resulting model files.

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/dalibor-frivaldsky/parametric-fff-printable-turnbuckle/main?labpath=build.ipynb)

## Printing instructions
PLA shows [comparably high tensile strength][1] to other FFF materials and is easy to print with. The project was developed on Prusa MK4 using PrusaSlicer, so the recommended settings are based on this fact.

- Material: PLA, Printer: Prusa MK4, Slicer: PrusaSlicer >= 2.6
  - layer height: 0.15mm
  - perimeters: 3
  - infill: 15%
  - infill type: gyroid

## Building locally
If you want to build the project locally on your computer instead of the Binder Jupyter environment, follow these instructions:
- install conda/mamba (e.g. https://github.com/conda-forge/miniforge)
- `mamba env create -f environment.yml --prefix ./envs`
- `mamba activate ./envs`
- `python -m build`

## Development
The project is being developed in VS Code using OCP CAD Viewer plugin - https://github.com/bernhard-42/vscode-ocp-cad-viewer. To setup your dev environment, follow the "Building locally" instructions and in addition do the following:
- `pip install -r requirements-dev.txt`
- `code .`
- install the OCP CAD Viewer plugin
- click the "OCP" icon on the left panel (the location of Explorer, Source Control, ...)
- open the `turnbuckle.py` file, which should also open the OCP viewer window. All libraries (except for "build123d") should show as installed.
- there are Jupyter Notebook comment markings in the code to allow for easy iterative development of the models
- run the very first one to initiate the notebook environment
- run the cell with the implementation of a part function, which should show the model in the OCP viewer window
- modify the code and re-run the part function cell to see the changes

## Acknowledgements
- the code in `core/metric_threads.py`, created by [Nerius](https://sourceforge.net/u/nerius/profile/), was taken from https://sourceforge.net/p/nl10/code/HEAD/tree/cq-code/common/metric_threads.py

## References
- [1]: [CNC Kitchen: The BEST 3D printing material? Comparing PLA, PETG & ASA (ABS)](https://www.youtube.com/watch?v=ycGDR752fT0)