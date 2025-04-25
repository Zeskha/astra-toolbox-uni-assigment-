# Astra Toolbox Example Use

This repository contains a set of functions that work with the **Astra Toolbox** Python library. It was developed for the 3rd-year Biomedical Engineering course *Image Techniques*.

The implementation focuses on 3D reconstruction, and the main program is located in `main.py`. This script handles 3D image simulation, result processing, and data storage.

## 🗂 Output Structure

To store the results, the program creates four directories and one JSON file:

- `phantoms_algorithm/` – Stores the original phantom images.
- `reconstructions_algorithm/` – Stores the reconstructed volumes.
- `sinograms_algorithm/` – Stores the generated sinograms.
- `comparisons_algorithm/` – Stores comparison data for each reconstruction.
- `reconstruction_results_algorithm.json` – Stores metadata and evaluation metrics for each run.

## 📁 Repository Overview

- **`main.py`**  
  Main reconstruction script: handles simulation, processing, and storage.

- **`functions.py`**  
  Contains mathematical functions to evaluate reconstruction quality using:
  - Euclidean distance
  - Average absolute distance
  - Maximum distance

- **`data_analysis.py`**  
  Extracts relevant metrics and information such as:
  - Total processing time
  - Best-performing algorithm (based on selected quality metric)

- **`data_visualization.py`**  
  Displays graphs and visual summaries of the reconstruction data.

## 📊 Experiment Results

The following experiments were performed with the following parameters:

- Image sizes: 256, 512 pixels
- Projector sizes: 1×pixels, 2×pixels
- Angles: π, 2π degrees
- Step sizes: 1, 0.5 degree steps
- Iterations: 10, 100, 1000, 2000 iterations
- Algorithms: SIRT and CGLS

You can access the results of these experiments [here](https://drive.google.com/drive/folders/1T54dIqOIKn_wsMlT6aMBKwZO_ZpHdUtK?usp=sharing).

---


