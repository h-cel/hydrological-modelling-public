# quarto_template_ugent

A starting point for making courses with Quarto at Ghent University with a focus on using Python code. 

## Installation instructions (local setup)

First, make a local copy of this repository using

```
git clone https://github.com/olivierbonte/quarto_template_ugent.git
```

or download as zip file and unzip. In each case, make sure to navigate inside the `quarto_template_ugent` folder before executing any of the command line interface (CLI) instructions below.

Go to the [Quarto download page](https://quarto.org/docs/download/) and download Quarto for your operating system (OS). This repository was built using Quarto 1.9.38.

Next, make sure you have (Mini)Conda installed (download links found [here](https://docs.anaconda.com/miniconda/)) to handle virtual environments in Python. Next open your CLI (or Anaconda prompt) and type:

```
conda env create -f environment.yml
conda activate quarto_template
```
This ensures that the correct version of Python is used in your CLI.

Next, it is recommended that following Quarto tools are installed:

- In this repository, a final output is rendered to pdf. Therefore, [a LaTeX distribution is needed](https://quarto.org/docs/output-formats/pdf-basics.html#prerequisites). Install the [TinyTex distribution](https://yihui.org/tinytex/), a lightweight version of [TeX Live](https://www.tug.org/texlive/), with following command in the CLI: `quarto install tinytex`. This should be more straightforward than managing your own [Tex distribution](https://www.latex-project.org/get/#tex-distributions).
- To render the diagrams, made with [Mermaid](https://mermaid.js.org/intro/), [quarto needs the Chrome or Edge browser](https://quarto.org/docs/authoring/diagrams.html#chrome-install). If you don't have Chrome or Edge in your local device and prefer to keep it that way, you can install a [Chrome Headless Shell](https://developer.chrome.com/blog/chrome-headless-shell) via quarto in the CLI with `quarto install chrome-headless-shell`

To check if these installations were successful, run
```
quarto check
```
in the CLI. You should see 
```
[✓] Checking LaTeX....................OK
```
for LaTex and
```
[✓] Checking Chrome Headless....................OK
```
for Chrome. 

## Hosting as a website with Github Actions and GitHub Pages

For this purpose, your clone or fork of this repository should be on GitHub. 

### Activating Github Pages

For this template, the website is hosted using [GitHub Pages](https://quarto.org/docs/publishing/github-pages.html). 

For your own use, start by running
```
quarto publish gh-pages
```
This wil automate the process of setting up a `gh-pages` branch from which the website is hosted. 

### Automating the publishing with Github Actions

Although you could publish every change manually with the command above, it is more convenient to automate this process with [Github Actions](https://github.com/features/actions). This is also eliminates the need to have rendered versions of your Quarto Book checked in to version control. 

The workflow to automate the publishing (including rendering) of this book is defined in [`.github/workflows/publish.yml`](.github/workflows/publish.yml). Also the installation of the needed dependencies (similar to what is described [above](#installation-instructions-local-setup)) is included here. For your own repository, you might need to change the *Read and write permissions* of your repo for this work, for more info please see the [corresponding Quarto documentation](https://quarto.org/docs/publishing/github-pages.html#publish-action). 



