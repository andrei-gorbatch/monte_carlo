# To run app locally
* Create env: python -m venv venv
* Activate env: source *path*/venv/Scripts/activate
* Install requirements: python -m pip install -r requirements.txt
* set env variables: export CLOUDSDK_PYTHON=python; export CLOUD_STORAGE_BUCKET="dnd-combat-simulator-bucket"
* Activate app: python main.py

# Do deploy app to google cloud:
* Install google cloud CLI if needed and login
* set env variables: export CLOUDSDK_PYTHON=python; 
* gcloud app deploy
* Follow this to add/update static files on google bucket: https://cloud.google.com/appengine/docs/flexible/serving-static-files?tab=python
* Go to https://dnd-combat-simulator.nw.r.appspot.com/ to check

# Useful links:
* https://console.cloud.google.com/
