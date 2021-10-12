_SOURCE_TEMPLATE = 'https://naturalearth.s3.amazonaws.com/{resolution}_{category}/ne_{resolution}_{name}.zip'

def update_config(config):
    """Configures cartopy to download NaturalEarth shapefiles from S3 instead
    of naciscdn."""
    from cartopy.io.shapereader import NEShpDownloader
    target_path_template = NEShpDownloader.default_downloader().target_path_template
    downloader = NEShpDownloader(url_template=_SOURCE_TEMPLATE,
                                 target_path_template=target_path_template)
    config['downloaders'][('shapefiles', 'natural_earth')] = downloader
