# Hydrological-modelling

This repository contains the assignment and processed data for the computer practicals of the course [Hydrological Modelling](https://studiekiezer.ugent.be/2026/studiefiche/en/I002659) at Ghent University. The [public repository](https://github.com/h-cel/hydrological-modelling-public) does not contain solutions to the exercise. Solutions can be found in the `solutions` branch of a a [private repository](https://github.com/h-cel/hydrological-modelling), access to which can be granted upon [contacting me](mailto:olivier.bonte@hotmail.com).

*For students, please follow the installation instructions at [https://h-cel.github.io/hydrological-modelling-public/0_practical_info.html](https://h-cel.github.io/hydrological-modelling-public/0_practical_info.html)*

## Installation instructions (local setup)

First, make a local copy of this repository using

```
git clone https://github.com/h-cel/hydrological-modelling.git
```

or download as zip file and unzip. In each case, make sure to navigate inside the `hydrological-modelling` folder before executing any of the command line interface (CLI) instructions below.

Go to the [Quarto download page](https://quarto.org/docs/download/) and download Quarto for your operating system (OS). This repository was built using Quarto 1.9.38.

Next, make sure you have (Mini)Conda installed (download links found [here](https://docs.anaconda.com/miniconda/)) to handle virtual environments in Python. Next open your CLI (or Anaconda prompt) and type:

```
conda env create -f environment.yml
conda activate hydromod_env
```
This ensures that the correct version of Python is used in your CLI.

Next, it is recommended that following Quarto tools are installed:

- In this repository, a final output is rendered to pdf. Therefore, [a LaTeX distribution is needed](https://quarto.org/docs/output-formats/pdf-basics.html#prerequisites). Install the [TinyTex distribution](https://yihui.org/tinytex/), a lightweight version of [TeX Live](https://www.tug.org/texlive/), with following command in the CLI: `quarto install tinytex`. This should be more straightforward than managing your own [Tex distribution](https://www.latex-project.org/get/#tex-distributions).


To check if these installations were successful, run
```
quarto check
```
in the CLI. You should see 
```
[✓] Checking LaTeX....................OK
```

