import json
import pandas as pd
from .models import Event
from django.http import HttpResponse


def get_geojson_from_model(queryset):
    """Returns dict."""
    FEATURES = []
    for row in queryset:
        FEATURES.append({
            "type": "Feature",
            "properties": {
                "parent_map": row.parent_map.title,
                "altitude": row.altitude,
                "content_online": row.content_online,
                "dates": row.dates,
                "hours": row.hours,
                "day": row.day,
                "primary_city_name": row.primary_city_name,
                "alternative_city_names": list(row.alternative_city_names.names()),
                "primary_region_name": row.primary_region_name,
                "alternative_region_names": list(row.alternative_region_names.names()),
                "primary_country_name": row.primary_country_name,
                "alternative_country_names": list(row.alternative_country_names.names()),
                "address": row.address,
                "postcode": row.postcode,
                "district": row.district,
                "neighborhood": row.neighborhood,
                "number_of_days_after_anchor_date_that_event_began": row.number_of_days_after_anchor_date_that_event_began,
                "number_of_days_after_anchor_date_that_event_ended": row.number_of_days_after_anchor_date_that_event_ended,
                "start_date": str(row.start_date),
                "end_date": str(row.end_date),
                "title": row.title,
                "description": row.description,
                "link": row.link,
                "marker_color": row.marker_color,
                "number_of_sites": row.number_of_sites,
                "number_of_casualties": row.number_of_casualties,
                "alternative_id": row.alternative_id,
                "number_of_memorials": row.number_of_memorials,
                "type_of_place_before_event": row.type_of_place_before_event,
                "occupation_period": row.occupation_period,
            },
            "geometry": {
                "type": row.geometry,
                "coordinates": [row.longitude, row.latitude]
            }
        })

    geojson =  {"type": "FeatureCollection", "features": FEATURES}
    return geojson


def db_model_to_geojson(queryset):
    """Takes model rows in database and converts it into GEOJSON."""
    geojson =  get_geojson_from_model(queryset=queryset)
    response = HttpResponse(content_type='text/json')
    response['Content-Disposition'] = 'attachment; filename=export.json'
    response = HttpResponse(json.dumps(geojson), content_type='application/json')
    return response


