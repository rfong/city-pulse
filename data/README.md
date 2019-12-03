This attempts to cache all biz data for a region from the Yelp API, circumventing the cap of 1000 businesses per category by parametrically subdividing down the category ontology until complete. If the process crashes, any progress made on complete biz categories is saved. Only incomplete biz categories will be retried.

### Fetch business data from Yelp API

Update your bash profile with your API keys (don't forget to `source` it).
```
export YELP_API_SECRET='MY_YELP_API_SECRET_KEY'
```

Run the fetcher script.
```
python fetch_yelp_data.py
```

This will begin downloading data from the Yelp API
into the `yelp` folder. It will track your progress, so it's ok to Ctrl-C
out of the script if you want to take a break.

See `yelp/settings.py` for the download path configuration.

### Transform fetched data into heatmap-palatable format

```
python datavis_transform.py
```

### Unit tests

```
python -m unittest discover
```
