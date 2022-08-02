from .models import ArticleByURL
from .custom_scraper import Scrape
from django.contrib import messages


from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup as bs
from readability import Document

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError, PermissionDenied


def get_languages():
    LANGUAGES = {
        'af': 'Afrikaans',
        'am': 'Amharic',
        'ar': 'Arabic',
        'az': 'Azerbaijani',
        'be': 'Belarusian',
        'bg': 'Bulgarian',
        'bn': 'Bengali',
        'bs': 'Bosnian',
        'ca': 'Catalan',
        'ceb': 'Cebuano',
        'co': 'Corsican',
        'cs': 'Czech',
        'cy': 'Welsh',
        'da': 'Danish',
        'de': 'German',
        'el': 'Greek',
        'en': 'English',
        'eo': 'Esperanto',
        'es': 'Spanish',
        'et': 'Estonian',
        'eu': 'Basque',
        'fa': 'Persian',
        'fi': 'Finnish',
        'fr': 'French',
        'fy': 'Frisian',
        'ga': 'Irish',
        'gd': 'Scots Gaelic',
        'gl': 'Galician',
        'gu': 'Gujarati',
        'ha': 'Hausa',
        'haw': 'Hawaiian',
        'he': 'Hebrew',
        'hi': 'Hindi',
        'hmn': 'Hmong',
        'hr': 'Croatian',
        'ht': 'Haitian Creole',
        'hu': 'Hungarian',
        'hy': 'Armenian',
        'id': 'Indonesian',
        'ig': 'Igbo',
        'is': 'Icelandic',
        'it': 'Italian',
        'iw': 'Hebrew',
        'ja': 'Japanese',
        'jw': 'Javanese',
        'ka': 'Georgian',
        'kk': 'Kazakh',
        'km': 'Khmer',
        'kn': 'Kannada',
        'ko': 'Korean',
        'ku': 'Kurdish (Kurmanji)',
        'ky': 'Kyrgyz',
        'la': 'Latin',
        'lb': 'Luxembourgish',
        'lo': 'Lao',
        'lt': 'Lithuanian',
        'lv': 'Latvian',
        'mg': 'Malagasy',
        'mi': 'Maori',
        'mk': 'Macedonian',
        'ml': 'Malayalam',
        'mn': 'Mongolian',
        'mr': 'Marathi',
        'ms': 'Malay',
        'mt': 'Maltese',
        'my': 'Myanmar (Burmese)',
        'ne': 'Nepali',
        'nl': 'Dutch',
        'no': 'Norwegian',
        'ny': 'Chichewa',
        'or': 'Odia',
        'pa': 'Punjabi',
        'pl': 'Polish',
        'ps': 'Pashto',
        'pt': 'Portuguese',
        'ro': 'Romanian',
        'ru': 'Russian',
        'sd': 'Sindhi',
        'si': 'Sinhala',
        'sk': 'Slovak',
        'sl': 'Slovenian',
        'sm': 'Samoan',
        'sn': 'Shona',
        'so': 'Somali',
        'sq': 'Albanian',
        'sr': 'Serbian',
        'st': 'Sesotho',
        'su': 'Sundanese',
        'sv': 'Swedish',
        'sw': 'Swahili',
        'ta': 'Tamil',
        'te': 'Telugu',
        'tg': 'Tajik',
        'th': 'Thai',
        'tl': 'Filipino',
        'tr': 'Turkish',
        'ug': 'Uyghur',
        'uk': 'Ukrainian',
        'ur': 'Urdu',
        'uz': 'Uzbek',
        'vi': 'Vietnamese',
        'xh': 'Xhosa',
        'yi': 'Yiddish',
        'yo': 'Yoruba',
        'zh-cn': 'Chinese (Simplified)',
        'zh-tw': 'Chinese (Traditional)',
        'zu': 'Zulu'
    }
    return LANGUAGES


def is_string_a_url(url_string: str) -> bool:
    validate_url = URLValidator()
    try:
        validate_url(url_string)
    except ValidationError as e:
        return False
    return True