def process_map_data(df, parent_map):
    """
    Takes a dataframe and creates a new Event object for each row in the DF."""
    print(df.columns)
    print(df.shape)
    print(df.head(15))
    print("First row:")
    print(df.iloc[0])
    # Delete row if there is no latitude or longitude:
    df = df[pd.notnull(df['latitude'])]
    df = df[pd.notnull(df['longitude'])]
    for index, row in df.iterrows():
        latitude = row.get('latitude'); longitude = row.get('longitude'); altitude = row.get('altitude'); geometry = row.get('geometry')
        primary_city_name = row.get('primary_city_name'); alternative_city_names = row.get('alternative_city_names')
        primary_region_name = row.get('primary_region_name'); alternative_region_names = row.get('alternative_region_names')
        primary_country_name = row.get('primary_country_name'); alternative_country_names = row.get('alternative_country_names')
        address = row.get('address'); postcode = row.get('postcode'); district = row.get('district'); neighborhood = row.get('neighborhood')
        number_of_days_after_anchor_date_that_event_began=int(row.get('number_of_days_after_anchor_date_that_event_began', 0))
        number_of_days_after_anchor_date_that_event_ended=int(row.get('number_of_days_after_anchor_date_that_event_ended', 0))
        start_date = row.get('start_date'); end_date = row.get('end_date')
        title = row.get('title') if row.get('title') is not None else row.get('primary_city_name', '')
        description = row.get('description', '')
        link = row.get('link', '')
        marker_color = row.get('marker_color') if row.get('marker_color') else 'blue'
        content_online = row.get('content_online', 0)
        number_of_sites = row.get('number_of_sites', 0)
        number_of_casualties = row.get('number_of_casualties', 0)
        alternative_id = row.get('alternative_id')
        number_of_memorials = row.get('number_of_memorials')
        type_of_place_before_event = row.get('type_of_place_before_event')
        occupation_period = row.get('occupation_period')

        print(f"latitude: {latitude}")
        print(f"longitude: {longitude}")
        print(f"altitude: {altitude}")
        print(f"geometry: {geometry}")
        print(f"primary_city_name: {primary_city_name}")
        print(f"alternative_city_names: {alternative_city_names}")
        print(f"primary_region_name: {primary_region_name}")
        print(f"alternative_region_names: {alternative_region_names}")
        print(f"primary_country_name: {primary_country_name}")
        print(f"alternative_country_names: {alternative_country_names}")
        print(f"address: {address}")
        print(f"postcode: {postcode}")
        print(f"district: {district}")
        print(f"neighborhood: {neighborhood}")
        print(f"number_of_days_after_anchor_date_that_event_began: {number_of_days_after_anchor_date_that_event_began}")
        print(f"number_of_days_after_anchor_date_that_event_ended: {number_of_days_after_anchor_date_that_event_ended}")
        print(f"start_date: {start_date}")
        print(f"end_date: {end_date}")
        print(f"title: {title}")
        print(f"description: {description}")
        print(f"link: {link}")
        print(f"marker_color: {marker_color}")
        print(f"content_online: {content_online}")
        print(f"number_of_sites: {number_of_sites}")
        print(f"number_of_casualties: {number_of_casualties}")
        print(f"alternative_id: {alternative_id}")
        print(f"number_of_memorials: {number_of_memorials}")
        print(f"type_of_place_before_event: {type_of_place_before_event}")
        print(f"occupation_period: {occupation_period}")

        e = Event(
            parent_map=parent_map,
            latitude=row.get('latitude'), longitude=row.get('longitude'), altitude=row.get('altitude'), geometry=row.get('geometry'), 
            primary_city_name=row.get('primary_city_name'), alternative_city_names=row.get('alternative_city_names'),
            primary_region_name=row.get('primary_region_name'), alternative_region_names=row.get('alternative_region_names'),
            primary_country_name=row.get('primary_country_name'), alternative_country_names=row.get('alternative_country_names'),
            address=row.get('address'), postcode=row.get('postcode'), district=row.get('district'), neighborhood=row.get('neighborhood'),
            number_of_days_after_anchor_date_that_event_began=int(row.get('number_of_days_after_anchor_date_that_event_began', 0)), 
            number_of_days_after_anchor_date_that_event_ended=int(row.get('number_of_days_after_anchor_date_that_event_ended', 0)),
            start_date=row.get('start_date'), end_date=row.get('end_date'),
            title=row.get('title') if row.get('title') is not None else row.get('primary_city_name', ''),
            description=row.get('description', ''),
            link=row.get('link', ''),
            marker_color=row.get('marker_color') if row.get('marker_color') else 'blue',
            content_online=row.get('content_online', 0),
            number_of_sites=row.get('number_of_sites', 0),
            number_of_casualties=row.get('number_of_casualties', 0),
            alternative_id=row.get('alternative_id'),
            number_of_memorials=row.get('number_of_memorials'),
            type_of_place_before_event=row.get('type_of_place_before_event'),
            occupation_period=row.get('occupation_period')
        )
        e.save()

    print(df.head())


def geojson_to_csv(data_dict):
    data = []
    data_dict = dict(data_dict)
    list_of_features = data_dict["features"]
    for feature in list_of_features:
        properties = feature["properties"]
        geometry = feature["geometry"]
        data.append([
            geometry.get('coordinates')[1], # latitude
            geometry.get('coordinates')[0], # longitude
            geometry.get('type'),
            properties.get('altitude'),
            properties.get('alternative_id'), properties.get('content_online'),
            properties.get('dates'), properties.get('hours'), properties.get('day'),
            properties.get('primary_city_name'), properties.get('alternative_city_names'),
            properties.get('primary_region_name'), properties.get('alternative_region_names'),
            properties.get('primary_country_name'), properties.get('alternative_country_names'),
            properties.get('number_of_sites'), properties.get('number_of_casualties'),
            properties.get('title'), properties.get('description'),
            properties.get('start_date'), properties.get('end_date'),
            properties.get('number_of_days_after_anchor_date_that_event_began'), properties.get('number_of_days_after_anchor_date_that_event_ended'),
            properties.get('number_of_memorials'), properties.get('type_of_place_before_event'), properties.get('occupation_period'),
            properties.get('address'), properties.get('postcode'), properties.get('district'), properties.get('neighborhood'), 
            properties.get('link'), properties.get('marker_color'),

        ])
    df = pd.DataFrame(data, columns=[ # 32 columns
        'latitude', 'longitude', 'geometry',
        'altitude',
        'alternative_id', 'content_online',
        'dates', 'hours', 'day',
        'primary_city_name', 'alternative_city_names',
        'primary_region_name', 'alternative_region_names',
        'primary_country_name', 'alternative_country_names',
        'number_of_sites', 'number_of_casualties',
        'title', 'description',
        'start_date', 'end_date',
        'number_of_days_after_anchor_date_that_event_began', 'number_of_days_after_anchor_date_that_event_ended',
        'number_of_memorials', 'type_of_place_before_event', 'occupation_period',
        'address', 'postcode', 'district', 'neighborhood', 
        'link', 'marker_color'
    ])
    return df