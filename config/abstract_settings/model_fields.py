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
ASSIGNMENT_FIELDS = ['title', 'due_date', 'description', 'language', 'submodule', 'estimated_minutes_to_complete', 'assignment_type', 'text', 'internal_link', 'external_reading_link', 'external_link', 'iframe_link', 'youtube_video_link', 'youtube_video_transcript_id', 'corsican_bible_chapter', 'article_by_url', 'article_id']
TASK_FIELDS = ['task_type', 'due_date', 'assignment', 'completed']