STATUS_REPORT_TEMPLATE = """
---------------
---------------
---------------
STATUS REPORT FOR QUERY:
    Article Source: {article_source}
    Website Page Title: {page_title}
    Article URL: {article_url}
    Image URL: {image_url}
    Article Title: {article_title}
    Article Description: {article_description}
    Domain Source: {domain_source}
    Domain Full: {domain_full}
    Article Published Date: {article_published_date}
    Article Author: {article_author}
---------------
---------------
---------------
"""


class ReadabilityArticle:
    """Describe what this is."""

    def __init__(self, url):
        self.url = url
        if is_string_a_url(self.url):
            self.response = requests.get(self.url)
            self.soup = bs(self.response.content, 'html.parser')
            self.doc = Document(self.response.text)
            self.page_title = self.doc.title()
            self.text = self.doc.summary()
        else:
            self.response, self.doc, self.page_title, self.text = "---", "---", "---", "---"

    def get_page_title(self):
        return self.page_title

    def get_text(self):
        return self.text

    def get_article_meta(self, keyword):
        """title, description, site_name"""
        try:
            content = self.soup.find("meta", property=f"og:{keyword}")["content"]
        except:
            if keyword == "site_name":
                domain_source = self.get_domain_source()
                if ".wikipedia.org" in domain_source:
                    content = "Wikipedia"
                else:
                    content = self.get_domain_source()
            elif keyword == "description" or keyword == "title":
                content = self.get_page_title()
            else:
                content = ""
        return content

    def get_icon(self):
        try:
            try:
                img = self.soup.find("link", rel="shortcut icon")["href"]
            except:
                img = self.soup.find("link", rel="icon")["href"]
        except:
            img = ""
        if is_string_a_url(img):
            return img
        return None

    def get_domain_source(self):
        domain = urlparse(self.url).netloc
        return domain

    def get_domain_full(self):
        domain = f"https://{self.get_domain_source()}"
        return domain


def get_article_data(request, article_url):
    """"""
    article_obj = ReadabilityArticle(article_url)
    page_title = article_obj.get_page_title()
    text = article_obj.get_text()
    article_title = article_obj.get_article_meta("title")
    if article_title is None:
        article_title = page_title
    article_source = article_obj.get_article_meta("site_name")
    article_description = article_obj.get_article_meta("description")
    domain_source = article_obj.get_domain_source()
    domain_full = article_obj.get_domain_full()
    image_url = article_obj.get_icon()
    article_published_date = ""
    article_author = ""
    article_data = {
        'article_source': article_source,
        'page_title': page_title.upper(),
        'article_url': article_url,
        'image_url': image_url,
        'article_title': article_title,
        'article_description': article_description,
        'domain_source': domain_source,
        'domain_full': domain_full,
        'text': text,
        'article_published_date': article_published_date,
        'article_author': article_author,
    }
    status_report = STATUS_REPORT_TEMPLATE.format(**article_data)
    print(status_report)
    return article_data


def get_custom_scrape_article_data(article):
    # 1. Get domain source (ex. https://newyorker.com -> newyorker.com)
    domain_source = urlparse(article.URL).netloc.replace("www.", "")
    print(f"\n\n\nCP0:{domain_source}\n\n\n")
    # print(domain_source * 100)

    # 2. If within base_arr (ex. of row: ['The New Yorker', 'newyorker.com', TheNewYorker]), the
    #    domain_source (ex. newyorker.com) is in the second item in the row, then proceed with
    #    the custom scraping.
    if filter(lambda source_row: (domain_source in source_row[1]), Scrape.base_arr):
        obj = Scrape(article.URL)
        print("OBJ")
        print(obj)
        if ".substack.com" in domain_source: # ex. my-newsletter.substack.com
            (dct, article_data) = obj.Substack('Substack')
        elif ".medium.com" in domain_source: # ex. braeden.medium.com
            (dct, article_data) = obj.Medium('Medium')
        else:
            src = obj.find_src(domain_source) # ex. find_src("newyorker.com")
            print(src * 100)
            (dct, article_data) = obj.run_method(src) # Using the row found above, find the first item, which is the source.
            text = ""
            for p in dct["text"]:
                p = "<p>" + p + "</p>"
                text += p
            dct["text"] = text
        print(f"\n\n\nCP1:{article_data.source}\n\n\n")
        print(article_data.__dict__)
        print(dct)
    return dct


