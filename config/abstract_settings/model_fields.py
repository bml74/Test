""" For ads app. """

AD_PURCHASE_FIELDS = [
        'group_that_purchased_ad', 
        'offer', 
        'advertisement_type', 
        'specialization_to_be_advertised',
        'course_to_be_advertised',
        'listing_to_be_advertised',
        'post_to_be_advertised',
        'general_advertisement_text'
]

AD_OFFER_FIELDS = [
    'title', 
    'description', 
    'price', 
    'metric', 
    'required_ad_impressions', 
    'required_unique_ad_impressions', 
    'required_clicks'
]


""" For ecoles app. """

CATEGORY_FIELDS = ['title', 'description', 'creator']
FIELD_FIELDS = ['title', 'category', 'description', 'creator']
SPECIALIZATION_FIELDS = ['title', 'field', 'visibility', 'description', 'difficulty_level', 'group']
COURSE_FIELDS = ['title', 'field', 'visibility', 'difficulty_level', 'description', 'specialization', 'group']
MODULE_FIELDS = ['title', 'course', 'description']
SUBMODULE_FIELDS = ['title', 'module', 'description']
ASSIGNMENT_FIELDS = [
    'title', 'due_date', 'description', 'language', 
    'submodule', 
    'estimated_minutes_to_complete', 
    'assignment_type', 
    'text', 
    'internal_link', 
    'external_reading_link', 
    'external_link', 
    'iframe_link', 
    'youtube_video_link', 
    'youtube_video_transcript_id', 
    'corsican_bible_chapter', 
    'article_by_url', 
    'article_id'
]
TASK_FIELDS = ['task_type', 'due_date', 'assignment', 'completed']


""" For market app. """

LISTING_FIELDS = [
    'title', 'description', 
    'price', 
    'date_due', 
    'visibility', 
    'group',
    'listing_category', 
    'infinite_copies_available', 
    'quantity_available', 
    'listing_medium', 
    'listing_type',
]


""" For messaging app. """

ROOM_FIELDS = ['title', 'room_group_profile']


""" For orgs app. """

LISTING_FOR_GROUP_MEMBERS_FIELDS = [
    'title',
    'description',
    'price',
    'due_date',
    'listing_for_group_members_type'
]

""" For market app. """

EVENT_FIELDS = [
    "parent_map",
    "latitude",
    "longitude",
    "altitude",
    "alternative_id",
    "content_online",
    "dates",
    "hours",
    "day",
    "primary_city_name",
    "alternative_city_names",
    "primary_region_name",
    "alternative_region_names",
    "primary_country_name",
    "alternative_country_names",
    "address",
    "postcode",
    "district",
    "neighborhood",
    "number_of_days_after_anchor_date_that_event_began",
    "number_of_days_after_anchor_date_that_event_ended",
    "start_date",
    "end_date",
    "title",
    "description",
    "number_of_sites",
    "number_of_casualties",
    "number_of_memorials",
    "type_of_place_before_event",
    "occupation_period",
]

EVENT_IMAGE_FIELDS = ["event", "link"]

EVENT_VIDEO_FIELDS = ["event", "link"]