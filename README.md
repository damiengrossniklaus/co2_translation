# CO2 Translation Web App

This project represents the visualization and web app repository for the semester project of the moduel *Data Warehouse and Data Lake* at the Lucerne University of Applied Sciences and Arts (HSLU). It represents a web app that helps users to contextualize the CO2 emission cause by a product by delivering comparing it to other products of different categories and estimating the time needed for compensation methods to offset the emission of the product. This repository builds the visualisation to reach the goal of creating a platform that helps users to translate the emissions caused by a specific product by providing them with transparent, actionable compensation methods that show for how much, with what and how long it would take to compensate the emission. The Dashboard is hosted on [Streamlit Cloud](https://streamlit.io/cloud) and directly linked to this repository. Meaning, changes in the main branch will directly be reflected on the dashboard on Streamlit Cloud. 

### [ Access to Web App](https://co2-translation.streamlit.app/)


## Project structure

```
.
|-- Pipfile
|-- Pipfile.lock
|-- assets
|   |-- hydro_calc_info.md
|   |-- lead_text.md
|   |-- offset_comparison_lead.md
|   |-- solar_calc_info.md
|   `-- tree_calc_info.md
|-- images
|   |-- hydro.jpeg
|   |-- solar.jpg
|   `-- trees.jpg
|-- requirements.txt
|-- streamlit_app.py
`-- utils
    |-- __pycache__
    |   |-- calc_co2_offset_functions.cpython-310.pyc
    |   |-- design_functions.cpython-310.pyc
    |   |-- helper_functions.cpython-310.pyc
    |   `-- plot_functions.cpython-310.pyc
    |-- calc_co2_offset_functions.py
    |-- design_functions.py
    |-- helper_functions.py
    `-- plot_functions.py
```

## Installation

The following section describes the local installation of the project. This setup can then be used for further development or debugging.

1. **Clone the project repository to your local machine:**

```
git clone https://YOURGITHUBUSERNAME@github.com/damiengrossniklaus/co2_translation.git
cd mobileup_dashboard
```

2. **Create virtual environment from Pipfile.lock:**

   1. Create Pipenv by typing in the terminal: `pipenv shell`
   2. Install requirements: `pip install -r requirements.txt`

3. **Create `.streamlit/secrects.toml` for local DB connection:**

   1. On the root directory level create a folder named `.streamlit`

   2. In this directory create the following file named `secrets.toml`. This secrets will be used accessing the DB for local development. Make sure to not commit them.

      ``````
      [postgres]
      host = "dwl-23.c6drip5o07l1.us-east-1.rds.amazonaws.com"
      port = 5432
      dbname = "dwl_23"
      user = "streamlit"
      password = "streamlit"
      ``````

   3. In order to not commit the `secrets.toml` make sure to create a `.gitignore` file on root directory level. In the there add `.streamlit/`. This will make sure that you do not commit the DB secrets.

4. **Run the dashboard locally**

   1. Run `streamlit run streamlit_app.py`
   2. The app should now be accessible on`http://localhost:8080`
      * With this changes to the app will be directly reflected and you can debug/develop locally

   