def save_and_get_dict_for_rendering_article(request, user, article_object, DatabaseModel, article_searched_by):
    """
    data_from_db parameter is a dict in the form:
    data_from_db = {
        "article_id": article.id,
        "article_is_starred": article_is_starred,
        "article_is_bookmarked": article_is_bookmarked,
        "article_searched_by": "url",
    }
    Returns contxt, a dictionary.
    """

    article_in_db = DatabaseModel.objects.filter(id=article_object.id).first() # Find row in DB using article ID from parameter
        
    # Starred or bookmarked?
    if DatabaseModel == ArticleByURL: # If using ArticleByURL
        article_is_starred = user in article_object.article_by_url_stars.all()
        article_is_bookmarked = user in article_object.article_by_url_bookmarks.all()
        article_is_flagged = user in article_object.article_by_url_flags.all()
    else: # If using ArticleByTitle
        article_is_starred = user in article_object.article_by_title_stars.all()
        article_is_bookmarked = user in article_object.article_by_title_bookmarks.all()
        article_is_flagged = user in article_object.article_by_title_flags.all()

    data_from_db = {
        "article_id": article_object.id,
        "article_is_starred": article_is_starred,
        "article_is_bookmarked": article_is_bookmarked,
        "article_is_flagged": article_is_flagged,
        "article_searched_by": article_searched_by,
    }


    # 1. Get domain source (ex. https://newyorker.com -> newyorker.com)
    domain_source = urlparse(article_object.URL).netloc.replace("www.", "")


    # 2. If within base_arr (ex. of row: ['The New Yorker', 'newyorker.com', TheNewYorker]), the
    #    domain_source (ex. newyorker.com) is in the second item in the row, then proceed with
    #    the custom scraping.
    try: # if filter(lambda source_row: (domain_source == source_row[1]), Scrape.base_arr):
        article_data = get_custom_scrape_article_data(article_object) # Returns dict

        messages.warning(request, f"This article has been retrieved using Version 3.1 of Unit 1789's custom search algorithms.")
    except:
        article_data = get_article_data(request, article_object.URL)  # Get article data; returns dict

    # SAVE DATA TO DB:
    # The following is for saving the article in the DB. 
    # The defaults are the '-' default specifief in models.py.
    # The following replaces these within the same row, so
    # the data saved for this article is completely updated.
    article_in_db.article_source = article_data.get("article_source") # article_source
    article_in_db.page_title = article_data.get("page_title")
    # article_in_db.title = article_data.get("article_title") # article_title
    article_in_db.title = article_data.get("article_title") if article_data.get("article_title") else article_data.get("page_title")
    if article_data.get("article_description"): 
        article_in_db.article_description = article_data.get("article_description") 
    article_in_db.domain_source = article_data.get("domain_source")
    article_in_db.domain_full = article_data.get("domain_full")
    article_in_db.text = article_data.get("text")
    if article_data.get("article_published_date"):
        article_in_db.article_published_date = article_data.get("article_published_date")
    if article_data.get("article_author"):
        article_in_db.article_author = article_data.get("article_author")
    article_in_db.save()

    article_data = { # This is for rendering the article.
        'article_source': article_data["article_source"],
        'page_title': article_data["page_title"],
        'article_url': article_data["article_url"],
        'article_title': article_data["article_title"],
        'article_description': article_data["article_description"],
        'domain_source': article_data["domain_source"],
        'domain_full': article_data["domain_full"],
        'text': article_data["text"],
        'article_published_date': article_data["article_published_date"],
        'article_author': article_data["article_author"],
    }

    context = {**article_data, **data_from_db}
    return context



