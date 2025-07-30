# quarto_template_ugent

A starting point for making courses with Quarto at Ghent University with a focus on using Python code. 

## Installation instructions (local setup)

First, make a local copy of this repository using

```
git clone https://github.com/olivierbonte/quarto_template_ugent.git
```

or download as zip file and unzip. In each case, make sure to navigate inside the `quarto_template_ugent` folder before executing any of the command line interface (CLI) instructions below.

Go to the [Quarto download page](https://quarto.org/docs/download/) and download Quarto for your operating system (OS). This repository was built using Quarto 1.7.32.

Next, make sure you have (Mini)Conda installed (download links found [here](https://docs.anaconda.com/miniconda/)) to handle virtual environments in Python. Next open your CLI (or Anaconda prompt) and type:

```
conda env create -f environment.yml
conda activate quarto_template
```
This ensures that the correct version of Python is used in your CLI.

Next, it is recommended that following Quarto tools are installed:

- In this repository, a final output is rendered to pdf. Therefore, [a LaTeX distribution is needed](https://quarto.org/docs/output-formats/pdf-basics.html#prerequisites). Install the [TinyTex distribution](https://yihui.org/tinytex/), a lightweight version of [TeX Live](https://www.tug.org/texlive/), with following command in the CLI: `quarto install tinytex`. This should be more straightforward than managing your own [Tex distribution](https://www.latex-project.org/get/#tex-distributions).
- To render the diagrams, made with [Mermaid](https://mermaid.js.org/intro/), [quarto needs the Chrome or Edge browser](https://quarto.org/docs/authoring/diagrams.html#chrome-install). As of 30/07/2025, it is recommended to install one of the two yourself on your local machine (if not already present). The use of `quarto install chromium` is as of now failing to my knowledge (see e.g. [here](https://github.com/quarto-dev/quarto-cli/issues/11581#issuecomment-2512194569)), this should be fixed once the stable 1.8 release of Quarto is out (progress can be followed [here](https://github.com/quarto-dev/quarto-cli/issues/11877)). 

## Hosting as a website with Github Actions and Quarto Pub

### Activating Quarto Pub

For this template, the website is hosted using [Quarto Pub](https://quartopub.com/). 

For your own use, start by deleting the `_publish.yml` file. In this way, you can create a new url for your website related to your own Quarto Pub account 
```
quarto publish quarto-pub
```
This wil automatically open a browser window for the needed actions. For more general info, see the [Quarto documentation](https://quarto.org/docs/publishing/quarto-pub.html).

### Automating the publishing with Github Actions

Although you could publish every change manually with the command above, it is more convenient to automate this process with Github Actions. This is also eliminates the need to have rendered versions of your Quarto Book checked in to version control. 

The workflow to automate the publishing (including rendering) of this book is defined in [`.github/workflows/publish.yml`](.github/workflows/publish.yml). Also the installation of the needed dependencies (similar to what is described [above](#installation-instructions-local-setup)) is included here. Following modifications to the template, results in changes in [`publish.yml`](.github/workflows/publish.yml):

- Changing name of conda environment: changing `name` in [environment.yml](environment.yml) from `quarto_template` to (e.g.) `new_env_name`, requires you to change  `activate-environment: quarto_template` to `activate-environment: new_env_name` in the step with the name `Setup Python with Miniconda`. 
- Changing title of the book: changing `title: "quarto_template_ugent"` in [_quarto.yml](_quarto.yml) to (e.g.) `title: "new_title"` requires you to change `name: quarto_template_ugent` to `name: new_title` in the step with the name ` Save PDF as artifact`. 



