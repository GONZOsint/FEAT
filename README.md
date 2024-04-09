<p align="center">
  <img src="https://github.com/GONZOsint/FEAT/blob/main/assets/FEAT2.png?raw=true" alt="FEAT" width="300"/>
</p>

FEAT, short for Factcheck Explorer Analysis Tool, is engineered to facilitate in-depth exploration, analysis, and visualization of fact-checking data. By leveraging the [FactCheckExplorer Python library](https://github.com/GONZOsint/factcheckexplorer), FEAT extends users' capabilities to access a broader dataset, enabling thorough investigations into misinformation. This tool can help researchers, journalists, and anyone dedicated to scrutinizing misinformation narratives.

---


## Dashboard Visuals

Explore the diverse functionalities of FEAT through these dashboard snapshots, showcasing the tool's capability to deliver rich insights and analyses.

|                                      ![Dashboard Sample 1](https://github.com/GONZOsint/FEAT/blob/main/assets/FEAT_sample1.png?raw=true)                                      |
|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|                                                                       **Fig 1. Search**                                                                          |

| ![Dashboard Sample 2](https://github.com/GONZOsint/FEAT/blob/main/assets/FEAT_sample2.png?raw=true) | ![Dashboard Sample 3](https://github.com/GONZOsint/FEAT/blob/main/assets/FEAT_sample3.png?raw=true) |
|:---------------------------------------------------------------------------------------------------:|:---------------------------------------------------------------------------------------------------:|
|                              **Fig 1. Verdict Distribution and Tags Volume**                                       |                               **Fig 2. Claims Timeline and  Source Volume**                                                |

| ![Dashboard Sample 3](https://github.com/GONZOsint/FEAT/blob/main/assets/FEAT_sample4.png?raw=true) | ![Dashboard Sample 4](https://github.com/GONZOsint/FEAT/blob/main/assets/FEAT_sample5.png?raw=true) |
|:---------------------------------------------------------------------------------------------------:|:---------------------------------------------------------------------------------------------------:|
|                              **Fig 3. Tags > Source Network Graph**                                            |                              **Fig 4. Table with detailed information**                                               |

---


## Features 🌟

- **Broad Data Access** 🔓: Navigate beyond the Google Fact Check Explorer's frontend limitations for access to extensive datasets.
- **Interactive Visualizations** 📊: Utilize Plotly and Dash for engaging and insightful data visualizations.
- **Customizable Searches** 🔍: Conduct searches tailored by queries, languages, and the desired number of results.
- **Network Graphs** 🕸️: Uncover the relationships between sources and claims through detailed network graphs.
- **CSV Export** 📁: Easily export your data in CSV format for offline analysis and reporting.

---

## Getting Started 🛠️

### Prerequisites:

Ensure Python 3.6+ is installed on your system. Follow these steps to get FEAT up and running:

### Setup Process:
#### Clone the Repository:
```bash
git clone https://github.com/yourusername/FEAT.git
```

#### Enter the Project Directory:
```
cd FEAT
```

#### Install Required Libraries:
```bash
pip install -r requirements.txt
```

#### Install FactCheckExplorer Library:

To utilize this project, you must install the FactCheckExplorer library. Run the following command for installation:
```bash
pip install git+https://github.com/GONZOsint/factcheckexplorer.git
```

---

## Launching FEAT 🚀

Execute the following command to start the FEAT dashboard:
```bash
python app.py
```
Navigate to http://127.0.0.1:8050/ in your web browser to interact with the tool.

---

## Contributing 🤝

Your contributions are welcome! Whether you're submitting bugs, requesting features, or contributing code, your input helps improve FEAT.

---

## License 📜

FEAT is available under the MIT License. For more details, see the LICENSE file.