def scrape_search_single_article(url):
    """returns url of first link in Google search"""
    page = requests.get(url)
    soup = bs(page.content, 'html.parser')

    print("\n\n\n")
    print(url)
    print("\n\n\n")

    u = soup.select('div.kCrYT a')[0]['href'].replace('/url?q=', "").split('&sa=')[0]
    return u


def scrape_search_multiple_articles(url):
    """
    returns array of tuples of urls and names in Google search but not youtube links because those are videos
    so, for example:
    [
        ('https://www.foreignaffairs.com/articles/china/2019-08-14/party-man', "Party Man: Xi Jinping's Quest to Dominate China - Foreign Affairs"),
        ('https://en.wikipedia.org/wiki/Xi_Jinping', 'Xi Jinping - Wikipedia'),
        etc........
    ]
    """
    page = requests.get(url)
    soup = bs(page.content, 'html.parser')
    urls = soup.select('div.kCrYT')
    linksArr = []
    namesArr = []
    idsArr = [] # Set up an id for each article
    i = 1 # first id = 1; increments by 1 each time
    for u in urls:
        try:
            u = u.find('a')
            href = u['href'].replace('/url?q=', "")
            if "www.youtube." not in href.lower() and "www.google.com" not in href.lower() and "/search?ie=UTF-8&q=" not in href.lower():
                href = href.split('&sa=')[0]
                nm = u.find('div', {'class': 'BNeawe'}).get_text()
                if href not in linksArr:
                    linksArr.append(href)
                    namesArr.append(nm)
                    idsArr.append(i)
                    i += 1
        except:
            pass
    return list(zip(linksArr, namesArr, idsArr))


def scrape_google_search_result_description(url):
    # Example URL: 'https://www.google.com/search?q=yves+bouvier'
    page = requests.get(url)
    soup = bs(page.content, 'html.parser')
    # pprint(soup)
    try:
        # try:
        #     first_try = soup.select("div.kCrYT")
        #     summary = first_try[0]
        # except:
        #     second_try = soup.select("div.BNeawe.s3v9rd.AP7Wnd")
        #     summary = second_try[0]
        first_try = soup.select("div.kCrYT")
        second_try = soup.select("div.BNeawe.s3v9rd.AP7Wnd")
        if first_try is not None:
            summary = first_try[0].get_text()
        elif first_try is None and second_try is not None:
            summary = second_try[0].get_text()
        else:
            summary = ""
    except:
        summary = ""
    return summary


def get_wikipedia_summary(wikipedia_url):
    """Returns the first paragraph with text on the Wikipedia page."""
    # Example URL: 'https://en.wikipedia.org/wiki/Yves_Bouvier'
    page = requests.get(wikipedia_url)
    soup = bs(page.content, 'html.parser')
    content = soup.select("div.mw-parser-output")[0]
    empty_paragraphs = soup.select(".mw-empty-elt")
    for p in empty_paragraphs:
        p.decompose()
    first_paragraph = soup.select("p")[0].get_text()
    return first_paragraph


def get_google_or_wikipedia_summary(query):
    try:
        try: # Wikipedia
            url_argument = "_".join(query.split()).title()
            wikipedia_page_url = f"https://en.wikipedia.org/wiki/{url_argument}"
            summary = get_wikipedia_summary(wikipedia_page_url)
        except: # Google
            url_argument = "+".join(query.lower().split()) + "+summary"
            google_search_results_page_url = f"https://www.google.com/search?q={url_argument}"
            summary = scrape_google_search_result_description(google_search_results_page_url)
    except:
        summary = ""
    return summary


def get_google_url(source, other_source, query):
    query = "+".join(query.lower().split())
    if source and (other_source is None):
        source_param = "+".join(source.lower().split())
        google_url = f"https://www.google.com/search?q=site:%22{source_param}%22+{query}"
    elif other_source and (source is None):
        other_source_param = "+".join(other_source.lower().split())
        google_url = f"https://www.google.com/search?q={other_source_param}+{query}"
    else: # If both source and other_source are None
        google_url = f"https://www.google.com/search?q={query}"
    print(f"Google URL: {google_url}")
    return google_url