# yelp

Possibly excessive multipart/multiparameter downloader to download all Yelp
businesses in a region by auto-re-parameterizing API requests to subdivide up
results into chunks small enough to get under the API limits, and
semi-robustly track download progress so I can pause/resume.

See `settings.py` for download path configuration.
