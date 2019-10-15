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
into the `yelp` folder. See `yelp/settings.py` for the download path
configuration.

### Transform fetched data into heatmap-palatable format

```
python datavis_transform.py
```

### Unit tests

```
python -m unittest discover
```
