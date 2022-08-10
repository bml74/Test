import numpy as np
import requests, json, re, os, datetime, urllib
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse
from datetime import date
from requests.exceptions import MissingSchema
from urllib.parse import urlparse


class SingleArticle:
    def __init__(self, source, url, title, descr, author, date, arr):
        self.source = source
        self.url = url
        self.title = title
        self.descr = descr
        self.author = author
        self.date = date
        self.arr = arr


class Scrape:

    def __init__(self, url=None):
        self.url = url
        try:
            self.page = requests.get(self.url)
            self.soup = bs(self.page.content, 'html.parser') # Instantiate soup object
        except MissingSchema:
            pass

    def find_src(self, domain):
        """
        If domain (ex. 'luxtimes.lu' or 'domains.google' or 'wsj.com' is in the dictionary of urls
        that we have, then return the associated value (ex. 'Luxembourg Times').
        Else raise exception.
        """
        if domain in self.url_dict:
            return self.url_dict[domain]
        raise Exception
        # return None

    def handle_meta(self, source):
        """
        Takes in a source as an argument.   Handles the initial stuff common to all scrape methods.
        Thus: returns url, and source, and soup.   Example call: (source, url, soup) = self.handle_meta(src)
        """
        url = self.url
        soup = self.soup
        return (source, url, soup)

    def handle_content(self, soup, content_selector, selectors, garbage_arr, data_arr, strs=None, arr_of_strs_to_remove_within_ps=None, is_wikipedia=False):
        """
        :param strs: Specifies strs that trigger the removal of a paragraph. For example, if the string "is a contributing author"
        is in a certain paragraph, then the entire paragph will be removed; it does not just remove the certain string, but the
        entire paragph that contains the string
        :param arr_of_strs_to_remove_within_ps: ex. will replace '«' with '"' and '»' with '"' but will not remove the whole html_p
        :return:
        """
        try:
            content = soup.select(content_selector)[0]
        except:
            content = soup.find(content_selector)
        content = self.removeOtherGarbage(content, *garbage_arr) # remove garbage ex. aside, table, img, blockquote
        ps = content.select(selectors)
        if not is_wikipedia:
            arr = self.handle_ps(ps, strs=strs, arr_of_strs_to_remove_within_ps=arr_of_strs_to_remove_within_ps)
        else:
            arr = self.handle_ps_wikipedia(ps, strs=strs, arr_of_strs_to_remove_within_ps=arr_of_strs_to_remove_within_ps)
        (dct, article_data) = self.addToDictAndCreateClass(*data_arr, arr)
        return (dct, article_data)

    def handle_ps(self, ps, strs=None, arr_of_strs_to_remove_within_ps=None):
        arr = []
        for p in ps:
            html_p = " ".join(p.text.strip().split())
            html_p = self.replace_strs(html_p, arr_of_strs_to_remove_within_ps)

            try:
                img = p.find("img")
                html_p += f"""<img src={img['src']} style='width: 100%; height: auto;'>"""
            except:
                pass

            if html_p in arr:
                continue
            noFlag = True
            if strs is not None:
                for str in strs:
                    if str.lower() in html_p.lower():
                        noFlag = False
            if html_p is not None and html_p != "" and noFlag:
                arr.append(html_p)
        return arr

    def handle_ps_wikipedia(self, ps, strs=None, arr_of_strs_to_remove_within_ps=None):
        arr = []
        for p in ps:
            html_p = " ".join(p.text.strip().split())
            html_p = self.replace_strs(html_p, arr_of_strs_to_remove_within_ps)
            if html_p == "Books" or html_p == "See also" or html_p == "References" or html_p == "External links":
                break
            if html_p in arr:
                continue
            noFlag = True
            if strs is not None:
                for item in strs:
                    if html_p.lower().find(item.lower()) > -1:
                        noFlag = False
                        break
            if html_p is not None and html_p != "" and noFlag:
                arr.append(html_p)
        return arr

    def replace_strs(self, html_p, arr_of_strs_to_remove_within_ps):
        if arr_of_strs_to_remove_within_ps is not None:
            for arr in arr_of_strs_to_remove_within_ps:
                html_p = html_p.replace(arr[0], arr[1])
        return html_p

    def handle_content_just_using_soup(self, soup, selectors, garbage_arr, dont_append_keys=None, breakers=None):
        soup = self.removeOtherGarbage(soup, *garbage_arr)
        arr = []
        ps = soup.select(selectors)
        for p in ps:
            flag = False
            html_p = " ".join(p.text.strip().split())
            if dont_append_keys is not None:
                for k in dont_append_keys:
                    if k.lower() in html_p.lower():
                        html_p = None
                        break
            if html_p is not None and html_p != "" and not flag:
                arr.append(html_p)
        if breakers is not None:
            for html_p in arr:
                for breaker in breakers:
                    if breaker.lower() in html_p.lower():
                        return arr[:arr.index(html_p)]
        return arr

    def addToDictAndCreateClass(self, source, url, title, descr, author, date, arr):
        """
        Takes in the data from the scrape methods. Handles it by doing two things:
        1) Creates new object of class 'SingleArticle' with all the specified attributes
        2) Creates dictionary 'dct' with all the specified keys and values
        Returns both the instantiated obj. and the dict.
        """
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {}
        dct['article_source'] = source
        dct['page_title'] = title
        dct['article_url'] = url
        dct['image_url'] = None
        dct['article_title'] = title
        dct['article_description'] = descr
        domain_source = urlparse(self.url).netloc
        dct['domain_source'] = domain_source
        dct['domain_full'] = f"https://{domain_source}"
        dct['text'] = arr
        dct['article_published_date'] = date
        dct['article_author'] = author

        print("\n\n\nDICT")
        print(dct)
        print("nDICT\n\n\n")
        print("\n\n\nAD")
        print(article_data)
        print("AD\n\n\n")

        return (dct, article_data)

    def removeOtherGarbage(self, soup, *args):
        """
        Remove Twitter blockquotes and any other garbage specified in arguments.
        For example, if you pass in "aside" and "div.ad-container", then all of
        the 'aside' elements and 'div' elements with a class of 'ad-container'
        will be removed from the soup (either soup itself or content variable
        which is essentially just the article's inner text div). Also takes in
        unspecified number of args -- thus you can remove however many elements
        you want.
        Example call:
        content = self.removeOtherGarbage(content, 'blockquote', 'div.embed-container', 'figure')
        Returns soup/content.
        """
        try:
            twitters = soup.select('blockquote.twitter-tweet')
            for t in twitters:
                t.decompose()
        except:
            pass
        try:
            for arg in args:
                items = soup.select(arg)
                for item in items:
                    item.decompose()
        except:
            pass
        return soup

    def select_title(self, soup, header_selector=None, selector=None, arr_of_strs_to_remove=None):
        title = soup.title.text.strip()
        if header_selector is None and selector is not None:
            try:
                title = soup.select(selector)[0].text.strip()
            except:
                title = title
        else:
            if selector is not None and header_selector is not None:
                try:
                    title = soup.select(header_selector)[0].select(selector)[0].text.strip()
                except:
                    title = title
        if arr_of_strs_to_remove is not None and title is not None:
            for arr in arr_of_strs_to_remove:
                title = title.replace(arr[0], arr[1])
        return title

    def select_descr(self, soup, header_selector=None, selector=None, arr_of_strs_to_remove=None):
        descr = ""
        if header_selector is None and selector is not None:
            try:
                descr = soup.select(selector)[0].text.strip()
            except:
                descr = descr
        else:
            if selector is not None and header_selector is not None:
                try:
                    descr = soup.select(header_selector)[0].select(selector)[0].text.strip()
                except:
                    descr = descr
        if arr_of_strs_to_remove is not None and descr is not None:
            for arr in arr_of_strs_to_remove:
                descr = descr.replace(arr[0], arr[1])
        return descr

    def select_date(self, soup, header_selector=None, selector=None, arr_of_strs_to_remove=None):
        date = ""
        if header_selector is None and selector is not None:
            try:
                date = soup.select(selector)[0].text.strip()
            except:
                date = date
        else:
            if selector is not None and header_selector is not None:
                try:
                    date = soup.select(header_selector)[0].select(selector)[0].text.strip()
                except:
                    date = date
        if arr_of_strs_to_remove is not None and date is not None:
            for arr in arr_of_strs_to_remove:
                date = date.replace(arr[0], arr[1])
        return date

    def select_author(self, soup, header_selector=None, selector=None, arr_of_strs_to_remove=None):
        author = ""
        if header_selector is None and selector is not None:
            try:
                a_links = []
                authors = soup.select(selector)
                [a_links.append(a.text.strip()) for a in authors if a.text.strip() not in a_links]
                author = ", ".join(a_links)
            except:
                author = author
        else:
            if selector is not None and header_selector is not None:
                try:
                    a_links = []
                    authors = soup.select(header_selector)[0].select(selector)
                    [a_links.append(a.text.strip()) for a in authors if a.text.strip() not in a_links]
                    author = ", ".join(a_links)
                except:
                    author = author
        if arr_of_strs_to_remove is not None and author is not None:
            for arr in arr_of_strs_to_remove:
                author = author.replace(arr[0], arr[1])
        return author

    def LuxembourgTimes(self, src="Luxembourg Times"):
        (source, url, soup) = self.handle_meta(src)
        ltPlus = False
        try:
            plusImg = soup.select('div.article-header')[0].select('.badge-title')[0].find('img')
            if plusImg:
                ltPlus = True
        except:
            pass
        title = self.select_title(soup, selector="h1", arr_of_strs_to_remove=[['«', '"'], ['»', '"']]) # 'h1', {'class': 'entry-title'}
        descr = self.select_descr(soup, header_selector=".article-header", selector=".article-summary", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        date = self.select_date(soup, header_selector=".article-header", selector=".time-item")
        author = self.select_author(soup, selector=".author-block")
        data_arr = [source, url, title, descr, author, date]
        if not ltPlus:
            content_selector = 'div.mag-top-30'
            selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
            garbage_arr = ['blockquote', 'figure', 'div.embed-container']
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['has a brand-new linkedin page, follow us here!'])
        else:
            arr = ["Noooooo! Unfortunately, this article is only available for Luxembourg Times users with a premium account. Sorry!"]
            (dct, article_data) = self.addToDictAndCreateClass(*data_arr, arr)
        return (dct, article_data)

    # Method for The Hill:
    def TheHill(self, src="The Hill"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="div.content-wrapper.title", selector="h1.title", arr_of_strs_to_remove=[['«', '"'], ['»', '"']]) # 'h1', {'class': 'entry-title'}
        date = self.select_date(soup, header_selector="span.submitted-by", selector=".submitted-date")
        author = self.select_author(soup, header_selector="div.content-wrapper.title", selector="span.submitted-by").split("-")[0].strip()
        data_arr = [source, url, title, None, author, date]
        content_selector = 'div.content-wrp'
        selectors = 'p, h4, ul li, ol li, div.ArticleBody-ad-slot-83sCj'
        garbage_arr = ['span.rollover-people-block']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        print("\n\n\n\nMETHOD FOR SITE" * 8)
        print(dct.keys())
        print()
        print(type(article_data))
        print(dir(article_data))
        print("\n\n\n\n")
        return (dct, article_data)

    # Method for Wikipedia:
    def Wikipedia(self, src="Wikipedia"):
        (source, url, soup) = self.handle_meta(src)
        title = soup.find('h1', {'class': 'firstHeading'}).text.strip()
        author = None
        date = None
        descr = None
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'div#mw-content-text'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['div.toc', 'span#coordinates', 'div.thumb', 'div.tright', 'div.tleft', 'table', 'img', '.mw-editsection']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, arr_of_strs_to_remove_within_ps=[["[edit]", ""]], is_wikipedia=True)
        return (dct, article_data)

    # Method for Britannica:# Method for Britannica:# Method for Britannica:
    # Method for Britannica:# Method for Britannica:# Method for Britannica:
    # Method for Britannica:# Method for Britannica:# Method for Britannica:
    def Britannica(self, src="Britannica"):
        (source, url, soup) = self.handle_meta(src)
        arr = []
        try:
            q_set = []
            a_set = []
            dict = {}
            questions = self.soup.select('h3.accordion--question')
            for i in range(len(questions)):
                q_set.append(questions[i].text.strip())
            answers = self.soup.select('h3.accordion--question + div')
            for i in range(len(answers)):
                a_set.append(answers[i].text.strip())
            if len(q_set) == len(a_set):
                for i in range(len(q_set)):
                    dict[q_set[i]] = a_set[i]
                arr.append("Top Questions")
                i = 1
                for key, value in dict.items():
                    arr.append(f"{i}. {str(key)}\t{str(value)}")
                    i += 1
                arr.append("End of top questions....Now on to the article!")

            for question in questions:
                question.decompose()
            for answer in answers:
                answer.decompose()
        except:
            pass
        title = self.select_title(soup, selector="h1") # 'h1', {'class': 'entry-title'}
        descr = self.select_descr(soup, selector=".topic-identifier")
        author = self.select_author(soup, header_selector="div.source", selector="a")
        dct = {}
        arr = []
        dct['source'] = source
        dct['url'] = url
        dct['title'] = title
        dct['descr'] = descr
        dct['author'] = author
        dct['date'] = None
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        (other_britannica_links, links) = self.other_britannica_links(soup)
        full_links = []
        if other_britannica_links:
            for i in range(len(links)):
                u = f'https://www.britannica.com{links[i]}'
                full_links.append(u)
        else:
            full_links.append(url)
        for u in full_links:
            article_arr = self.handleBritannica(u)
            for p in article_arr:
                arr.append(p)

        dct['text'] = arr
        return (dct, article_data)

    def handleBritannica(self, url):
        try:
            page_britannica = requests.get(url)
            soup_britannica = bs(page_britannica.content, 'html.parser')
            article_arr = []
            content = soup_britannica.find_all('section', {'data-level': '1'})
            for section in content:
                ps = section.select('p, h2, h3, h4, h5, h6, ul li, ol li')
                for p in ps:
                    article_arr.append(p.text.strip())
            return article_arr
        except MissingSchema:
            return False

    def other_britannica_links(self, soup):
        try:
            if soup.select('div.drawer')[0] is not None:
                all_links = []
                links = soup.select('div.drawer ul li a')
                hrefs = []
                for link in links:
                    hrefs.append(link['href'])
                for i in range(len(hrefs)):
                    href = hrefs[i].split("#")[0]
                    hrefs[i] = href
                [all_links.append(link) for link in hrefs if link not in all_links]
                return (True, all_links)
            return (False, None)
        except:
            return (False, None)
    # End Method for Britannica:# End Method for Britannica:# End Method for Britannica:
    # End Method for Britannica:# End Method for Britannica:# End Method for Britannica:
    # End Method for Britannica:# End Method for Britannica:# End Method for Britannica:

    # Method for TODAY:
    def Today(self, src):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.entry-title", arr_of_strs_to_remove=[['«', '"'], ['»', '"']]) # 'h1', {'class': 'entry-title'}
        descr = self.select_descr(soup, selector="p.entry-summary", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        date = self.select_date(soup, selector="time.datestamp")
        author = self.select_author(soup, selector="span.author-name")
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'div.entry-content-body'
        selectors = 'p, h2, ul li, ol li'
        garbage_arr = ['span.rollover-people-block', 'div.related-stories', 'div.widget-moovit', 'div.photo-gallery-preview']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Italia Oggi:
    def ItaliaOggi(self, src="Italia Oggi"):
        (source, url, soup) = self.handle_meta(src)
        arr = []
        try:
            head_div = soup.find('div', {'class': 'titolodettaglio tacenter'})
            title = head_div.find('h3').text.strip()
            author = head_div.find('span', {'class': 'mtop10'}).text.strip()
        except:
            title = None
            author = None
        try:
            date = soup.find('div', {'class': 'testatadata-mob'}).text.strip()
        except:
            date = None
        try:
            descr = soup.find('div', {'class': 'sottotitolo'}).text
        except:
            descr = None
        articolo = soup.find('div', {'id': 'articolo'}).find_all('p')
        soup_p = bs(self.page.content, 'html.parser')
        first = soup_p.find('div', {'id': 'articolo'})
        first.find('p').decompose()
        first_p = first.text.strip().replace('«', '"').replace('»', '"')
        arr.append(first_p)
        for p in articolo:
            html_p = p.text.strip().replace('«', '"').replace('»', '"').replace("© Riproduzione riservata", "").split()
            html_p = " ".join(html_p)
            if html_p is not None and html_p != "":
                arr.append(html_p)
        (dct, article_data) = self.addToDictAndCreateClass(source, url, title, descr, author, date, arr)
        return (dct, article_data)

    # Method for InsideOver
    def InsideOver(self, src="InsideOver"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        author = self.select_author(soup, header_selector="p.post-meta", selector="span.author_meta")
        date = self.select_date(soup, header_selector="p.post-meta", selector="time.updated")
        data_arr = [source, url, title, None, author, date]
        content_selector = 'div.entry-content'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['span.rollover-people-block']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for La Gazzetta del Mezziogiorno:
    def LaGazzettadelMezziogiorno(self, src="La Gazzetta del Mezziogiorno"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.titolo_articolo.titolo", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        descr = self.select_descr(soup, selector="h2.sottotitolo_articolo.sottotitolo", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        date = self.select_date(soup, selector=".data_articolo")
        author = self.select_author(soup, selector=".autore_articolo")
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'div.testo_articolo'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['div.vc_shortcode_article_preview']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, arr_of_strs_to_remove_within_ps=[['«', '"'], ['»', '"']]) # [['«', '"'], ['»', '"']]
        return (dct, article_data)

    # Method for La Sicilia:
    def LaSicilia(self, src="La Sicilia"):
        (source, url, soup) = self.handle_meta(src)
        descr = self.select_descr(soup, selector="h2.sottotitolo_articolo.sottotitolo", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        author = self.select_author(soup, selector=".autore_articolo")
        try:
            title = soup.find('h1', {'itemprop': 'headline name'}).text.strip().replace('«', '"').replace('»', '"')
        except:
            title = None
        try:
            date = soup.find('p', {'itemprop': 'datePublished'}).text.strip().replace('	        ', '')
        except:
            date = None
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'div.testo_articolo'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['div.vc_shortcode_article_preview', 'div.widget_fotogallery', 'div.blocco', 'div.text_edit_riproduzione_v2']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, arr_of_strs_to_remove_within_ps=[['«', '"'], ['»', '"']])
        return (dct, article_data)

    # Method for Gazzetta del Sud:
    def GazzettadelSud(self, src="Gazzetta del Sud"):
        (source, url, soup) = self.handle_meta(src)
        # title = self.select_title(soup, selector="h1.titolo_articolo.titolo", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        descr = self.select_descr(soup, selector=".occhiello_articolo", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        author = self.select_author(soup, selector=".autore_articolo").title().split('—')[0]
        if "19" in str(author) or "20" in str(author):
            author = None
        try:
            title = soup.find('div', {'class': 'top_articolo'}).find('h1', {'itemprop': 'name'}).text.strip().replace('«', '"').replace('»', '"')
        except:
            title = None
        try:
            date = soup.find('div', {'class': 'top_articolo'}).find('time', {'itemprop': 'datePublished'}).text.strip().replace('	        ', '')
        except:
            date = None
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'div#txt_corpo_articolo'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['div.vc_shortcode_article_preview', 'div.widget_fotogallery', 'div.blocco', 'div.text_edit_riproduzione_v2']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, arr_of_strs_to_remove_within_ps=[['«', '"'], ['»', '"'], ["© Riproduzione riservata", ""]])
        return (dct, article_data)

    # Method for Fortune
    def Fortune(self, src="Fortune"):
        (source, url, soup) = self.handle_meta(src)

        data = soup.find('script', {'id': 'preload'})
        data = str(data).replace("</script>", "").replace('<script defer="" id="preload">', "").replace(
            "window.__PRELOADED_STATE__ = ", '').strip().replace(";", "")
        data = json.loads(json.dumps(data))
        data = json.loads(data)
        data_copy = data.copy()
        metadata = data_copy['components']['page'][urlparse(url).path][1]['config'][
            'metadata']
        try:
            title = metadata['headline']
        except:
            title = soup.title.text.strip()
        try:
            descr = metadata['description']
        except:
            descr = None
        try:
            author = ", ".join(metadata['author'])
        except:
            author = None
        try:
            date = metadata['datePublished']
        except:
            date = None
        arr = []
        i = data['components']['page'][urlparse(url).path][5]['children'][0]['children'][3]['children'][0]['children']
        for item in i:
            p = str(item['config']['text'])
            if '<p>' in p:
                ps = p.split("</p>")
                for p in ps:
                    clean = re.compile('<.*?>')
                    p = re.sub(clean, '', p.replace("<p>", "")).replace("  ", "\n").replace("&nbsp;", " ").replace(
                        "&nbsp", " ").strip()
                    if len(p) > 0 and p is not None:
                        arr.append(p)
        data_arr = [source, url, title, descr, author, date]
        (dct, article_data) = self.addToDictAndCreateClass(*data_arr, arr)
        return (dct, article_data)

    # Method for Balkan Insight:
    def BalkanInsight(self, src="Balkan Insight"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".headline")
        author = self.select_author(soup, header_selector=".btSubTitle", selector="a.author")
        date = self.select_date(soup, header_selector=".btSubTitle", selector=".btArticleDate")
        descr = self.select_descr(soup, selector=".btArticleExcerpt")
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'div.bt_bb_wrapper'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['small', 'img']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for New Yorker:
    def TheNewYorker(self, src="The New Yorker"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.content-header__row")
        if title == soup.title.text.strip():
            title = self.select_title(soup, selector="h1.content-header__row")
        if title == soup.title.text.strip():
            title = self.select_title(soup, selector="h1")
        author = self.select_author(soup, selector=".byline__name-link")
        if author is None:
            try:
                author = soup.find('span', {'itemprop': 'name'}).text.strip()
            except:
                author = None
        date = self.select_date(soup, selector=".content-header__publish-date")
        if date is None:
            date = self.select_date(soup, selector=".split-screen-content-header__publish-date")
        if date is None:
            date = self.select_date(soup, selector=".content-header__publish-date--with-float-left")
        if date is None:
            date = self.select_date(soup, header_selector="body", selector="time")
        descr = self.select_descr(soup, selector=".content-header__row.content-header__dek")
        if descr is None:
            descr = self.select_descr(soup, selector=".split-screen-content-header__dek")
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'div.content-background'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['small', 'img', 'figure', '.content-header__rubric-block', '.rubric__link']
        try:
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['ign up for our daily newsletter'])
        except:
            content_selector = 'div.article__chunks'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['ign up for our daily newsletter'])
        return (dct, article_data)

    # Method for The Daily Beast:
    def TheDailyBeast(self, src="The Daily Beast"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.StandardHeader__title")
        if title == soup.title.text.strip():
            title = self.select_title(soup, selector="h1.FeatureHeader__title")
        author = self.select_author(soup, selector=".Byline__name")
        if author is None:
            author = self.select_author(soup, selector=".Byline__author")
        descr = self.select_descr(soup, selector=".StoryDescription") #  StoryDescription--featureStoryDescription StoryDescription--feature
        date = self.select_date(soup, header_selector=".PublicationTime__pub-time", selector=".PublicationTime__date")
        if date is None:
            date = self.select_date(soup, header_selector=".PublicationTime__mod-time", selector=".PublicationTime__date")
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'div.Mobiledoc'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['small', 'img']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        msg = "NOTE FROM NABOO: Some articles are only available for Daily Beast users with a premium account. If the content you see on this page has 3 or less paragraphs, it is probably an article reserved for premium subscribers!"
        dct['text'] = [msg.upper()] + dct['text']
        return (dct, article_data)

    # Method for The Atlantic:
    def TheAtlantic(self, src="The Atlantic"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.c-article-header__hed")
        if title == soup.title.text.strip():
            title = self.select_title(soup, selector=".ArticleHeader_hed__3CykF")
        author = self.select_author(soup, header_selector=".c-byline__author", selector="a.c-byline__link")
        if author is None:
            author = self.select_author(soup, selector=".IdeasArticleByline_authorLink__2KBbq")
        if author is None:
            author = self.select_author(soup, selector=".ArticleByline_link__1aQm_")
        if author is None or len(str(author)) < 3:
            try:
                a_links = []
                authors = soup.find('li', {'class': 'byline'}).select('span', {'itemprop': 'name'})
                [a_links.append(a.text.strip()) for a in authors if a.text.strip() not in a_links]
                author = ", ".join(a_links)
            except:
                author = None
        date = self.select_date(soup, header_selector=".c-dateline", selector=".c-dateline__link")
        if date is None:
            try:
                date = soup.find('time', {'itemprop': 'datePublished'}).text.strip()
            except:
                date = None
        if date is None:
            date = self.select_date(soup, selector=".ArticleDateline_root__1tgeR")
        if date is None:
            date = self.select_date(soup, selector=".ArticleDateline_ideasRoot__X748G")
        if date is None:
            date = self.select_date(soup, selector=".date")
        descr = self.select_descr(soup, selector=".c-dek")
        if descr is None:
            descr = self.select_descr(soup, selector=".ArticleDek_root__1_tnX")
        if descr is None:
            descr = self.select_descr(soup, selector=".ArticleDek_ideasRoot__okvtN")
        if descr is None:
            descr = self.select_descr(soup, selector=".dek")
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'body'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['p.c-recirculation-link', 'p.c-letters-cta__text', 'p.c-footer__copyright', 'nav', 'gpt-ad', '.article-cover-extra', '.ArticleRecirc_itemRoot__1Jcqk', '.ArticleRecirc_heading__c8Axp', 'aside', 'img']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['Link Copied'])
        return (dct, article_data)

    # Method for Vanity Fair:
    def VanityFair(self, src="Vanity Fair"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.content-header__row.content-header__hed")
        if title is None:
            title = self.select_title(soup, selector="h1.hed")
        author = self.select_author(soup, header_selector=".byline--author", selector=".byline__name")
        if author is None:
            author = self.select_author(soup, selector=".byline--author")
        if author is None:
            author = self.select_author(soup, selector=".byline__name-link")
        if author is None:
            author = self.select_author(soup, selector=".byline--byline__name")
        if author is None:
            author = self.select_author(soup, selector=".author")
        date = self.select_date(soup, selector=".content-header__publish-date")
        if date is None:
            date = self.select_date(soup, selector=".split-screen-content-header__publish-date")
        if date is None:
            date = self.select_date(soup, selector="time")
        descr = self.select_descr(soup, selector=".content-header__row.content-header__dek")
        if descr is None:
            descr = self.select_descr(soup, selector=".split-screen-content-header__dek")
        if descr is None:
            descr = self.select_descr(soup, selector=".div.dek")
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'div.article__chunks'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['Not a subscriber', 'Join Vanity Fair', 'More Great Stories From Vanity Fair'])
        return (dct, article_data)

    # Method for Vanity Fair Italia:
    def VanityFairIT(self, src="Vanity Fair Italia"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector=".article-header", selector='h1')
        author = self.select_author(soup, header_selector=".article-header", selector='span.name')
        date = self.select_date(soup, header_selector=".article-header", selector='time.date')
        descr = self.select_date(soup, selector='.article-header .lead')
        selectors = 'p, h2, h3, h4, h5, h6'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'iframe', '.instagram-media', 'aside', 'header', 'footer', '.dropdown', '.read-more-link', '.read-more', '.article-preview-circle', 'nav', '.dropdown', '.article-more-list', '.article-footer', '.scrollable-container', '.scrollable-content', '.article-preview-list', '.col-text', '.title', '.meta', '.section-title']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr, dont_append_keys=["read more", "A post shared by"])
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Vanity Fair España:
    def VanityFairES(self, src="Vanity Fair España"):
        (source, url, soup) = self.handle_meta(src)
        soup = self.removeOtherGarbage(soup, *[".tags"])
        title = self.select_title(soup, selector="h1.headline")
        author = self.select_author(soup, selector="div.header .author_content [itemprop='name']")
        date = self.select_date(soup, selector="div.header .publication-date")
        descr = self.select_date(soup, selector='div.header .lead-in')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.esto_le_interesa', '.lo_mas_visto', '.tambien_le_puede_interesar', '.suscription_newsletter', 'footer', 'header', 'nav', '#header_scroll', '.header', '.share', '.promoted_stories']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr)
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Vanity Fair France:
    def VanityFairFR(self, src="Vanity Fair France"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="header.entry-header", selector=".hero__title")
        author = self.select_author(soup, selector=".hero__author")
        date = self.select_date(soup, selector=".hero__publication")
        descr = self.select_descr(soup, selector=".hero__posttitle")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'form', 'header', 'nav', 'footer', '.social-share', '.nav-social__item', '.site-header', '.slider-section', '.slider-section__header', '.newsletter-block', '.site-nav__text', '.site-header__text']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr)
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Vanity Fair Archive:
    def VanityFairArchive(self, src='Vanity Fair Archive'):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".bndwgt__headline")
        author = self.select_author(soup, selector=".bndwgt__author")
        date = self.select_date(soup, selector=".full_date")
        descr = self.select_descr(soup, selector=".bndwgt__subhead")
        vfPlus = False
        try:
            plusImg = soup.select('.user_login_nomdl')[0]
            if plusImg:
                vfPlus = True
        except:
            pass
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', '.floatedimage', 'blockquote']
        if not vfPlus:
            try:
                content_selector = 'div.bndwgt__article_body'
                (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
            except:
                content_selector = 'div.bndwgt__inline_text'
                (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        else:
            arr = [
                "Nooooo! Unfortunately, this article is only available for Vanity Fair users with a premium account. Sorry!"]
            (dct, article_data) = self.addToDictAndCreateClass(*data_arr, arr)
        return (dct, article_data)

    # Method for Tech Crunch:
    def TechCrunch(self, src="Tech Crunch"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.article__title")
        author = self.select_author(soup.find('div', {'class': 'article__byline-wrapper'}), header_selector=".article__byline", selector="a")
        words = author.split(" ")
        for word in words:
            if "@" in word:
                author = author.replace(f", {word}", "")
        date = self.select_date(soup, header_selector=".article__byline__meta", selector=".full-date-time")
        if date is None:
            parts = url.replace("//", "").split("/")
            date = "/".join(parts[1:4])
            for char in date:
                if char not in "0123456789/":
                    date = None
                    break
        descr = self.select_descr(soup, selector="#speakable-summary")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, div.heading-h2, div.heading-h3, div.heading-h4, div.heading-h5, div.heading-h6'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'blockquote + p', 'aside', '.wp-caption-text', 'p.wp-caption-text', 'div.embed', 'div.breakout']
        try:
            content_selector = 'div.content-background'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        except:
            content_selector = '.article-content'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Politico:
    def Politico(self, src="Politico"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector=".story-intro.header", selector="h1")
        if title == soup.title.text.strip():
            title = self.select_title(soup, header_selector=".summary header", selector="h1")
        if title == soup.title.text.strip():
            title = self.select_title(soup, header_selector="section", selector=".headline")
        if title == soup.title.text.strip():
            title = self.select_title(soup, header_selector=".summary", selector="header h1")
        author = self.select_author(soup, selector=".story-meta__authors")
        if author is None or len(author) < 1:
            author = self.select_author(soup, header_selector=".summary", selector="p.byline")
        if author is not None:
            author = author.title()
        date = self.select_date(soup, header_selector=".story-meta__timestamp", selector="time")
        if date is None:
            date = self.select_date(soup, header_selector="p.timestamp", selector="time")
        descr = self.select_descr(soup, selector="p.dek")
        data_arr = [source, url, title, descr, author, date]
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'header', '.cms-textAlign-center', 'div.pb-header-ad', 'div.summary', 'div.story-meta__details', 'p.story-meta__credit', '.dek', '.headline']
        # content_selector = 'div.content-background' # story-text
        keys = np.array(["newsletters", "huddle", "playbook", "playbook-pm", "politico-nightly", "transition-playbook", "corridors", "politico-china-watcher", "global-translations", "global-pulse", "the-long-game", "californiaplaybook", "floridaplaybook", "illinoisplaybook", "massachusettsplaybook", "newjerseyplaybook", "newyorkplaybook", "politicoinfluence", "2020-elections", "weekly-cybersecurity", "weekly-agriculture", "morningdefense", "women-rule", "weekly-education", "morningenergy", "morning-money", "weekly-score", "weekly-shift", "weekly-tax", "morningtech", "weekly-trade", "weekly-transportation", "politicopulse", "future-pulse", "prescriptionpulse", "politico-space"])
        for key in keys:
            if f"/{key.lower()}" in url.lower():
                selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, div.heading-h2, div.heading-h3, div.heading-h4, div.heading-h5, div.heading-h6'
                try:
                    content_selector = 'div.story-text'
                    (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
                except:
                    content_selector = 'div.story-text'
                    (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
                return (dct, article_data)

        soup = self.removeOtherGarbage(soup, *garbage_arr)
        arr = []
        blocks = soup.select('section.page-content__row.page-content__row--story') # page-content__row page-content__row--story
        for block in blocks:
            ps = block.select('p.story-text__paragraph, p, h2, h3, h4, h5, h6, ul li, ol li, div.heading-h2, div.heading-h3, div.heading-h4, div.heading-h5, div.heading-h6')
            for p in ps:
                html_p = " ".join(p.text.strip().split())
                if html_p is not None and html_p != "":
                    arr.append(html_p)
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {}
        dct['source'] = source
        dct['url'] = url
        dct['title'] = title
        dct['descr'] = descr
        dct['author'] = author
        dct['date'] = date
        dct['text'] = arr
        return (dct, article_data)

    # Method for Bellingcat:
    def Bellingcat(self, src="Bellingcat"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".singular__content__text__title h1")
        author = self.select_author(soup, header_selector=".sidebar--author", selector="span")
        date = " ".join(self.select_date(soup, selector="time.meta__time").split())
        try:
            a = self.soup.find(class_='sidebar--author')
            ps_ = a.find_all('p')
            for p in ps_:
                p.decompose()
        except:
            pass
        data_arr = [source, url, title, None, author, date]
        content_selector = '.singular__content__text__content'
        # selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, div.heading-h2, div.heading-h3, div.heading-h4, div.heading-h5, div.heading-h6, blockquote'
        # garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.cms-textAlign-center', '.wp-caption-text']
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, div.heading-h2, div.heading-h3, div.heading-h4, div.heading-h5, div.heading-h6, blockquote, div.wp-caption' # '.wp-caption-text'
        garbage_arr = [] # 'figure', 'figcaption', 'small', 'aside', '.cms-textAlign-center'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Times of Malta:
    def TheTimesofMalta(self, src="The Times of Malta"):
        (source, url, soup) = self.handle_meta(src)
        title = self.soup.title.text.strip()
        data_arr = [source, url, title, None, None, None]
        content_selector = '.ar-Article_Content'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, div.heading-h2, div.heading-h3, div.heading-h4, div.heading-h5, div.heading-h6'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.do-DonateSnippet', '.image', '.bbcode_attach', '.bbcode_attach_left', '.bbcode_attach_right']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Baltic Times:
    def TheBalticTimes(self, src="The Baltic Times"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1#tbt-main-header")
        try:
            header = self.soup.find('ul', {'class': 'blog-info'})
            uls = header.find_all('li')
            try:
                date = uls[0].text.strip()
            except:
                date = None
            try:
                author = uls[1].text.strip()
            except:
                author = None
        except:
            author = None
            date = None
        data_arr = [source, url, title, None, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, div.heading-h2, div.heading-h3, div.heading-h4, div.heading-h5, div.heading-h6'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside']
        try:
            content_selector = '.tbtarticleb'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        except:
            content_selector = '.tbt-abig'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        if len(dct['text']) < 1:
            dct['text'] = ["Nooooo! Unfortunately, this article is only available for Baltic Times users with a premium account. Sorry!"]
        return (dct, article_data)

    # Method for Time:
    def Time(self, src="Time"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.headline")
        author = self.select_author(soup, header_selector="div.author-text", selector=".author-name")
        date = self.select_date(soup, selector="div.timestamp")
        data_arr = [source, url, title, None, author, date]
        content_selector = 'div.article'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, div.heading-h2, div.heading-h3, div.heading-h4, div.heading-h5, div.heading-h6'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.ad', '.author-feedback-text', '.article-bottom', '.social-share-hed', '.most-popular-feed', '.newsletter-callout', '.newsletter-inline-signup', '.newsletter-signup-confirmation-message']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Verge:
    def TheVerge(self, src="The Verge"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.c-page-title")
        descr = self.select_descr(soup, selector=".btArticleExcerpt")
        if descr is None:
            descr = self.select_descr(soup, selector=".c-entry-summary.p-dek") # c-byline__author-name
        author = self.select_author(soup, selector=".c-byline__author-name")
        date = self.select_date(soup, selector=".c-byline time")
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.c-entry-content'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, div.heading-h2, div.heading-h3, div.heading-h4, div.heading-h5, div.heading-h6'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.c-float-right', '.c-float-left']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Conversation:
    def TheConversation(self, src="The Conversation"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.entry-title")
        if title == soup.title.text.strip():
            title = self.select_title(soup, selector="h1.instapaper_title")
        if title == soup.title.text.strip():
            title = self.select_title(soup, selector="h1.legacy")
        author = self.select_author(soup, header_selector="div.content-authors-group", selector="span.author-name")
        date = self.select_date(soup, selector="time")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside']
        soup = self.removeOtherGarbage(soup, *garbage_arr)
        arr = []
        content = soup.find('div', {'itemprop': 'articleBody'}) # page-content__row page-content__row--story
        ps = content.select(selectors)
        for p in ps:
            html_p = " ".join(p.text.strip().split())
            if html_p is not None and html_p != "":
                arr.append(html_p)
        article_data = SingleArticle(source, url, title, None, author, date, arr)
        dct = {}
        dct['source'] = source
        dct['url'] = url
        dct['title'] = title
        dct['descr'] = None
        dct['author'] = author
        dct['date'] = date
        dct['text'] = arr
        return (dct, article_data)

    # Method for Wired:
    def Wired(self, src="Wired"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.content-header__row.content-header__hed")
        author = self.select_author(soup, header_selector="div.content-header__rubric-block", selector="span.byline__name")
        date = self.select_date(soup, header_selector="div.content-header__rubric-block", selector="time.content-header__publish-date")
        if date is None:
            date = self.select_date(soup, header_selector="div.content-header__rubric-block", selector="time.content-header__title-block-publish-date")
        descr = self.select_descr(soup, selector="div.content-header__row.content-header__dek")
        data_arr = [source, url, title, descr, author, date]
        content_selector = "div.article__chunks"
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.callout', '.pullquote-embed__content', 'div + ul']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Write to him at", "This article appears in the", "Subscribe now", "is a WIRED contributor", "regular contributor to WIRED"])
        return (dct, article_data)

    # Method for La Stampa:
    def LaStampa(self, src="La Stampa"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="header.entry__header", selector="h1.entry__title", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        author = self.select_author(soup, header_selector="header.entry__header", selector="span.entry__author", arr_of_strs_to_remove=[['«', '"'], ['»', '"']]).title()
        date = self.select_date(soup, header_selector="header.entry__header", selector="span.entry__date")
        descr = self.select_descr(soup, selector=".entry__subtitle", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'div.entry__content'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'div.inline-embed']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['lazampa', 'leggi anche'])
        return (dct, article_data)

    # Method for Il Secolo XIX:
    def IlSecoloXIX(self, src="Il Secolo XIX"):
        (source, url, soup) = self.handle_meta(src)
        soup = self.removeOtherGarbage(soup, ".swiper-slide", "aside")
        title = self.select_title(soup, header_selector="header.entry_intro", selector="h1.entry_title", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        author = self.select_author(soup, selector="span.entry_author").title()
        date = self.select_date(soup, selector="span.entry_date")
        descr = self.select_descr(soup, selector=".entry_subtitle", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'div.entry_content'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'div.inline-embed']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['leggi anche'], arr_of_strs_to_remove_within_ps=[['«', '"'], ['»', '"']])
        return (dct, article_data)

    # Method for La Nuova Sardegna:
    def LaNuovaSardegna(self, src="La Nuova Sardegna"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.entry_title", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        author = self.select_author(soup, selector="span.entry_author").title()
        date = self.select_date(soup, selector="span.entry_date")
        descr = self.select_descr(soup, selector="p.entry_subtitle", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'div.entry_content'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'div.inline-embed']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['leggi anche'], arr_of_strs_to_remove_within_ps=[['«', '"'], ['»', '"']])
        return (dct, article_data)

    # Method for IL PICCOLO, GAZZETTA DI MANTOVA, GAZZETTA DI REGGIO, GAZZETTA DI MODENA, LA NUOVA VENEZIA, LA NUOVA FERRARA, LA PROVINCIA PAVESE, LA SENTINELLA DEL CANAVESE, LA TRIBUNA DI TREVISO, MESSAGGERO VENETO, IL CORRIERE DELLE ALPI, IL MATTINO DI PADOVA
    def Gelocal(self, src=None):
        if "ilpiccolo." in self.url:
            src = "Il Piccolo"
        elif "gazzettadimantova." in self.url:
            src = "Gazzetta di Mantova"
        elif "gazzettadimodena." in self.url:
            src = "Gazzetta di Modena"
        elif "gazzettadireggio." in self.url:
            src = "Gazzetta di Reggio"
        elif "nuovavenezia." in self.url:
            src = "La Nuova Venezia"
        elif "nuovaferrara." in self.url:
            src = "La Nuova Ferrara"
        elif "laprovinciapavese." in self.url:
            src = "La Provincia Pavese"
        elif "lasentinella." in self.url:
            src = "La Sentinella del Canavese"
        elif "tribunatreviso." in self.url:
            src = "La Tribuna di Treviso"
        elif "messaggeroveneto." in self.url:
            src = "Messaggero Veneto"
        elif "mattinopadova." in self.url:
            src = "Il Mattino di Padova"
        elif "corrierealpi." in self.url:
            src = "Il Corriere delle Alpi"
        else:
            src = "Gelocal"
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.entry_title", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        author = self.select_author(soup, header_selector=".entry_meta", selector="span.entry_author")
        date = self.select_date(soup, header_selector=".entry_meta", selector="span.entry_date")
        descr = self.select_descr(soup, selector=".entry_subtitle", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'div.entry_content'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'div.inline-embed']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['leggi anche'], arr_of_strs_to_remove_within_ps=[['«', '"'], ['»', '"']])
        return (dct, article_data)

    # Method for Vox:
    def Vox(self, src="Vox"):
        (source, url, soup) = self.handle_meta(src)
        soup = self.removeOtherGarbage(soup, '.c-compact-river__entry')
        title = self.select_title(soup, selector="h1.c-page-title")
        author = self.select_author(soup, selector=".c-byline__author-name")
        date = self.select_date(soup, selector="time.c-byline__item", header_selector=".l-segment")
        descr = self.select_descr(soup, selector="p.c-entry-summary.p-dek")
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'div.c-entry-content'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.c-read-more', '.c-article-footer']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["up for our newsletter here", "a post shared"], arr_of_strs_to_remove_within_ps=[['«', '"'], ['»', '"']])
        return (dct, article_data)

    # Method for Foreign Affairs:
    def ForeignAffairs(self, src="Foreign Affairs"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1")
        author = self.select_author(soup, selector=".article-header--metadata-date")
        date = self.select_date(soup, selector="h3")
        descr = self.select_descr(soup, selector=".article-header--metadata-content h2")
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.article-content-offset'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.paywall-prompt', '.article-inline-img-block--caption']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["up for our newsletter here", "a post shared"], arr_of_strs_to_remove_within_ps=[['«', '"'], ['»', '"']])
        return (dct, article_data)

    # Method for IL GIORNALE:
    def IlGiornale(self, src="Il Giornale"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.entry-title")
        author = self.select_author(soup, header_selector="div#info_articolo", selector="span.author")
        date = self.select_date(soup, header_selector="div#info_articolo", selector="span.updated.dtstamp")
        descr = self.select_descr(soup, selector=".entry-summary")
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'div#insertbox_text'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['leggi anche'], arr_of_strs_to_remove_within_ps=[['«', '"'], ['»', '"']])
        return (dct, article_data)

    # Method for IL GIORNALE BLOG:
    def IlGiornaleBlog(self, src="Il Giornale Blog"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="div.post h2")
        try:
            author = soup.title.text.strip()
            i = author.lower().index('il blog di')
            author = author[i:].replace("Il Blog di ", "").replace("Il blog di ", "")
        except:
            author = None
        try:
            date = soup.find('p', {'class': 'postmetadata alt'}).find('small').text.strip().split()
            date = " ".join(date).replace("Questo articolo è stato scritto ", "")
            i = date.index(" nella categoria")
            date = date[:i]
        except:
            date = None
        data_arr = [source, url, title, None, author, date]
        content_selector = 'div.post-content'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['leggi anche', "nella categoria", "questo articolo è stato scritto"], arr_of_strs_to_remove_within_ps=[['«', '"'], ['»', '"']])
        return (dct, article_data)

    # Method for Giornale di Sicilia:
    def GiornalediSicilia(self, src="Giornale di Sicilia"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1[itemprop='name']")
        author = self.select_author(soup, selector="span[itemprop='name']")
        date = self.select_date(soup, selector="time.entry-date")
        descr = self.select_descr(soup, selector="p.entry_subtitle")
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'div#txt_corpo_articolo'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.digital_edition_cta', '.embed_post']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['leggi anche', "© Riproduzione riservata"], arr_of_strs_to_remove_within_ps=[['«', '"'], ['»', '"']])
        return (dct, article_data)

    # Method for Libertà:
    def Liberta(self, src="Libertà"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1", header_selector="div.row.testata-articolo")
        date = self.select_date(soup, selector="p.par_data")
        data_arr = [source, url, title, None, None, date]
        content_selector = '.testo-articolo'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'footer', '.article-tags', '.art-correlato', '.article-cat']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['leggi anche', "© Riproduzione riservata", "© copyright"], arr_of_strs_to_remove_within_ps=[['«', '"'], ['»', '"']])
        return (dct, article_data)

    # Method for Zenith:
    def Zenith(self, src="Zenith"):
        (source, url, soup) = self.handle_meta(src)
        domain = urlparse(url).netloc.replace("www.", "")
        if domain == "lebanon.zenith.me":
            source = 'Lebanon Chronicles by Zenith'
        elif domain == 'libya.zenith.me':
            source = 'Libya Chronicles by Zenith'
        title = self.select_title(soup, header_selector=".group-article-header", selector="h1")
        if title is None:
            title = self.select_title(soup, header_selector=".article-top-area", selector="h1")
        if title is None:
            title = self.select_title(soup, header_selector=".header-article", selector="h1")
        author = self.select_author(soup, header_selector=".group-article-header", selector=".field-name-by")
        if author is None:
            author = self.select_author(soup, header_selector=".article-top-area", selector=".field-name-by")
        if author is None:
            author = self.select_author(soup, header_selector=".header-article", selector=".field-name-by")
        date = self.select_date(soup, header_selector=".group-article-header", selector=".field-name-post-date")
        if date is None:
            date = self.select_date(soup, header_selector=".article-top-area", selector=".field-name-post-date")
        if date is None:
            date = self.select_date(soup, header_selector=".header-article", selector=".field-name-post-date")
        descr = self.select_descr(soup, header_selector="div.article-content", selector=".field-name-summary")
        data_arr = [source, url, title, descr, author, date]
        garbage_arr = ['.field-name-summary', 'header#navbar', 'div.copyright', 'cite']
        soup = self.removeOtherGarbage(soup, *garbage_arr)
        ps = soup.select('p, .article-content h2, .article-content h3, .article-content h4')
        arr = []
        for p in ps:
            html_p = " ".join(p.text.strip().split())
            if html_p in arr:
                continue
            for item in arr:
                if html_p in item:
                    html_p = ""
            if html_p is not None and html_p != "":
                arr.append(html_p)
        (dct, article_data) = self.addToDictAndCreateClass(*data_arr, arr)
        return (dct, article_data)

    # Method for The Irish Times:
    def TheIrishTimes(self, src="The Irish Times"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="section.header", selector="h1")
        author = self.select_author(soup, header_selector="div.article-top-area", selector="div.author")
        date = self.select_date(soup, header_selector="div.article-top-area", selector="div.time-metadata time")
        descr = self.select_descr(soup, header_selector="section.header", selector="h2")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.c-read-more', '.c-article-footer', '.cta-wrapper']
        try:
            content_selector = 'div.article_bodycopy'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["up for our newsletter here", "a post shared"])
        except:
            content_selector = '.article_body'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["up for our newsletter here", "a post shared"])
            dct['text'].append("Nooooo! Unfortunately, the rest of this article is only available for Irish TImes users with a premium account. Sorry!")
        return (dct, article_data)

    # Method for Contrarian Edge:
    def ContrarianEdge(self, src="Contrarian Edge"):
        (source, url, soup) = self.handle_meta(src)
        title = self.soup.find('h1').text.strip()
        data_arr = [source, url, title, None, "Vitaliy Katsenelson", None]
        content_selector = 'div.sub-content'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'form']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["read this before you buy your next stock", "listen on: itunes | google podcasts | online", " am not a journalist or reporter; I am an investor who thinks through writing", "ew information comes our way and we continue to do research, which may lead us to", "but as luck may or may not have it, by the time you read this article we may have already sold the stock"], arr_of_strs_to_remove_within_ps=[['And one more thing…', '']])
        return (dct, article_data)

    # Method for Federation of American Scientists:
    def FederationofAmericanScientists(self, src="Federation of American Scientists"):
        (source, url, soup) = self.handle_meta(src)
        (dct, article_data) = self.FAS(soup, source, url)
        return (dct, article_data)

    # Method for Federation of American Scientists Blog:
    def FAS(self, soup, source, url):
        title = self.select_title(soup, header_selector="header", selector="h1.entry-title")
        author = self.select_author(soup, header_selector="header", selector=".author")
        descr = self.select_descr(soup, header_selector="header", selector=".btArticleExcerpt")
        try:
            date = soup.select('header.article-header')[0].text.strip().split("•")[1]
        except:
            date = None
        data_arr = [source, url, title, descr, author, date]
        garbage_arr = ['figure', 'figcaption', 'footer', 'header']
        soup = self.removeOtherGarbage(soup, *garbage_arr)
        ps = soup.select('p, h2, h3, h4, h5, h6, ul li, ol li')
        arr = []
        for p in ps:
            html_p = " ".join(p.text.strip().split())
            if html_p in arr:
                continue
            for item in arr:
                if html_p in item:
                    html_p = ""
            if html_p is not None and html_p != "":
                arr.append(html_p)
        (dct, article_data) = self.addToDictAndCreateClass(*data_arr, arr)
        return (dct, article_data)

    # Method for Asia Times:
    def AsiaTimes(self, src="Asia Times"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="header.entry-header", selector="h1.entry-title")
        author = self.select_author(soup, selector="span.author")
        date = self.select_date(soup, header_selector="header.entry-header", selector="time.entry-date.published")
        descr = self.select_descr(soup, header_selector="header.entry-header", selector=".newspack-post-subtitle")
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'div.entry-content'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'form', 'amp-layout', 'amp-animation', 'amp-analytics', 'section']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Asia Times Financial:
    def AsiaTimesFinancial(self, src="Asia Times Financial"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="header.rich-text", selector="h1")
        author = self.select_author(soup, header_selector="header.rich-text", selector="span.blog-author")
        date = self.select_date(soup, header_selector="header.rich-text", selector="span.timestamp")
        descr = self.select_descr(soup, header_selector="header.rich-text", selector="h3")
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'article'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'form', 'amp-layout', 'amp-animation', 'amp-analytics', 'section', 'p.tags']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["read more:", "photo: ", "see: "])
        return (dct, article_data)

    # Method for New York Magazine:
    def NewYorkMagazine(self, src="New York Magazine"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="header.article-header", selector="h1")
        author = self.select_author(soup, header_selector="header.article-header", selector="span[itemprop='author']")
        date = self.select_date(soup, header_selector="header.article-header", selector="time.article-timestamp")
        descr = self.select_descr(soup, header_selector="header.article-header", selector="h2")
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'div.article-content'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["this article appears in", "issue of new york magazine", "Subscribe Now!"])
        return (dct, article_data)

    # Method for Dealbreaker:
    def Dealbreaker(self, src="Dealbreaker"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector=".m-detail-header--content", selector="h1")
        author = self.select_author(soup, header_selector=".m-detail-header--content", selector=".m-detail-header--meta-author")
        date = self.select_date(soup, header_selector=".m-detail-header--content", selector=".m-detail-header--date")
        descr = self.select_descr(soup, header_selector=".m-detail-header--content", selector=".m-detail-header--dek")
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'div.m-detail--body'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["this article appears in", "issue of new york magazine", "Subscribe Now!"])
        return (dct, article_data)

    # Method for openDemocracy:
    def openDemocracy(self, src="openDemocracy"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="div.article-page__wrapper", selector="h1.article-page__title")
        author = self.select_author(soup, header_selector="div.article-page__wrapper", selector="div.article-page__authors")
        date = self.select_date(soup, header_selector="div.article-page__wrapper", selector="div.article-page__date")
        descr = self.select_descr(soup, header_selector="div.article-page__wrapper", selector="div.article-page__summary")
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'article.article-page' # article-page__rich-text
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.sidebar', '.article-page__summary']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["this article appears in", "issue of new york magazine", "Subscribe Now!"])
        return (dct, article_data)

    # Method for The Moscow Times:
    def TheMoscowTimes(self, src="The Moscow Times"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector=".article__header", selector="h1")
        author = self.select_author(soup, header_selector=".byline__details", selector=".byline__author")
        date = self.select_date(soup, header_selector=".byline__details", selector="time")
        descr = self.select_descr(soup, header_selector=".article__header", selector="h2")
        arr = []
        soup = self.removeOtherGarbage(soup, "aside")
        blocks = soup.find_all('div', {'article__block'})
        for block in blocks:
            ps = block.select('p, h2, h3, h4, h5, h6, ul li, ol li')
            for p in ps:
                html_p = " ".join(p.text.strip().split())
                if html_p is not None and html_p != "":
                    arr.append(html_p)
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {}
        dct['source'] = source
        dct['url'] = url
        dct['title'] = title
        dct['descr'] = descr
        dct['author'] = author
        dct['date'] = date
        dct['text'] = arr
        print("\n\n\n\nMETHOD FOR SITE" * 8)
        print(dct.keys())
        print()
        print(article_data.keys())
        print("\n\n\n\n")
        return (dct, article_data)

    # Method for Il Sole 24 Ore:
    def IlSole24Ore(self, src="Il Sole 24 Ore"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="div.aentry", selector="h1.atitle", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        author = self.select_author(soup, header_selector="div.aentry", selector="p.auth")
        date = self.select_date(soup, header_selector="div.aentry", selector="time.time", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        descr = self.select_descr(soup, header_selector="div.aentry", selector="h2.asummary", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        selectors = 'ul li, ol li, p.atext, div.asubtitle'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'div.ahead', '.reading-time', '.abox', '.main-header', 'section.rel', 'div.ainfo', 'div.aread', 'script', '#commentsform', '.afoot']
        soup = self.removeOtherGarbage(soup, *garbage_arr)
        arr = []
        aentries = soup.select('div.aentry')
        for aentry in aentries:
            ps = aentry.select(selectors)
            for p in ps:
                html_p = " ".join(p.text.strip().split()).replace('«', '"').replace('»', '"')
                if html_p is not None and html_p != "":
                    arr.append(html_p)
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {}
        dct['source'] = source
        dct['url'] = url
        dct['title'] = title
        dct['descr'] = descr
        dct['author'] = author
        dct['date'] = date
        dct['text'] = arr
        if "..." in dct['text'][-1][-4:]:
            dct['text'] += ["Nooooo! Unfortunately, the rest of this article is only available for Il Sole 24 Ore users with a premium account. Sorry!"]
        return (dct, article_data)

    # Method for Gazzetta di Parma:
    def GazzettadiParma(self, src="Gazzetta di Parma"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="section.art-title", selector="h2")
        date = self.select_date(soup, selector="p.data")
        data_arr = [source, url, title, None, None, date]
        content_selector = 'div.art-text'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.tag-art-list', 'div.art-text article']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["© riproduzione riservata"])
        return (dct, article_data)

    # Method for Corriere del Ticino:
    def CorrieredelTicino(self, src="Corriere del Ticino"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector=".article-header", selector="h1", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        author = self.select_author(soup, selector="span.auth")
        date = self.select_date(soup, selector="time")
        descr = self.select_descr(soup, header_selector="div.redesign-subtitle", selector=".subtitle-txt", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'div.article-text'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.categoryGroup']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        for item in dct['text']:
            if item == "Vuoi leggere di più?":
                del dct['text'][len(dct['text'])-3:len(dct['text'])]
                dct['text'].append("Nooooo! Unfortunately, the rest of this article is only available for Corriere del Ticino users with a premium account. Sorry!")
                break
        return (dct, article_data)

    # Method for Giornale di Brescia:
    def GiornalediBrescia(self, src="Giornale di Brescia"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector=".article-base-head", selector="h1", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        author = self.select_author(soup, header_selector=".btSubTitle", selector="span.auth")
        descr = self.select_descr(soup, header_selector=".article-base-head .redesign-subtitle", selector=".subtitle-txt", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        try:
            date = soup.find('date', {'class': 'date'}).text.strip()
            if "oggi" in date.lower():
                now = datetime.datetime.now()
                date = now.strftime("%Y-%m-%d")
        except:
            date = None
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'div.article-base-body'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'p.advertise', 'div.inset', '.article-service']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['riproduzione riservata ©'], arr_of_strs_to_remove_within_ps=[['»', '"'], ['«', '"']])
        return (dct, article_data)

    # Method for Il Giornale di Vicenza:
    def IlGiornalediVicenza(self, src="Il Giornale di Vicenza"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector=".div.content-heading", selector="h1", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        author = self.select_author(soup, selector="div.signature")
        date = self.select_date(soup, selector="div.content-date")
        descr = self.select_descr(soup, header_selector=".div.content-heading", selector=".summary", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'div.content-body'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'p.advertise', 'div.inset']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['riproduzione riservata ©'], arr_of_strs_to_remove_within_ps=[['»', '"'], ['«', '"']])
        return (dct, article_data)

    # Method for Ticinonews:
    def Ticinonews(self, src="Ticinonews"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="div.heading-data", selector="div.title", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        author = self.select_author(soup, header_selector="div.heading-data", selector="div.author")
        descr = self.select_descr(soup, header_selector="div.heading-data", selector="div.subtitle")
        date = self.select_date(soup, header_selector="div.heading-data", selector=".date")
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'div.text-flow-data'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['riproduzione riservata ©'], arr_of_strs_to_remove_within_ps=[['»', '"'], ['«', '"']])
        return (dct, article_data)

    # Method for Il Tirreno:
    def IlTirreno(self, src="Il Tirreno"):
        (source, url, soup) = self.handle_meta(src)
        soup = self.removeOtherGarbage(soup, 'aside')
        title = self.select_title(soup, selector="h1.entry_title", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        author = self.select_author(soup, selector="span.entry_author").title()
        date = self.select_date(soup, selector="span.entry_date")
        descr = self.select_descr(soup, selector=".entry_subtitle", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'div.entry_content'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['riproduzione riservata ©', 'leggi anche'], arr_of_strs_to_remove_within_ps=[['»', '"'], ['«', '"']])
        return (dct, article_data)

    # Method for La Nazione:
    def LaNazione(self, src="La Nazione"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="div.detail-heading", selector="h1.title", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        author = self.select_author(soup, selector="span.entry__author")
        if author is not None:
            author = author.title()
        date = self.select_date(soup, selector="div.date")
        descr = self.select_descr(soup, header_selector="div.detail-heading", selector=".subtitle", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside']
        try:
            content_selector = 'div.lp_article_content'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['© Riproduzione riservata', 'leggi anche'], arr_of_strs_to_remove_within_ps=[['»', '"'], ['«', '"']])
        except:
            content_selector = 'div.detail-text'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['© Riproduzione riservata', 'leggi anche'], arr_of_strs_to_remove_within_ps=[['»', '"'], ['«', '"']])
        return (dct, article_data)

    # Method for Quotidiano.net:
    def Quotidiano(self, src="Quotidiano.net"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="div.detail-heading", selector="h1.title", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        author = self.select_author(soup, selector="span.entry__author")
        if author is not None:
            author = author.title()
        date = self.select_date(soup, selector="div.date")
        descr = self.select_descr(soup, header_selector="div.detail-heading", selector=".subtitle", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside']
        try:
            content_selector = 'div.lp_article_content'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['© Riproduzione riservata', 'leggi anche'], arr_of_strs_to_remove_within_ps=[['»', '"'], ['«', '"']])
        except:
            content_selector = 'div.detail-text'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['© Riproduzione riservata', 'leggi anche'], arr_of_strs_to_remove_within_ps=[['»', '"'], ['«', '"']])
        return (dct, article_data)

    # Method for Il Telegrafo Livorno:
    def IlTelegrafoLivorno(self, src="Il Telegrafo Livorno"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="div.detail-heading", selector="h1.title", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        author = self.select_author(soup, selector="span.entry__author")
        if author is not None:
            author = author.title()
        date = self.select_date(soup, selector="div.date")
        descr = self.select_descr(soup, header_selector="div.detail-heading", selector=".subtitle", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside']
        try:
            content_selector = 'div.lp_article_content'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['© Riproduzione riservata', 'leggi anche'], arr_of_strs_to_remove_within_ps=[['»', '"'], ['«', '"']])
        except:
            content_selector = 'div.detail-text'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['© Riproduzione riservata', 'leggi anche'], arr_of_strs_to_remove_within_ps=[['»', '"'], ['«', '"']])
        return (dct, article_data)

    # Method for Il Resto del Carlino:
    def IlRestodelCarlino(self, src="Il Resto del Carlino"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="div.detail-heading", selector="h1.title", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        author = self.select_author(soup, selector="div.detail-author")
        if author is not None:
            author = author.title()
        date = self.select_date(soup, selector="div.date")
        descr = self.select_descr(soup, header_selector="div.detail-heading", selector=".subtitle", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        try:
            asides = soup.find_all('a', {'data-type': 'article'})
            for aside in asides:
                aside.decompose()
        except:
            pass
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h2.title-paragraph, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside']
        content_selector = 'div.main-column'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['© Riproduzione riservata', 'leggi anche'], arr_of_strs_to_remove_within_ps=[['»', '"'], ['«', '"']])
        return (dct, article_data)

    # Method for Il Giorno:
    def IlGiorno(self, src="Il Giorno"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="div.detail-heading", selector="h1.title", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        author = self.select_author(soup, selector=".detail-author")
        if author is None:
            author = self.select_author(soup, selector="span.entry__author")
        if author is not None:
            author = author.title()
        date = self.select_date(soup, selector="div.date")
        descr = self.select_descr(soup, header_selector="div.detail-heading", selector=".subtitle", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h2.title-paragraph, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside']
        try:
            content_selector = 'div.lp_article_content'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["leggi anche", "© Riproduzione riservata"])
        except:
            try:
                content_selector = 'div.article-text'
                (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["leggi anche", "© Riproduzione riservata"])
            except:
                content_selector = 'div.detail-text'
                (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["leggi anche", "© Riproduzione riservata"])
        return (dct, article_data)

    # Method for The Smithsonian Magazine:
    def TheSmithsonianMagazine(self, src="The Smithsonian Magazine"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="header.article-header", selector="h1")
        date = self.select_date(soup, selector="time.pub-date")
        descr = self.select_descr(soup, header_selector="header.article-header", selector="h2")
        try:
            authors = soup.find_all('a', {'itemprop': 'author'})
            as_ = []
            [as_.append(x.text.strip()) for x in authors if x.text.strip() not in as_]
            author = ", ".join(as_)
        except:
            author = None
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.wp-caption', '.external-associated']
        content_selector = 'div.article-body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['© Riproduzione riservata', 'leggi anche'], arr_of_strs_to_remove_within_ps=[['»', '"'], ['«', '"']])
        return (dct, article_data)

    # Method for Slate:
    def Slate(self, src="Slate"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.article__hed")
        author = self.select_author(soup, selector="div.article__byline")
        date = self.select_date(soup, selector="time.article__dateline")
        if date is not None:
            try:
                date = date.split()
                yr = date[2][0:4]
                date = date[0] + " " + date[1] + " " + yr
            except:
                pass
        descr = self.select_descr(soup, selector="h2.article__dek")
        if descr is None:
            descr = self.select_descr(soup, header_selector="div.StoryWhyCare", selector="p")
            if descr is not None:
                descr = "Why You Should Care: " + descr
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p.slate-paragraph, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.top-notes', '.social-share']
        content_selector = 'div.article__content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['© Riproduzione riservata', 'leggi anche'], arr_of_strs_to_remove_within_ps=[['»', '"'], ['«', '"']])
        return (dct, article_data)

    # Method for ProPublica:
    def ProPublica(self, src="ProPublica"):
        (source, url, soup) = self.handle_meta(src)
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.top-notes', 'footer', '.ad', '.global-promos', '.latest-stories', '.related-stories', '.post-article', 'form', '.masthead-wrapper', 'nav', '.modal', '.intro', '.license', '.endnote']
        meta_selectors = ["header.article-header", "h2.hed", "p.byline", "time.timestamp", "p.dek"]
        title = self.select_title(soup, header_selector=meta_selectors[0], selector=meta_selectors[1])
        author = self.select_author(soup, header_selector=meta_selectors[0], selector=meta_selectors[2])
        date = self.select_date(soup, selector=meta_selectors[3])
        descr = self.select_descr(soup, header_selector=meta_selectors[0], selector=meta_selectors[-1])
        garbage_arr += meta_selectors
        soup = self.removeOtherGarbage(soup, *garbage_arr)
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        arr = []
        ps = soup.select(selectors)
        for p in ps:
            html_p = " ".join(p.text.strip().split())
            if html_p is not None and html_p != "":
                arr.append(html_p)
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        arr.insert(0, "This story was originally published by ProPublica. Click 'Visit link' above to view the original article.")
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for The Jerusalem Post:
    def TheJerusalemPost(self, src="The Jerusalem Post"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.article-title")
        descr = self.select_descr(soup, selector="h2.article-subtitle")
        try:
            author = soup.find(class_='article-reporter').text.strip().split()
            for i in range(len(author)):
                author[i] = author[i].capitalize()
            author = " ".join(author)
        except:
            author = None
        try:
            date = soup.find('div', {'class': 'article-subline-name'}).text.strip().split()
            for i in range(len(date)):
                date[i] = date[i].capitalize()
            date = " ".join(date)
        except:
            date = None
        soup = self.removeOtherGarbage(soup, 'div.hide-for-premium')
        content = soup.find('div', {'class': 'article-inner-content'})
        arr = []
        text = content.text.strip()
        text = " ".join(text.split())
        arr.append(text)
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Russian International Affairs Council:
    def RussianInternationalAffairsCouncil(self, src="Russian International Affairs Council"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector='article', selector='h1')
        author = self.select_author(soup, header_selector='article', selector='div.person-list a.person__name')
        date = self.select_date(soup, selector='div.date')
        data_arr = [source, url, title, None, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside'] # span.rollover-people-block
        content_selector = 'div#detail'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        strs = ["/activity/", "/workingpapers/", "/longreads/", "/policybriefs/"]
        flag = False
        a_arr = []
        a = []
        for s in strs:
            if s in url:
                flag = True
        if flag:
            ps = soup.select(content_selector)[0].select(selectors)
            for p in ps:
                html_p = p.text.strip()
                if html_p is not None and html_p != "" and html_p not in a_arr:
                    a.append(html_p)
                dct['text'] = a + list([f"NOTE: THIS SITE OFTEN HAS LINKS TO REPORTS AND PUBLICATIONS THAT DO NOT APPEAR ON NABOO. TO VIEW THESE DOCUMENTS, VISIT THE ORIGINAL PAGE HERE: {url}"])
        return (dct, article_data)

    # Method for Foreign Policy:
    def ForeignPolicy(self, src="Foreign Policy"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector='article.article', selector='h1.hed')
        if title == soup.title.text.strip():
            title = self.select_title(soup, selector='h1.hed')
        descr = self.select_descr(soup, header_selector='article.article', selector='h2.dek-heading')
        if descr is None:
            descr = self.select_descr(soup, header_selector='article.article div.feature-header-text', selector='h2.dek-heading')
        if descr is None:
            descr = self.select_descr(soup, header_selector='figure.figure-image + div.feature-header-text', selector='h2.dek-heading')
        date = self.select_date(soup, header_selector='div.meta-data', selector='time.date-time')
        if date is None:
            date = self.select_date(soup, header_selector='article.article', selector='time.date-time')
        if date is None:
            date = self.select_date(soup, header_selector='article.article div.feature-header-text', selector='time.date-time')
        if date is None:
            date = self.select_date(soup, header_selector='figure.figure-image + div.feature-header-text', selector='time.date-time')
        # author = self.select_author(soup, header_selector='.about-quote', selector='p')
        # if author is None:
        #     author = self.select_author(soup, header_selector='article.article div.feature-header-text', selector='.author-list')
        # if author is None:
        #     author = self.select_author(soup, header_selector='figure.figure-image + div.feature-header-text', selector='.author-list')
        # if author is None:
        #     author = self.select_author(soup, header_selector='div.meta-data', selector='address.author-list .author')
        # if author is None:
        #     author = self.select_author(soup, header_selector='article.article', selector='.author-list')
        author = None
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.ds_cpp', '.social-share', '.in-article-dynamic-ad', '.fp_choose_placement_related_posts', '.pull-quote-sidebar', '.the-comments', '.the-tags', '.taboola', 'footer', 'nav', '.sidebar', 'header', '.trending-articles', '.top-ten-stories', '.department', '.hed', '.dek-heading', '.smallgray', '.media-contain about-quote', '.about-quote', '.in-article-dynamic-ad', '.fp_choose_placement_related_posts', '.pull-quote-sidebar', '.wp-caption-text', '.media-contain', '.sidebar-box_right', '.sidebar-box_left']
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr, dont_append_keys=["read more"])
        # FOR WASHINGTON POST: arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr, dont_append_keys=["read more"], breakers=["read more"])
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Washington Post:
    def WashingtonPost(self, src="Washington Post"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector='header', selector='.font--headline')
        descr = self.select_descr(soup, header_selector='article', selector='h2.dek-heading')
        date = self.select_date(soup, header_selector='article', selector='div.display-date')
        author = self.select_author(soup, header_selector='article', selector='div.author-names .author-name-link')
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'nav', '.side-nav__scroll-container', '#link-box', 'footer', '.newsletter-form', 'form', "div[data-qa='interstitial-link']", "a[data-qa='interstitial-link']"]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr, breakers=["read more"])
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Spisok Putina:
    def SpisokPutina(self, src="Spisok Putina"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector='header.entry-header', selector='h1.material__title')
        author = self.select_author(soup, header_selector='div.metadata__block', selector='div.material__source_link')
        date = self.select_date(soup, header_selector='div.metadata__block', selector='time.entry-date')
        data_arr = [source, url, title, None, author, date]
        selectors = 'p, div#adzone-outstream, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.wp-caption', '.external-associated']
        content_selector = 'div.entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['© Riproduzione riservata', 'leggi anche'], arr_of_strs_to_remove_within_ps=[['»', '"'], ['«', '"']])
        return (dct, article_data)

    # Method for DW:
    def DW(self, src="DW"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector='#bodyContent', selector='h1')
        descr = self.select_descr(soup, header_selector='#bodyContent', selector='p.intro')
        try:
            author = ""
            date = ""
            sl = soup.find('ul', {'class': 'smallList'}).find_all('li')
            for item in sl:
                if "author" in item.text.strip().lower():
                    author = " ".join(item.text.strip().lower().replace("author", "").title().split())
                if "date" in item.text.strip().lower():
                    date = " ".join(item.text.strip().lower().replace("date", "").title().split())
        except:
            author = None
            date = None
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, div#adzone-outstream, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.picBox', '.articleWidget', 'p.intro', '.col3']
        content_selector = 'div.longText'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['ead more: '])
        return (dct, article_data)

    # Method for The Intercept:
    def TheIntercept(self, src="The Intercept"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector='div.Post-title-block', selector='h1') # h1.Post-title
        if title is None:
            title = self.select_title(soup, header_selector='div.Post-header', selector='h1') # h1.Post-feature-title
        descr = self.select_descr(soup, header_selector='div.Post-title-block', selector='h2.Post-excerpt')
        if descr is None:
            descr = self.select_descr(soup, header_selector='div.Post-header', selector='h2.Post-excerpt')
        if descr is None:
            descr = self.select_descr(soup, header_selector='div.Post-title-block', selector='.Excerpt')
        if descr is None:
            descr = self.select_descr(soup, header_selector='div.Post-header', selector='.Excerpt')
        if descr is None:
            descr = self.select_descr(soup, header_selector='div.Post-title-block', selector='.Post-feature-subtitle-container')
        if descr is None:
            descr = self.select_descr(soup, header_selector='div.Post-header', selector='.Post-feature-subtitle-container')
        author = self.select_author(soup, header_selector='div.Post-title-block', selector='.PostByline-names')
        if author is None:
            author = self.select_author(soup, header_selector='div.Post-header', selector='.PostByline-names')
        date = self.select_date(soup, selector='.PostByline-date')
        garbage_arr = ['figure', 'figcaption', 'small', 'footer', 'nav', 'blockquote', 'aside', '.LatestPosts', '.RelatedPosts', '.InlineDonationPromo-container', '.caption', '.Header-TM', '.Newsletter', '.NewsletterEmbed-container', '.Post-contact', '.SiteFooter-copyrightText', '.PartnershipArticleStandard', '.Post-opinion-title-block', '.Excerpt', '.Post-excerpt']
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, div#adzone-outstream'
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr)
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for AmericanMafia.com:
    def AmericanMafia(self, src="AmericanMafia.com"):
        (source, url, soup) = self.handle_meta(src)
        title = self.soup.title.text.strip()
        authors = ["John William Tuohy", "Rick Porrello", "Clarence Walker", "J. R. de Szigethy", "James Ridgway de Szigethy", "Nick Christophers", "Julie A. Thompson", "Neil Gordon", "Mike La Sorte", "Sonny Girard", "Nino Perrotta", "Emma Stevens", "Christian Cipollini", "William Hyrb", "Allan R. May", "Peter Lance", "Ron Chepesiuk", "George Hassett", "George Anastasia", "Martin Iacampo, Sr.", "Richard Stanley Cagan", "Glen Macnow", "Tim Newark", "Arthur Nash", "Sandra Harmon", "Frank R. Hayde", "Anthony Gonzalez", "Amy A. Kisil", "Ellen Poulsen", "Cherie Rohn", "Parry Desmond", "John Bollinger", "Lou Eppolito, Jr.", "Lou Eppolito Jr.", "Gary Cohen", "Bob Siler", "James Dubro", "David Kales", "Scott M. Deitche", "Ken Prendergast", "John Tuohy", "Terry M. Mors, Ph.D.", "Gary Dimmock", "Kenneth J. Prendergast", "David Perlman", "David Foglietta", "Walter Fontane", "Wiseguy Wally", "Wayne A. Johnson"]
        a = []
        for item in authors:
            if item in self.soup.text:
                a.append(item)
        author = ", ".join(a)
        ps = soup.select('p')
        str1 = " plr internationa"
        str2 = "opyright © "
        arr = []
        for p in ps:
            html_p = " ".join(p.text.strip().replace("", "'").replace(" ", " '").split())
            if html_p in arr:
                continue
            if str1 in html_p.lower() or str2 in html_p.lower():
                continue
            if html_p is not None and html_p != "":
                arr.append(html_p)
        article_data = SingleArticle(source, url, title, None, author, None, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': None, 'author': author, 'date': None,
               'text': arr}
        return (dct, article_data)

    # Method for LIFE:
    def LIFE(self, src="LIFE"):
        (source, url, soup) = self.handle_meta(src)
        title = soup.find('header', {'class': 'entry-header'}).find('h1', {'class': 'entry-title'}).text.strip()
        data_arr = [source, url, title, None, None, None]
        selectors = 'p, div#adzone-outstream, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.picBox', '.articleWidget', 'p.intro', '.col3']
        content_selector = 'div.entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        dct['text'] += ["PLEASE NOTE THAT MOST ARTICLES FROM 'LIFE' CONTAIN PHOTOGRAPHS. RIGHT NOW, NABOO ONLY SUPPORTS TEXT. IF WE WANT, WE WILL CHANGE THIS IN THE FUTURE. BUT TO VIEW THE PHOTOS NEW, PLEASE CLICK 'Visit link' ABOVE AND GO TO THE ORIGINAL ARTICLE."]
        return (dct, article_data)

    # Method for L'Osservatore Romano:
    def LOsservatoreRomano(self, src="L'Osservatore Romano"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector='div.title', selector='h1')
        date = self.select_date(soup, header_selector='div.content', selector='div.date')
        data_arr = [source, url, title, None, None, date]
        selectors = 'p, div#adzone-outstream, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside']
        content_selector = 'div.article--body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['© Riproduzione riservata', 'leggi anche'], arr_of_strs_to_remove_within_ps=[['»', '"'], ['«', '"']])
        return (dct, article_data)

    # Method for Le Monde diplomatique:
    def LeMondediplomatique(self, src="Le Monde diplomatique"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector='div.cartouche', selector='h1')
        author = self.select_author(soup, selector='span.auteurs')
        header = soup.find('div', {'class': 'cartouche'})
        try:
            try:
                d = header.find('p', {'class': 'surtitre'}).text.strip()
            except:
                d = None
            descr = header.find('div', {'class': 'crayon'}).text.strip()
            if d is not None:
                descr = f"{d}: {descr}"
        except:
            descr = None
        try:
            date = " ".join(soup.find('div', {'class': 'fil'}).find('a', {'class': 'filin'}).text.strip().replace(">", "").split())
        except:
            date = None

        try:
            intro_pf = self.soup.find('div', {'class': 'chapodactu'}).find('p').text.strip()
            intro_p = f"[Intro Paragraph:] {intro_pf}"
        except:
            intro_p = None
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, div#adzone-outstream, h2, h3, h3.spip, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside']
        content_selector = 'div.texte'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['© Riproduzione riservata', 'leggi anche'], arr_of_strs_to_remove_within_ps=[['»', '"'], ['«', '"']])
        if intro_p is not None:
            dct['text'] = list(intro_p) + dct['text']
        return (dct, article_data)

    # Method for Süddeutsche Zeitung:
    def SuddeutscheZeitung(self, src="Süddeutsche Zeitung"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector='div.er-plate', selector='h1.er-title__headline')
        soup = self.removeOtherGarbage(soup, ".er--hidden")
        try:
            div = soup.select("div.er-plate")[0].find('div', {'class': 'er-title__content'}).select('p')
            if len(div) <= 2:
                try:
                    descr = div[0].text.strip()
                    descr = " ".join(descr.split())
                except:
                    descr = None
                try:
                    author = div[1].text.strip()
                except:
                    try:
                        author = soup.find('div', {'class': 'er-title__authors'}).find(class_="authors").text.strip()
                    except:
                        try:
                            authors = soup.find('div', {'class': 'er-crate er-crate--author'}).text.strip().replace(":", " by").split()
                            author = " ".join(authors)
                        except:
                            author = None
            else:
                descr = None
                author = None
        except:
            descr = None
            author = None
        date = self.select_date(soup, selector='time.publishdate')
        if date is not None:
            date = date.replace("- ", "")
        if date is None:
            date = self.select_date(soup, selector='div.er-crate--publishdate')
        if date is None:
            date = self.select_date(soup, selector='article header time')
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.er-title__authors', '.authors', '.er-crate--author', '.szig-sharing', 'footer', "div[data-testid='closing-line']", '.css-1gzpcil', 'nav', '.css-1wh425o', 'header', '.css-1ev38p0', '.er-plank--project']
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr)
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Il Messaggero:
    def IlMessaggero(self, src="Il Messaggero"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector='.contenuto', selector='header h1', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        author = self.select_author(soup, header_selector='.contenuto', selector='.firma', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        date = self.select_date(soup, header_selector='.contenuto', selector='.data_pub', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        descr = None
        str1 = "in un'Italia divisa in zona rossa, zona arancione e zona gialla con differenti livelli di lockdown, non va per nulla abbassata la guardia: quasi tutte le Regioni sono ancora classificate a rischio alto di una epidemia non controllata e non gestibile sul territorio o a rischio moderato con alta probabilità di progredire a rischio alto"
        selectors = 'p' # h2, h3, h4, h5, h6, ul li, ol li
        garbage_arr = ['figure', 'figcaption', 'small', '.testatabox', 'blockquote', 'aside', 'header', 'footer', 'nav', "#correlati", ".approfondimento", ".strip-autopromo", ".strip-box-newscovid", "form", ".html_base_no_foto", ".adv_banner", ".testatabox", "article.icon", ".icon", ".strip-box-correlati-tag", "#correlati-verticali", ".infinite_scroller", "article.col-xs-12", "#correlati", ".slick-list", ".body-text aside", ".body-text #correlati", "h2 a", ".testatabox h2 a"]
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr)
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Independent Balkan News Agency:
    def IndependentBalkanNewsAgency(self, src="Independent Balkan News Agency"):
        (source, url, soup) = self.handle_meta(src)
        header = soup.find('div', {'class': 'th-pagetitle afp-custom-title'})
        title = header.find('h1').text.strip()
        try:
            data = soup.find('div', {'class': 'th-pagetitle afp-custom-title'}).find('div', {'class': 'afp_postAuthor'}).text.strip()
            p = "/ Published on: "
            i = data.index(p)
            date = data[i + 16:]
            data = data.replace(p, '')
            author = data[:i]
        except:
            date = None
            author = None
        data_arr = [source, url, title, None, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside']
        content_selector = 'div.th-description'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Mainichi:
    def TheMainichi(self, src="The Mainichi"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector='#main-cont', selector='h1')
        date = self.select_date(soup, header_selector='#main-cont', selector='time')
        data_arr = [source, url, title, None, None, date]
        selectors = 'p.txt, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '#tools']
        content_selector = 'div.main-text'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The New Republic:
    def TheNewRepublic(self, src="The New Republic"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector='.article-header-grid', selector='h1')
        descr = self.select_descr(soup, header_selector='.article-header-grid', selector='h2')
        author = self.select_author(soup, header_selector='.article-header-grid', selector='.AuthorList')
        date = self.select_date(soup, header_selector='.article-header-grid', selector="time")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.article-side-ad']
        content_selector = '.article-body-wrap'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Monaco Tribune:
    def MonacoTribune(self, src="Monaco Tribune"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector='div.column.post-header', selector='h1')
        author = self.select_author(soup, selector='a.author-link')
        date = self.select_date(soup, selector=".post-date")
        data_arr = [source, url, title, None, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.article-side-ad']
        content_selector = 'div.the_content_wrapper'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['suggested article', '>> READ MORE:'])
        return (dct, article_data)

    # Method for Crux:
    def Crux(self, src="Crux"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='h1.post_title')
        author = self.select_author(soup, selector='a.author')
        date = self.select_date(soup, selector="div.date")
        data_arr = [source, url, title, None, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.crp_related', '.support-ad-bottom']
        content_selector = 'div.text'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["follow ", " on twitter:"])
        return (dct, article_data)

    # Method for L'Espresso:
    def LEspresso(self, src="L'Espresso"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="article header", selector='h1')
        descr = self.select_descr(soup, header_selector="header", selector='h2')
        if descr is None:
            descr = self.select_descr(soup, header_selector="article.main-article", selector='h2')
        author = self.select_author(soup, header_selector=".testata-autore", selector='h2')
        if author is None:
            author = self.select_author(soup, selector='div.author-container')
        date = self.select_date(soup, selector="footer time")
        if date is None:
            date = self.select_date(soup, selector="time[itemprop='datePublished']")
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'footer']
        soup = self.removeOtherGarbage(soup, *garbage_arr)
        contents = soup.find('div', {'class': 'body-text'}).text.strip().replace('«', '"').replace('»', '"').split()
        arr = [" ".join(contents)]
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for The Gentleman's Journal:
    def TheGentlemansJournal(self, src="The Gentleman's Journal"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="header.c-post__header", selector='h1.c-post__title')
        descr = self.select_descr(soup, header_selector="header.c-post__header", selector='.c-post__standfirst')
        author = self.select_author(soup, header_selector="div.c-post__container", selector='.c-by-line__item')
        data_arr = [source, url, title, descr, author, None]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.c-sponsored-by', '.c-content-builder-info-block']
        content_selector = 'div.c-post__container'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr) # , strs=["become a gentleman’s journal member. find out more here"]
        return (dct, article_data)

    # Method for AP News:
    def AP(self, src="AP News"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector=".CardHeadline", selector='h1')
        descr = self.select_descr(soup, header_selector="header.c-post__header", selector='.c-post__standfirst')
        author = self.select_author(soup, selector='.CardHeadline span')
        date = self.select_date(soup, header_selector=".CardHeadline", selector='.Timestamp')
        try:
            if date in author:
                author = author.replace(date, "").replace(",", "")
        except:
            pass
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.c-sponsored-by', '.c-content-builder-info-block']
        content_selector = '.Article'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr) # , strs=["become a gentleman’s journal member. find out more here"]
        return (dct, article_data)

    # Method for In Moscow's Shadows:
    def InMoscowsShadows(self, src="In Moscow's Shadows"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="div#c2", selector='h1.post-title')
        try:
            date = soup.select('div.post-meta')[0].text.strip()#.select('div.row')[0].text.strip().replace("by Mark Galeotti on ", "")
            i1 = date.index("by") + 2
            try:
                i2 = date.index('•')
            except:
                i2 = -1
            date = date[i1:i2].strip().replace("Mark Galeotti on", "").strip()
        except:
            date = None
        data_arr = [source, url, title, None, "Dr Mark Galeotti", date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.sharedaddy', '.sd-like-enabled', '.sd-sharing-enabled']
        content_selector = 'div.post-text'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Vatican News:
    def VaticanNews(self, src="Vatican News"):
        (source, url, soup) = self.handle_meta(src)
        soup = self.removeOtherGarbage(soup, ".social-utility")
        title = self.select_title(soup, selector='h1.article__title')
        try:
            descr = " ".join(self.soup.find('div', {'class': 'article__subTitle'}).text.strip().split())
        except:
            descr = None
        try:
            date = " ".join(soup.find('div', {'class': 'article__extra'}).text.strip().split())
        except:
            date = None
        author = None
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.social-utility']
        content_selector = 'div.article__text'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["©"])
        return (dct, article_data)

    # Method for Mafia Today:
    def MafiaToday(self, src="Mafia Today"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="div.single_post", selector='h1.title')
        if title == soup.title.text.strip():
            title = self.select_title(soup, header_selector="div.single_page", selector='h1.title')
        date = self.select_date(soup, header_selector="div.single_post", selector='.date', arr_of_strs_to_remove=[["/", ""]])
        if date is None:
            date = self.select_date(soup, header_selector="div.single_page", selector='.date', arr_of_strs_to_remove=[["/", ""]])
        author = self.select_author(soup, selector=".theauthor", arr_of_strs_to_remove=[["/", ""]])
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.wp-caption', '#header', '.breadcrumb', 'footer', 'h1.title', '.date', '.theauthor', 'title', '.bottomad', '.shareit', '.postauthor', '.post-info']
        soup = self.removeOtherGarbage(soup, *garbage_arr)
        contents = soup.text.strip().split()  # 'div', {'class': 'post-content'}
        arr = [" ".join(contents)]
        article_data = SingleArticle(source, url, title, None, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': None, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for applet-magic.com:
    def appletmagic(self, src="applet-magic.com"):
        (source, url, soup) = self.handle_meta(src)
        title = self.soup.title.text.strip()
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'center']
        soup = self.removeOtherGarbage(soup, *garbage_arr)
        text = " ".join(soup.text.strip().replace(title, "").replace("Their names are:", "").strip().split()).replace("applet-magic.com thayer watkinssilicon valley& tornado alleyusa", "")
        arr = [text]
        article_data = SingleArticle(source, url, title, None, "Thayer Watkins", None, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': None, 'author': "Thayer Watkins", 'date': None, 'text': arr}
        return (dct, article_data)

    # Method for SWI swissinfo.ch:
    def SWI(self, src="SWI swissinfo.ch"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector=".si-detail__header", selector='h1', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        descr = self.select_descr(soup, header_selector=".si-detail__content", selector='.lead-text', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        date = self.select_date(soup, header_selector=".si-detail__content", selector='time.si-detail__date', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        author = self.select_author(soup, header_selector=".si-detail__content", selector=".si-detail__author-name", arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.si-detail__translation', '.si-teaser', 'div.infobox', 'div.infobox-left', 'div.infobox-right', '.si-taxonomies', 'nav', 'ul.si-detail__translation-list', '.si-detail__migration', ".si-detail__author-profile", '.si-teaser']
        content_selector = '.si-detail__content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Rolling Stone:
    def RollingStone(self, src="Rolling Stone"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="header.l-article-header", selector='h1')
        descr = self.select_descr(soup, header_selector="header.l-article-header", selector='h2')
        date = self.select_date(soup, header_selector="header.l-article-header", selector='time')
        author = self.select_author(soup, header_selector=".c-byline__authors", selector=".c-byline__link")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.social-utility', 'section', 'aside', 'div.admz', 'p.copy', 'div.l-article-content__pull', 'div.c-related', 'div.wp-caption']
        content_selector = 'div.c-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["©"])
        return (dct, article_data)

    # Method for Longreads:
    def Longreads(self, src="Longreads"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='h1.entry-title')
        descr = self.select_descr(soup, selector='.entry-subhead')
        author = self.select_author(soup, header_selector="section.entry-content", selector='a')
        date = None
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'section', 'aside', '.admz', '.l-article-content__pull', '.c-related', '.wp-caption', '.sharedaddy', '.sponsor-double', '.entry-meta', 'footer', '.nav-off-canvas--container', '.sm-button-red']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr)
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for The Week:
    def TheWeek(self, src="The Week"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="div.article-headline", selector='h1')
        descr = None
        date = self.select_date(soup, selector='div.article-date')
        author = self.select_author(soup, header_selector="div.author", selector=".name")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'section']
        if "speedreads" in url:
            content_selector = '.sr-text'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
            return (dct, article_data)
        content_selector = 'div.zephr'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Week UK:
    def TheWeekUK(self, src="The Week UK"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector=".polaris__content", selector='h1')
        descr = self.select_descr(soup, header_selector=".polaris__content", selector='h2')
        date = self.select_date(soup, header_selector=".polaris__content", selector='.polaris__post-meta--date')
        author = self.select_author(soup, header_selector=".polaris__content", selector='.polaris__post-meta--author')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'header', 'footer', '.polaris__breadcrumb', '.polaris__image--meta', '.polaris__image--credits', '.polaris__image--wrapper', '.polaris__related-links', '.polaris__heading', '.-tags-social', '.polaris__tags', '.polaris__article-card']
        content_selector = 'body' # div.polaris__body div.polaris__content
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Standard:
    def TheStandard(self, src="The Standard"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="div.heading", selector='h1')
        author = self.select_author(soup, header_selector="div.heading", selector='span.pull-left span.writer')
        date = self.select_date(soup, header_selector="div.heading", selector='span.pull-left')
        descr = None
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'header', 'footer', '.dropdown']
        content_selector = 'div.content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Il Tempo:
    def IlTempo(self, src="Il Tempo"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="main", selector='h1', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        author = self.select_author(soup, header_selector=".article-data", selector='.author')
        if "blog" in url:
            author = self.select_author(soup, header_selector="main", selector='.author-wrapper span')
        date = self.select_date(soup, header_selector=".article-data", selector='time')
        descr = self.select_descr(soup, selector='.catenaccio', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        if descr is None:
            descr = self.select_descr(soup, selector='.briefly', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'header', 'footer', '.read-also', '.briefly', '.author-wrapper']
        content_selector = 'div.main-wrapper'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Libero Quotidiano:
    def LiberoQuotidiano(self, src="Libero Quotidiano"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="main", selector='h1', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        author = self.select_author(soup, header_selector=".article-data", selector='.author')
        if "blog" in url:
            author = self.select_author(soup, header_selector="main", selector='.author-wrapper span')
        date = self.select_date(soup, header_selector=".article-data", selector='time')
        descr = self.select_descr(soup, selector='.catenaccio', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        if descr is None:
            descr = self.select_descr(soup, selector='.briefly', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'header', 'footer', '.read-also', '.briefly', '.author-wrapper']
        content_selector = 'div.main-wrapper'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Corriere dell'Umbria:
    def CorrieredellUmbria(self, src="Corriere dell'Umbria"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="main", selector='h1', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        author = self.select_author(soup, header_selector=".article-data", selector='.author')
        if "blog" in url:
            author = self.select_author(soup, header_selector="main", selector='.author-wrapper span')
        date = self.select_date(soup, header_selector=".article-data", selector='time')
        descr = self.select_descr(soup, selector='.catenaccio', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        if descr is None:
            descr = self.select_descr(soup, selector='.briefly', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'header', 'footer', '.read-also', '.briefly', '.author-wrapper']
        content_selector = 'div.main-wrapper'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Irpinia News:
    def IrpiniaNews(self, src="Irpinia News"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="main", selector='h1', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        date = self.select_date(soup, header_selector=".article-header", selector='span')
        data_arr = [source, url, title, None, None, date]
        selectors = 'p, h2, h3, h4, h5, h6'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'header', 'footer', '.read-also', '.briefly', '.author-wrapper']
        content_selector = 'div.article-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for L'Unione Sarda:
    def LUnioneSarda(self, src="L'Unione Sarda"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="div.post-heading", selector='h1', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        descr = self.select_descr(soup, header_selector="div.post-heading", selector='h6', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        date = self.select_date(soup, header_selector="header.post-header", selector='time.date-str')
        author = self.select_author(soup, selector='div.author')
        data_arr = [source, url, title, descr, author, date]
        # selectors = 'p, h2, h3, h4, h5, h6'
        selectors = "p[itemprop='articleBody']"
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'header', 'footer', '.read-also', '.briefly', '.author-wrapper']
        content_selector = '.post'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Asahi Shimbun:
    def TheAsahiShimbun(self, src="The Asahi Shimbun"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="div#MainInner", selector='div.Title h1', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        descr = self.select_descr(soup, header_selector="div#MainInner", selector='h2', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        date = self.select_date(soup, selector='p.EnLastUpdated')
        author = self.select_author(soup, selector='p.EnArticleName')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'header', 'footer', '.read-also', '.briefly', '.author-wrapper']
        content_selector = 'div.ArticleText'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for New Statesman:
    def NewStatesman(self, src="New Statesman"):
        (source, url, soup) = self.handle_meta(src)
        soup = self.removeOtherGarbage(soup, ['.author-twitter', '.twitter-button'])
        title = self.select_title(soup, header_selector=".article-header", selector='h1.title', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        descr = self.select_descr(soup, header_selector=".article-header", selector='.field-name-field-subheadline', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        date = self.select_date(soup, header_selector=".article-header", selector='.article-date')
        author = self.select_author(soup, selector='.author-byline')
        selectors = 'p' # , h2, h3, h4, h5, h6
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'header', 'footer', '.read-also', '.briefly', '.author-wrapper', '.modal-content', '.cookie-compliance', '.ns-form-item']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr)
        arr = [arr[0]]
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Il Gazzettino:
    def IlGazzettino(self, src="Il Gazzettino"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector=".contenuto", selector='h1', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        descr = None
        date = self.select_date(soup, header_selector=".contenuto", selector='span.data_pub')
        author = self.select_author(soup, header_selector=".contenuto", selector='.firma')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', '.embedly-card', '.testatabox', 'aside', 'header', 'footer', 'nav', '.inread_adv', '.newsDetailPage', '.prezzo', '.html_base_no_foto', '.ml_primary_link']
        content_selector = '#main-content'     #a.link_item
        str1 = 'leggi anche'
        str2 = "in un'Italia divisa in zona rossa, zona arancione e zona gialla con differenti livelli di lockdown, non va per nulla abbassata la guardia: quasi tutte le Regioni sono ancora classificate a rischio alto di una epidemia non controllata e non gestibile sul territorio o a rischio moderato con alta probabilità di progredire a rischio alto"
        str3 = "Covid-19 non colpisce soltanto i polmoni. Dopo aver contratto il contagio ed essere guarita, una persona su venti evidenzia conseguenze più o meno transitorie a danno del cervello. Si chiama nebbia cognitiva e provoca vuoti di memoria, spaesamento, incapacità di svolgere azioni"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=[str1,str2,str3], arr_of_strs_to_remove_within_ps=[['«', '"'], ['»', '"']])
        return (dct, article_data)

    # Method for Il Mattino:
    def IlMattino(self, src="Il Mattino"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector=".contenuto", selector='h1', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        descr = None
        date = self.select_date(soup, header_selector=".contenuto", selector='span.data_pub')
        author = self.select_author(soup, header_selector=".contenuto", selector='.firma')
        selectors = 'p'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', '.embedly-card', '.testatabox', 'aside', 'header', 'footer', 'nav', '.inread_adv', '.newsDetailPage', '.prezzo', '.html_base_no_foto', '.ml_primary_link', '#right-rail', '.slick-list', '#correlati', '.slick-slide', '.approfondimento', '.slick-cloned', '.link_snippet_small', '.snippet_titolo', '.content_moreinfo', '.item_content', '.col-xs-9', '.textitem']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr)
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date,
               'text': arr}
        return (dct, article_data)

    # Method for El País:
    def ElPais(self, src="El País"):
        if "/america/" in self.url:
            src = "El País Edición América"
        if "/mexico/" in self.url:
            src = "El País Edición México"
        if "brasil.elpais.com" in self.url:
            src = "Edição Brasil no El País"
        if "english.elpais.com" in self.url:
            src = "El País in English"
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="#article_header", selector='h1', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        if title == soup.title.text.strip():
            title = self.select_title(soup, header_selector=".articulo-encabezado", selector='h1', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        descr = self.select_descr(soup, header_selector="#article_header", selector='h2', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        if descr is None:
            descr = self.select_descr(soup, header_selector=".articulo-encabezado", selector='h2', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        date = self.select_date(soup, header_selector=".articulo-apertura", selector='.a_ti')
        if date is None:
            date = self.select_date(soup, header_selector=".articulo-apertura", selector='.articulo-actualizado')
        if date is None:
            date = self.select_date(soup, selector='.a_ti')
        author = self.select_author(soup, header_selector=".articulo-apertura", selector='a.a_aut_n')
        if author is None:
            author = self.select_author(soup, header_selector=".articulo-apertura", selector='.autor-nombre')
        if author is None:
            author = self.select_author(soup, selector='.a_aut')
        if author is None:
            author = self.select_author(soup, selector='.a_aut_n')
        if author is None:
            author = self.select_author(soup, selector='.a_pl')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'section']
        try:
            content_selector = '.articulo-cuerpo'  # articulo-cuerpo
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, arr_of_strs_to_remove_within_ps=[['«', '"'], ['»', '"']])
        except:
            content_selector = '.article_body'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, arr_of_strs_to_remove_within_ps=[['«', '"'], ['»', '"']])
        return (dct, article_data)

    # Method for El País.cat:
    def ElPaiscat(self, src="El País.cat"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="#article_header", selector='h1', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        if title == soup.title.text.strip():
            title = self.select_title(soup, header_selector=".articulo-encabezado", selector='h1', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        descr = self.select_descr(soup, header_selector="#article_header", selector='h2', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        if descr is None:
            descr = self.select_descr(soup, header_selector=".articulo-encabezado", selector='h2', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        date = self.select_date(soup, header_selector=".articulo-apertura", selector='.a_ti')
        if date is None:
            date = self.select_date(soup, header_selector=".articulo-apertura", selector='.articulo-actualizado')
        if date is None:
            date = self.select_date(soup, selector='.a_ti')
        author = self.select_author(soup, header_selector=".articulo-apertura", selector='a.a_aut_n')
        if author is None or len(author) < 3:
            author = self.select_author(soup, header_selector=".articulo-apertura", selector='.autor-nombre')
        if author is None or len(author) < 3:
            author = self.select_author(soup, selector='.autor')
        if author is None or len(author) < 3:
            author = self.select_author(soup, selector='.a_aut')
        if author is None or len(author) < 3:
            author = self.select_author(soup, selector='.a_aut_n')
        if author is None or len(author) < 3:
            author = self.select_author(soup, selector='.a_pl')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'section', '#elpais_gpt-INTEXT']
        try:
            content_selector = '.articulo-cuerpo'  # articulo-cuerpo
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, arr_of_strs_to_remove_within_ps=[['«', '"'], ['»', '"']])
        except:
            content_selector = '.article_body'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, arr_of_strs_to_remove_within_ps=[['«', '"'], ['»', '"']])
        return (dct, article_data)

    # Method for OCCRP:
    def OCCRP(self, src="OCCRP"):
        ##### NOTE: THIS DOES NOT INCLUDE THE INFOBOXES AND INSET BOXES FOR OCCRP INVESTIGATIONS.
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="article.single", selector='h1')
        if title == soup.title.text.strip():
            title = self.select_title(soup, selector='div.title')
        author = self.select_author(soup, header_selector="article.single", selector='.authors')
        if author is None:
            author = self.select_author(soup, header_selector="div.occrp-story", selector='.by')
        if author is None:
            author = self.select_author(soup, header_selector="div.occrp-page", selector='.by')
        date = self.select_date(soup, header_selector="article.single", selector='.date')
        if date is None:
            date = self.select_date(soup, header_selector="div.occrp-story", selector='.date')
        if date is None:
            date = self.select_date(soup, header_selector="div.occrp-page", selector='.date')
        descr = None
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'section', '.wf_caption', '.related-stories-secondary', '.occrp-shelf-half', '.title', '.occrp-teaser-box', 'aside', '.image-caption', '.occrp-inset-box', '.inset-caption', '.inset-image']
        try:
            content_selector = 'div.content'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        except:
            content_selector = 'div.occrp-page'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Al Jazeera:
    def AlJazeera(self, src="Al Jazeera"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector=".article-header", selector='h1')
        descr = self.select_descr(soup, header_selector=".article-header", selector='.article__subhead')
        date = self.select_date(soup, header_selector=".article-dates", selector='.date-simple')
        author = self.select_author(soup, header_selector=".article-author__info", selector='.article-author__name')
        if author is None:
            author = self.select_author(soup, selector='.article-author-name')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'section', 'aside']
        content_selector = '.wysiwyg--all-content' # .wysiwyg
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["tips page"])
        return (dct, article_data)

    # Method for Vice:
    def Vice(self, src="Vice"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.smart-header__hed')
        descr = self.select_descr(soup, selector='.article__header__dek')
        date = self.select_date(soup, selector='.article__header__datebar__date--original')
        try:
            authors_arr = []
            author_meta = soup.find(class_='contributors')
            origins = author_meta.find_all(class_='contributor__meta__origin')
            for a in origins:
                a.decompose()
            authors = author_meta.find_all(class_='contributor__meta')
            for a in authors:
                authors_arr.append(a.text.strip())
            author = ", ".join(authors_arr).replace('  ', ' ')
        except:
            author = None
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'section', 'aside', '.user-newsletter__terms', '.body-image__caption', 'nav', 'footer', '.article__socialize', '.user-newsletter-signup', '.vice-card', '.abc__article_embed']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr)
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Avvenire:
    def Avvenire(self, src="Avvenire"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="div#page-content", selector='h1', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        descr = self.select_descr(soup, header_selector="div#page-content", selector='div.page_abstract', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        author = self.select_author(soup, header_selector="div#page-content", selector='.author')
        date = self.select_date(soup, header_selector="div#page-content", selector='.navBar-today')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, .numeri-e-sommario'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'section', 'aside', '.topicsBar', "p[itemprop='description']", '.articleImage', '.didascalia']
        content_selector = 'div#page-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, arr_of_strs_to_remove_within_ps=[['«', '"'], ['»', '"']], strs=['leggi anche'])
        return (dct, article_data)

    # Method for Il Fatto Quotidiano:
    def IlFattoQuotidiano(self, src="Il Fatto Quotidiano"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='h1.title-article', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        descr = self.select_descr(soup, selector='.catenaccio', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        author = self.select_author(soup, header_selector="div.wrapper-info-article", selector='cite')
        date = self.select_date(soup, header_selector="div.wrapper-info-article", selector='.date')
        if date is not None:
            if "|" in date:
                date = date.replace("| ", "").strip()
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, .numeri-e-sommario'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'section', 'aside']
        content_selector = '.article-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, arr_of_strs_to_remove_within_ps=[['«', '"'], ['»', '"']], strs=['leggi anche'])
        return (dct, article_data)

    # Method for Wall Street Italia:
    def WallStreetItalia(self, src="Wall Street Italia"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="#article", selector='.article__title h1', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        descr = None
        try:
            span = self.soup.find('span', {'class': 'info'}).text.strip()
            i = span.index(" di ")
            author = span[i:].replace(" di ", "").strip()
            date = span[:i].replace(",", "")
        except:
            date = None
            author = None
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, .numeri-e-sommario'
        garbage_arr = ['figure', 'figcaption', 'small', 'section', 'aside', '.partial-newsletter', '.social-btn', '.moreread', '.ainfo']
        content_selector = 'div.article__content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, arr_of_strs_to_remove_within_ps=[['«', '"'], ['»', '"']], strs=['leggi anche'])
        return (dct, article_data)

    # Method for Il Giornale d'Italia:
    def IlGiornaledItalia(self, src="Il Giornale d'Italia"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector=".entry-header", selector='h1', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        if title == soup.title.text.strip():
            title = self.select_title(soup, selector='.titolo_articolo', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        descr = self.select_descr(soup, header_selector=".entry-header", selector='h2', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        if descr is None:
            descr = self.select_descr(soup, selector='.sottotitolo_articolo', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        author = self.select_author(soup, selector='.detail-author')
        date = self.select_date(soup, header_selector=".entry-header", selector='.jeg_meta_date')
        if date is None:
            date = self.select_date(soup, selector='.data', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, .numeri-e-sommario'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'section', 'aside', '.footer-holder', '.jeg_ad', '.jnews_prev_next_container', '.jeg_prevnext_post', '.jnews_related_post_container', '.jnews_popup_post_container', '.jnews_comment_container', '.jeg_sidebar', '.copyright', '.jeg_breadcrumbs', '#jeg_off_canvas']
        a = [['«', '"'], ['»', '"']]
        strs = ['leggi anche', 'riproduzione riservata ©']
        try:
            content_selector = 'div.testo_articolo'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, arr_of_strs_to_remove_within_ps=a, strs=strs)
        except:
            content_selector = 'div.content-inner'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, arr_of_strs_to_remove_within_ps=a, strs=strs)
        if "/news/" not in url:
            dct['text'] = ["This is NOT a news article!"]
        return (dct, article_data)

    # Method for Esquire:
    def Esquire(self, src="Esquire"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="div.content-header-inner", selector='h1.content-hed')
        if title == soup.title.text.strip():
            title = self.select_title(soup, header_selector="div.longform-header-inner", selector='h1')
        descr = self.select_descr(soup, header_selector="div.content-header-inner", selector='.content-dek')
        if descr is None:
            descr = self.select_descr(soup, header_selector="div.longform-header-inner", selector='.longform-dek')
        author = self.select_author(soup, header_selector="div.content-info-metadata", selector='div.byline')
        date = self.select_date(soup, header_selector="div.content-info-metadata", selector='time')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, blockquote'
        garbage_arr = ['figure', 'figcaption', 'small', 'section', 'aside', '.embed', '.screen-reader-only', '.authors', '.content-lede-image-wrap', '.body-btn-link']
        data_arr = [source, url, title, descr, author, date]
        strs = ["like this article? sign up to our newsletter", "need some positivity right now", "subscribe to esquire"]
        try:
            content_selector = 'div.standard-body'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=strs)
        except:
            try:
                content_selector = 'div.article-body'
                (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=strs)
            except:
                selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, blockquote, .listicle-slide-hed-text'
                content_selector = 'div.content-container'
                (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=strs)
        return (dct, article_data)

    # Method for CEE Bankwatch Network:
    def CEEBankwatchNetwork(self, src="CEE Bankwatch Network"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="main.content", selector='h1')
        if title == soup.title.text.strip():
            title = self.select_title(soup, header_selector=".entry-content", selector='h1')
        descr = self.select_descr(soup, header_selector="div.entry-content", selector='.teaser')
        if descr is None:
            descr = self.select_descr(soup, selector='.teaser')
        header = self.soup.find('div', {'class': 'wpb_wrapper'})
        try:
            sec = header.select('h4 + p')[0].text.strip()
            i = sec.index('|')
            author = sec[:i].replace('|', "").strip()
            date = sec[i:].replace('|', "").strip()
        except:
            date = None
            author = None
        if "/press_release/" in url:
            author = "CEE Bankwatch Network"
        if date is None:
            date = self.select_date(soup, selector='h4.teaser + p')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, .numeri-e-sommario'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'section', 'aside', '.wp-caption', 'div.external-associated', 'div.wp-block-group', 'header.site-header', 'div.footer-widgets', '.small-text', 'ul.genesis-skip-link', 'div.pea_cook_wrapper', '.teaser', '.pea_cook_more_info_popover']
        if "/blog/" in url or "/press_release/" in url:
            content_selector = 'div.blog-post-body'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        else:
            arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr, dont_append_keys=["enjoyed this story?"])
            article_data = SingleArticle(source, url, title, descr, author, date, arr)
            dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Ozy:
    def Ozy(self, src="Ozy"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="div.StoryTplImgHead-title", selector='h1')
        if title == soup.title.text.strip():
            title = self.select_title(soup, header_selector=".StoryPage", selector='h1')
        descr = self.select_descr(soup, header_selector="div.StoryWhyCare", selector='p')
        if descr is not None:
            descr = "Why You Should Care: " + descr
        try:
            ff = soup.find('div', {'class': 'StoryContent'}).find('div', {'class': 'factfile'}).text.strip()#.find('ul').find_all('li')
        except:
            ff = None
        if ff is not None and descr is not None:
            descr = ff + ' . . . ' + descr
        author = self.select_author(soup, selector='div.StoryByAuthor')
        date = self.select_date(soup, selector='time.StoryDate')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'section', 'aside', '.inline_image', '.factfile', '.NewsletterPreviewListStyled__NewsletterPreviewListItemsStyled-rqcavt-5', '.email-footer', '.Footer']
        if "/newsletter/" in url:
            arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr)
            article_data = SingleArticle(source, url, title, descr, author, date, arr)
            dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
            return (dct, article_data)
        content_selector = 'div.StoryContent'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for La Regione:
    def LaRegione(self, src="La Regione"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="div.section.article.clearfix", selector='h1', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        date = self.select_date(soup, header_selector="div.section.article.clearfix", selector='.lh-r')
        try:
            descrs = soup.find('div', {'class': 'section article clearfix'}).find_all('h2')
            ds = []
            for d in descrs:
                ds.append(d.text.strip().replace('«', '"').replace('»', '"'))
            descr = " ".join(ds)
            for item in descrs:
                item.decompose()
        except:
            descr = None

        soup = self.removeOtherGarbage(soup, *["span.author_smaller_text"])

        author = self.select_author(soup, selector='.authors')
        if author is None:
            author = self.select_author(soup, header_selector="div.section.article.clearfix", selector='div.authors .author')

        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, .numeri-e-sommario'
        garbage_arr = ['figure', 'figcaption', 'small', 'section', 'aside', '.right-box']
        content_selector = 'div.rcontent'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, arr_of_strs_to_remove_within_ps=[['«', '"'], ['»', '"']], strs=['leggi anche'])
        return (dct, article_data)

    # Method for Ticinonline:
    def Ticinonline(self, src="Ticinonline"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="div.section.article.clearfix", selector='h1', arr_of_strs_to_remove=[['«', '"'], ['»', '"']])
        date = self.select_date(soup, header_selector="div.section.article.clearfix", selector='.lh-r')
        try:
            descrs = soup.find('div', {'class': 'section article clearfix'}).find_all('h2')
            ds = []
            for d in descrs:
                ds.append(d.text.strip().replace('«', '"').replace('»', '"'))
            descr = " ".join(ds)
            for item in descrs:
                item.decompose()
        except:
            descr = None

        soup = self.removeOtherGarbage(soup, *["span.author_smaller_text"])

        author = self.select_author(soup, selector='.authors')
        if author is None:
            author = self.select_author(soup, header_selector="div.section.article.clearfix", selector='div.authors .author')

        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, .numeri-e-sommario'
        garbage_arr = ['figure', 'figcaption', 'small', 'section', 'aside', '.right-box']
        content_selector = 'div.rcontent'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, arr_of_strs_to_remove_within_ps=[['«', '"'], ['»', '"']], strs=['leggi anche'])
        return (dct, article_data)

    # Method for Institute of Modern Russia:
    def InstituteofModernRussia(self, src="Institute of Modern Russia"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h2[itemprop='name']")
        date = self.select_date(soup, selector="time[itemprop='datePublished']") # article-info createdby-info muted
        author = self.select_author(soup, selector=".createdby")
        descr = self.select_descr(soup, selector=".page-header h3")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, .numeri-e-sommario'
        garbage_arr = ['figure', 'figcaption', 'small', 'section', 'aside', '.partial-newsletter', '.caption']
        content_selector = "div[itemprop='articleBody']"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, arr_of_strs_to_remove_within_ps=[['«', '"'], ['»', '"']], strs=['leggi anche'])
        return (dct, article_data)

    def carngie_external_link(self, soup, dct):
        extLink = None
        try:
            checkBtn = self.soup.find('a', {'class': 'button-big'}) #h5 bigButton large register
            btnTxt = checkBtn.text.strip()
            if "read the full text" in btnTxt.lower() or "read full text" in btnTxt.lower():
                extLink = "EXTERNAL LINK: " + checkBtn['href']
        except:
            extLink = None
        if extLink is None:
            try:
                checkBtn = self.soup.find('h5', {'class': 'bigButton'}).find('a')
                btnTxt = checkBtn.text.strip()
                if "read the full text" in btnTxt.lower() or "read full text" in btnTxt.lower():
                    extLink = "EXTERNAL LINK: " + checkBtn['href']
            except:
                extLink = None
        if extLink is not None:
            dct['text']  += [extLink]
        return dct["text"]

    # Method for CARNEGIE MOSCOW CENTER, CARNEGIE ENDOWMENT FOR INTERNATIONAL PEACE, CARNEGIE INDIA:
    def CarnegieEndowment(self, src="Carnegie Endowment for International Peace"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="div.container-title", selector='h1')
        if title == soup.title.text.strip():
            title = self.select_title(soup, header_selector="div.section.center", selector='h1')
        author = self.select_author(soup, selector='.post-author')
        date = self.select_date(soup, selector='.post-date li')
        descr = self.select_descr(soup, selector='div.zone-title__summary')
        if descr is None:
            descr = self.select_descr(soup, selector='div.largest-text')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, .numeri-e-sommario'
        garbage_arr = ['figure', 'figcaption', 'small', 'section', 'aside', '.partial-newsletter', '.social-btn', '.moreread', '.ainfo', '.wp-caption', '.external-associated', '.photo-caption', '.gutter-bottom', '.related-content__inline', '.related-pubs', '.author-box']
        content_selector = 'div.article-body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        dct['text'] = self.carngie_external_link(soup, dct)
        return (dct, article_data)

    # Method for Carnegie Moscow Center:
    def CarnegieMoscowCenter(self, src="Carnegie Moscow Center"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="div.container-title", selector='h1')
        if title == soup.title.text.strip():
            title = self.select_title(soup, header_selector="div.section.center", selector='h1')
        author = self.select_author(soup, selector='div.avatar + div.overflow-hidden')
        if author is None:
            author = self.select_author(soup, selector='.post-author')
        date = self.select_date(soup, selector='.post-date li')
        descr = self.select_descr(soup, selector='div.zone-title__summary')
        if descr is None:
            descr = self.select_descr(soup, selector='em.large-text')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, .numeri-e-sommario'
        garbage_arr = ['figure', 'figcaption', 'small', 'section', 'aside', '.partial-newsletter', '.social-btn', '.moreread', '.ainfo', '.wp-caption', '.external-associated', '.photo-caption', '.gutter-bottom', '.related-content__inline', '.related-pubs', '.author-box']
        content_selector = 'div.article-body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        dct['text'] = self.carngie_external_link(soup, dct)
        return (dct, article_data)

    # Method for Carnegie India
    def CarnegieIndia(self, src="Carnegie India"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="div.container-title", selector='h1')
        if title == soup.title.text.strip():
            title = self.select_title(soup, header_selector="div.section.center", selector='h1')
        author = self.select_author(soup, selector='.post-author')
        date = self.select_date(soup, selector='.post-date li')
        descr = self.select_descr(soup, selector='div.zone-title__summary')
        if descr is None:
            descr = self.select_descr(soup, selector='div.largest-text')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, .numeri-e-sommario'
        garbage_arr = ['figure', 'figcaption', 'small', 'section', 'aside', '.partial-newsletter', '.social-btn', '.moreread', '.ainfo', '.wp-caption', '.external-associated', '.photo-caption', '.gutter-bottom', '.related-content__inline', '.related-pubs', '.author-box']
        content_selector = 'div.article-body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        dct['text'] = self.carngie_external_link(soup, dct)
        return (dct, article_data)

    # Method for "Carnegie-Tsinghua Center for Global Policy":
    def CarnegieTsinghua(self, src='Carnegie-Tsinghua Center for Global Policy'):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="div.container-title", selector='h1')
        if title == soup.title.text.strip():
            title = self.select_title(soup, header_selector="div.section.center", selector='h1')
        author = self.select_author(soup, selector='.post-author')
        date = self.select_date(soup, selector='.post-date li')
        descr = self.select_descr(soup, selector='div.zone-title__summary')
        if descr is None:
            descr = self.select_descr(soup, selector='div.largest-text')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, .numeri-e-sommario'
        garbage_arr = ['figure', 'figcaption', 'small', 'section', 'aside', '.partial-newsletter', '.social-btn', '.moreread', '.ainfo', '.wp-caption', '.external-associated', '.photo-caption', '.gutter-bottom', '.related-content__inline', '.related-pubs', '.author-box']
        content_selector = 'div.article-body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        dct['text'] = self.carngie_external_link(soup, dct)
        return (dct, article_data)

    # Method for Malcolm H. Kerr Carnegie Middle East Center
    def CarnegieMiddleEast(self, src="Malcolm H. Kerr Carnegie Middle East Center"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="div.container-title", selector='h1')
        if title == soup.title.text.strip():
            title = self.select_title(soup, header_selector="div.section.center", selector='h1')
        author = self.select_author(soup, selector='.post-author')
        if author is None or len(author) < 2:
            author = self.select_author(soup, selector='div.large-text')
        date = self.select_date(soup, selector='.post-date li')
        descr = self.select_descr(soup, selector='div.zone-title__summary')
        if descr is None:
            descr = self.select_descr(soup, selector='div.largest-text')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'section', 'aside', '.partial-newsletter', '.social-btn', '.moreread', '.ainfo', '.wp-caption', '.external-associated', '.photo-caption', '.gutter-bottom', '.related-content__inline', '.related-pubs', '.author-box']
        content_selector = 'div.article-body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        dct['text'] = self.carngie_external_link(soup, dct)
        return (dct, article_data)

    # Method for Carnegie Europe:
    def CarnegieEurope(self, src="Carnegie Europe"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="div.container-title", selector='h1')
        if title == soup.title.text.strip():
            title = self.select_title(soup, header_selector="div.section.center", selector='h1')
        author = self.select_author(soup, selector='.post-author')
        if author is None or len(author) < 2:
            author = self.select_author(soup, selector='div.large-text')
        date = self.select_date(soup, selector='.post-date li')
        descr = self.select_descr(soup, selector='div.zone-title__summary')
        if descr is None:
            descr = self.select_descr(soup, selector='div.largest-text')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'section', 'aside', '.partial-newsletter', '.social-btn', '.moreread', '.ainfo', '.wp-caption', '.external-associated', '.photo-caption', '.gutter-bottom', '.related-content__inline', '.related-pubs', '.author-box']
        content_selector = 'div.article-body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        dct['text'] = self.carngie_external_link(soup, dct)
        return (dct, article_data)

    # Method for Carnegie Council:
    def CarnegieCouncil(self, src="Carnegie Council"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="div.header-row", selector='h1')
        author = self.select_author(soup, selector="a[itemprop='author']")
        date = self.select_date(soup, selector='.date')
        descr = self.select_descr(soup, header_selector="div.header-row", selector='h2')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'section', 'aside', '.article-image']
        content_selector = 'div.content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Read MoreRead Less"])
        dct['text'] = self.carngie_external_link(soup, dct)
        return (dct, article_data)

    # Method for Insider:
    def Insider(self, src="Insider"):
        if "markets.businessinsider.com" in self.url:
            src = "Markets Insider"
        if "businessinsider.com" in self.url:
            src = "Business Insider"
        if "insider.com" in self.url:
            src = "Insider"
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='h1.post-headline')
        if title == soup.title.text.strip():
            title = self.select_title(soup, selector='h1.article-title')
        author = self.select_author(soup, selector="div.byline-author")
        if author is None or len(author) < 2:
            author = self.select_author(soup, selector=".news-post-source a")
        date = self.select_date(soup, selector='div.byline-timestamp')
        if date is None:
            date = self.select_date(soup, selector='.news-post-quotetime')
        descr = self.select_descr(soup, selector='ul.summary-list')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, h2.slide-title-text'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.copy-promo-drawer', '.category-tagline', 'header', 'nav', 'footer', '.image-source', '.headline-regular', '.arrow-title-wrapper', '.box', '.box-headline', '.share-post-button', '.read-more-links']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr, dont_append_keys=["SEE ALSO:", "NOW WATCH:", "READ MORE:", "ubscriber account active sinc", "leading-edge research firm focused on digital transformatio", "isit business insider's homepage for more storie", "DON'T MISS"])
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for ANSA:
    def ANSA(self, src="ANSA"):
        if "/europa/" in self.url:
            src = "ANSA Europa"
        if "/english/" in self.url:
            src = "ANSA English"
        if "/nuova_europa/" in self.url:
            src = "ANSA Nuova Europa"
        if "ansamed.info" in self.url:
            src = "ANSAmed"
        (source, url, soup) = self.handle_meta(src) # .header-content
        title = self.select_title(soup, header_selector=".header-news", selector='h1')
        if title == soup.title.text.strip():
            title = self.select_title(soup, header_selector=".header-content", selector='h1')
        descr = self.select_descr(soup, header_selector=".header-news", selector='h2')
        if descr is None:
            descr = self.select_descr(soup, header_selector=".header-content", selector='h2')
        author = self.select_author(soup, selector='.news-author')
        date = self.select_date(soup, header_selector="div.news-time", selector='time strong')
        if date is None:
            date = self.select_date(soup, header_selector="div.news-date", selector='time strong')
        if date is None:
            date = self.select_date(soup, header_selector="div.news-time", selector='time em')
        if date is None:
            date = self.select_date(soup, header_selector="div.news-date", selector='time em')
        if date is None:
            date = self.select_date(soup, header_selector=".header-content", selector='span.date')

        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'footer', '.press-releases', '.adv-static']
        data_arr = [source, url, title, descr, author, date]
        try:
            content_selector = "div[itemprop='articleBody']"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
            if len(dct['text']) == 0:
                dct['text'] = [soup.select(content_selector)[0].text.strip()]
        except:
            content_selector = "body"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
            dct['text'] = [soup.select('#content-corpo')[0].text.strip()]
        return (dct, article_data)

    # Method for ANSA Latina:
    def ANSALatina(self, src="ANSA Latina"):
        (source, url, soup) = self.handle_meta(src) # .header-content
        title = self.select_title(soup, selector='h1')
        descr = self.select_descr(soup, selector='h2')
        author = self.select_author(soup, selector='.news-info')
        date = self.select_date(soup, header_selector=".news-info", selector='span')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'footer', '.press-releases', '.adv-static']
        data_arr = [source, url, title, descr, author, date]
        content_selector = "div.news-txt"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["© Copyright ANSA"])
        if len(dct['text']) == 0:
            dct['text'] = [soup.select(content_selector)[0].text.strip()]
        return (dct, article_data)

    # Method for La Repubblica:
    def LaRepubblica(self, src="La Repubblica"):
        (source, url, soup) = self.handle_meta(src)  # .header-content
        title = self.select_title(soup, selector='title')
        descr = self.select_descr(soup, selector='.story__summary')
        author = self.select_author(soup, selector='.story__author')
        date = self.select_date(soup, header_selector=".story__toolbar", selector='time') # time.story__date
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'footer', '.inline-article', '.inline-video']
        data_arr = [source, url, title, descr, author, date]
        if "rep.repubblica.it" in url:
            content_selector = "body"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
            dct['text'] = ["Nooooo! This is only available to paying users of La Repubblica!"]
            return (dct, article_data)
        try:
            content_selector = "div.story__text"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        except:
            content_selector = "div.story__content"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Atlantic Council:
    def TheAtlanticCouncil(self, src="The Atlantic Council"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector=".ac-single-post--marquee", selector='h2')
        descr = None
        author = None
        date = self.select_date(soup, selector='.ac-single-post--marquee--heading')
        if date is None:
            date = self.select_date(soup, selector='.gta-site-banner--heading.gta-post-site-banner--heading')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'footer', '.wp-caption', '.external-associated', '.wp-block-group', '.wp-block-media-text', '.has-small-font-size', '.ac-single-post--marquee--caption', '.gta-horizontal-featured gutenblock', '.gutenblock--horizontal-multi-item-feature', '.horizontal-multi-item-feature', '.gta-form', '.gta-site-banner--image-caption', '.gta-post-site-banner--image-caption', '#h-further-reading', '.gta-embed', '.gta-combo-featured', '.gta-horizontal-featured--single']
        data_arr = [source, url, title, descr, author, date]
        content_selector = "div.ac-single-post--content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Further Reading:", "Follow us on social media"])
        return (dct, article_data)

    # Method for The Wilson Center:
    def TheWilsonCenter(self, src="The Wilson Center"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector=".publication-detail-hero-main", selector='h1')
        if title == soup.title.text.strip():
            title = self.select_title(soup, header_selector=".insight-detail-hero-content", selector='h1')
        descr = self.select_descr(soup, selector=".insight-detail-hero-intro")
        author = self.select_author(soup, selector=".insight-detail-hero-author-byline-authors")
        if author is None:
            author = self.select_author(soup, selector='.publication-detail-hero-author-byline')
        date = self.select_date(soup, selector='.insight-detail-hero-author-byline-text.-date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', 'footer', '.wp-caption', '.external-associated', '.wp-block-group', '.wp-block-media-text', '.has-small-font-size', '.ac-single-post--marquee--caption', '.gta-horizontal-featured gutenblock', '.gutenblock--horizontal-multi-item-feature', '.horizontal-multi-item-feature', '.gta-form', '.gta-site-banner--image-caption', '.gta-post-site-banner--image-caption', '#h-further-reading', '.gta-embed', '.gta-combo-featured', '.gta-horizontal-featured--single']
        data_arr = [source, url, title, descr, author, date]
        content_selector = "div.text-block-inner"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Further Reading:", "Follow us on social media", "click here to download"])
        return (dct, article_data)

    # Method for The Wilson Quarterly:
    def TheWilsonQuarterly(self, src="The Wilson Quarterly"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='._Title')
        descr = self.select_descr(soup, selector="._Summary")
        author = self.select_author(soup, selector=".Byline")
        date = self.select_date(soup, selector='._DateLink')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', 'footer', '.wp-caption', '.external-associated', '.wp-block-group', '.wp-block-media-text']
        data_arr = [source, url, title, descr, author, date]
        content_selector = "._Content__"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Further Reading:", "Follow us on social media", "click here to download"])
        return (dct, article_data)

    # Method for The Wilson Center | Africa Up Close:
    def AfricaUpClose(self, src="The Wilson Center | Africa Up Close"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector=".list-news-item", selector='h3')
        descr = self.select_descr(soup, selector=".insight-detail-hero-intro")
        date = self.select_date(soup, selector='.box-posted em.blue')
        soup = self.removeOtherGarbage(soup, *[".box-posted em.blue"])
        author = self.select_author(soup, selector=".box-posted em")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', 'footer', '.wp-caption', '.external-associated', '.wp-block-group', '.wp-block-media-text', '.has-small-font-size', '.ac-single-post--marquee--caption', '.gta-horizontal-featured gutenblock', '.gutenblock--horizontal-multi-item-feature', '.horizontal-multi-item-feature', '.gta-form', '.gta-site-banner--image-caption', '.gta-post-site-banner--image-caption', '#h-further-reading', '.gta-embed', '.gta-combo-featured', '.gta-horizontal-featured--single']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".news-text"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Photo credit:", "Photo source:", "Cover image:"])
        return (dct, article_data)

    # Method for Lausan:
    def Lausan(self, src="Lausan"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector=".meta", selector='h1.entry-title')
        descr = self.select_descr(soup, header_selector=".meta", selector=".subtitle")
        date = self.select_date(soup, header_selector=".byline", selector=".date")
        author = self.select_author(soup, header_selector=".byline", selector=".author")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', '.inline-post']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".entry-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Photo credit:", "Photo source:", "Cover image:"])
        return (dct, article_data)

    # Method for MIT Technology Review:
    def MITTechnologyReview(self, src="MIT Technology Review"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="main header", selector='h1')
        descr = self.select_descr(soup, header_selector="main header", selector='p')
        date = self.select_date(soup, selector=".contentHeader__publishDate--37zcW")
        soup = self.removeOtherGarbage(soup, *[".screen-reader-text"])
        author = self.select_author(soup, selector=".byline__author--g26Rn") # .byline__list--2jfa5
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', '.inline-post']
        data_arr = [source, url, title, descr, author, date]
        content_selector = "#content--body" # .content-area
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Photo credit:", "Photo source:", "Cover image:"])
        return (dct, article_data)

    # Method for The National Interest:
    def TheNationalInterest(self, src="The National Interest"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='h1.detail__title')
        descr = self.select_descr(soup, selector=".detail__sub")
        date = self.select_date(soup, selector=".meta__date")
        author = self.select_author(soup, selector=".meta__author")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', '.ad']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".detail__content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Global Asia:
    def GlobalAsia(self, src="Global Asia"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector=".forum", selector='.title-article')
        descr = self.select_descr(soup, header_selector=".forum", selector='.author')
        date = self.select_date(soup, header_selector=".forum", selector='.breview')
        author = self.select_author(soup, header_selector=".forum", selector='.title-article-user')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', '.ad']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".forum-detail-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Acquirer's Multiple:
    def TheAcquirersMultiple(self, src="The Acquirer's Multiple"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="header.entry-header", selector='h1')
        meta = self.select_descr(soup, header_selector="header.entry-header", selector='p')
        if meta is not None:
            meta = meta.replace("Stock Screener", "").replace("Leave a Comment", "")
        try:
            months = np.array(["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sept", "Oct", "Nov", "Dec"])
            date = None
            for month in months:
                if meta.find(month) > -1:
                    i = meta.index(month)
                    date = meta[i:]
                    meta = meta.replace(date, "")
                    break
        except:
            date = None
        try:
            author = meta
        except:
            author = None
        descr = None
        # date = self.select_date(soup, header_selector="header.entry-header", selector='.breview')
        # author = self.select_author(soup, header_selector="header.entry-header", selector='.title-article-user')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', '.sharedaddy', '.jp-relatedposts']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".entry-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["FREE Stock Screener", "For more articles like this, check out our value investing news here.", "Don’t forget to check out our FREE Large Cap 1000 – Stock Screener, here at The Acquirer’s Multiple"])
        return (dct, article_data)

    # Method for Deadline:
    def Deadline(self, src="Deadline"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="header.a-article-grid__header", selector='h1')
        descr = self.select_descr(soup, header_selector=".forum", selector='.author')
        date = self.select_date(soup, selector='time')
        soup = self.removeOtherGarbage(soup, *["section.author"])
        author = self.select_author(soup, selector='.author__byline a')
        if author is not None:
            if len(author) < 2:
                author = self.select_author(soup, selector='.a-article-grid__author a')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', 'article.related-story', '.admz', '.subscribe-to', '.article-tags']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".a-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Gothamist:
    def Gothamist(self, src="Gothamist"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="header.c-article__header", selector='h1')
        descr = self.select_descr(soup, header_selector="header.c-article__header", selector='.author')
        date = self.select_date(soup, header_selector="header.c-article__header", selector='.o-published-date')
        author = self.select_author(soup, header_selector="header.c-article__header", selector='.o-byline')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', '.ad']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".c-article__body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for CNN:
    def CNN(self, src="CNN"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='h1.pg-headline')
        descr = self.select_descr(soup, selector='.author')
        date = self.select_date(soup, selector='.update-time')
        author = self.select_author(soup, selector='.metadata__byline')
        selectors = '.zn-body__paragraph' # p, h2, h3, h4, h5, h6, ul li, ol li,
        garbage_arr = ['figure', 'blockquote', 'figcaption']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr)
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        if len(dct['text']) < 1:
            descr = self.select_descr(soup, selector='article.sc-bwzfXH.sc-kIPQKe.iWZQaB')
            selectors = "article.sc-bwzfXH.sc-kIPQKe.jjVnED"
            arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr)
            article_data = SingleArticle(source, url, title, descr, author, date, arr)
            dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        print("\n\n\n\nMETHOD FOR CNN" * 8)
        print(dct.keys())
        print()
        print(article_data.keys())
        print("\n\n\n\n")
        return (dct, article_data)

    # Method for Fox News:
    def FoxNews(self, src="Fox News"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="header.article-header", selector='h1.headline')
        descr = self.select_descr(soup, header_selector="header.article-header", selector='h2.sub-headline')
        date = self.select_date(soup, header_selector="header.article-header", selector='.article-date')
        author = self.select_author(soup, header_selector="header.article-header", selector='.author-byline')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', '.caption', '.featured']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".article-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["CLICK HERE TO GET THE FOX NEWS APP", "CLICK HERE TO SIGN UP FOR OUR", "CLICK HERE FOR", "CLICK HERE TO READ MORE", "CLICK HERE TO GET"])
        return (dct, article_data)

    # Method for Fox Business:
    def FoxBusiness(self, src="Fox Business"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="header.article-header", selector='h1.headline')
        descr = self.select_descr(soup, header_selector="header.article-header", selector='h2.sub-headline')
        date = self.select_date(soup, header_selector="header.article-header", selector='.article-date')
        author = self.select_author(soup, header_selector="header.article-header", selector='.author-byline')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', '.caption', '.featured']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".article-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["CLICK HERE TO GET THE FOX NEWS APP", "CLICK HERE TO SIGN UP FOR OUR", "CLICK HERE FOR MORE", "CLICK HERE TO READ MORE", "CLICK HERE TO GET", "GET FOX BUSINESS ON THE GO BY CLICKING HERE"])
        return (dct, article_data)

    # Method for CNBC:
    def CNBC(self, src="CNBC"):
        (source, url, soup) = self.handle_meta(src) # Author-styles-makeit-authorName--tiaxO
        title = self.select_title(soup, header_selector="header.ArticleHeader-articleHeader", selector='h1.ArticleHeader-headline')
        descr = self.select_descr(soup, header_selector=".RenderKeyPoints-keyPoints", selector='ul')
        date = self.select_date(soup, selector='.ArticleHeader-headerContentContainer time') # .ArticleHeader-time
        author = self.select_author(soup, header_selector="header.ArticleHeader-articleHeader", selector='.Author-authorName')
        ##### FOR MAKE IT #####
        if title == soup.title.text.strip():
            title = self.select_title(soup, header_selector="header.ArticleHeader-styles-makeit-articleHeader--2hCOp", selector='h1')
        if date is None:
            date = self.select_date(soup, selector='.ArticleHeader-styles-makeit-articleHeader--2hCOp time')
        if author is None:
            author = self.select_author(soup, header_selector="header.ArticleHeader-styles-makeit-articleHeader--2hCOp", selector='.Author-styles-makeit-authorName--tiaxO')
        #######################
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', '.caption', '.featured', '.InlineImage-imageEmbed']
        data_arr = [source, url, title, descr, author, date]
        try:
            content_selector = ".ArticleBody-articleBody"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Subscribe to CNBC on YouTube."])
        except:
            content_selector = ".ArticleBody-styles-makeit-articleBody--3rfGP"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Subscribe to CNBC on YouTube."])
        return (dct, article_data)

    # Method for Bloomberg Quint:
    def BloombergQuint(self, src="Bloomberg Quint"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector=".story-base-template-module__story-content__3hwxe", selector='h1')
        descr = self.select_descr(soup, header_selector=".story-base-template-module__story-content__3hwxe", selector='h2.sub-headline')
        date = self.select_date(soup, header_selector=".story-base-template-module__story-content__3hwxe", selector='.published-info-module__published-info__3611I')
        author = self.select_author(soup, header_selector=".story-base-template-module__story-content__3hwxe", selector='.authors-module__author-info__C8zNP li')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', '.caption', '.featured']
        data_arr = [source, url, title, descr, author, date]
        content_selector = "#piano-content-controller"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Read more:"])
        return (dct, article_data)

    # Method for Foreign Policy in Focus:
    def ForeignPolicyInFocus(self, src="Foreign Policy In Focus"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="header.article-header", selector='h1')
        descr = self.select_descr(soup, header_selector="header.article-header", selector='.lede')
        date = self.select_date(soup, header_selector="header.article-header", selector='time')
        author = self.select_author(soup, header_selector="header.article-header", selector='.author')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.wp-caption-text', '.sharedaddy']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".entry-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Read more:"])
        return (dct, article_data)

    # Method for The Nation:
    def TheNation(self, src="The Nation"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="header.article-header", selector='h1.title')
        descr = self.select_descr(soup, header_selector="header.article-header", selector='h2.subtitle')
        date = self.select_date(soup, header_selector="header.article-header", selector='.time')
        author = self.select_author(soup, header_selector="header.article-header", selector='.author')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".article-body-inner"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Read more:"])
        try:
            dct['text'] = [dct['text'][0]]
        except:
            pass
        return (dct, article_data)

    # Method for Value Walk:
    def ValueWalk(self, src="Value Walk"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="header.td-post-title", selector='.entry-title')
        descr = self.select_descr(soup, header_selector="header.td-post-title", selector='h2.subtitle')
        date = self.select_date(soup, header_selector="header.td-post-title", selector='.td-post-date')
        author = self.select_author(soup, header_selector="header.td-post-title", selector='.td-post-author-name')
        try:
            author = author.replace("-", "").strip()
        except:
            pass
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.td-post-featured-image', '.vwp_ext_post', '.two-thirds', '.first', '.one-third', 'footer', '.tdc-header-wrap', '.td-category', '.menu-item', '.comments', '.wppopups-whole', '.no-results']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr, dont_append_keys=["2020 hedge fund letters, conferences and more", "See the full ebook here."])
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Institutional Investor:
    def InstitutionalInvestor(self, src="Institutional Investor"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="header.article_header", selector='h1')
        if title == soup.title.text.strip():
            title = self.select_title(soup, header_selector="header.article_header--featured", selector='h1')
        descr = self.select_descr(soup, header_selector="header.article_header", selector='.standfirst')
        try:
            if descr is None or len(descr) < 2:
                descr = self.select_descr(soup, header_selector="header.article_header--featured", selector='.standfirst')
        except:
            pass
        date = self.select_date(soup, header_selector="header.article_header", selector='time')
        try:
            if date is None or len(date) < 2:
                date = self.select_date(soup, header_selector="header.article_header--featured", selector='time')
        except:
            pass
        author = self.select_author(soup, header_selector="header.article_header", selector='.author_name')
        try:
            if author is None or len(author) < 2:
                author = self.select_author(soup, header_selector="header.article_header--featured", selector='.author_name')
        except:
            pass
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.wp-caption-text', '.sharedaddy']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".article_body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Read more:"])
        return (dct, article_data)

    # Method for The New York Times:
    def NYT(self, src="The New York Times"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="header.css-z40kjo.euiyums1", selector='h1')
        descr = self.select_descr(soup, header_selector="header.css-z40kjo.euiyums1", selector='#article-summary')
        date = self.select_date(soup, header_selector="header.css-z40kjo.euiyums1", selector='time') # .css-ld3wwf.e16638kd2
        author = self.select_author(soup, header_selector="header.css-z40kjo.euiyums1", selector='.css-brehiz.e1jsehar0')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.wp-caption-text', '.sharedaddy']
        if "/live/" in url or "/interactive/" in url:
            arr = ["This is a multimedia article, not a text article."]
            article_data = SingleArticle(source, url, title, descr, author, date, arr)
            dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date,
                   'text': arr}
            return (dct, article_data)
        data_arr = [source, url, title, descr, author, date]
        content_selector = "[name='articleBody']"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Economist:
    def TheEconomist(self, src="The Economist"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="header.article__header", selector='.article__headline')
        descr = self.select_descr(soup, header_selector="header.article__header", selector='.article__description')
        date = self.select_date(soup, selector='.article__section-edition')
        author = self.select_author(soup, header_selector="header.article__header", selector='.author')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'aside', '.wp-caption-text', '.sharedaddy', '.related-articles', '.newsletter-signup', '.article__description']
        data_arr = [source, url, title, descr, author, date]
        content_selector = "main#content article"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Read more:", "Enjoy more audio and podcasts on iOS or Android"])
        return (dct, article_data)

    # Method for The Guardian:
    def TheGuardian(self, src="The Guardian"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='h1') # .content__headline  header_selector="header.content__head",
        descr = self.select_descr(soup, selector='.content__standfirst p')
        if descr is None:
            descr = self.select_descr(soup, selector=".css-cxo7s2")
        if descr is None:
            descr = self.select_descr(soup, selector=".css-1uix35z")
        date = self.select_date(soup, selector='.content__dateline')
        if date is None or len(date) < 2:
            date = self.select_date(soup, selector='.css-1kkxezg')
        soup = self.removeOtherGarbage(soup, *[".css-1ntdfk2"])
        author = self.select_author(soup, selector="[itemprop='name']")
        try:
            if author[0] == ",":
                author = author[1:].strip()
        except:
            pass
        if author is None or len(author) < 2:
            author = self.select_author(soup, selector='[aria-label="Contributor info"]')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'aside', '.submeta', '.submeta__share', 'nav', 'header', '.submeta__syndication', 'footer', '.css-l3d9fd', '.css-1fznh52', '#slot-body-end', '.css-739uag', '#sub-nav-root', '.css-1861z7y', '.pillars', '.pillars__item', 'ul.social', '.fc-container', '.content-footer']
        data_arr = [source, url, title, descr, author, date]
        content_selector = "body" # .content__article-body
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["comments ("])
        return (dct, article_data)

    # Method for Forbes:
    def Forbes(self, src="Forbes"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector=".body-container .header-content-container", selector='h1')
        descr = self.select_descr(soup, header_selector=".body-container .header-content-container", selector='.article__description')
        date = self.select_date(soup, header_selector=".content-data", selector='time')
        author = self.select_author(soup, header_selector=".body-container", selector='.contrib-link--name.remove-underline')
        try:
            date = date.replace(",", "")
        except:
            pass
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'aside', '.article-sharing']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".article-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Read more:"])
        return (dct, article_data)

    # Method for Forbes Argentina:
    def ForbesArgentina(self, src="Forbes Argentina"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='h1.tit')
        descr = self.select_descr(soup, selector='.subtitulo')
        date = self.select_date(soup, selector=".date")
        author = self.select_author(soup, selector='.autor a')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'aside', '.article-sharing', '.relacionados', '.sharer']
        data_arr = [source, url, title, descr, author, date]
        content_selector = "article.content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Forbes France:
    def ForbesFrance(self, src="Forbes France"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='h1.entry-title')
        descr = self.select_descr(soup, selector='.subtitulo')
        date = self.select_date(soup, selector="time.entry-date")
        author = self.select_author(soup, selector='.entry-header .author')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'aside', '.article-sharing', '.relacionados', '.sharer']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".entry-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["À lire également :", "À lire également: "])
        return (dct, article_data)

    # Method for Forbes Hungary:
    def ForbesHungary(self, src="Forbes Hungary"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.article-content-area h1')
        descr = None
        date = self.select_date(soup, selector=".article-date-published")
        author = self.select_author(soup, selector='.autor a')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'aside', '.article-sharing', '.relacionados', '.sharer', '.wp-embedded-content', '.wp-caption-text']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".article-content-area"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Ezt olvastad már?"])
        return (dct, article_data)

    # Method for Forbes Russia:
    def ForbesRussia(self, src="Forbes Russia"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='header.article__header h1')
        descr = self.select_descr(soup, selector=".article__lead")
        date = self.select_date(soup, selector=".breadcrumbs__date")
        author = self.select_author(soup, selector='.author__name')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'aside', '.article-sharing', '.relacionados', '.sharer', '.wp-embedded-content', '.wp-caption-text']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".article__body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Ezt olvastad már?"])
        return (dct, article_data)

    # Method for Forbes Brasil:
    def ForbesBrasil(self, src="Forbes Brasil"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='h1.entry-title')
        descr = None
        date = self.select_date(soup, selector=".entry-meta-date")
        author = self.select_author(soup, selector='.entry-header .nome-autor')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'aside', 'header', 'nav', 'footer', '.wp-caption-text', '.entry-tags', '.mh-share-buttons', '.swal2-container', '.mh-social-bottom', '.link-audima']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr, dont_append_keys=["LEIA TAMBÉM:", "VEJA TAMBÉM:", "Siga FORBES Brasil nas redes sociais:", "da Forbes Brasil na Play Store e na App Store", "Tenha também a Forbes no"])
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Forbes Baltics:
    def ForbesBaltics(self, src="Forbes Baltics"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='article main h1')
        descr = self.select_descr(soup, header_selector="article main", selector='.main_paragraph')
        date = self.select_date(soup, header_selector="article main .date", selector='span')
        author = self.select_author(soup, selector='.author a')
        if author is None:
            author = self.select_author(soup, selector='.author')
        if author is None:
            author = self.select_author(soup, selector='.small-headline h4')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'aside', '.article-sharing', '.breadcrumbs', '.date', '.author', '.main_paragraph', '.slick-slide', '.slick-slide.slick-cloned', '.recent-article', '.bottom-preview']
        data_arr = [source, url, title, descr, author, date]
        try:
            content_selector = "article main"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        except:
            content_selector = "article"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Morningstar:
    def Morningstar(self, src="Morningstar"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="article header", selector='h1')
        descr = self.select_descr(soup, header_selector="article header", selector="[itemprop='description']")
        date = self.select_date(soup, header_selector="article header", selector='.article__published-on')
        author = self.select_author(soup, header_selector="article header", selector='.article__author')
        if author is None or len(author) < 2:
            author = self.select_author(soup, selector='.news-article__provider')
        if date is None:
            date = self.select_date(soup, selector='.news-article__published-on')
        flag = False
        try:
            paywall = soup.body.select(".article__paywall")
            if paywall:
                flag = True
        except:
            pass
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'aside', 'blockquote']
        data_arr = [source, url, title, descr, author, date]
        try:
            content_selector = ".article__body"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        except:
            content_selector = ".news-article__body"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        if flag:
            dct['text'] += ["Nooooo! This article is only available for Morningstar Basic members."]
        return (dct, article_data)

    # Method for MoneyWeek:
    def MoneyWeek(self, src="MoneyWeek"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector=".polaris__content", selector='h1')
        descr = self.select_descr(soup, header_selector=".polaris__content", selector='h2')
        date = self.select_date(soup, header_selector=".polaris__content", selector='.polaris__post-meta--date')
        author = self.select_author(soup, header_selector=".polaris__content", selector='.polaris__post-meta--author')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'header', 'footer', '.polaris__breadcrumb', '.polaris__image--meta', '.polaris__image--credits', '.polaris__image--wrapper', '.polaris__related-links', '.polaris__heading', '.-tags-social', '.polaris__tags', '.polaris__article-card']
        content_selector = 'body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for NFX:
    def NFX(self, src="NFX"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector=".polaris__content", selector='h1')
        descr = self.select_descr(soup, header_selector=".polaris__content", selector='h2')
        date = self.select_date(soup, header_selector=".polaris__content", selector='.polaris__post-meta--date')
        author = self.select_author(soup, header_selector=".polaris__content", selector='.polaris__post-meta--author')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'header', 'footer', '.polaris__breadcrumb', '.polaris__image--meta', '.polaris__image--credits', '.polaris__image--wrapper', '.polaris__related-links', '.polaris__heading', '.-tags-social', '.polaris__tags', '.polaris__article-card']
        try:
            content_selector = '#content .single-page-content'  # div.polaris__body div.polaris__content
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        except:
            content_selector = 'body'  # div.polaris__body div.polaris__content
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for FiveThirtyEight:
    def FiveThirtyEight(self, src="FiveThirtyEight"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="header.post-info", selector='h1')
        descr = self.select_descr(soup, header_selector="header.post-info", selector='h2')
        date = self.select_date(soup, header_selector="header.post-info", selector='time')
        author = self.select_author(soup, header_selector="header.post-info", selector='.author')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'header', 'footer', '.video-title']
        content_selector = '.entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Boston.com:
    def Boston(self, src="Boston.com"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="header.content-header", selector='h1')
        descr = self.select_descr(soup, header_selector="header.content-header", selector='h2')
        date = self.select_date(soup, selector='.content-byline__timestamp')
        author = self.select_author(soup, selector='.content-byline__producer')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'header', 'footer', '.ad-container', '.airship-web-notifications', '.related-links']
        content_selector = '.content-text'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Marketplace:
    def Marketplace(self, src="Marketplace"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector=".c-story-head__body", selector='h1')
        descr = self.select_title(soup, header_selector=".c-story-head__body", selector='.inner')
        date = self.select_date(soup, selector='.c-story-head__body .c-story-head__body-meta-date')
        author = self.select_author(soup, selector='.c-story-head__body .c-story-head__body-meta-author')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.top-latest-stories', '.jp-relatedposts', '#global-giving-item', '.faq-container']
        content_selector = '.original-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Washington Times:
    def TheWashingtonTimes(self, src="The Washington Times"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.page-headline')
        descr = self.select_title(soup, header_selector=".c-story-head__body", selector='.inner')
        date = self.select_date(soup, selector='.meta .source')
        try:
            date = date.split("-")[-1].strip()
        except:
            pass
        author = self.select_author(soup, selector='.meta .byline')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.top-latest-stories', '.jp-relatedposts', '#global-giving-item', '.faq-container', '#newsletter-form-story']
        content_selector = '.article-text'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Prospect Magazine:
    def ProspectMagazine(self, src="Prospect Magazine"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector=".blog-header__row", selector='h1')
        descr = self.select_title(soup, header_selector=".blog-header__row", selector='p')
        date = self.select_date(soup, selector='.blog-header__row .blog-header__date-link')
        author = self.select_author(soup, selector='.blog-header__row .blog-header__author-link ')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', '.top-latest-stories', '.jp-relatedposts', '#global-giving-item', '.faq-container']
        content_selector = '.blog__main'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Total Politics:
    def TotalPolitics(self, src="Total Politics"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="article", selector='h1')
        descr = self.select_title(soup, header_selector=".field-content", selector='p')
        soup = self.removeOtherGarbage(soup, *[".field-content p"])
        author = self.select_author(soup, selector='.date .author')
        date = self.select_date(soup, selector='.date')
        try:
            date = date.replace("Written by", "").replace(author, "").replace(" on ", "").split(" in ")[0].strip()
        except:
            pass
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'aside']
        content_selector = '.content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Forbes Africa:
    def ForbesAfrica(self, src="Forbes Africa"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector="#mvp-post-head", selector="[itemprop='headline']")
        descr = self.select_descr(soup, header_selector="#mvp-post-head", selector='.author')
        date = self.select_date(soup, header_selector="#mvp-post-head", selector='.mvp-author-info-date')
        author = self.select_author(soup, header_selector="#mvp-post-head", selector="[itemprop='author']")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', '.ad']
        data_arr = [source, url, title, descr, author, date]
        content_selector = "#mvp-content-main"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Forbes Italia:
    def ForbesIT(self, src="Forbes Italia"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.entry-title")
        descr = self.select_descr(soup, header_selector="#mvp-post-head", selector='.author')
        date = self.select_date(soup, selector='.data-posted')
        author = self.select_author(soup, selector=".data-author .author")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'nav', 'header', 'footer', '.bfc-main-menu', '.share-post', '.forbes-newsletter-invite', '.related', '.bfc-related-posts', '.bfc-content', '.data-author']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr)
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Forbes España:
    def ForbesES(self, src="Forbes España"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, header_selector=".td-post-header", selector="h1")
        descr = self.select_descr(soup, header_selector=".td-post-header", selector='p')
        date = self.select_date(soup, header_selector=".td-post-header", selector='time')
        author = self.select_author(soup, header_selector=".td-post-header", selector=".td-post-author-name")
        try:
            author = author.replace("-","").strip()
        except:
            pass
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'blockquote', 'figcaption']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".td-post-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for LatinAmerican Post:
    def LAP(self, src="LatinAmerican Post"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="article h1")
        descr = self.select_descr(soup, selector="article h2")
        date = self.select_date(soup, selector="[itemprop='datePublished']")
        author = None
        selectors = 'p, h2, h3, h4, h5, h6'
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', '.ad', '#bottommain', '.module', 'footer', '#cpanel_wrapper']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr, dont_append_keys=["also read:", "read also:", "Your browser does not support the audio tag", "Listen to this article"])
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for The Lexington Institute:
    def TheLexingtonInstitute(self, src="The Lexington Institute"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = self.select_descr(soup, selector=".insight-detail-hero-intro")
        date = self.select_date(soup, selector='.entry-date')
        author = self.select_author(soup, selector=".author a")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', 'footer', '.archive-select']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".entry-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Photo credit:", "Photo source:", "Cover image:"])
        return (dct, article_data)

    # Method for BBC:
    def BBC(self, src="BBC"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='article header h1')
        descr = self.select_descr(soup, selector=".insight-detail-hero-intro")
        date = self.select_date(soup, selector='article header time')
        if date is None:
            date = self.select_date(soup, selector='.css-1hizfh0-MetadataSnippet.ecn1o5v0 time')
        author = self.select_author(soup, selector=".author a")
        if author is None or len(author) < 2:
            author = self.select_author(soup, selector=".css-1pjc44v-Contributor.e5xb54n0 span strong")
        selectors = 'p, h2, h3, h4, h5, h6'#, ul li, ol li
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', 'footer', '.css-1kpdaxb-TagShareWrapper', '.e1nh2i2l6', '[data-component="tag-list"]', '[data-component="see-alsos"]']
        data_arr = [source, url, title, descr, author, date]
        content_selector = "body article"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The New York Post:
    def NYPost(self, src="The New York Post"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.article-header h1')
        descr = self.select_descr(soup, selector=".insight-detail-hero-intro")
        date = self.select_date(soup, selector='.byline-date')
        author = self.select_author(soup, selector="#author-byline .byline")
        selectors = 'p, h2, h3, h4, h5, h6'#, ul li, ol li
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', 'footer', '#more-on']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".entry-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The New York Daily News:
    def NYDailyNews(self, src="The New York Daily News"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.pb-f-article-header h1')
        descr = None
        date = self.select_date(soup, selector='.pb-f-article-header .timestamp-wrapper')
        author = self.select_author(soup, selector=".pb-f-article-header .byline-wrapper .byline-article")
        selectors = 'p, h2, h3, h4, h5, h6'#, ul li, ol li
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', 'footer', '#more-on', '.pb-f-article-gallery', '.fte-hd']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".pb-f-article-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Chicago Tribune:
    def ChicagoTribune(self, src="The Chicago Tribune"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.pb-f-article-header h1')
        descr = None
        date = self.select_date(soup, selector='.pb-f-article-header .timestamp-wrapper')
        author = self.select_author(soup, selector=".pb-f-article-header .byline-wrapper .byline-article")
        selectors = 'p, h2, h3, h4, h5, h6'#, ul li, ol li
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', 'footer', '#more-on', '.pb-f-article-gallery', '.fte-hd']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".pb-f-article-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Denver Post:
    def TheDenverPost(self, src="The Denver Post"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = self.select_descr(soup, '.subheadline')
        date = self.select_date(soup, selector='.time')
        author = self.select_author(soup, selector=".author-name")
        selectors = 'p, h2, h3, h4, h5, h6'#, ul li, ol li
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', 'footer', '#more-on', '.pb-f-article-gallery', '.fte-hd']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".article-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Real Deal:
    def TheRealDeal(self, src="The Real Deal"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.single-header h1')
        descr = self.select_descr(soup, selector='.single-header p') # .single-header-date
        date = self.select_date(soup, selector='.single-header .single-header-date')
        try:
            date = date.split(".")[1]
        except:
            pass
        author = self.select_author(soup, selector=".single-header .single-header-byline")
        selectors = 'p, h2, h3, h4, h5, h6'#, ul li, ol li
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', 'footer', '.wp-caption-text', '.read-more', '.single-content-share', '.single-content-tags']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".single-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Chicago Sun-Times:
    def ChicagoSunTimes(self, src="Chicago Sun-Times"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.c-entry-hero__header-wrap h1')
        descr = self.select_descr(soup, selector='.c-entry-hero p.c-entry-summary')
        date = self.select_date(soup, selector='.c-entry-hero time.c-byline__item')
        try:
            soup = self.removeOtherGarbage(soup, *['.c-entry-hero time.c-byline__item'])
        except:
            pass
        author = self.select_author(soup, selector=".c-entry-hero .c-byline__item")
        try:
            author = author.replace(",", "")
        except:
            pass
        selectors = 'p, h2, h3, h4, h5, h6'#, ul li, ol li
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', 'footer', '.wp-caption-text', '.read-more', '.single-content-share', '.single-content-tags']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".c-entry-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Graph not displaying properly? Click here."])
        return (dct, article_data)

    # Method for International Business Times:
    def IBTimes(self, src="International Business Times"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.article-header h1')
        descr = self.select_descr(soup, selector='.article-header .author')
        date = self.select_date(soup, selector='.c-entry-hero time.c-byline__item')
        author = self.select_author(soup, selector="time[itemprop='datePublished']")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', 'footer', '.figcaption', '.wp-caption-text', '.read-more', '.single-content-share', '.single-content-tags', '.figure']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".article-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Graph not displaying properly? Click here."])
        return (dct, article_data)

    # Method for The Boston Herald:
    def BostonHerald(self, src="The Boston Herald"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='h1.entry-title')
        descr = None#self.select_descr(soup, selector='.article-header .author')
        date = self.select_date(soup, selector='div.time')
        author = self.select_author(soup, selector="a.author-name")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', 'footer', '.figcaption', '.wp-caption-text', '.read-more', '.single-content-share', '.single-content-tags', '.figure']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".article-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Graph not displaying properly? Click here."])
        return (dct, article_data)

    # Method for Observer:
    def Observer(self, src="Observer"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='header.entry-header h1')
        descr = None#self.select_descr(soup, selector='.article-header .author')
        date = self.select_date(soup, selector='header.entry-header .entry-date')
        author = self.select_author(soup, selector='header.entry-header .author')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', '.wp-caption']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".entry-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, arr_of_strs_to_remove_within_ps=[["Subscribe to Observer’s Royals Newsletter", ""]])
        dct['text'] = [dct['text'][0]]
        return (dct, article_data)

    # Method for Kiplinger:
    def Kiplinger(self, src="Kiplinger"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='h1.polaris__heading.polaris__heading--title')
        descr = self.select_descr(soup, selector='h2')
        date = self.select_date(soup, selector='.polaris__post-meta--date')
        try:
            date = date.replace("-", "").strip()
        except:
            pass
        author = self.select_author(soup, selector='.polaris__post-meta--author')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'header', 'footer', '.polaris__breadcrumb', '.polaris__image--meta', '.polaris__image--credits', '.polaris__image--wrapper', '.polaris__related-links', '.polaris__heading', '.-tags-social', '.polaris__tags', '.polaris__article-card']
        content_selector = 'body' # div.polaris__body div.polaris__content
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Sign up for the Kiplinger Today E-Newsletter."])
        return (dct, article_data)

    # Method for Reuters:
    def Reuters(self, src="Reuters"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.TwoColumnsLayout-inner-e5KaJ h1')
        descr = None
        date = None
        author = self.select_author(soup, selector='.Byline-byline-1sVmo.ArticleBody-byline-10B7D')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'header', 'footer', '.TrustBadge-trust-badge-20GM8']
        content_selector = '.ArticleBodyWrapper'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Diplomat:
    def TheDiplomat(self, src="The Diplomat"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='header h1')
        descr = self.select_descr(soup, selector="header #td-lead")
        date = self.select_date(soup, selector='header .td-date')
        author = self.select_author(soup, selector='header .td-author')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'header', 'footer', '.td-ad-inline']
        content_selector = "[itemprop='articleBody']"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Street:
    def TheStreet(self, src="The Street"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.m-detail-header h1')
        descr = self.select_descr(soup, selector='.m-detail-header .m-detail-header--dek')
        date = self.select_date(soup, selector='.m-detail-header time')
        author = self.select_author(soup, selector='.m-detail-header--meta-author')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'header', 'footer', '.TrustBadge-trust-badge-20GM8']
        content_selector = '.m-detail--body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Investopedia"):
    def Investopedia(self, src="Investopedia"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='header.article-header h1')
        descr = self.select_descr(soup, selector='header.article-header h2')
        date = self.select_date(soup, selector='.displayed-date')
        author = self.select_author(soup, selector='.byline__link')
        try:
            if author is None or len(author) < 2:
                author = self.select_author(soup, selector='.byline__link--no-short-bio')
        except:
            pass
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'header', 'footer', '.TrustBadge-trust-badge-20GM8']
        content_selector = '.article-body-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for MarketWatch:
    def MarketWatch(self, src="MarketWatch"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.article__masthead h1')
        descr = self.select_descr(soup, selector='.article__masthead .article__subhead')
        date = self.select_date(soup, selector='.article__masthead time.timestamp')
        author = self.select_author(soup, selector='.article__masthead .author')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'header', 'footer', '.TrustBadge-trust-badge-20GM8']
        content_selector = '.article__body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for ESPN:
    def ESPN(self, src="ESPN"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.article-header h1')
        descr = self.select_descr(soup, selector='.article__masthead .article__subhead')
        date = self.select_date(soup, selector='.timestamp')
        author = self.select_author(soup, selector='.authors .author')
        try:
            author = author.split("ESPN")[0]
        except:
            pass
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'header', 'footer', '.article-social', '.article-meta']
        content_selector = '.article-body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Bleacher Report:
    def BleacherReport(self, src="Bleacher Report"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='article header h1')
        descr = None
        date = self.select_date(soup, selector='article header .date')
        author = self.select_author(soup, selector='article .authorInfo .name')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'header', 'footer', '.article-social', '.article-meta', '.footer-wrapper']
        content_selector = 'body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Euronews:
    def Euronews(self, src="Euronews"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='body article h1')
        descr = self.select_descr(soup, selector='.m-detail-header .m-detail-header--dek')
        date = self.select_date(soup, selector='body article .c-article-date')
        try:
            date = date.replace("•", "").replace("&bullet", "").strip()
        except:
            pass
        soup = self.removeOtherGarbage(soup, *['body article .c-article-date'])
        author = self.select_author(soup, selector='body article .c-article-meta__info')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'header', 'footer', '.widget', '.widget--type-related']
        content_selector = '.article__content' # .c-article-content
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for EUbusiness:
    def EUbusiness(self, src="EUbusiness"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='#content #parent-fieldname-title')
        descr = None
        date = None
        author = self.select_author(soup, selector='body article .c-article-meta__info')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'header', 'footer', '.link-external', '.external-link', '.documentActions']
        try:
            content_selector = '#parent-fieldname-text'  #
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        except:
            content_selector = '#content'  #
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    def yahoo_determine_strs(self, u):
        domain = urlparse(u).netloc.replace("www.", "")
        if domain == "news.yahoo.com" or domain == "finance.yahoo.com" or domain == "sports.yahoo.com" or domain == "yahoo.com":
            return ["View this post on Instagram", "A Post shared by", "VIDEO -", "READ MORE:", "WATCH:"]
        if "uk." in domain or "sg." in domain or "de." in domain:
            return ["View this post on Instagram", "A Post shared by", "VIDEO -", "VIDEO:", "READ MORE:", "WATCH:"]
        elif "it." in domain:
            return ["View this post on Instagram", "A Post shared by", "VIDEO -", "LEGGI ANCHE: ", "LEGGI ANCHE -", "GUARDA ANCHE -", "GUARDA ANCHE:"]
        elif "fr." in domain:
            return ["Lire la suite sur", "Ce contenu peut également vous intéresser"]
        else:
            return []

    # Method for Yahoo Finance:
    def YahooFinance(self, src="Yahoo Finance"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="article header h1")
        descr = self.select_descr(soup, selector='.__0838e-2Ta0u') # data-test-id="article-summary-item"
        date = self.select_date(soup, selector=".caas-content-wrapper time")
        author = self.select_author(soup, selector=".caas-attr.author .caas-attr-meta a")
        if author is None or len(author) < 1:
            author = self.select_author(soup, selector=".caas-attr.caas-attr-authors a")
        try:
            for n in "0123456789":
                if n in author:
                    author = None
        except:
            pass
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside']
        content_selector = '.caas-body' #
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=self.yahoo_determine_strs(url))
        return (dct, article_data)

    # Method for Yahoo Sports:
    def YahooSports(self, src="Yahoo Sports"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="article header h1")
        descr = self.select_descr(soup, selector='.__0838e-2Ta0u') # data-test-id="article-summary-item"
        date = self.select_date(soup, selector=".caas-content-wrapper time")
        author = self.select_author(soup, selector=".caas-attr.author .caas-attr-meta a")
        if author is None or len(author) < 1:
            author = self.select_author(soup, selector=".caas-attr.caas-attr-authors a")
        try:
            for n in "0123456789":
                if n in author:
                    author = None
        except:
            pass
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside']
        content_selector = '.caas-body' #
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=self.yahoo_determine_strs(url))
        return (dct, article_data)

    # Method for Yahoo News:
    def YahooNews(self, src="Yahoo News"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="article header h1")
        descr = self.select_descr(soup, selector='.__0838e-2Ta0u') # data-test-id="article-summary-item"
        date = self.select_date(soup, selector=".caas-content-wrapper time")
        author = self.select_author(soup, selector=".caas-attr-meta a") # .caas-attr.author
        if author is None or len(author) < 1:
            author = self.select_author(soup, selector=".caas-attr.caas-attr-authors a")
        if author is None or len(author) < 1:
            author = self.select_author(soup, selector=".caas-attr-meta") # .caas-attr
        try:
            author = author.replace(date, "").strip()
        except:
            pass
        try:
            for n in "0123456789":
                if n in author:
                    author = None
        except:
            pass
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside']
        content_selector = '.caas-body' #
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=self.yahoo_determine_strs(url))
        return (dct, article_data)

    # Method for Radio Free Europe/Radio Liberty:
    def RFERL(self, src="Radio Free Europe/Radio Liberty"):
        (source, url, soup) = self.handle_meta(src)
        soup = self.removeOtherGarbage(soup, *[".link-print"])
        title = self.select_title(soup, selector="h1.title")
        descr = self.select_descr(soup, selector='.__0838e-2Ta0u')  # data-test-id="article-summary-item"
        date = self.select_date(soup, selector=".date time")
        author = self.select_author(soup, selector="div.links")
        try:
            if author.strip()[-1] == ",":
                author = author[:-2]
        except:
            pass
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.media-block', '.also-read', '.wsw__embed', '.banner', '.print-dialogue__opt-group', 'form', '#comments']
        content_selector = '#article-content'  #
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Gulf News:
    def GulfNews(self, src="Gulf News"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='header h1')
        descr = self.select_descr(soup, selector='header .lead')
        date = self.select_date(soup, selector='.article-meta time')
        author = self.select_author(soup, selector='.article-meta .author')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', '.related-package', '.more-similar-article']
        content_selector = '.article-body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for WNYC Studios:
    def WNYCStudios(self, src="WNYC Studios"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='header .story__title')
        descr = None
        date = self.select_date(soup, selector='.story-metadata__date')
        author = None
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer']
        content_selector = '.transcript .text'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Onion:
    def TheOnion(self, src="The Onion"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.sc-1efpnfq-0.bBLibw')
        descr = None
        date = self.select_date(soup, selector='.js_starterpost time')
        author = None
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer']
        content_selector = '.js_post-content' # .r43lxo-0 gqfcxx
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Haaretz:
    def Haaretz(self, src="Haaretz"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="[data-test='articleHeaderTitle']")
        descr = self.select_descr(soup, selector="[data-test='articleHeaderSubtitle']")
        date = self.select_date(soup, selector=".wg time")
        if date is None:
            date = self.select_date(soup, selector=".wb time")
        author = self.select_author(soup, selector=".wg address")
        if author is None or len(author) < 2:
            author = self.select_author(soup, selector=".wb address")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', "[data-test='relatedArticles']", "[data-test='tags']"]
        content_selector = "[data-test='articleBody']"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Axios:
    def Axios(self, src="Axios"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="article h1")
        descr = self.select_descr(soup, selector="[data-test='articleHeaderSubtitle']")
        date = self.select_date(soup, selector="article time")
        try:
            date = date.split("-")[0].strip()
        except:
            pass
        author = self.select_author(soup, selector="article .truncate")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', "[data-test='relatedArticles']", "[data-test='tags']"]
        content_selector = ".gtm-story-text"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Quartz:
    def Quartz(self, src="Quartz"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="article header h1")
        descr = self.select_descr(soup, selector="[data-test='articleHeaderSubtitle']")
        date = self.select_date(soup, selector="article time")
        author = self.select_author(soup, selector=".bi4tr")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer']
        content_selector = "#article-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Fast Company:
    def FastCompany(self, src="Fast Company"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".post__title")
        descr = self.select_descr(soup, selector=".post__deck")
        date = self.select_date(soup, selector=".post__header time")
        author = self.select_author(soup, selector=".post__byline cite")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer']
        content_selector = "article.post__article"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for RT:
    def RT(self, src="RT"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".article h1")
        descr = self.select_descr(soup, selector=".article .summary")
        date = self.select_date(soup, selector=".article .article__date")
        author = self.select_author(soup, selector=".article .name")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer']
        content_selector = ".article__text.text"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Think your friends would be interested? Share this story!", "Like this story? Share it with a friend!"])
        return (dct, article_data)

    # Method for The Moscow Project:
    def TheMoscowProject(self, src="The Moscow Project"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.page-title")
        descr = self.select_descr(soup, selector=".article .summary")
        if descr is None:
            try:
                descr = self.select_descr(soup, selector=".alt-secondary")
            except:
                pass
            try:
                descr += ": " + self.select_descr(soup, selector=".deck")
            except:
                descr = self.select_descr(soup, selector=".deck")
        date = self.select_date(soup, selector=".page-meta")
        author = self.select_author(soup, selector=".post-info")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer']
        content_selector = ".content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for PBS:
    def PBS(self, src="PBS"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.post__title")
        descr = self.select_descr(soup, selector=".article .summary")
        date = self.select_date(soup, selector="time.post__date")
        author = self.select_author(soup, selector=".post__byline [itemprop='name']")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer']
        if "/show/" in url:
            content_selector = ".video-transcript" ##### FOR TRANSCRIPT #####
            selectors = "p"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["READ MORE:"])
            return (dct, article_data)
        content_selector = ".body-text"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["READ MORE:"])
        return (dct, article_data)

    # Method for ABC News:
    def ABC(self, src="ABC News"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".Article__Headline__Title")
        descr = self.select_descr(soup, selector=".Article__Headline__Desc")
        date = self.select_date(soup, selector=".Byline__Meta--publishDate")
        author = self.select_author(soup, selector=".Byline__Author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h1, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'nav']
        if "/live-updates/" in url:
            arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr)
            article_data = SingleArticle(source, url, title, descr, author, date, arr)
            dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
            return (dct, article_data)
        content_selector = ".Article__Content.story"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for CBS News:
    def CBSNews(self, src="CBS News"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.content__title")
        descr = self.select_descr(soup, selector=".article .summary")
        date = self.select_date(soup, selector=".content__header time")
        author = self.select_author(soup, selector=".content__meta.content__meta-byline")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer']
        content_selector = ".content__body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for NBC News:
    def NBC(self, src="NBC News"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.article-hero__headline")
        descr = self.select_descr(soup, selector=".article-dek")
        date = self.select_date(soup, selector="[itemprop='datePublished']")
        author = self.select_author(soup, selector=".article-byline__name")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.inlineVideo___3Rd2d', '.contentBody___1zFVF', '.mv8'] 
        content_selector = ".article-body__content"
        # (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        content = soup.select(content_selector)
        ps = []
        for div in content:
            pars = div.select("p")
            ps += pars
        content = self.removeOtherGarbage(content, *garbage_arr)
        arr = self.handle_ps(ps) # strs=strs, arr_of_strs_to_remove_within_ps=arr_of_strs_to_remove_within_ps
        (dct, article_data) = self.addToDictAndCreateClass(*data_arr, arr)

        return (dct, article_data)

    # Method for MSNBC:
    def MSNBC(self, src="MSNBC"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.article-hero__headline")
        descr = self.select_descr(soup, selector=".article-dek")
        date = self.select_date(soup, selector="[itemprop='datePublished']")
        author = self.select_author(soup, selector=".article-byline__name")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.inlineVideo___3Rd2d', '.contentBody___1zFVF', '.mv8']
        content_selector = ".article-body__content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for USA Today:
    def USAToday(self, src="USA Today"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".gnt_pr h1")
        descr = self.select_descr(soup, selector=".article-dek")
        date = soup.select(".gnt_ar_dt")[0]["aria-label"]
        author = self.select_author(soup, selector=".gnt_ar_by_a")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote']
        content_selector = ".gnt_ar_b"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for NPR News:
    def NPRNews(self, src="NPR News"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".storytitle h1")
        descr = self.select_descr(soup, selector=".article-dek") # .dateblock
        date = self.select_date(soup, selector=".dateblock")
        author = self.select_author(soup, selector=".byline__name")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.caption-wrap', '.caption', '.slug', '.bucketwrap']
        content_selector = ".storytext"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Tower:
    def TheTower(self, src="The Tower"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.ttl")
        descr = self.select_descr(soup, selector=".pf-content h2") # .dateblock
        date = self.select_date(soup, selector=".dateblock")
        author = self.select_author(soup, selector=".author-box .fn")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.wp-caption-text']
        content_selector = ".entry"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Center for American Progress Action Fund:
    def APA(self, src="Center for American Progress Action Fund"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.entry-title")
        descr = self.select_descr(soup, selector=".overview-container p") # .dateblock
        date = self.select_date(soup, selector="time.published")
        author = self.select_author(soup, selector=".byline")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.wp-caption-text']
        content_selector = ".entry-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The National:
    def TheNational(self, src="The National"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.headline")
        descr = None
        date = None
        soup = self.removeOtherGarbage(soup, *[".twitter-button"])
        author = self.select_author(soup, selector=".author-name a")
        try:
            if author.strip()[-1] == ",":
                author = author[:-2]
        except:
            pass
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.wp-caption-text']
        content_selector = ".article-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for CEO Magazine:
    def CEOMagazine(self, src="CEO Magazine"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".news-content h4")
        descr = self.select_descr(soup, selector=".overview-container p")
        date = self.select_date(soup, selector=".news-content h5")
        author = self.select_author(soup, selector=".byline")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.wp-caption-text', 'nav', '.navbar-collapse', '#menu-main-menu', 'form', '.main-modal-content', '.widget-home', '.share-this', '.news-content h4', '.news-content h5']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr, breakers=["YOU MAY ALSO LIKE"])
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for The CEO Magazine:
    def TheCEOMagazine(self, src="The CEO Magazine"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.post-title")
        descr = self.select_descr(soup, selector=".lead") # .dateblock
        date = self.select_date(soup, selector=".post-date")
        try:
            date = date.replace(title, "").split("›")[-1]
        except:
            pass
        author = self.select_author(soup, selector=".post-author-name")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.wp-caption-text']
        content_selector = ".entry-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Farnam Street:
    def FarnamStreet(self, src="Farnam Street"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.entry-title")
        descr = self.select_descr(soup, selector=".lead") # .dateblock
        date = self.select_date(soup, selector=".post-date")
        author = self.select_author(soup, selector=".post-author-name")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', '.wp-caption-text']
        try:
            content_selector = ".entry-content"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        except:
            content_selector = "body"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for CTech:
    def CTech(self, src="CTech"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".art-content h1")
        descr = self.select_descr(soup, selector=".art-sub-title")
        date = self.select_date(soup, selector=".art-publish-date")
        author = self.select_author(soup, selector=".art-author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.wp-caption-text', '.art-tags-list', '.headerList', '.header-user-profile']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr, breakers=["YOU MAY ALSO LIKE"])
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Jewish Business News:
    def JewishBusinessNews(self, src="Jewish Business News"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".post h2")
        descr = self.select_descr(soup, selector=".post .entry")
        date = self.select_descr(soup, selector="#datemeta_l")
        author = self.select_author(soup, selector=".gnt_ar_by_a")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.comments-box']
        content_selector = "#content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for TAdviser:
    def TAdviser(self, src="TAdviser"):
        (source, url, soup) = self.handle_meta(src)
        data_arr = [source, url, soup.title.text.strip(), None, None, None]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.comments-box']
        content_selector = "[itemprop='text']"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Nikkei Asia:
    def NikkeiAsia(self, src="Nikkei Asia"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".article-header__title")
        descr = self.select_descr(soup, selector=".article-header__sub-title")
        date = self.select_descr(soup, selector="time.timestamp__time")
        author = self.select_author(soup, selector=".article__author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.comments-box']
        content_selector = ".ezrichtext-field"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Alchetron:
    def Alchetron(self, src="Alchetron"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".article-header__title")
        descr = self.select_descr(soup, selector=".article-header__sub-title")
        date = self.select_descr(soup, selector="time.timestamp__time")
        author = self.select_author(soup, selector=".article__author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, .alchetronTopicHeaderClass, .citation.book, #tronWikiArticleLink, .alchetronInfoTable.infobox.vcard .topicDataElement'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.mw-headline', '#tronListHeader']
        content_selector = "body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Reveal News:
    def Reveal(self, src="Reveal News"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="#content_body h2")
        descr = self.select_descr(soup, selector="#content_body p")
        date = self.select_descr(soup, selector=".date")
        author = self.select_author(soup, selector=".module-article-meta")
        try:
            author = author.replace(date, "").strip()
        except:
            pass
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, .gist'
        garbage_arr = ['figure', 'figcaption', 'aside', 'header', 'footer', 'blockquote', '.republish-modal-open-container', '#republish-modal', '.reveal-widget', '.newsletter', '.newsletter-title']
        content_selector = "#content_body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for American Banker:
    def AmericanBanker(self, src="American Banker"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.ArticlePage-headline")
        descr = self.select_descr(soup, selector=".overview-container p")
        date = self.select_date(soup, selector=".ArticlePage-datePublished")
        author = self.select_author(soup, selector=".ArticlePage-authorName")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.wp-caption-text']
        if "/list/" in url:
            content_selector = ".RichTextArticleBody"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
            soup = self.removeOtherGarbage(soup, *garbage_arr)
            arr = []
            blocks = soup.select('.ListicleCardRow-cards-card')
            for block in blocks:
                ttl = block.select('.PromoListicle-title')[0].text.strip()
                txt = block.select('.PromoListicle-description')[0].text.strip()
                full = ttl + txt
                arr.append(full)
            dct['text'] += arr
            return (dct, article_data)
        content_selector = ".RichTextArticleBody"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Rand:
    def Rand(self, src="Rand"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".post-heading h1")
        descr = self.select_descr(soup, selector=".overview-container p") # .dateblock
        date = self.select_date(soup, selector=".date")
        author = self.select_author(soup, selector="article.blog .date-author-wrap .authors")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.caption', '.credit', '.pull-quote', '.social-media-buttons']
        content_selector = ".body-text"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Mercury News:
    def TheMercuryNews(self, src="The Mercury News"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".entry-title")
        descr = self.select_descr(soup, selector=".subheadline") # .dateblock
        date = self.select_date(soup, selector=".meta .time")
        author = self.select_author(soup, selector=".meta .author-name")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.caption', '.credit', '.pull-quote', '.social-media-buttons']
        content_selector = ".article-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Complex:
    def Complex(self, src="Complex"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="header.article-header h1")
        descr = self.select_descr(soup, selector=".subheadline") # .dateblock
        date = self.select_date(soup, selector="time.info-row__datetime")
        author = self.select_author(soup, selector=".info-row-author .mini-author__name")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.share-this', '.related-articles', '.module-title', '.vidible-max']
        content_selector = ".article-body-main"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Mother Jones:
    def MotherJones(self, src="Mother Jones"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.entry-title")
        descr = self.select_descr(soup, selector="h2.dek") # .dateblock
        date = self.select_date(soup, selector=".time-ago")
        author = self.select_author(soup, selector=".byline .fn")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', '.wp-caption-text']
        content_selector = ".entry-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Tontine Coffee-House:
    def TheTontineCoffeeHouse(self, src="The Tontine Coffee-House"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".page-title")
        date = self.select_date(soup, selector=".date time")
        data_arr = [source, url, title, None, "Daniel DeMatos", date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', '.wp-caption-text']
        content_selector = ".entry-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for HighSnobiety:
    def HighSnobiety(self, src="HighSnobiety"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="main article h2")
        descr = self.select_descr(soup, selector="h2.dek")
        date = self.select_date(soup, selector="main article time")
        author = self.select_author(soup, selector=".author___3iaaJ")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', '.wp-caption-text', 'blockquote']
        content_selector = ".articleContent___1rlX-"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Cosmopolitan:
    def Cosmopolitan(self, src="Cosmopolitan"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".content-hed")
        descr = self.select_descr(soup, selector=".content-dek")
        date = self.select_date(soup, selector=".content-info-date")
        author = self.select_author(soup, selector=".byline")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', '.wp-caption-text', 'blockquote', '.body-btn-link']
        content_selector = ".article-body-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Like this article? Sign up to our newsletter to get more articles like this delivered straight to your inbox"])
        return (dct, article_data)

    # Method for Trends Magazine MENA:
    def TrendzMENA(self, src="Trends Magazine MENA"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".page_title")
        descr = self.select_descr(soup, selector="h2.dek")
        date = self.select_date(soup, selector=".single_date")
        author = self.select_author(soup, selector=".author___3iaaJ")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', '.wp-caption-text', 'blockquote', '.related', '#comments', '.tagline']
        content_selector = ".page_body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Middle East Eye:
    def MiddleEastEye(self, src="Middle East Eye"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".field-title")
        descr = self.select_descr(soup, selector=".field-field-subhead")
        date = self.select_date(soup, selector=".submitted-date")
        author = self.select_author(soup, selector=".author-name")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', '.wp-caption-text', 'blockquote', '.related', '#comments', '.tagline']
        content_selector = ".field-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for GQ Britain:
    def GQBritain(self, src="GQ Britain"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.BaseText-sc-19af275-0.BaseTitle-sc-19af275-2.Headline-sc-1mp3md8-0.Hed-jniobe-0.ieXHyy")
        author = self.select_author(soup, selector="span.Name-wdo2uk-2.feyehI")
        descr = self.select_descr(soup, selector="p.BaseText-sc-19af275-0.Detail-sc-1me9nov-0.DekText-abvmkk-1.ifulf")
        date = self.select_date(soup, selector="time.BaseText-sc-19af275-0.Label-lpqysz-0.SmallestLabel-lpqysz-1.Wrapper-sc-1bx32fv-0.cGAnDw.sc-10mo5yu-0.caWWuk")
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.MainContentWrapper-s89gjf-14' # .cHneBC
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'blockquote', '.AdWrapperRow-s89gjf-3', '.Detail-sc-1me9nov-0', 'aside', 'img', '.Credit-sc-1nf3byq-0', '.dmEjRM']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=['</param>', 'Click here to see', 'Click here to explore'])
        return (dct, article_data)

    # Method for GQ:
    def GQ(self, src="GQ"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.content-header__row")
        if title == soup.title.text.strip():
            title = self.select_title(soup, selector="h1.content-header__hed")
        author = self.select_author(soup, header_selector=".content-header", selector=".byline__name")
        if author is None:
            try:
                a_links = []
                authors = soup.select('.content-header')[0].find_all('span', {'itemprop': 'name'})
                [a_links.append(a.text.strip()) for a in authors if a.text.strip() not in a_links]
                author = ", ".join(a_links)
            except:
                author = None
        descr = self.select_descr(soup, selector="div.content-header__row.content-header__dek")
        date = self.select_date(soup, selector=".content-header__publish-date")
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'div.content-background'
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, div.heading-h2, div.heading-h3, div.heading-h4, div.heading-h5, div.heading-h6'
        garbage_arr = ['figure', 'figcaption', 'figcaption span p', 'blockquote', 'aside', '.content-card-embed']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for GQ Italia:
    def GQItalia(self, src="GQ Italia"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="[data-test-id='Hed']")
        descr = self.select_descr(soup, selector="[data-test-id='DekText']")
        date = self.select_date(soup, selector="[data-test-id='PublishedDate']")
        author = self.select_author(soup, selector="[data-test-id='Name']")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', "[data-test-id='Caption']", "[data-test-id='Credit']"]
        try:
            content_selector = "[data-test-id='ArticleBodyContent']"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        except:
            content_selector = "body"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for GQ Germany:
    def GQDE(self, src="GQ Germany"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="[data-test-id='Hed']")
        if title == soup.title.text.strip():
            title = self.select_title(soup, selector="#content-wrapper header h1")
        descr = self.select_descr(soup, selector="[data-test-id='DekText']")
        if descr is None:
            descr = self.select_descr(soup, selector="summary")
        date = self.select_date(soup, selector="[data-test-id='PublishedDate']")
        if date is None:
            date = self.select_date(soup, selector=".date")
        author = self.select_author(soup, selector="[data-test-id='Name']")
        if author is None:
            author = self.select_author(soup, selector=".author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', "[data-test-id='Caption']", "[data-test-id='Credit']", "#site-header", "#site-footer", ".components-taxonomy", '.kicker', '.blocks']
        try:
            content_selector = "[data-test-id='ArticleBodyContent']"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Um diese Inhalte zu sehen, akzeptieren Sie bitte unsere Cookies."])
        except:
            content_selector = "body"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Um diese Inhalte zu sehen, akzeptieren Sie bitte unsere Cookies."])
        return (dct, article_data)

    # Method for GQ Thailand:
    def GQThailand(self, src="GQ Thailand"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".article-detail-content h2")
        author = self.select_author(soup, selector=".content-type-details_author")
        descr = self.select_descr(soup, selector=".content-type-details_author")
        date = self.select_date(soup, selector=".date")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.head_newest', '.article-more', '.box-the-last', '.content-footer', '.tag']
        content_selector = ".article-detail-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for GQ Türkiye:
    def GQTR(self, src="GQ Türkiye"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".detail-header h1")
        author = self.select_author(soup, selector=".spot-text")
        descr = self.select_descr(soup, selector=".content-type-details_author")
        date = self.select_date(soup, selector=".date")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.breadcrumb', '.date', '.spot-text']
        content_selector = ".contents"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for GQ Россия:
    def GQRU(self, src="GQ Россия"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="[data-test-id='Hed']")
        descr = self.select_descr(soup, selector="[data-test-id='DekText']")
        date = self.select_date(soup, selector="[data-test-id='PublishedDate']")
        author = self.select_author(soup, selector="[data-test-id='Name']")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', "[data-test-id='Caption']", "[data-test-id='Credit']"]
        try:
            content_selector = "[data-test-id='ArticleBodyContent']"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        except:
            content_selector = "body"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for GQ México:
    def GQMX(self, src="GQ México"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="[data-test-id='Hed']")
        descr = self.select_descr(soup, selector="[data-test-id='DekText']")
        date = self.select_date(soup, selector="[data-test-id='PublishedDate']")
        author = self.select_author(soup, selector="[data-test-id='Name']")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', "[data-test-id='Caption']", "[data-test-id='Credit']"]
        try:
            content_selector = "[data-test-id='ArticleBodyContent']"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        except:
            content_selector = "body"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for GQ Taiwan:
    def GQTW(self, src="GQ Taiwan"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="[data-test-id='Hed']")
        descr = self.select_descr(soup, selector="[data-test-id='DekText']")
        date = self.select_date(soup, selector="[data-test-id='PublishedDate']")
        author = self.select_author(soup, selector="[data-test-id='Name']")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', "[data-test-id='Caption']", "[data-test-id='Credit']"]
        try:
            content_selector = "[data-test-id='ArticleBodyContent']"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        except:
            content_selector = "body"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for GQ Portugal:
    def GQPT(self, src="GQ Portugal"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="article h1")
        descr = self.select_descr(soup, selector=".perex")
        date = self.select_date(soup, selector=".article-category span")
        author = self.select_author(soup, selector="article .author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', "[data-test-id='Caption']", "[data-test-id='Credit']"]
        try:
            content_selector = ".readzone-is"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        except:
            content_selector = "body"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for GQ Korea:
    def GQKR(self, src="GQ Korea"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="article h1")
        descr = self.select_descr(soup, selector=".perex")
        date = self.select_date(soup, selector=".article-category span")
        author = self.select_author(soup, selector="article .author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.wp-caption-text']
        try:
            content_selector = ".post-content"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        except:
            content_selector = "body"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for GQ Japan:
    def GQJP(self, src="GQ Japan"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="[data-test-id='Hed']")
        descr = self.select_descr(soup, selector="[data-test-id='DekText']")
        date = self.select_date(soup, selector="[data-test-id='PublishedDate']")
        author = self.select_author(soup, selector="[data-test-id='Name']")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', "[data-test-id='Caption']", "[data-test-id='Credit']", '.l-header']
        try:
            content_selector = "[data-test-id='ArticleBodyContent']"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        except:
            content_selector = "body"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for GQ India:
    def GQIN(self, src="GQ India"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="[data-test-id='Hed']")
        descr = self.select_descr(soup, selector="[data-test-id='DekText']")
        date = self.select_date(soup, selector="[data-test-id='PublishedDate']")
        author = self.select_author(soup, selector="[data-test-id='Name']")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', "[data-test-id='Caption']", "[data-test-id='Credit']", '.l-header']
        try:
            content_selector = "[data-test-id='ArticleBodyContent']"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        except:
            content_selector = "body"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for GQ France:
    def GQFR(self, src="GQ France"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="[data-test-id='Hed']")
        descr = self.select_descr(soup, selector="[data-test-id='DekText']")
        date = self.select_date(soup, selector="[data-test-id='PublishedDate']")
        author = self.select_author(soup, selector="[data-test-id='Name']")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', "[data-test-id='Caption']", "[data-test-id='Credit']", '.l-header']
        try:
            content_selector = "[data-test-id='ArticleBodyContent']"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        except:
            content_selector = "body"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for GQ España:
    def GQES(self, src="GQ España"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="[data-test-id='Hed']")
        descr = self.select_descr(soup, selector="[data-test-id='DekText']")
        date = self.select_date(soup, selector="[data-test-id='PublishedDate']")
        author = self.select_author(soup, selector="[data-test-id='Name']")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', "[data-test-id='Caption']", "[data-test-id='Credit']", '.l-header']
        try:
            content_selector = "[data-test-id='ArticleBodyContent']"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        except:
            content_selector = "body"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for GQ China:
    def GQCN(self, src="GQ China"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.h1")
        descr = self.select_descr(soup, selector="p.p")
        date = self.select_date(soup, selector=".signature")
        author = self.select_author(soup, selector=".signature")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside']
        try:
            content_selector = ".content"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        except:
            content_selector = "body"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for GQ South Africa:
    def GQSA(self, src="GQ South Africa"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="main article h1")
        date = self.select_date(soup, selector=".meta p")
        author = self.select_author(soup, selector=".meta p")
        try:
            author = author.replace(date, "").replace(",", "").strip()
        except:
            pass
        data_arr = [source, url, title, None, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', "[data-test-id='Caption']", "[data-test-id='Credit']", ".sharethis-inline-share-buttons", ".article-tags"]
        try:
            content_selector = "[itemprop='articleBody']"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        except:
            content_selector = "body"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for GQ Brasil:
    def GQBR(self, src="GQ Brasil"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".featured-text h1")
        descr = self.select_descr(soup, selector=".featured-text h2")
        date = self.select_date(soup, selector=".authorship time")
        author = self.select_author(soup, selector=".authorship li")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', "article header", '.social-share']
        content_selector = ".protected-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Tatler:
    def Tatler(self, src="Tatler"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.a-header__title")
        author = self.select_author(soup, selector=".a-header__byline-name")
        date = self.select_date(soup, selector=".a-header__date")
        descr = self.select_date(soup, selector='.a-header__teaser')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'blockquote', 'aside', 'footer', 'header', 'nav', '.a-share', '.a-share__list-item', '.c-card-section-wrapper', '.c-card-section__card-listitem', '.c-nav__social-list', '.c-cookie-warning', '.a11y__main-content-anchor']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr)
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Economic Times:
    def EconomicTimes(self, src="Economic Times"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.a-header__title")
        author = self.select_author(soup, selector=".a-header__byline-name")
        date = self.select_date(soup, selector=".a-header__date")
        descr = self.select_date(soup, selector='.a-header__teaser')
        arr = [soup.select('.artText')[0].text.strip()]
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for The India Times:
    def TheIndiaTimes(self, src="The India Times"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="main h1")
        descr = self.select_descr(soup, selector=".highlight")
        date = self.select_date(soup, selector=".author-strip-date")
        author = self.select_author(soup, selector=".author-strip-editor")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', '.wp-caption-text', 'blockquote', '.caption-image-wrapper']
        content_selector = "#article-description-0"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Swissquote:
    def Swissquote(self, src="Swissquote"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".field-title-field")
        descr = self.select_descr(soup, selector=".highlight")
        date = self.select_date(soup, selector=".field-pub-date")
        author = self.select_author(soup, selector=".field-pubauthor")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', '.wp-caption-text', 'blockquote', '.caption-image-wrapper', '.disclaimer-content', 'nav', '.research-report-header']
        if "/morning-news/" in url:
            arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr)
            article_data = SingleArticle(source, url, title, descr, author, date, arr)
            dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
            return (dct, article_data)
        content_selector = ".contentblock-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Schweizerische Bankiervereinigung (The Swiss Bankers Association):
    def SwissBanking(self, src="Schweizerische Bankiervereinigung (The Swiss Bankers Association)"):
        (source, url, soup) = self.handle_meta(src)
        soup = self.removeOtherGarbage(soup, *[".email"])
        title = self.select_title(soup, selector="#content .documentFirstHeading")
        descr = self.select_descr(soup, selector="#content .description")
        date = self.select_date(soup, selector="#content .documentDate")
        author = self.select_author(soup, selector="main section.portlet .portletContent .contributorInfo a")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', '.wp-caption-text', 'blockquote', '.caption-image-wrapper', '.factBox', '.relatedItems', '#viewlet-below-content-body']
        content_selector = "#content-core"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Vogue - Business:
    def VogueBusiness(self, src="Vogue Business"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="[data-test-id='Hed']")
        descr = self.select_descr(soup, selector="[data-test-id='Dek']")
        date = self.select_date(soup, selector="[data-test-id='TopperMeta'] [data-test-id='PublishedDate']")
        author = self.select_author(soup, selector="[data-test-id='TopperMeta'] [data-test-id='Byline']")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', "[data-test-id='Caption']", "[data-test-id='Credit']", "[data-test-id='ArticleBodyGallery']", ".UnorderedListWrapper-l408ef-0.kSSOIN", "[data-test-id='ArticleBodyTeaser']", '#SlimNavContent']
        content_selector = "[data-test-id='ArticleBodyContent']"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Nuestros periodistas recomiendan de manera independiente productos y servicios que puedes comprar o adquirir en Internet. Cada vez que compras a través de algunos enlaces añadidos en nuestros textos, Condenet Iberica S.L. puede recibir una comisión. Lea nuestra política de afiliación"])
        return (dct, article_data)

    # Method for Vogue - Italia:
    def VogueItalia(self, src="Vogue - Italia"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="[data-test-id='Hed']")
        descr = self.select_descr(soup, selector="[data-test-id='Dek']")
        date = self.select_date(soup, selector="[data-test-id='TopperMeta'] [data-test-id='PublishedDate']")
        author = self.select_author(soup, selector="[data-test-id='TopperMeta'] [data-test-id='Byline']")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', "[data-test-id='Caption']", "[data-test-id='Credit']", "[data-test-id='ArticleBodyGallery']", ".UnorderedListWrapper-l408ef-0.kSSOIN", "[data-test-id='ArticleBodyTeaser']", '#SlimNavContent']
        content_selector = "[data-test-id='ArticleBodyContent']"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Nuestros periodistas recomiendan de manera independiente productos y servicios que puedes comprar o adquirir en Internet. Cada vez que compras a través de algunos enlaces añadidos en nuestros textos, Condenet Iberica S.L. puede recibir una comisión. Lea nuestra política de afiliación"])
        return (dct, article_data)

    # Method for Vogue - España:
    def VogueES(self, src="Vogue - España"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="[data-test-id='Hed']")
        descr = self.select_descr(soup, selector="[data-test-id='Dek']")
        date = self.select_date(soup, selector="[data-test-id='TopperMeta'] [data-test-id='PublishedDate']")
        author = self.select_author(soup, selector="[data-test-id='TopperMeta'] [data-test-id='Byline']")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', "[data-test-id='Caption']", "[data-test-id='Credit']", "[data-test-id='ArticleBodyGallery']", ".UnorderedListWrapper-l408ef-0.kSSOIN", "[data-test-id='ArticleBodyTeaser']", '#SlimNavContent']
        content_selector = "[data-test-id='ArticleBodyContent']"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Nuestros periodistas recomiendan de manera independiente productos y servicios que puedes comprar o adquirir en Internet. Cada vez que compras a través de algunos enlaces añadidos en nuestros textos, Condenet Iberica S.L. puede recibir una comisión. Lea nuestra política de afiliación"])
        return (dct, article_data)

    # Method for Vogue - Paris:
    def VogueFR(self, src="Vogue - Paris"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="[data-test-id='Hed']")
        descr = self.select_descr(soup, selector="[data-test-id='Dek']")
        date = self.select_date(soup, selector="[data-test-id='TopperMeta'] [data-test-id='PublishedDate']")
        author = self.select_author(soup, selector="[data-test-id='TopperMeta'] [data-test-id='Byline']")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', "[data-test-id='Caption']", "[data-test-id='Credit']", "[data-test-id='ArticleBodyGallery']", ".UnorderedListWrapper-l408ef-0.kSSOIN", "[data-test-id='ArticleBodyTeaser']", '#SlimNavContent']
        content_selector = "[data-test-id='ArticleBodyContent']"#[data-test-id='ArticleBodyContent']
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Nuestros periodistas recomiendan de manera independiente productos y servicios que puedes comprar o adquirir en Internet. Cada vez que compras a través de algunos enlaces añadidos en nuestros textos, Condenet Iberica S.L. puede recibir una comisión. Lea nuestra política de afiliación"])
        return (dct, article_data)

    # Method for Vogue - México:
    def VogueMX(self, src="Vogue - México"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="[data-test-id='Hed']")
        descr = self.select_descr(soup, selector="[data-test-id='Dek']")
        date = self.select_date(soup, selector="[data-test-id='TopperMeta'] [data-test-id='PublishedDate']")
        author = self.select_author(soup, selector="[data-test-id='TopperMeta'] [data-test-id='Byline']")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', "[data-test-id='Caption']", "[data-test-id='Credit']", "[data-test-id='ArticleBodyGallery']", ".UnorderedListWrapper-l408ef-0.kSSOIN", "[data-test-id='ArticleBodyTeaser']", '#SlimNavContent']
        content_selector = "[data-test-id='ArticleBodyContent']"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Vogue - Business - España:
    def VogueBusinessES(self, src="Vogue - Business - España"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="[itemprop='headline']")
        descr = self.select_descr(soup, selector="[itemprop='alternativeHeadline'] p")
        date = self.select_date(soup, selector=".header .publication-date")
        author = self.select_author(soup, selector=".header .author_content")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', "[data-test-id='Caption']", "[data-test-id='Credit']", "[data-test-id='ArticleBodyGallery']", ".UnorderedListWrapper-l408ef-0.kSSOIN", 'nav', '.nav_menu', '.header', '.tags', '#header_scroll', '.ads', '.share', '.relacionados', '.social_icons', '.social', '#SlimNavContent']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr)
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Vogue - U.S.:
    def VogueUS(self, src="Vogue - U.S."):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".content-header__row.content-header__hed")
        descr = self.select_descr(soup, selector="[data-test-id='Dek']")
        date = self.select_date(soup, selector="time.content-header__publish-date")
        author = self.select_author(soup, selector=".byline__name-link")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote']#, "[data-test-id='Caption']", "[data-test-id='Credit']", "[data-test-id='ArticleBodyGallery']", ".UnorderedListWrapper-l408ef-0.kSSOIN"]
        content_selector = "article.article"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Vogue - Brasil:
    def VogueBR(self, src="Vogue - Brasil"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".featured-text h1")
        descr = self.select_descr(soup, selector=".featured-text h2")
        date = self.select_date(soup, selector=".authorship time")
        author = self.select_author(soup, selector=".authorship li")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', "article header", '.social-share']
        content_selector = ".protected-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Vogue - Britain:
    def VogueUK(self, src="Vogue - Britain"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="[data-test-id='Hed']")
        descr = self.select_descr(soup, selector="[data-test-id='Dek']")
        date = self.select_date(soup, selector="[data-test-id='TopperMeta'] [data-test-id='PublishedDate']")
        author = self.select_author(soup, selector="[data-test-id='TopperMeta'] [data-test-id='Byline']")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', "[data-test-id='Caption']", "[data-test-id='Credit']", "[data-test-id='ArticleBodyGallery']", ".UnorderedListWrapper-l408ef-0.kSSOIN", "[data-test-id='ArticleBodyTeaser']", '#SlimNavContent']
        content_selector = "[data-test-id='ArticleBodyContent']"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["More from British Vogue:"])
        return (dct, article_data)

    # Method for Vogue - China:
    def VogueCN(self, src="Vogue - China"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".artitle")
        descr = self.select_descr(soup, selector=".art-guidecont")
        date = self.select_date(soup, selector=".art-author")
        author = self.select_author(soup, selector=".art-author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', "[data-test-id='Caption']", "[data-test-id='Credit']", "[data-test-id='ArticleBodyGallery']", ".UnorderedListWrapper-l408ef-0.kSSOIN", "[data-test-id='ArticleBodyTeaser']"]
        content_selector = ".artile-bodycont"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Vogue - Czechoslovakia:
    def VogueCZ(self, src="Vogue - Czechoslovakia"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".ArticleDefaultPage__HeadlineWrapper-xupu1u-1.kihOWc.hq")
        descr = self.select_descr(soup, selector=".ArticleDefaultPage__HeadlineWrapper-xupu1u-1.kihOWc")
        date = self.select_date(soup, selector=".PublishedAt__Text-xmxhot-0.gXEWkx")
        author = self.select_author(soup, selector=".ArticleAuthor__Component-sc-4vhbma-0 .Note__Component-sc-176s80f-1.kUOVCp")
        data_arr = [source, url, title, descr, author, date]
        selectors = '.PlainText__Paragraph-sc-1mb4yz4-0.dgxAmC, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.Tags__Component-sc-1rss0du-0.guVCKX', '.ArticleLink__Component-sc-1t3da42-0.gohRPL']
        content_selector = ".Layout__Content-ukbg15-0.fMVlIl"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Vogue - Russia:
    def VogueRU(self, src="Vogue - Russia"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="[data-test-id='Hed']")
        descr = self.select_descr(soup, selector="[data-test-id='Dek']")
        date = self.select_date(soup, selector="[data-test-id='TopperMeta'] [data-test-id='PublishedDate']")
        author = self.select_author(soup, selector="[data-test-id='TopperMeta'] [data-test-id='Byline']")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', "[data-test-id='Caption']", "[data-test-id='Credit']", "[data-test-id='ArticleBodyGallery']", ".UnorderedListWrapper-l408ef-0.kSSOIN", "[data-test-id='ArticleBodyTeaser']", '#SlimNavContent']
        content_selector = "[data-test-id='ArticleBodyContent']"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["More from British Vogue:"])
        return (dct, article_data)

    # Method for Vogue - Singapore:
    def VogueSG(self, src="Vogue - Singapore"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".entry-title")
        descr = self.select_descr(soup, selector=".entry-excerpt")
        date = self.select_date(soup, selector=".entry-date")
        author = self.select_author(soup, selector=".entry-author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.entry-related', '.editions', '.footer-subscribe-magazine', '#menu-main-menu', '.menu-main-menu-container', '.genesis-skip-link', '#SlimNavContent']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr)
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Vogue - Taiwan:
    def VogueTW(self, src="Vogue - Taiwan"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="[data-test-id='Hed']")
        descr = self.select_descr(soup, selector="[data-test-id='Dek']")
        date = self.select_date(soup, selector="[data-test-id='TopperMeta'] [data-test-id='PublishedDate']")
        author = self.select_author(soup, selector="[data-test-id='TopperMeta'] [data-test-id='Byline']")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', "[data-test-id='Dek']", "[data-test-id='Hed']", 'blockquote', "[data-test-id='Caption']", "[data-test-id='Credit']", "[data-test-id='TopperCredit']", "[data-test-id='ArticleBodyGallery']", ".UnorderedListWrapper-l408ef-0.kSSOIN", "[data-test-id='ArticleBodyTeaser']", '#SlimNavContent']
        content_selector = "[data-test-id='ArticleBodyContent']"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["©"])
        return (dct, article_data)

    # Method for Vogue - Thailand:
    def VogueTH(self, src="Vogue - Thailand"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="[data-test-id='Hed']")
        descr = self.select_descr(soup, selector="[data-test-id='Dek']")
        date = self.select_date(soup, selector="[data-test-id='TopperMeta'] [data-test-id='PublishedDate']")
        author = self.select_author(soup, selector="[data-test-id='TopperMeta'] [data-test-id='Byline']")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', "[data-test-id='Dek']", "[data-test-id='Hed']", 'blockquote', "[data-test-id='Caption']", "[data-test-id='Credit']", "[data-test-id='TopperCredit']", "[data-test-id='ArticleBodyGallery']", ".UnorderedListWrapper-l408ef-0.kSSOIN", "[data-test-id='ArticleBodyTeaser']", '#SlimNavContent']
        content_selector = ".content_box_detail"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Vogue - Türkiye:
    def VogueTR(self, src="Vogue - Türkiye"):
        (source, url, soup) = self.handle_meta(src)
        title = soup.title.text.strip()
        descr = None
        date = self.select_date(soup, selector=".subinfo")
        author = None
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', "[data-test-id='Dek']", "[data-test-id='Hed']", 'blockquote', '.subinfo', '.photo_credit']
        content_selector = ".text"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Vogue - Germay:
    def VogueDE(self, src="Vogue - Germany"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="[data-test-id='Hed']")
        descr = self.select_descr(soup, selector="[data-test-id='Dek']")
        date = self.select_date(soup, selector="[data-test-id='TopperMeta'] [data-test-id='PublishedDate']")
        author = self.select_author(soup, selector="[data-test-id='TopperMeta'] [data-test-id='Byline']")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', "[data-test-id='Caption']", "[data-test-id='Credit']", "[data-test-id='ArticleBodyGallery']", ".UnorderedListWrapper-l408ef-0.kSSOIN", "[data-test-id='ArticleBodyTeaser']", '#SlimNavContent']
        content_selector = "[data-test-id='ArticleBodyContent']"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Mehr bei VOGUE", "Das könnte Sie auch interessieren:"])
        return (dct, article_data)

    # Method for Vogue - Greece:
    def VogueGR(self, src="Vogue - Greece"):
        (source, url, soup) = self.handle_meta(src)
        soup = self.removeOtherGarbage(soup, *[".read-more-section .jet-listing-dynamic-meta__author.jet-listing-dynamic-meta__item"])
        title = self.select_title(soup, selector="h1.elementor-heading-title.elementor-size-default")
        descr = self.select_descr(soup, selector=".theme-post-excerpt.default")
        date = self.select_date(soup, selector=".elementor-post-info__item--type-date")
        author = self.select_author(soup, selector=".authorname")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.elementor-text-editor', '.elementor-clearfix', 'nav', '.read-more-section', '.elementor-hidden-tablet']
        content_selector = "body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Vogue - Hong Kong:
    def VogueHK(self, src="Vogue - Hong Kong"):
        (source, url, soup) = self.handle_meta(src)
        soup = self.removeOtherGarbage(soup, *[".read-more-section .jet-listing-dynamic-meta__author.jet-listing-dynamic-meta__item"])
        title = self.select_title(soup, selector="h1.elementor-heading-title.elementor-size-default")
        descr = self.select_descr(soup, selector=".theme-post-excerpt.default")
        date = self.select_date(soup, selector=".elementor-post-info__item--type-date")
        author = self.select_author(soup, selector=".authorname")
        data_arr = [source, url, title, descr, author, date] # 繼續使用此網站即表示您同意
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.elementor-text-editor', '.elementor-clearfix', 'nav', '.read-more-section', '.elementor-hidden-tablet', '.editor__read-next', '.popup-cookies', '.popup-subscribe-btn', '.article__info', '.editor__read-next']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr, dont_append_keys=["提供您的電子郵件地址即表示您同意我們的隱私政策."])
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Vogue - India:
    def VogueIN(self, src="Vogue - India"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="[data-test-id='Hed']")
        descr = self.select_descr(soup, selector="[data-test-id='Dek']")
        date = self.select_date(soup, selector="[data-test-id='TopperMeta'] [data-test-id='PublishedDate']")
        author = self.select_author(soup, selector="[data-test-id='TopperMeta'] [data-test-id='Byline']")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', "[data-test-id='Caption']", "[data-test-id='Credit']", "[data-test-id='ArticleBodyGallery']", ".UnorderedListWrapper-l408ef-0.kSSOIN", "[data-test-id='ArticleBodyTeaser']", '#SlimNavContent']
        content_selector = "[data-test-id='ArticleBodyContent']"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Vogue - Japan:
    def VogueJP(self, src="Vogue - Japan"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="[data-test-id='Hed']")
        descr = self.select_descr(soup, selector="[data-test-id='Dek']")
        date = self.select_date(soup, selector="[data-test-id='TopperMeta'] [data-test-id='PublishedDate']")
        author = self.select_author(soup, selector="[data-test-id='TopperMeta'] [data-test-id='Byline']")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', "[data-test-id='Caption']", "[data-test-id='Credit']", "[data-test-id='ArticleBodyGallery']", ".UnorderedListWrapper-l408ef-0.kSSOIN", "[data-test-id='ArticleBodyTeaser']", '#SlimNavContent']
        content_selector = "[data-test-id='ArticleBodyContent']"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Vogue - Nederland:
    def VogueNL(self, src="Vogue - Nederland"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".content-hed")
        descr = self.select_descr(soup, selector=".content-dek")
        date = self.select_date(soup, selector=".content-info-date")
        author = self.select_author(soup, selector=".byline .byline-name")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', "[data-test-id='Caption']", "[data-test-id='Credit']", "[data-test-id='ArticleBodyGallery']", ".UnorderedListWrapper-l408ef-0.kSSOIN", "[data-test-id='ArticleBodyTeaser']", '#SlimNavContent']
        try:
            content_selector = ".article-body-content"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        except:
            selectors += ', .listicle-slide-hed-number, .listicle-slide-hed-text'
            content_selector = ".content-container"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Vogue - Korea:
    def VogueKR(self, src="Vogue - Korea"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".entry-title")
        descr = None
        date = None
        author = None
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.wp-caption-text']
        try:
            content_selector = ".post-content"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        except:
            content_selector = "body"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Vogue - Polska:
    def VoguePL(self, src="Vogue - Polska"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.maintitle")
        descr = self.select_descr(soup, selector="p.description")
        date = self.select_date(soup, selector="div.date")
        author = self.select_author(soup, selector="div.author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', "[data-test-id='Caption']", "[data-test-id='Credit']", "[data-test-id='ArticleBodyGallery']", ".UnorderedListWrapper-l408ef-0.kSSOIN", "[data-test-id='ArticleBodyTeaser']", '#SlimNavContent']
        content_selector = ".article-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Vogue - Portugal:
    def VoguePT(self, src="Vogue - Portugal"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="article h1")
        descr = self.select_descr(soup, selector=".perex")
        date = self.select_date(soup, selector=".article-category span")
        author = self.select_author(soup, selector="article .author")
        if title == soup.title.text.strip():
            title = self.select_title(soup, selector=".article-page h1")
        if descr is None:
            descr = self.select_descr(soup, selector=".perex")
        if date is None or len(date) < 2:
            date = self.select_date(soup, selector=".article2-title span")
        if author is None or len(author) < 2:
            author = self.select_author(soup, selector=".article-page .author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', "[data-test-id='Caption']", "[data-test-id='Credit']"]
        try:
            content_selector = ".readzone-is"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        except:
            content_selector = "body"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Nine Network News:
    def TheNine(self, src="The Nine Network News"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.article__headline")
        descr = self.select_descr(soup, selector="p.description")
        date = self.select_date(soup, selector="time.text--byline")
        author = self.select_author(soup, selector="div.author .text--author")
        selectors = '.block-content'#'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.article__social', '.article__share', '.article__related', '.article__tags']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr)
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for World Wide of Sports:
    def WWOS(self, src="World Wide of Sports"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.article__headline")
        descr = self.select_descr(soup, selector="p.description")
        date = self.select_date(soup, selector="time.text--byline")
        author = self.select_author(soup, selector="div.author .text--author")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.article__social', '.article__share', '.article__related', '.article__tags', 'nav', '.content-feed', '.article__breadcrumbs', '.footer-netkit', '.ninemsn-light-footer']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".article__body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for 9Honey:
    def Honey(self, src="9Honey"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".Headline__MyHeadline-sc-101n78c-0.kZjpoo")
        descr = self.select_descr(soup, selector="p.description")
        date = self.select_date(soup, selector=".Author__MyAuthor-sc-1gcx9jq-0.hJAFNc time")
        author = self.select_author(soup, selector=".Author__MyAuthor-sc-1gcx9jq-0.hJAFNc a")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.article__social', '.article__share', '.article__related', '.article__tags', 'nav', '.content-feed', '.article__breadcrumbs', '.footer-netkit', '.ninemsn-light-footer']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".component__Body-sc-1xo0jg3-0.zIbye"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Nine Entertainment:
    def NineEnt(self, src="Nine Entertainment"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".Header-sc-1y0pkty-0")
        descr = self.select_descr(soup, selector="p.description")
        date = self.select_date(soup, selector=".ByLine__Container-xc9pav-0")
        try:
            date = date.split("|")[1]
        except:
            pass
        author = self.select_author(soup, selector=".ByLine__AuthorLink-xc9pav-2")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.article__social', '.article__share', '.article__related', '.article__tags', 'nav', '.content-feed', '.article__breadcrumbs', '.footer-netkit', '.ninemsn-light-footer', '.Tags__TagsContainer-sc-11ta7yc-0.hFiRlx', '.SocialSharing__InfoShare-ycxf47-0.QnXei', '.PartnerLink__PartnerLinkContainer-pfcagm-0.dollms', '._3nTeVxtA ']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".article__ArticleContainer-g7ogz4-4"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Nine Finance:
    def NineFinance(self, src="Nine Finance"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.article__headline")
        descr = self.select_descr(soup, selector="p.description")
        author = self.select_author(soup, selector="div.author .text--author")
        soup = self.removeOtherGarbage(soup, *[".text--author"])
        date = self.select_date(soup, selector=".text--byline")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.article__social', '.article__share', '.article__related', '.article__tags', 'nav', '.content-feed', '.article__breadcrumbs', '.footer-netkit', '.ninemsn-light-footer']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".article__body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Valor Econômico:
    def ValorEconomico(self, src="Valor Econômico"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.content-head__title")
        descr = self.select_descr(soup, selector=".subtitle")
        author = self.select_author(soup, selector=".content-publication-data__from")
        date = self.select_date(soup, selector="time[itemprop='datePublished']")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', 'nav', '.content-head', '.content__signa-share']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr)
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Valor Investe:
    def ValorInveste(self, src="Valor Investe"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.content-head__title")
        descr = self.select_descr(soup, selector=".subtitle")
        author = self.select_author(soup, selector=".content-publication-data__from")
        date = self.select_date(soup, selector="time[itemprop='datePublished']")
        selectors = 'p, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', 'nav', '.content-head', '.content__signa-share', '.mais-lidas__header', '.mais-lidas__card', '.mais-lidas__card__title', '.content-media__container', '.content-courses', '.show-table', '.content-media']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr)
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Cronache della Campania:
    def CronachedellaCampania(self, src="Cronache della Campania"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.entry-title")
        descr = self.select_descr(soup, selector="h3")
        author = self.select_author(soup, selector=".entry-meta .entry-author")
        date = self.select_date(soup, selector="time.time.published")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'blockquote']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr, breakers=["Leggi anche:"])
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Fanpage.IT:
    def FanpageIT(self, src="Fanpage.IT"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".art-title h1")
        descr = self.select_descr(soup, selector=".art-subtitle")
        author = self.select_author(soup, selector=".art-autor")
        date = self.select_date(soup, selector=".date-attached")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'blockquote']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".articleContent"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Security Middle East:
    def SecurityMiddleEast(self, src="Security Middle East"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".entry_title")
        descr = self.select_descr(soup, selector=".art-subtitle")
        author = self.select_author(soup, selector=".post_author_link")
        date = self.select_date(soup, selector=".post_text .date")
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'blockquote', '.post_info', '.entry_title', '.ssba']
        soup = self.removeOtherGarbage(soup, *garbage_arr)
        arr = [soup.select(".post_text")[0].text.strip()]
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Harvard Business Review:
    def HBR(self, src="Harvard Business Review"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".article-hed")
        descr = self.select_descr(soup, selector=".article-summary")
        author = self.select_author(soup, selector=".article-author")
        date = self.select_date(soup, selector=".pub-date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.utility--icon-label', 'embedded-video', '.article-sidebar', '.sidebar']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".article-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Entrepreneur:
    def Entrepreneur(self, src="Entrepreneur"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.headline")
        descr = self.select_descr(soup, selector=".art-deck")
        author = self.select_author(soup, selector="[itemprop='name']")
        date = self.select_date(soup, selector="[itemprop='datePublished']")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.block']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".art-v2-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for S&P Global:
    def SP(self, src="S&P Global"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.article__title")
        descr = self.select_descr(soup, selector=".article-highlights")
        author = self.select_author(soup, selector='[data-gtm-action="Author"]')
        date = self.select_date(soup, selector=".meta-data__date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.inset-cta']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".article__content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Global Finance Magazine:
    def GFMag(self, src="Global Finance Magazine"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="#page-title")
        descr = self.select_descr(soup, selector=".leadin")
        author = self.select_author(soup, selector='.vcard .author')
        date = self.select_date(soup, selector=".vcard time")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.inset-cta', 'table']
        data_arr = [source, url, title, descr, author, date]
        content_selector = "article.article-full"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Ars Technica:
    def ArsTechnica(self, src="Ars Technica"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="[itemprop='headline']")
        descr = self.select_descr(soup, selector="[itemprop='description']")
        author = self.select_author(soup, selector=".post-meta [itemprop='name']")
        date = self.select_date(soup, selector=".post-meta time.date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.inset-cta', 'table']
        data_arr = [source, url, title, descr, author, date]
        content_selector = "[itemprop='articleBody']"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The South African:
    def TheSouthAfrican(self, src="The South African"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".jeg_post_title")
        descr = self.select_descr(soup, selector=".jeg_post_subtitle")
        author = self.select_author(soup, selector=".jeg_meta_author a")
        date = self.select_date(soup, selector=".jeg_meta_date a")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.inset-cta', 'table']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".content-inner"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["READ | ", "MUST READ | ", "Also on thesouthafrican.com: "])
        return (dct, article_data)

    # Method for Corriere della Sera:
    def CorrieredellaSera(self, src="Corriere della Sera"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".article-title")
        descr = self.select_descr(soup, selector=".article-subtitle")
        author = self.select_author(soup, selector=".article-signature .writer")
        date = self.select_date(soup, selector=".jeg_meta_date a")
        selectors = '.chapter'  # p.chapter-paragraph, .chapter-title
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.c-modulo-contesto', '.chapter-title']
        if "/economia/" in url:
            selectors = '.body-article .content'
            title = self.select_title(soup, selector=".header-article h1.title")
            author = self.select_author(soup, selector=".header-article .signature")
            date = self.select_date(soup, selector=".header-article .article-date")
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr)
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        if len(dct['text']) == 0:
            dct['text'].append("Nooooo! If no other content is showing up, then that is likely because you do not have a Corriere subscription.")
        return (dct, article_data)

    # Method for Corriere della Sera - ViviMilano:
    def CorrieredellaSeraViviMilano(self, src="Corriere della Sera - ViviMilano"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.tappoTitle")
        descr = self.select_descr(soup, selector=".article-subtitle")
        author = self.select_author(soup, selector=".authorName")
        date = self.select_date(soup, selector=".infoText .fw500")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.inset-cta', 'table']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".infoText.flatText"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for allAfrica:
    def allAfrica(self, src="allAfrica"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".topic h1")
        descr = self.select_descr(soup, selector=".article-subtitle")
        author = self.select_author(soup, selector=".authorName")
        if author is None or len(author) < 2:
            author = self.select_author(soup, selector="cite.byline")
        date = self.select_date(soup, selector=".infoText .fw500")
        if date is None or len(date) < 2:
            date = self.select_author(soup, selector=".publication-date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.sharebar', '.newsletter-signup', '.inread']
        data_arr = [source, url, title, descr, author, date]
        try:
            content_selector = "div.topic"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        except:
            content_selector = ".story-body"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for African Business:
    def AfricanBusiness(self, src="African Business"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".entry-title")
        descr = self.select_descr(soup, selector=".intro-text")
        author = self.select_author(soup, selector=".post-author .meta-text a")
        date = self.select_date(soup, selector=".post-date .meta-text a")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.sharebar', '.newsletter-signup', '.inread']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".entry-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Africanews:
    def Africanews(self, src="Africanews"):
        (source, url, soup) = self.handle_meta(src)
        title = soup.title.text.strip()
        descr = None
        author = self.select_author(soup, selector=".article__header .article__author")
        date = self.select_date(soup, selector=".article__header time.article__date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.sharebar', '.newsletter-signup', '.inread']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".article-content__text"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Spectator:
    def TheSpectator(self, src="The Spectator"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.ContentPageTitle-module__headline")
        descr = None
        author = self.select_author(soup, selector=".ContentPageAuthor-module__author__name")
        date = self.select_date(soup, selector=".ContentPageMetadataItem-module__item")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".ContentPageBody-module__body__content--drop-cap"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for New Scientist:
    def NewScientist(self, src="New Scientist"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".article-header h1")
        descr = None
        author = self.select_author(soup, selector=".article-content .author-byline")
        date = self.select_date(soup, selector=".article-header .published-date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.box-out', '.author-byline', '.mpu', '.article-topics']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".article-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Science Alert:
    def ScienceAlert(self, src="Science Alert"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.article-title")
        descr = None
        author = self.select_author(soup, selector=".author-name-name span")
        date = self.select_date(soup, selector=".author-name-date span")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.box-out', '.author-byline', '.mpu', '.article-topics']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".article-fulltext"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for InterNapoli:
    def InterNapoli(self, src="InterNapoli"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.entry-title")
        descr = descr = self.select_title(soup, selector=".td-post-sub-title")
        author = self.select_author(soup, selector=".td-post-header .td-post-author-name")
        try:
            if author[-1] == "-":
                author = author[:-2].strip()
        except:
            pass
        date = self.select_date(soup, selector=".td-post-date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.box-out', '.author-byline', '.mpu', '.article-topics']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".td-post-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Voce di Napoli:
    def VocediNapoli(self, src="Voce di Napoli"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.news-title")
        descr = None
        author = self.select_author(soup, selector=".fa.fa-user-circle-o + span")
        date = self.select_date(soup, selector=".fa.fa-calendar + span")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header']
        data_arr = [source, url, title, descr, author, date]
        content_selector = "#post-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for CFO:
    def CFO(self, src="CFO"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".titles h1")
        descrTag = self.select_title(soup, selector=".titles a")
        descr = self.select_descr(soup, selector=".titles .deck")
        if descrTag is not None and descr is not None:
            descr = f"{descrTag}: {descr}"
        author = self.select_author(soup, selector=".author.url.fn")
        date = self.select_date(soup, selector=".titles .post-date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".article-text"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Business Today Journal:
    def BusinessToday(self, src="Business Today Journal"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.BlogItem-title")
        descr = None
        author = self.select_author(soup, selector=".Blog-meta-item.Blog-meta-item--author")
        date = self.select_date(soup, selector=".Blog-meta-item.Blog-meta-item--date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'blockquote', 'nav']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".Main-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Georgetown Business Magazine:
    def GeorgetownBusinessMagazine(self, src="Georgetown Business Magazine"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".l-main-page h1")
        descr = None
        author = self.select_author(soup, selector=".Blog-meta-item.Blog-meta-item--author")
        date = self.select_date(soup, selector=".Blog-meta-item.Blog-meta-item--date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'blockquote', 'nav']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".l-main-page"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Georgetown Magazine:
    def GeorgetownMagazine(self, src="Georgetown Magazine"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".text-container h1")
        descr = None
        author = self.select_author(soup, selector="div.author")
        date = self.select_date(soup, selector="div.date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'blockquote', 'nav']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".content-main"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Stanford Business Magazine:
    def StanfordBusinessMagazine(self, src="Stanford Business Magazine"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".field-name-title h1")
        descr = self.select_descr(soup, selector=".field-name-field-editorial-summary")
        author = self.select_author(soup, selector=".field-name-field-authors")
        try:
            if "|" in author:
                author = author.replace("|", "").strip()
        except:
            pass
        date = self.select_date(soup, selector=".field-name-field-date span")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'blockquote', '.file-resource-sidebar', '.file-application-resource']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".field-name-field-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for People Magazine:
    def People(self, src="People Magazine"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".main-header.article-main-header h1")
        descr = self.select_descr(soup, selector=".main-header.article-main-header .dek")
        author = self.select_author(soup, selector=".main-header.article-main-header .author .author-name")
        date = self.select_date(soup, selector=".main-header.article-main-header .author .timestamp")
        selectors = 'p, h2, h3, h4, h5, h6'#ul li, ol li
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'blockquote', 'header', 'footer', 'nav', '.menu', '.menu-item', '.menu-link', '.menu-subscribe', '.menu-search', '.subcontainer', '.modal', '.dek']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr, dont_append_keys=["RELATED:"])
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Inc. Magazine:
    def Inc(self, src="Inc. Magazine"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="header.article__header h2")
        descr = self.select_descr(soup, selector="header.article__header h3")
        author = self.select_author(soup, selector="header.article__header .by-line a")
        date = self.select_date(soup, selector="header.article__header h3 a")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'blockquote', '#native_mid_article_inject', '.card--embed']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".article-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Money:
    def Money(self, src="Money"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".article-header h2")
        descr = self.select_descr(soup, selector=".article-header h3")
        author = self.select_author(soup, selector=".article-header .author-name")
        date = self.select_date(soup, selector=".article-header .timestamp")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'blockquote', '#native_mid_article_inject', '.card--embed']
        data_arr = [source, url, title, descr, author, date]
        content_selector = "#article-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Money Magazine:
    def MoneyMagazine(self, src="Money Magazine"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="[itemprop='headline']")
        descr = None
        author = self.select_author(soup, selector="[itemprop='author']")
        date = self.select_date(soup, selector="[itemprop='datePublished']")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'blockquote', '#native_mid_article_inject', '.card--embed']
        data_arr = [source, url, title, descr, author, date]
        content_selector = "[itemprop='articleBody']"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Le Monde:
    def LeMonde(self, src="Le Monde"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="header.article__header h1")
        descr = self.select_descr(soup, selector="header.article__header .article__desc")
        author = self.select_author(soup, selector="header.article__header .meta__author")
        date = self.select_date(soup, selector="header.article__header .meta__date.meta__date--header")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'blockquote', '.meta__social']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".article__content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Le Figaro:
    def LeFigaro(self, src="Le Figaro"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.fig-headline")
        descr = self.select_descr(soup, selector=".fig-standfirst")
        author = self.select_author(soup, selector=".fig-main .fig-content-metas__authors")
        date = self.select_date(soup, selector=".fig-main .fig-content-metas__pub")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'blockquote', '.meta__social', '.fig-standfirst']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".fig-main"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["À lire aussi :", "À lire aussi:", "À lire aussi -", "À VOIR AUSSI -", "À VOIR AUSSI:", "À VOIR AUSSI :"])
        return (dct, article_data)

    # Method for Sport24 - Le Figaro:
    def Sport24(self, src="Sport24 - Le Figaro"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.s24-art-header__title")
        descr = self.select_descr(soup, selector=".s24-art-chapo")
        author = self.select_author(soup, selector=".s24-art__content [itemprop='name']")
        date = self.select_date(soup, selector=".s24-art__content [itemprop='datePublished']")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'blockquote', '.meta__social', '.fig-standfirst', '.s24-art-cross-linking']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".s24-art-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["À lire aussi :", "LIRE AUSSI -", "À lire aussi:", "À lire aussi -", "À VOIR AUSSI -", "À VOIR AUSSI:", "À VOIR AUSSI :"])
        return (dct, article_data)

    # Method for Madame Figaro:
    def MadameFigaro(self, src="Madame Figaro"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.mad__titre")
        descr = self.select_descr(soup, selector=".mad__article__chapo")
        author = self.select_author(soup, selector=".header-info__author")
        date = self.select_date(soup, selector=".header-info")
        try:
            date = date.replace(author, "").replace("•", "").strip()
        except:
            pass
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'blockquote', '.meta__social', '.fig-standfirst', '.s24-art-cross-linking', '.mad__article__content__redac-conseil']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".article-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["À lire aussi :", "LIRE AUSSI -", "À lire aussi:", "À lire aussi -", "À VOIR AUSSI -", "À VOIR AUSSI:", "À VOIR AUSSI :"])
        return (dct, article_data)

    # Method for finews:
    def finews(self, src="finews"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="[itemprop='headline']")
        descr = None
        author = None
        date = self.select_date(soup, selector=".article-container .label.date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'blockquote', 'form', '.moduletable', '.advpoll', '.advpoll-graph-wrapper']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".article-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Town & Country:
    def TownAndCountry(self, src="Town & Country"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".content-hed")
        descr = self.select_descr(soup, selector=".content-dek")
        author = self.select_author(soup, selector="div.byline a.byline-name span")
        date = self.select_date(soup, selector="time.content-info-date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'blockquote']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".article-body-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Growth Manifesto:
    def TheGrowthManifesto(self, src="The Growth Manifesto"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".content h1")
        descr = None
        date = self.select_date(soup, selector=".article-date")
        author = self.select_author(soup, selector=".content .author")
        try:
            author = author.replace("Get more articles like this sent to your email here", "").replace("-", "").replace(date, "").strip()
        except:
            pass
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'blockquote']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".single_article_content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Harper's Bazaar:
    def HarpersBazaar(self, src="Harper's Bazaar"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".content-hed")
        descr = self.select_descr(soup, selector=".content-dek")
        author = self.select_author(soup, selector=".byline .byline-name")
        date = self.select_date(soup, selector="time.content-info-date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'blockquote']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".article-body-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for CIO:
    def CIO(self, src="CIO"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="[itemprop='headline']")
        descr = self.select_descr(soup, selector="[itemprop='description']")
        author = self.select_author(soup, selector="[itemprop='author']")
        date = self.select_date(soup, selector=".pub-date") # pub-date
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'blockquote']
        data_arr = [source, url, title, descr, author, date]
        content_selector = "[itemprop='articleBody']"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for CNET:
    def CNET(self, src="CNET"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".c-head h1")
        descr = self.select_descr(soup, selector=".c-head_dek")
        author = self.select_author(soup, selector=".c-assetAuthor_authors")
        date = self.select_date(soup, selector=".c-assetAuthor_date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'blockquote', '.newsletter-subscribe-form']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".article-main-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Anteprima24:
    def Anteprima24(self, src="Anteprima24"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.entry-title")
        descr = self.select_descr(soup, selector=".td-post-sub-title")
        author = self.select_author(soup, selector=".td-post-header .td-post-author-name")
        try:
            if author[-1] == "-":
                author = author[:-2].strip()
        except:
            pass
        date = self.select_date(soup, selector=".td-post-date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.box-out', '.author-byline', '.mpu', '.article-topics']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".td-post-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Nuova Irpinia:
    def NuovaIrpinia(self, src="Nuova Irpinia"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.entry-title")
        descr = self.select_descr(soup, selector=".td-post-sub-title")
        author = self.select_author(soup, selector=".td-post-header .td-post-author-name")
        try:
            if author[-1] == "-":
                author = author[:-2].strip()
        except:
            pass
        date = self.select_date(soup, selector=".td-post-date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, pre'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.box-out', '.author-byline', '.mpu', '.article-topics']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".td-post-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Affaritaliani.it:
    def Affaritaliani(self, src="Affaritaliani.it"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="[itemprop='headline']")
        descr = self.select_descr(soup, selector="[itemprop='description']")
        author = self.select_author(soup, selector=".page-header .author")
        date = self.select_date(soup, selector="[itemprop='datePublished']")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.box-out', '.author-byline', '.mpu', '.article-topics']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".cnt-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for areanapoli.it:
    def areanapoli(self, src="areanapoli.it"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="#content h1")
        descr = self.select_descr(soup, selector="#content .art-incipit")
        author = self.select_author(soup, selector=".art-author")
        date = self.select_date(soup, selector=".art-author div")
        try:
            author = author.replace(date, "").strip()
        except:
            pass
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".art-text"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Calcio Napoli 1926:
    def CalcioNapoli1926(self, src="Calcio Napoli 1926"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".entry-title h1")
        descr = self.select_descr(soup, selector=".entry-excerpt")
        author = self.select_author(soup, selector=".bar-author")
        date = self.select_date(soup, selector=".entry-date-content .meta-date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".entry-content-text"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["CLICCA QUI PER", "CLICCA QUI SE", "© RIPRODUZIONE RISERVATA", "SEGUICI ANCHE SU TWITTER", "LEGGI QUI"])
        return (dct, article_data)

    # Method for Calcio Napoli 24:
    def CalcioNapoli24(self, src="Calcio Napoli 24"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".article h1")
        descr = self.select_descr(soup, selector=".article h2")
        author = "Redazione"#self.select_author(soup, selector=".bar-author")
        date = self.select_date(soup, selector=".entry-date-content .meta-date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".reader"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Calcio Napoli 24:
    def CalcioNapoli24M(self, src="Calcio Napoli 24"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".article h1")
        descr = self.select_descr(soup, selector=".article h2")
        author = self.select_author(soup, selector=".autore")
        date = self.select_date(soup, selector=".entry-date-content .meta-date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".corpo"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Prima Tivvù:
    def PrimaTivvu(self, src="Prima Tivvù"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.single-title")
        descr = self.select_descr(soup, selector=".single-entry-summary h3")
        author = self.select_author(soup, selector=".author-meta")
        date = self.select_date(soup, selector=".posted-date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".single-entry-summary"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Virgilio Notizie:
    def VirgilioNotizie(self, src="Virgilio Notizie"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".content-articolo h1")
        descr = self.select_descr(soup, selector=".content-articolo h2")
        meta = self.select_date(soup, selector=".content-articolo .fonte-articolo")
        try:
            author = meta.split("|")[0].strip()
            date = meta.split("|")[1].strip()
        except:
            author = None
            date = None
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside']
        data_arr = [source, url, title, descr, author, date]
        content_selector = "#foglia"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for La Città di Salerno:
    def LaCittadiSalerno(self, src="La Città di Salerno"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.article__headline")
        descr = self.select_descr(soup, selector="div.article__lead")
        author = self.select_author(soup, selector=".td-post-header .td-post-author-name")
        date = self.select_date(soup, selector="time.publishing-date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".article__body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Cronache Salerno:
    def CronacheSalerno(self, src="Cronache Salerno"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="#post-area h1")
        descr = None #self.select_descr(soup, selector="div.article__lead")
        author = self.select_author(soup, selector="#post-info")
        date = self.select_date(soup, selector="#post-info")
        selectors = "p, h2, h3, h4, h5, h6, ul li, ol li, [dir='auto']"
        garbage_arr = ['figure', 'figcaption', 'small', 'aside']
        data_arr = [source, url, title, descr, author, date]
        content_selector = "#content-area"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Cronache Salerno:
    def IlQuotidianodiSalerno(self, src="Cronache Salerno"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".posttitle")
        descr = None #self.select_descr(soup, selector="div.article__lead")
        meta = self.select_author(soup, selector=".postmetadata")
        try:
            meta = meta.split("•")[0].strip()
            i = meta.index(":")
            author = meta[:i-4].strip()
            date = meta[i-2:].strip()
        except:
            author = None
            date = None
        selectors = "p, h2, h3, h4, h5, h6, ul li, ol li"
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.wp-caption-text']
        data_arr = [source, url, title, descr, author, date]
        content_selector = "#content .entry"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Occhio Notizie:
    def OcchioNotizie(self, src="Occhio Notizie"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.entry-title")
        descr = self.select_descr(soup, selector=".entry-sub-title")
        author = self.select_author(soup, selector=".meta-author")
        date = self.select_date(soup, selector=".date.meta-item")
        selectors = "p, h2, h3, h4, h5, h6, ul li, ol li, [dir='auto']"
        garbage_arr = ['figure', 'figcaption', 'small', 'aside']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".entry-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Quanta Magazine:
    def QuantaMagazine(self, src="Quanta Magazine"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.post__title__title")
        descr = self.select_descr(soup, selector=".post__title__excerpt")
        author = self.select_author(soup, selector=".sidebar__author h3")
        date = self.select_date(soup, selector=".h6.o6.mv1.pv025")
        selectors = "p, h2, h3, h4, h5, h6, ul li, ol li, [dir='auto']"
        garbage_arr = ['figure', 'figcaption', 'small', 'aside']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".post__content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for CBS Local:
    def CBSLocal(self, src="CBS Local"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.title")
        descr = self.select_descr(soup, selector=".post__title__excerpt")
        author = self.select_author(soup, selector=".post-personality")
        date = self.select_date(soup, selector="time.post-date")
        selectors = "p, h2, h3, h4, h5, h6, ul li, ol li"
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.wp-caption-text']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".main-story-wrapper"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for BusinessWorld:
    def BusinessWorld(self, src="BusinessWorld"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='[itemprop="headline"]')
        descr = self.select_descr(soup, selector=".big_article_summary")
        author = self.select_author(soup, selector=".article-meta .author")
        date = self.select_date(soup, selector='[itemprop="datePublished"]')
        selectors = "p, h2, h3, h4, h5, h6, ul li, ol li"
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.wp-caption-text']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".article_text_desc"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        if dct['text'][1] in dct['text'][0]:
            dct['text'].pop(0)
        return (dct, article_data)

    # Method for Le Courrier de Russie:
    def LeCourrierDeRussie(self, src="Le Courrier de Russie"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='h1.hero__title')
        descr = self.select_descr(soup, selector=".big_article_summary")
        author = self.select_author(soup, selector=".single-author .post-link-author")
        date = self.select_date(soup, selector='.single-author .post-link.by')
        selectors = "p, h2, h3, h4, h5, h6, ul li, ol li"
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.wp-caption-text', '.sharedaddy']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".entry-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for TGCOM24:
    def TGCOM24(self, src="TGCOM24"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='h1.hero__title')
        descr = self.select_descr(soup, selector=".big_article_summary")
        author = self.select_author(soup, selector=".single-author .post-link-author")
        date = self.select_date(soup, selector='.single-author .post-link.by')
        selectors = "p, h2, h3, h4, h5, h6, ul li, ol li"
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.wp-caption-text', '.sharedaddy']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".entry-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Il Centro:
    def IlCentro(self, src="Il Centro"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.article__headline")
        descr = self.select_descr(soup, selector="div.article__lead")
        author = self.select_author(soup, selector=".td-post-header .td-post-author-name")
        date = self.select_date(soup, selector="time.publishing-date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".article__body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        if len(dct['text']) == 0:
            dct['text'] = [soup.select(".article__body")[0].text.strip()]
        return (dct, article_data)

    # Method for Corriere Adriatico:
    def CorriereAdriatico(self, src="Corriere Adriatico"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".contenuto header h1")
        descr = None
        date = self.select_date(soup, selector=".contenuto header .data_pub")
        author = self.select_author(soup, selector="article.blog .date-author-wrap .authors")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.caption', '.credit', '.pull-quote', '.social-media-buttons', '.link_snippet_small']
        content_selector = ".body-text"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["LEGGI ANCHE:"])
        return (dct, article_data)

    # Method for The Hacker News:
    def TheHackerNews(self, src="The Hacker News"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="main.main .story-title")
        descr = None
        date = self.select_date(soup, selector="main.main .author")
        author = self.select_author(soup, selector="main.main .author")
        try:
            author = author.replace(date, "").strip()
            if author[0] == ",":
                author = author[1:].strip()
        except:
            pass
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, blockquote'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', '.caption', '.credit', '.pull-quote', '.social-media-buttons', '.link_snippet_small']
        content_selector = ".articlebody"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["LEGGI ANCHE:"])
        return (dct, article_data)

    # Method for The Daily Swig:
    def TheDailySwig(self, src="The Daily Swig"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".post-card h1")
        descr = self.select_descr(soup, selector=".standfirst")
        date = self.select_date(soup, selector=".post-additionalinfo")
        author = self.select_author(soup, selector=".post-additionalinfo a")
        try:
            date = date.replace(author, "").strip()
        except:
            pass
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', '.standfirst']
        content_selector = ".post-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Cyware:
    def Cyware(self, src="Cyware"):
        (source, url, soup) = self.handle_meta(src)
        # soup = self.removeOtherGarbage(soup, *[".cy-card__list.cy-alert__info .list-inline-item a"])
        title = self.select_title(soup, selector="h1")
        descr = None
        meta = self.select_author(soup, selector=".cy-card__list.cy-alert__info .list-inline-item")
        try:
            meta = meta.replace(", Cyware Alerts - Hacker News", "")
            i = meta.index(",")
            date = meta[i:].replace(",", "").strip()
        except:
            date = None
        author = "Cyware"
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', '.cy-card__list.cy-alert__info .list-inline-item', 'h1', '.cy-tags', '.cy-hover-card']
        soup = self.removeOtherGarbage(soup, *garbage_arr)
        arr = [soup.select(".single-page-content")[0].text.replace("Go to listing page", "").strip()]
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for ZDNet:
    def ZDNet(self, src="ZDNet"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".storyHeader h1")
        descr = self.select_descr(soup, selector=".storyHeader .summary") # .dateblock
        date = self.select_date(soup, selector=".byline .meta time")
        author = self.select_author(soup, selector=".byline .meta [rel='author']")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.caption', '.credit', '.pull-quote', '.social-media-buttons', '.link_snippet_small']
        content_selector = ".storyBody"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["LEGGI ANCHE:"])
        return (dct, article_data)

    # Method for WikiLeaks:
    def WikiLeaks(self, src="WikiLeaks"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".content h1")
        descr = None#self.select_descr(soup, selector=".storyHeader .summary")
        date = self.select_date(soup, selector=".date")
        if date is None:
            date = self.select_date(soup, selector=".timestamp")
        author = None#self.select_author(soup, selector=".byline .meta [rel='author']")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h1, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside']
        try:
            if len(soup.select(".release")) > 1:
                arr = []
                leaks = soup.select(".release")
                for leak in leaks:
                    txt = leak.text.strip()
                    arr.append(txt)
                article_data = SingleArticle(source, url, title, descr, author, date, arr)
                dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
                return (dct, article_data)
            else:
                content_selector = ".leak-content"
                (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
                return (dct, article_data)
        except:
            try:
                content_selector = ".text-content"
                (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
            except:
                content_selector = ".container-fluid.row-fluid" # For old WikiLeaks
                (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for TechRepublic:
    def TechRepublic(self, src="TechRepublic"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.title")
        descr = self.select_descr(soup, selector=".takeaway")
        date = self.select_date(soup, selector="span.byline-item")
        try:
            date = date.split("on")[-1].strip()
        except:
            pass
        author = self.select_author(soup, selector="a.author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.caption', '.credit', '.pull-quote', '.social-media-buttons', '.link_snippet_small']
        content_selector = ".content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["LEGGI ANCHE:"])
        return (dct, article_data)

    # Method for KrebsOnSecurity:
    def KrebsOnSecurity(self, src="KrebsOnSecurity"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".post-title")
        descr = None
        date = self.select_date(soup, selector=".post-smallerfont small")
        author = 'KrebsOnSecurity'
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.wp-caption']
        content_selector = ".entry"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["LEGGI ANCHE:"])
        return (dct, article_data)

    # Method for Infosecurity Magazine:
    def InfosecurityMagazine(self, src="Infosecurity Magazine"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1[itemprop='name']")
        descr = None#self.select_descr(soup, selector="h1[itemprop='name']")
        date = self.select_date(soup, selector=".article-meta time")
        author = self.select_author(soup, selector=".author .author-name a")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'blockquote']
        content_selector = ".article-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        words = dct['text'][1].split(" ")
        if len(words) > 200:
            dct['text'] = dct['text'][0:2]
        return (dct, article_data)

    # Method for Modern War Institute:
    def ModernWarInstitute(self, src="Modern War Institute"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.entry-title")
        descr = None#self.select_descr(soup, selector="h1[itemprop='name']")
        author = self.select_author(soup, selector=".post-meta .author")
        soup = self.removeOtherGarbage(soup, *[".author"])
        date = self.select_date(soup, selector=".post-meta").replace(",", "").replace("|", "").replace("and", "").strip()
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'blockquote']
        content_selector = ".entry-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Image credit:"])
        return (dct, article_data)

    # Method for Paris Capitale:
    def ParisCapitale(self, src="Paris Capitale"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="#main h1")
        descr = self.select_descr(soup, selector="div.introduction")
        author = self.select_author(soup, selector=".jeg_meta_author")
        date = self.select_date(soup, selector="#main .time")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'blockquote', '#moreArticles']
        content_selector = ".content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Follow Israel Hayom on Facebook and Twitter"])
        return (dct, article_data)

    # Method for Globes:
    def Globes(self, src="Globes"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="#F_Title")
        descr = self.select_descr(soup, selector="#coteret_SubCoteret")
        author = self.select_author(soup, selector=".articleAuthor")
        date = self.select_date(soup, selector=".articleDate")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'blockquote', '#moreArticles']
        content_selector = "#article article"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        dct['text'].pop(0)
        return (dct, article_data)

    # Method for HelloMonaco:
    def HelloMonaco(self, src="HelloMonaco"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".entry-title")
        descr = self.select_descr(soup, selector="#coteret_SubCoteret")
        author = self.select_author(soup, selector=".articleAuthor")
        date = self.select_date(soup, selector=".date.meta-item")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'blockquote', '#moreArticles']
        content_selector = ".entry-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Geneva Business News:
    def GBNews(self, src="Geneva Business News"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".entry-title")
        descr = self.select_descr(soup, selector="h2.dek") # .dateblock
        date = self.select_date(soup, selector=".post-meta .date")
        author = self.select_author(soup, selector=".entry-author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', '.wp-caption-text', '.heateor_sss_sharing_container']
        content_selector = ".entry-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Newswire:
    def Newswire(self, src="Newswire"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".article-header")
        descr = self.select_descr(soup, selector=".lead.article-summary") # .dateblock
        date = self.select_date(soup, selector=".ai-date")
        author = None#self.select_author(soup, selector=".entry-author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', '.wp-caption-text', '.heateor_sss_sharing_container']
        content_selector = ".html-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Business Wire:
    def BusinessWire(self, src="Business Wire"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".bw-release-main header h1")
        descr = self.select_descr(soup, selector=".bw-release-subhead") # .dateblock
        date = self.select_date(soup, selector=".bw-release-timestamp")
        author = None#self.select_author(soup, selector=".entry-author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', '.wp-caption-text', '.heateor_sss_sharing_container']
        content_selector = ".bw-release-story"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for PR Newsire:
    def PRNewswire(self, src="PR Newsire"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="article header h1")
        descr = self.select_descr(soup, selector=".subtitle") # .dateblock
        date = self.select_date(soup, selector=".mb-no")
        author = self.select_author(soup, selector=".meta + a strong")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', '.wp-caption-text', '.heateor_sss_sharing_container']
        content_selector = ".release-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for EIN Pressswire:
    def EINPressswire(self, src="EIN Pressswire"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="#main-column h1")
        descr = self.select_descr(soup, selector=".subtitle") # .dateblock
        date = self.select_date(soup, selector=".sv-date")
        author = self.select_author(soup, selector=".sv-who")
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', '.wp-caption-text', '.pr_images_column', 'pr_image', '.article-footer']
        soup = self.removeOtherGarbage(soup, *garbage_arr)
        arr = [soup.select(".article_column")[0].text.strip()]
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for The Peninsula (Qatar):
    def ThePeninsulaQatar(self, src="The Peninsula (Qatar)"):
        (source, url, soup) = self.handle_meta(src)
        soup = self.removeOtherGarbage(soup, *[".fa"])
        title = self.select_title(soup, selector=".entry-title")
        descr = None#self.select_descr(soup, selector=".subtitle") # .dateblock
        date = self.select_date(soup, selector=".time")
        author = self.select_author(soup, selector=".writer-title")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', '.wp-caption-text', '.blog-social', '.cat-title', '.post-box.related-art']
        content_selector = ".blog-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["READ ALSO:"])
        return (dct, article_data)

    # Method for The News International:
    def TheNewsInternational(self, src="The News International"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".detail-heading h1")
        descr = None#self.select_descr(soup, selector=".subtitle")
        date = self.select_date(soup, selector=".category-date")
        author = self.select_author(soup, selector=".authorFullName")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', '.wp-caption-text']
        content_selector = ".story-detail"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        if len(dct['text'][0].split()) > 200:
            dct['text'] = [dct['text'][0]]
        return (dct, article_data)

    # Method for Mint:
    def Mint(self, src="Mint"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.headline")
        summary = self.select_author(soup, selector=".summary")
        descr = self.select_author(soup, selector="ul.highlights li") # USED select_author HERE TO SEPERATE THE liS WITH A COMMA!
        if summary is not None and descr is not None and len(summary) > 5 and len(descr) > 5:
            descr = f"{summary} . . . {descr}"
        elif summary is not None and (descr is None or len(descr) < 2):
            descr =  summary
        date = self.select_date(soup, selector=".articleInfo.pubtime")
        try:
            date = date[date.index("read")+5:].replace(".", "").strip()
        except:
            pass
        author = self.select_author(soup, selector=".articleInfo.author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', '.wp-caption-text', '.moreNews']
        content_selector = "#mainArea"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Also Read |"])
        return (dct, article_data)

    # Method for Global Market Insights:
    def GMInsights(self, src="Global Market Insights"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".blog-post h1")
        descr = None#self.select_descr(soup, selector=".subtitle") # .dateblock
        # date = self.select_date(soup, selector=".p-info")
        # author = self.select_author(soup, selector=".p-info")
        meta = self.select_author(soup, selector=".p-info")
        try:
            date, author = meta.split("|")[0].strip(), meta.split("|")[2].strip()
        except:
            date, author = None, None
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, .tab-label-collaps-1, .tab-content-collapspr-1'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', '.wp-caption-text', 'table']
        content_selector = ".detail-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["READ ALSO:"])
        return (dct, article_data)






    # Method for Agenzia Giornalistica Italia (AGI):
    def AGI(self, src="Agenzia Giornalistica Italia (AGI)"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1")
        descr = self.select_descr(soup, selector=".article-excerpt") # .dateblock
        date = self.select_date(soup, selector=".article-date")
        author = self.select_author(soup, selector=".article-author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', '.wp-caption-text']
        content_selector = ".article-content-wrap"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        if len(dct['text']) > 1:
            popped = ""
            if len(dct['text'][0].split()) > 200 or dct['text'][1] in dct['text'][0]:
                popped = dct['text'].pop(0)
            if len(dct['text']) == 0:
                dct['text'] == [popped]
        return (dct, article_data)

    # Method for Adnkronos:
    def Adnkronos(self, src="Adnkronos"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.title")
        descr = self.select_descr(soup, selector=".art-text.text-big")
        date = self.select_date(soup, selector=".arpage-info span")
        author = self.select_author(soup, selector=".writer-title")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', '.wp-caption-text', '.widget-cursive', '.ar-leggi']
        content_selector = ".ar-main"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Spaceflight Now:
    def SpaceflightNow(self, src="Spaceflight Now"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.entry-title")
        descr = self.select_descr(soup, selector=".art-text.text-big")
        date = self.select_date(soup, selector=".entry-meta-date")
        author = self.select_author(soup, selector=".entry-meta-author.vcard")
        data_arr = [source, url, title, descr, author, date]
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', '.wp-caption-text', '.widget-cursive', '.ar-leggi']
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        content_selector = ".entry-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Makers India:
    def MakersIndia(self, src="Makers India"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="article header h1")
        descr = self.select_descr(soup, selector='.__0838e-2Ta0u') # data-test-id="article-summary-item"
        date = self.select_date(soup, selector="time.date")
        author = self.select_author(soup, selector="a.author-link") # .caas-attr.author
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside']
        content_selector = '.caas-body' #
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Also Read:"])
        return (dct, article_data)

    # Method for Al Arabiya - English:
    def AlArabiyaEN(self, src="Al Arabiya - English"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".content h1")
        descr = self.select_descr(soup, selector='.__0838e-2Ta0u') # data-test-id="article-summary-item"
        date = self.select_date(soup, selector=".article-info .caption")
        author = self.select_author(soup, selector=".article-info .source") # .caas-attr.author
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.media_box']
        content_selector = '.article-content' #
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Al Arabiya - Urdu:
    def AlArabiyaUrdu(self, src="Al Arabiya - Urdu"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".highline")
        descr = self.select_descr(soup, selector='.headline')
        date = self.select_date(soup, selector=".date")
        author = self.select_author(soup, selector=".source .author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.media_box']
        content_selector = '.article-body' #
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Al Arabiya - Farsi:
    def AlArabiyaFarsi(self, src="Al Arabiya - Farsi"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".article-hdr h1")
        descr = self.select_descr(soup, selector='.headline')
        date = self.select_date(soup, selector=".article-hdr time")
        author = self.select_author(soup, selector=".author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.media_box']
        content_selector = '#body-text' #
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Al Arabiya :
    def AlArabiya(self, src="Al Arabiya"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".headingInfo_title")
        descr = self.select_descr(soup, selector='.headingInfo_subtitle')
        date = self.select_date(soup, selector=".timeDate")
        author = self.select_author(soup, selector=".author_link")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.media_box']
        content_selector = '#body-text' #
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Independent.ie :
    def IndependentIE(self, src="Independent.ie"):
        (source, url, soup) = self.handle_meta(src)
        soup = self.removeOtherGarbage(soup, *[".icon1"])
        title = self.select_title(soup, selector=".title1-main")
        descr = self.select_descr(soup, selector='.headingInfo_subtitle')
        date = self.select_date(soup, selector="time.time1")
        author = self.select_author(soup, selector=".c-byline1-author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.c-more1', '.c-join2', '.source1']
        content_selector = '.n-body1' #
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for thejournal.ie:
    def TheJournalIE(self, src="thejournal.ie"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".content h1")
        descr = self.select_descr(soup, selector='.excerpt')
        date = self.select_date(soup, selector=".date")
        author = self.select_author(soup, selector=".name")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.contribution-prompt']
        content_selector = '#articleContent' #
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Scientific American:
    def ScientificAmerican(self, src="Scientific American"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".t_article-title")
        descr = self.select_descr(soup, selector='.t_article-subtitle')
        date = self.select_date(soup, selector="[itemprop='datePublished']")
        author = self.select_author(soup, selector="[itemprop='author']")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.contribution-prompt']
        content_selector = '.article-text'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Management Today:
    def ManagementToday(self, src="Management Today"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".gatedArticle__title")
        descr = self.select_descr(soup, selector='.gatedArticle__summary')
        date = self.select_date(soup, selector="[itemprop='datePublished']")
        author = self.select_author(soup, selector=".author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.contribution-prompt']
        content_selector = '#articleMain'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        if "Sign in to continue" in dct['text']:
            i = dct['text'].index("Sign in to continue")
            dct['text'] = dct['text'][:i]
            dct['text'].append("Nooooo! If no other content is showing up, then that is because it is only available for Management Today subscribers.")
        return (dct, article_data)

    # Method for Playtech.ro:
    def PlaytechRO(self, src="Playtech.ro"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".titlezone h1")
        descr = None#self.select_descr(soup, selector='.gatedArticle__summary')
        date = self.select_date(soup, selector=".date")
        author = self.select_author(soup, selector=".co-authors")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.contribution-prompt']
        content_selector = '.text'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for BusinessTech:
    def BusinessTech(self, src="BusinessTech"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".entry-title")
        descr = None#self.select_descr(soup, selector='.gatedArticle__summary')
        date = self.select_date(soup, selector=".post-date")
        author = self.select_author(soup, selector=".vcard.author.post-author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.contribution-prompt']
        content_selector = '.entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Read:"])
        return (dct, article_data)

    # Method for Daily Maverick:
    def DailyMaverick(self, src="Daily Maverick"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".titles h1")
        descr = self.select_descr(soup, selector='.first-paragraph')
        meta = self.select_author(soup, selector=".author-title")
        try:
            date, author = meta.split("•")[1].strip(), meta.split("•")[0].strip()
        except:
            date, author = None, None
        if date is None and author is None:
            meta = self.select_author(soup, selector=".opionista-header h4")
            try:
                date, author = meta.split("•")[2].strip(), meta.split("•")[1].strip()
            except:
                date, author = None, None
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.article-tags', '.image-caption', '.comments-area']
        content_selector = '.article-container'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for CBS Sports:
    def CBSSports(self, src="CBS Sports"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".Article-headline")
        descr = self.select_descr(soup, selector='.Article-subline')
        date = self.select_date(soup, selector=".TimeStamp")
        author = self.select_author(soup, selector=".ArticleAuthor-name--link")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.contribution-prompt']
        content_selector = '.Article-bodyContent'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Read:"])
        return (dct, article_data)

    # Method for News24:
    def News24(self, src="News24"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".article__title")
        descr = self.select_descr(soup, selector='.Article-subline')
        date = self.select_date(soup, selector=".article__date")
        author = self.select_author(soup, selector=".article__author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.contribution-prompt']
        try:
            content_selector = '.article__body'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        except:
            content_selector = '.article__body--locked'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
            dct['text'] = dct['text'][1:] + ["Nooooo! If no other content is showing up, then that is because it is only available for News24 subscribers."]
        return (dct, article_data)

    # Method for Moneyweb:
    def Moneyweb(self, src="Moneyweb"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".article-headline")
        descr = self.select_descr(soup, selector='.article-excerpt')
        date = self.select_date(soup, selector="[itemprop='datePublished']")
        author = self.select_author(soup, selector=".article-meta .author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.block.m1010']
        content_selector = '.article-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        if len(dct['text'][0].split()) > 200:
            dct['text'] = [dct['text'][0]]
        return (dct, article_data)

    # Method for BusinessLive:
    def BusinessLive(self, src="BusinessLive"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".article-title-primary")
        descr = self.select_descr(soup, selector='.article-title-tertiary')
        date = self.select_date(soup, selector=".article-pub-date")
        author = self.select_author(soup, selector=".authors-list")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.no-access-comments', '.related-container', '.related-articles', '.most-read']
        content_selector = '.article-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for TimesLIVE:
    def TimesLIVE(self, src="TimesLIVE"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".primary-title")
        descr = self.select_descr(soup, selector='.tertiary-title')
        date = self.select_date(soup, selector=".article-pub-date")
        author = self.select_author(soup, selector=".article-author")
        if author is None or len(author) < 2:
            author = self.select_author(soup, selector=".author-name a")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.no-access-comments', '.related-container', '.related-articles', '.most-read', '.article-widget-related_articles']
        content_selector = '.article-widgets'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for NBC Sports:
    def NBCSports(self, src="NBC Sports"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".entry-title")
        descr = self.select_descr(soup, selector=".article-dek")
        date = self.select_date(soup, selector=".posted-on")
        author = self.select_author(soup, selector=".byline")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.inlineVideo___3Rd2d', '.contentBody___1zFVF', '.mv8']
        content_selector = ".entry-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Golf Channel:
    def GolfChannel(self, src="Golf Channel"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".content-title")
        descr = self.select_descr(soup, selector=".article-dek")
        date = self.select_date(soup, selector=".byline__date")
        author = self.select_author(soup, selector=".byline .name")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.inlineVideo___3Rd2d', '.contentBody___1zFVF', '.mv8']
        content_selector = "#article-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for MMA Fighting:
    def MMAFighting(self, src="Golf Channel"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".c-page-title")
        descr = None#self.select_descr(soup, selector=".article-dek")
        date = self.select_date(soup, selector="time.c-byline__item")
        author = self.select_author(soup, selector=".c-byline__author-name")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote', '.inlineVideo___3Rd2d', '.contentBody___1zFVF', '.mv8']
        content_selector = ".c-entry-content "
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for TASS Russian News Agency:
    def TASS(self, src="TASS Russian News Agency"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".news-header__title")
        if title == soup.title.text.strip():
            title = self.select_title(soup, selector=".article__title")
        try:
            st = self.select_title(soup, selector=".article__subtitle")
            title = title + ": " + st
        except:
            pass
        descr = self.select_descr(soup, selector=".news-header__lead")
        if descr is None:
            descr = self.select_descr(soup, selector=".article-lead")
        date = self.select_date(soup, selector=".ng-binding.ng-scope")
        author = None#self.select_author(soup, selector=".c-byline__author-name")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote']
        content_selector = ".text-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Agence France-Presse:
    def AFP(self, src="Agence France-Presse"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".content-title")
        descr = self.select_descr(soup, selector=".news-header__lead")
        if descr is None or "factcheck." in url:
            descr = self.select_descr(soup, selector="h3.ltr")
        date = self.select_date(soup, selector=".meta-date")
        author = self.select_author(soup, selector=".meta-author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote']
        content_selector = ".article-entry"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for United Press International:
    def UPI(self, src="United Press International"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="[itemprop='headline']")
        descr = None
        date = self.select_date(soup, selector=".article-date")
        author = self.select_author(soup, selector=".news-head .author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote']
        content_selector = "[itemprop='articleBody']"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Australian Associated Press:
    def AAP(self, src="Australian Associated Press"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".c-article__title")
        descr = self.select_descr(soup, selector=".news-header__lead")
        date = self.select_date(soup, selector=".c-article__date")
        author = self.select_author(soup, selector=".c-article__byline")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote']
        content_selector = ".c-article__content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for China Daily:
    def ChinaDaily(self, src="China Daily"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".content h1")
        if title == soup.title.text.strip():
            title = self.select_title(soup, selector=".main_art h1")
        descr = self.select_descr(soup, selector=".news-header__lead")
        meta = self.select_date(soup, selector=".data")
        if meta is None or len(meta) < 2:
            meta = self.select_date(soup, selector=".info_l")
        try:
            if meta.count("|") == 1:
                author, date = meta.split("|")[0].strip(), meta.split("|")[1].strip()
            elif meta.count("|") == 2:
                author, date = meta.split("|")[0].strip(), meta.split("|")[2].strip()
            else:
                author, date = None, None
        except:
            author, date = None, None
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote']
        if "chinadailyasia.com" in url:
            content_selector = ".news-cut"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        else:
            content_selector = "#Content"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        if len(dct['text'][0].split()) > 200:
            dct['text'] = [dct['text'][0]]
        return (dct, article_data)

    # Method for China Daily Asia:
    def ChinaDailyAsia(self, src="China Daily Asia"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".title_txt")
        descr = None#self.select_descr(soup, selector=".news-header__lead")
        date = self.select_date(soup, selector=".time_text")
        author = self.select_author(soup, selector=".news-edit")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote']
        content_selector = ".news-cut"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["READ MORE:", "ALSO READ:"])
        if len(dct['text'][0].split()) > 200:
            dct['text'] = [dct['text'][0]]
        return (dct, article_data)

    # Method for South China Morning Post (NOTE: ONLY CAN GET THE SUMMARY):
    def SCMP(self, src="South China Morning Post"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".info__headline.headline")
        descr = self.select_author(soup, selector=".generic-article__summary--li.content--li") # SELECT AUTHOR SO IT CAN BE SEPARATED W/COMMAS
        date = self.select_date(soup, selector=".article-author__published-date")
        author = self.select_author(soup, selector=".article-author__name-link")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote']
        content_selector = "body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for ChinaTechNews:
    def ChinaTechNews(self, src="ChinaTechNews"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".entry-title")
        descr = None#self.select_author(soup, selector=".generic-article__summary--li.content--li")
        date = self.select_date(soup, selector=".td-post-date")
        author = self.select_author(soup, selector=".td-post-author-name")
        try:
            author = author.replace("-", "")
        except:
            pass
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote']
        content_selector = ".td-post-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for TechNode:
    def TechNode(self, src="TechNode"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".entry-title ")
        descr = None#self.select_descr(soup, selector="#summary")
        date = self.select_date(soup, selector=".posted-on")
        author = self.select_author(soup, selector=".author.vcard")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote']
        content_selector = ".entry-content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Caixin Global:
    def CaixinGlobal(self, src="Caixin Global"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".cons-title ")
        descr = None#self.select_descr(soup, selector="#summary")
        date = self.select_date(soup, selector=".cons-date")
        author = self.select_author(soup, selector=".cons-author")
        if author is not None:
            if "/" in author:
                author, date = author.split("/")[0].strip(), author.split("/")[1].strip()
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote']
        try:
            content_selector = ".live-content"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        except:
            content_selector = "#appContent"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Russia Beyond:
    def RussiaBeyond(self, src="Russia Beyond"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".article__head h1")
        descr = self.select_descr(soup, selector=".article__summary")
        date = self.select_date(soup, selector="time.date")
        author = self.select_author(soup, selector=".article__author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', 'blockquote']
        content_selector = ".article__text"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["If using any of Russia Beyond's content, partly or in full, always provide an active hyperlink to the original material."])
        return (dct, article_data)

    # Method for Marchmont Innovation News:
    def MarchmontInnovationNews(self, src="Marchmont Innovation News"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".article__head h1")
        descr = self.select_descr(soup, selector=".article__summary")
        date = self.select_date(soup, selector="time.date")
        author = self.select_author(soup, selector=".article__author")
        arr = [soup.select(".new_anonse_txt")[0].text.strip()]
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Schneier on Security:
    def SchneieronSecurity(self, src="Schneier on Security"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".entry")
        descr = None#self.select_descr(soup, selector=".article__summary")
        date = self.select_date(soup, selector=".posted a")
        author = "Bruce Schneier"#self.select_author(soup, selector=".article__author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', '.entry', '.posted', '.entry-tags', '.entry-categories']
        content_selector = ".article"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["If using any of Russia Beyond's content, partly or in full, always provide an active hyperlink to the original material."])
        return (dct, article_data)

    # Method for Lawfare:
    def Lawfare(self, src="Lawfare"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".title")
        descr = None#self.select_descr(soup, selector=".article__summary")
        date = self.select_date(soup, selector=".article-top datetime")
        author = self.select_author(soup, selector=".article-top__contributors")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'header', 'footer', '.region-content-footer', '.pane-node-field-article-tags', '.pane-node-field-article-topics']
        content_selector = "body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Brookings:
    def Brookings(self, src="Brookings"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".headline-wrapper h1")
        descr = None#self.select_descr(soup, selector=".article__summary")
        date = self.select_date(soup, selector="time.date")
        author = self.select_author(soup, selector=".names")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.linear-related', '.inline-widget', 'blockquote']
        content_selector = ".post-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Russia Matters:
    def RussiaMatters(self, src="Russia Matters"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.node__title")
        descr = None#self.select_descr(soup, selector=".article__summary")
        date = self.select_date(soup, selector=".node__published")
        author = self.select_author(soup, selector=".node__author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.linear-related', '.inline-widget', 'blockquote']
        content_selector = ".node-inner"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Photo:"])
        return (dct, article_data)

    # Method for The Earth Institute:
    def TheEarthInstitute(self, src="The Earth Institute"):
        (source, url, soup) = self.handle_meta(src)
        if "blogs.ei.columbia.edu" in url:
            title = self.select_title(soup, selector=".page-title")
            descr = self.select_descr(soup, selector=".subtitle")
            date = self.select_date(soup, selector=".time")
            author = self.select_author(soup, selector=".author")
        else:
            title = self.select_title(soup, selector=".page-title")
            descr = self.select_descr(soup, selector=".subtitle")
            date = self.select_date(soup, selector=".date")
            author = self.select_author(soup, selector=".author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'aside', '.subtitle', '.date', '.time', '.wp-caption-text', '.page-title', '.tags', '.related-posts', '#wpmchimpab', '#comments']
        content_selector = ".content"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The History Blog:
    def TheHistoryBlog(self, src="The History Blog"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".post h2")
        descr = None  # self.select_descr(soup, selector=".article__summary")
        date = self.select_date(soup, selector=".prefix")
        author = self.select_author(soup, selector=".node__author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside']
        content_selector = ".entry"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Business Today:
    def BusinessTodayIN(self, src="Business Today"):
        (source, url, soup) = self.handle_meta(src)
        if "/money/" in url:
            title = self.select_title(soup, selector="#storybody h1")
            descr = self.select_descr(soup, selector=".story_kicker")
            date = self.select_date(soup, selector=".storycomment_date li")
            author = self.select_author(soup, selector=".in_webtitle")
        else:
            title = self.select_title(soup, selector="#storybody h1")
            descr = self.select_descr(soup, selector=".story_kicker")
            # date = self.select_date(soup, selector=".prefix")
            meta = self.select_author(soup, selector=".story-details")
            try:
                if meta.count("|") == 1:
                    author, date = meta.split("|")[0].strip(), meta.split("|")[1].strip()
                elif meta.count("|") == 2:
                    author, date = meta.split("|")[0].strip(), meta.split("|")[2].strip()
                else:
                    author, date = None, None
            except:
                author, date = None, None
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside']
        content_selector = '[itemprop="articleBody"]'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["ALSO READ:"])
        if len(dct['text'][0].split()) > 200:
            dct['text'] = [dct['text'][0]]
        return (dct, article_data)

    # Method for Confectionery News:
    def ConfectioneryNews(self, src="Confectionery News"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".Detail-title")
        descr = self.select_descr(soup, selector=".Detail-intro")
        date = self.select_date(soup, selector=".Detail-date")
        author = self.select_author(soup, selector=".Detail-author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside']
        content_selector = ".RichText"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Candy Industry:
    def CandyIndustry(self, src="Candy Industry"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".headline")
        descr = self.select_descr(soup, selector=".sub-headline")
        date = self.select_date(soup, selector=".date")
        author = None#self.select_author(soup, selector=".Detail-author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside']
        content_selector = ".article-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)
















    # Method for The San Francisco Chronicle:
    def SFChronicle(self, src="The San Francisco Chronicle"):
        (source, url, soup) = self.handle_meta(src)
        if "/visionsf/" in url:
            return self.VisionSF(src="VisionSF")
        title = self.select_title(soup, selector=".header-title")
        descr = None#self.select_descr(soup, selector=".sub-headline")
        date = self.select_date(soup, selector=".header-author-time time")
        author = self.select_author(soup, selector=".header-byline")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside']
        if "projects.sfchronicle" in url:
            garbage_arr += ["header", "footer", "nav"]
            content_selector = "body"
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
            return (dct, article_data)
        content_selector = ".body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for VisionSF:
    def VisionSF(self, src="VisionSF"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".headline")
        descr = None#self.select_descr(soup, selector=".sub-headline")
        date = self.select_date(soup, selector=".datestamp")
        author = self.select_author(soup, selector=".byline")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.asset_media', '.asset_gallery']
        content_selector = ".article-text"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Datebook:
    def Datebook(self, src="Datebook"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector=".entry-header h1")
        descr = None#self.select_descr(soup, selector=".sub-headline")
        date = self.select_date(soup, selector=".dateline")
        author = self.select_author(soup, selector=".byline .author")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.asset_media', '.asset_gallery', '.wp-caption']
        content_selector = ".post-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Newsday:
    def Newsday(self, src="Newsday"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="header h1")
        descr = None#self.select_descr(soup, selector=".sub-headline")
        date = self.select_date(soup, selector=".byline time")
        author = self.select_author(soup, selector=".byline strong")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.asset_media', '.asset_gallery', '.wp-caption']
        content_selector = "#contentAccess"#.story-body
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Philadelphia Inquirer:
    def Inquirer(self, src="The Philadelphia Inquirer"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.lede")
        descr = None#self.select_descr(soup, selector=".sub-headline")
        date = self.select_date(soup, selector=".byline .timestamp")
        author = self.select_author(soup, selector=".pb-f-article-author .byline .font-bold")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.wp-caption', '.card-embedded-content']
        content_selector = ".article-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["READ MORE:", "Get the news you need to start your day", "HELP US REPORT:"])
        return (dct, article_data)

    # Method for The Globe And Mail:
    def TheGlobeAndMail(self, src="The Globe And Mail"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="header h1")
        descr = None#self.select_descr(soup, selector=".sub-headline")
        date = self.select_date(soup, selector=".c-timestamp")
        author = self.select_author(soup, selector=".c-byline.c-link.byline")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.fsk-ad', '.fsk-ad-message']
        content_selector = ".c-article-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Story continues below advertisement", "Sign up today"])
        return (dct, article_data)

    # Method for The Star Tribune:
    def TheStarTribune(self, src="The Star Tribune"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector="h1.article-headline")
        descr = None#self.select_descr(soup, selector=".sub-headline")
        date = self.select_date(soup, selector=".article-dateline")
        author = self.select_author(soup, selector=".article-byline a")
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.wp-caption', '.card-embedded-content', '.inline-media', '.is-promo h3']
        content_selector = ".article-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Omaha World-Herald:
    def TheOmahaWorldHerald(self, src="The Omaha World-Herald"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='[itemprop="headline"]')
        descr = None#self.select_descr(soup, selector=".sub-headline")
        date = self.select_date(soup, selector=".meta time")
        author = self.select_author(soup, selector='.meta [itemprop="author"]')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.social-share-links', '.lee-featured-subscription', '.inline-asset', '.asset-tags', '.asset-tagline', '.asset-author', '.p402_hide.hidden-print']
        content_selector = '[itemprop="articleBody"]'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for New Food Magazine:
    def NewFoodMagazine(self, src="New Food Magazine"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='main article h1')
        descr = self.select_descr(soup, selector=".excerpt")
        date = self.select_date(soup, selector=".date")
        author = self.select_author(soup, selector='.author')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.essb_links', '.date', '.author', '#meta2', '.wp-caption-text', '.crossPromo', '#taxos2', '.terms', '.calloutRight', '.calloutLeft', '.callout']
        content_selector = 'article.single'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for SBS:
    def SBS(self, src="SBS"):
        (source, url, soup) = self.handle_meta(src)
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', 'footer', '.block__container', '.video-player']
        if "/sport/" in url:
            title = self.select_title(soup, selector='#page-title')
            descr = self.select_descr(soup, selector=".field-name-field-abstract")
            date = self.select_date(soup, selector='.content-created')
            author = self.select_author(soup, selector='.author-text .field-value.field-label-inline')
            garbage_arr += [".view-image-list-with-abstract-wrapper"]
            data_arr = [source, url, title, descr, author, date]
            content_selector = '.field-body'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
            return (dct, article_data)
        else:
            title = self.select_title(soup, selector='.text-headline h1')
            descr = self.select_descr(soup, selector=".text-abstract")
            date = self.select_date(soup, selector='.article__meta-date time')
            author = self.select_author(soup, selector='.article__meta-author')
            data_arr = [source, url, title, descr, author, date]
            content_selector = '.article__body'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
            return (dct, article_data)

    # Method for VoxEU:
    def VoxEU(self, src="VoxEU"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.article-title')
        descr = self.select_descr(soup, selector=".article-teaser")
        date = self.select_date(soup, selector=".date-display-single")
        author = self.select_author(soup, selector='.article-title + p strong')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.bookmarks', '.related-content-side']
        content_selector = '.article-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Jim and Nancy Forest:
    def JimAndNancyForest(self, src="Jim and Nancy Forest"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = None#self.select_descr(soup, selector=".article-teaser")
        date = self.select_date(soup, selector="time.entry-date")
        author = self.select_author(soup, selector='a.url.fn.n')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside']
        content_selector = '.entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Inamerrata:
    def Inamerrata(self, src="Inamerrata"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.post h2')
        date = self.select_date(soup, selector=".postmetadata")
        data_arr = [source, url, title, None, "Anthony Towns", date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside']
        content_selector = '.entry'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Buzzfeed:
    def Buzzfeed(self, src="Buzzfeed"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.news-article-header__title')
        descr = self.select_descr(soup, selector=".news-article-header__dek")
        date = self.select_date(soup, selector=".news-article-header__timestamps-posted")
        author = self.select_author(soup, selector='.news-byline-full__name')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside']
        content_selector = '.js-article-wrapper'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Salon:
    def Salon(self, src="Salon"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.title-container h1')
        descr = self.select_descr(soup, selector=".title-container h2")
        date = self.select_date(soup, selector=".writer_info_wrapper h6")
        author = self.select_author(soup, selector='.writer_info_wrapper h5')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.social_comments_app_wrapper', '.topic_explore_box', '.right-rail']
        content_selector = '.article_rail_wrapper'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["To enable screen reader support, press ⌘+Option+Z To learn about keyboard shortcuts, press ⌘slash"])
        return (dct, article_data)

    # Method for GeekWire:
    def GeekWire(self, src="GeekWire"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = None#self.select_descr(soup, selector=".news-article-header__dek")
        date = self.select_date(soup, selector="time.published")
        author = self.select_author(soup, selector='span[itemprop="author"]')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside']
        content_selector = '.entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Tampa Bay Times:
    def TheTampaBayTimes(self, src="The Tampa Bay Times"):
        (source, url, soup) = self.handle_meta(src)
        if "/opinion/" in url:
            title = self.select_title(soup, selector='.opinion__headline')
            descr = self.select_descr(soup, selector=".opinion__subheadline")
        else:
            title = self.select_title(soup, selector='.article__headline')
            descr = self.select_descr(soup, selector=".article__summary")
        date = self.select_date(soup, selector=".timestamp--published")
        author = self.select_author(soup, selector='.author-bio__content--byline')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside']
        content_selector = '.article__body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Christian Science Monitor:
    def ChristianScienceMonitor(self, src="Christian Science Monitor"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='#headline')
        descr = self.select_descr(soup, selector="#summary")
        if descr is None:
            descr = self.select_descr(soup, selector=".editor-intro")
        date = self.select_date(soup, selector="#date-published")
        author = self.select_author(soup, selector='.story-bylines .author')
        data_arr = [source, url, title, descr, author, date]
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '.injection']
        content_selector = '.deep-read'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Editor’s note: As a public service, the Monitor has removed the paywall for all our coronavirus coverage. It’s free."])
        return (dct, article_data)

    # Method for The Baltimore Sun:
    def TheBaltimoreSun(self, src="The Baltimore Sun"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.pb-f-article-header h1')
        descr = None
        date = self.select_date(soup, selector='.pb-f-article-header .timestamp-wrapper')
        author = self.select_author(soup, selector=".pb-f-article-header .byline-wrapper .byline-article")
        selectors = 'p, h2, h3, h4, h5, h6'#, ul li, ol li
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', 'footer', '#more-on', '.pb-f-article-gallery', '.fte-hd', '.nws-cnt']
        data_arr = [source, url, title, descr, author, date]
        content_selector = ".pb-f-article-body"
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The New York Sun:
    def TheNewYorkSun(self, src="The New York Sun"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.article_head h1')
        descr = None
        date = self.select_date(soup, selector='.byline')
        try:
            date = date.split("|")[-1].strip()
        except:
            date = None
        author = self.select_author(soup, selector='[itemprop="author"]')
        selectors = 'p, h2, h3, h4, h5, h6'#, ul li, ol li
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', 'footer', '#more-on', '.pb-f-article-gallery', '.fte-hd', '.nws-cnt']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '[itemprop="articleBody"]'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Atlanta Journal-Constitution:
    def TheAtlantaJournalConstitution(self, src="The Atlanta Journal-Constitution"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.headline-text')
        descr = None
        date = self.select_date(soup, selector='.article-timestamp')
        if date is not None:
            date = date.replace("|", "").strip()
        author = self.select_author(soup, selector='.byline')
        selectors = 'p, h2, h3, h4, h5, h6'#, ul li, ol li
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', 'footer', '#more-on', '.pb-f-article-gallery', '.fte-hd', '.nws-cnt']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.c-articleBodyContainer'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Atlanta Journal-Constitution - Doctors & Sex Abuse Investigation:
    def DoctorsSexAbuseInvestigation(self, src="The Atlanta Journal-Constitution - Doctors & Sex Abuse Investigation"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.title h1')
        descr = None
        date = None#self.select_date(soup, selector='.article-timestamp')
        author = self.select_author(soup, selector='.byline')
        selectors = 'p, h2, h3, h4, h5, h6'#, ul li, ol li
        garbage_arr = ['figure', 'figcaption', 'aside', '.video']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.story-body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        dct['text'].append("This is only a summary. Click 'Visit link' above to view the full article.")
        return (dct, article_data)

    # Method for LosAngelesDailyNews:
    def LosAngelesDailyNews(self, src="LosAngelesDailyNews"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-header .entry-title')
        descr = None
        date = self.select_date(soup, selector='.time')
        author = self.select_author(soup, selector='.author-name')
        selectors = 'p, h2, h3, h4, h5, h6'#, ul li, ol li
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', 'footer', '#more-on', '.pb-f-article-gallery', '.fte-hd', '.nws-cnt']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.article-body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Daily Journal:
    def DailyJournal(self, src="The Daily Journal"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.post-header h1')
        descr = None
        date = self.select_date(soup, selector='.post-header h4')
        author = self.select_author(soup, selector='.box-primary-title')
        selectors = 'p, h2, h3, h4, h5, h6'#, ul li, ol li
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', 'footer', '.modal', 'nav', '#collapseSearch', '.top-nav-links', '.dropdown-menu']
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Pacific Standard:
    def PacificStandard(self, src="Pacific Standard"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.m-detail-header--title')
        descr = self.select_descr(soup, selector='.m-detail-header--dek')
        date = self.select_date(soup, selector='.m-detail-header--date')
        author = self.select_author(soup, selector='.m-detail-header--meta-author')
        selectors = 'p, h2, h3, h4, h5, h6'#, ul li, ol li
        garbage_arr = ['figure', 'blockquote', 'figcaption', 'small', 'aside', 'footer', '.modal', 'nav', '#collapseSearch', '.top-nav-links', '.dropdown-menu']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.m-detail--body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for TechDirt:
    def TechDirt(self, src="TechDirt"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.posttitle')
        descr = None#self.select_descr(soup, selector='.m-detail-header--dek')
        date = self.select_date(soup, selector='.pub_date')
        author = self.select_author(soup, selector='.byline a')
        selectors = 'p, h2, h3, h4, h5, h6'#, ul li, ol li
        garbage_arr = ['figure', 'figcaption', 'small', 'aside', '#post_end', '.filed']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.postbody'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Reading.Guru:
    def ReadingGuru(self, src="Reading.Guru"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = None#self.select_descr(soup, selector='.m-detail-header--dek')
        date = self.select_date(soup, selector='.published')
        author = self.select_author(soup, selector='.byline a')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Read More Like This", "Recent Articles"])
        return (dct, article_data)

    # Method for Taylor Pearson:
    def TaylorPearson(self, src="Taylor Pearson"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = None#self.select_descr(soup, selector='.m-detail-header--dek')
        date = None#self.select_date(soup, selector='.published')
        author = None#self.select_author(soup, selector='.entry-author-name')
        selectors = 'p, h1, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', '.tve-leads-conversion-object']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Read More Like This", "Recent Articles"])
        if len(dct['text']) < 12:
            garbage_arr += [".header-widget-area", '.my-essay', '.site-title', 'footer', '.wpc-small-footer']
            arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr, dont_append_keys=["RELATED:"])
            article_data = SingleArticle(source, url, title, descr, author, date, arr)
            dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
            return (dct, article_data)
        return (dct, article_data)

    # Method for Collaborative Fund:
    def CollaborativeFund(self, src="Collaborative Fund"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.header__header h1')
        descr = None#self.select_descr(soup, selector='.m-detail-header--dek')
        date = self.select_date(soup, selector='.header__header time')
        author = self.select_author(soup, selector='.header__header .js-author')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'footer', '.newsletter']
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'article.post'#entry-content
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Read More Like This", "Recent Articles"])
        return (dct, article_data)

    # Method for Nat Eliason:
    def NatEliason(self, src="Nat Eliason"):
        (source, url, soup) = self.handle_meta(src)
        selectors = 'p, h1, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', '.also-like-section', '.email-cta']
        if "/notes/" in url:
            title = self.select_title(soup, selector='.notes-title')
            descr = None#self.select_descr(soup, selector='.m-detail-header--dek')
            date = None#self.select_date(soup, selector='.blog-date')
            author = "Nat Eliason"  # self.select_author(soup, selector='.blog-author')
            garbage_arr += [".header-widget-area", '.my-essay', '.site-title', 'footer', '.wpc-small-footer']
            arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr)
            article_data = SingleArticle(source, url, title, descr, author, date, arr)
            dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
            return (dct, article_data)
        else:
            title = self.select_title(soup, selector='.blog-heading')
            descr = self.select_descr(soup, selector='.m-detail-header--dek')
            date = self.select_date(soup, selector='.blog-date')
            author = "Nat Eliason"  # self.select_author(soup, selector='.blog-author')
            data_arr = [source, url, title, descr, author, date]
            content_selector = '.blog-body'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Greylock Blog:
    def GreylockBlog(self, src="Greylock Blog"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = self.select_descr(soup, selector='.section-info__title')
        date = self.select_date(soup, selector='.posted-on')
        author = self.select_author(soup, selector='.author')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'footer']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Read More Like This", "Recent Articles"])
        return (dct, article_data)

    # Method for Greylock News:
    def GreylockNews(self, src="Greylock News"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='article h1')
        descr = None#self.select_descr(soup, selector='.section-info__title')
        date = None#self.select_date(soup, selector='.posted-on')
        author = None#self.select_author(soup, selector='.author')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'footer']
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'body article'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Read More Like This", "Recent Articles"])
        return (dct, article_data)

    # Method for Movement Capital:
    def MovementCapital(self, src="Movement Capital"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = None#self.select_descr(soup, selector='.section-info__title')
        date = None#self.select_date(soup, selector='.posted-on')
        author = None#self.select_author(soup, selector='.author')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'footer', '.mc4wp-form-fields']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Read More Like This", "Recent Articles"])
        return (dct, article_data)

    # Method for Graham Mann:
    def GrahamMann(self, src="Graham Mann"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = None#self.select_descr(soup, selector='.section-info__title')
        date = None#self.select_date(soup, selector='.posted-on')
        author = None#self.select_author(soup, selector='.author')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, blockquote'
        garbage_arr = ['aside', 'footer', '.form-block']
        if "/blog/" in url:
            data_arr = [source, url, title, descr, author, date]
            content_selector = '.blog-content'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
            return (dct, article_data)
        elif "/shorts/" in url:
            data_arr = [source, url, title, descr, author, date]
            content_selector = '.w-richtext'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
            return (dct, article_data)
        elif "/book-notes/" in url:
            data_arr = [source, url, title, descr, author, date]
            content_selector = '.book-notes-content'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
            return (dct, article_data)
        else:
            data_arr = [source, url, title, descr, author, date]
            content_selector = 'body'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
            return (dct, article_data)

    # Method for Growth.me:
    def GrowthME(self, src="Movement Capital"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = self.select_descr(soup, selector='.summary-overview-text')
        try:
            top_quote = self.select_descr(soup, selector='.featured-top-quote-text')
            if top_quote is not None and descr is not None:
                descr = f"{descr} . . . Featured top quote: {top_quote}"
        except:
            pass
        date = None#self.select_date(soup, selector='.posted-on')
        author = None#self.select_author(soup, selector='.author')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'footer', '.related-books-horizontal-section', '.under-title-meta-tags', '.summary-featured-video', 'header']
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'body'#entry-content
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for James Clear:
    def JamesClear(self, src="James Clear"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.page__header h1')
        descr = None#self.select_descr(soup, selector='.section-info__title')
        date = None#self.select_date(soup, selector='.posted-on')
        author = None#self.select_author(soup, selector='.author')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, .footnotetitle'
        garbage_arr = ['aside', 'footer']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.page__content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Read More Like This", "Recent Articles"])
        return (dct, article_data)

    # Method for The Daily Express:
    def TheDailyExpress(self, src="The Daily Express"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='[itemprop="headline"]')
        descr = self.select_descr(soup, selector='header.clearfix h3')
        date = self.select_date(soup, selector='.dates')
        author = self.select_author(soup, selector='[itemprop="author"]')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, .footnotetitle'
        garbage_arr = ['aside', 'footer', '.jw-player-container', '.box', '.newsletter-pure']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '[data-type="article-body"]'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["READ MORE:"])
        return (dct, article_data)

    # Method for The Daily Mail:
    def TheDailyMail(self, src="The Daily Mail"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='#content h2')
        descr = self.select_author(soup, selector='.mol-bullets-with-font li')
        date = self.select_date(soup, selector='.article-timestamp.article-timestamp-published')
        author = self.select_author(soup, selector='.author-section')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, .footnotetitle'
        garbage_arr = ['aside', 'footer', '.jw-player-container', '.box', '.newsletter-pure', '.imageCaption', '.related-carousel', '.art-ins', '.mol-factbox', 'span.mol-style-bold.mol-style-medium']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '[itemprop="articleBody"]'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["READ MORE:"])
        return (dct, article_data)

    # Method for The Daily Mirror:
    def TheDailyMirror(self, src="The Daily Mirror"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='[itemprop="headline name"]')
        descr = self.select_descr(soup, selector='[itemprop="description"]')
        date = self.select_date(soup, selector='.time-info')
        author = self.select_author(soup, selector='.author a')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'footer', 'form']
        data_arr = [source, url, title, descr, author, date]
        try:
            content_selector = '.article-body'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["READ MORE:"])
        except:
            content_selector = 'body'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["READ MORE:"])
        return (dct, article_data)

    # Method for The Daily Star:
    def TheDailyStar(self, src="The Daily Star"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='[itemprop="headline name"]')
        descr = self.select_descr(soup, selector='[itemprop="description"]')
        date = self.select_date(soup, selector='.time-info')
        author = self.select_author(soup, selector='.author a')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'footer', 'form']
        data_arr = [source, url, title, descr, author, date]
        try:
            content_selector = '.article-body'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["READ MORE:"])
        except:
            content_selector = 'body'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["READ MORE:"])
        return (dct, article_data)

    # Method for The Evening Standard:
    def TheEveningStandard(self, src="The Daily Star"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='article header h1')
        descr = self.select_descr(soup, selector='article header p')
        date = self.select_date(soup, selector='.publish-date')
        author = self.select_author(soup, selector='.author')
        try:
            author = author.replace(date, "").strip()
        except:
            pass
        selectors = '.sc-clsHhM.eSXakm, .sc-fkubWd.dVlZWi ul li'#'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'footer', 'form']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '#main'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Telegraph:
    def TheTelegraph(self, src="The Telegraph"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='title')
        descr = None#self.select_descr(soup, selector='article header p')
        date = None#self.select_date(soup, selector='.dateTimeStory')
        author = None#self.select_author(soup, selector='.Author')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'footer', 'form', 'header', 'nav']
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Twitter Icon", "Instagram Icon", "Email Icon", "WhatsApp Icon", "Facebook Icon"])
        return (dct, article_data)

    # Method for This Is Money:
    def ThisIsMoney(self, src="This Is Money"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='#content h2')
        descr = self.select_descr(soup, selector='.mol-bullets-with-font li')
        date = self.select_date(soup, selector='.article-timestamp.article-timestamp-published')
        author = self.select_author(soup, selector='.author-section')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, .footnotetitle'
        garbage_arr = ['aside', 'footer', '.jw-player-container', '.box', '.newsletter-pure', '.imageCaption', '.related-carousel', '.art-ins', '.mol-factbox', 'span.mol-style-bold.mol-style-medium', '.moduleFull']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '[itemprop="articleBody"]'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["READ MORE:"])
        return (dct, article_data)

    # Method for Sequoia Capital Blog:
    def SequoiaCap(self, src="Sequoia Capital Blog"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.page-content h1')
        descr = self.select_descr(soup, selector='.mol-bullets-with-font li')
        date = self.select_date(soup, selector='.article-timestamp.article-timestamp-published')
        author = self.select_author(soup, selector='.author-section')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, .footnotetitle'
        garbage_arr = ['aside', 'footer']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.js-article-body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["READ MORE:"])
        return (dct, article_data)

    # Method for Fact Check:
    def FactCheck(self, src="Fact Check"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = self.select_descr(soup, selector='.mol-bullets-with-font li')
        date = self.select_date(soup, selector='.entry-date')
        author = self.select_author(soup, selector='.byline')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'footer']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["READ MORE:"])
        return (dct, article_data)

    # Method for Next Draft:
    def NextDraft(self, src="Next Draft"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = self.select_descr(soup, selector='.mol-bullets-with-font li')
        date = self.select_date(soup, selector='.blurb-date')
        author = self.select_author(soup, selector='.byline')
        garbage_arr = ['aside', 'footer', '.blurb-social', '.email-item-box']

        blurbs = False
        try:
            if len(soup.select('.daily-blurb')) > 0:
                blurbs = True
        except:
            pass
        if blurbs:
            soup = self.removeOtherGarbage(soup, *garbage_arr)
            full = []
            selected = soup.select(".daily-blurb")
            selectors = '.blurb-count, .blurb-content h3, .blurb-content p'
            for item in selected:
                ps = item.select(selectors)
                for p in ps:
                    full.append(p.text.strip())
            article_data = SingleArticle(source, url, title, descr, author, date, full)
            dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date,'text': full}
            return (dct, article_data)
        else:
            selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
            data_arr = [source, url, title, descr, author, date]
            content_selector = '.entry-content'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr,)
            return (dct, article_data)

    # Method for Nautilus:
    def Nautilus(self, src="Nautilus"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.article-title')
        descr = self.select_descr(soup, selector='.article-subtitle')
        author = self.select_author(soup, selector='[itemprop="author"]')
        date = self.select_date(soup, selector='.byline')
        try:
            date = date.replace(author, "").replace("By", "").strip()
        except:
            pass
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'footer']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.page-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for National Geographic:
    def NationalGeographic(self, src="National Geographic"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.main-title')
        descr = self.select_descr(soup, selector='.article__deck')
        author = self.select_author(soup, selector='[itemprop="name"]')
        date = self.select_date(soup, selector='.byline-component__publish')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'footer']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for History.com:
    def History(self, src="History.com"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.m-detail-header--title')
        descr = self.select_descr(soup, selector='.m-detail-header--dek')
        author = self.select_author(soup, selector='.m-detail-header--meta-author')
        if "/this-day-in-history" in url:
            date = self.select_date(soup, selector=".m-component-header--datepicker-trigger.m-datepicker--trigger")
        else:
            date = self.select_date(soup, selector='.m-detail-header--date.m-detail-header--updated-date-definition')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figure', 'figcaption']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.m-detail--body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Kleiner Perkins | Perspectives:
    def KleinerPerkins(self, src="Kleiner Perkins | Perspectives"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.article__title')
        descr = None#self.select_descr(soup, selector='.m-detail-header--dek')
        author = None#self.select_author(soup, selector='.m-detail-header--meta-author')
        date = self.select_date(soup, selector=".article__datetime")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figure', 'figcaption']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.article__body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Haystack:
    def Haystack(self, src="Haystack"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = None#self.select_descr(soup, selector='.m-detail-header--dek')
        author = "Semil Shah"#self.select_author(soup, selector='.m-detail-header--meta-author')
        date = self.select_date(soup, selector=".post-date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figure', 'figcaption']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Index Ventures | Perspectives:
    def IndexVentures(self, src="Index Ventures | Perspectives"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.article-post-hero__headline')
        descr = None#self.select_descr(soup, selector='.m-detail-header--dek')
        author = self.select_author(soup, selector='.article-post-hero__author-anchor')
        date = self.select_date(soup, selector=".post-date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, blockquote'
        garbage_arr = ['aside', 'figure', 'figcaption']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.body-copy'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Sifted:
    def Sifted(self, src="Sifted"): # NOTE: NOT FOR LISTS RIGHT NOW
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='header h1')
        descr = self.select_descr(soup, selector='header h2')
        author = self.select_author(soup, selector='header p span a')
        date = self.select_date(soup, selector="header time")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figure', 'figcaption', 'blockquote']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Accel Blog:
    def TheAccelBlog(self, src="The Accel Blog"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = self.select_descr(soup, selector='.sqs-block-content')
        author = None#self.select_author(soup, selector='header p span a')
        date = self.select_date(soup, selector=".date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figure', 'figcaption', 'blockquote', 'nav', 'header']
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Bessemer Venture Partners | Atlas:
    def Bessemer(self, src="Bessemer Venture Partners | Atlas"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='article h1')
        descr = self.select_descr(soup, selector='article h2')
        author = self.select_author(soup, selector='.author')
        date = self.select_date(soup, selector=".date")
        selectors = 'p, h1, h2, h3, h4, h5, h6, ul li, ol li, span.line'
        garbage_arr = ['aside', 'figcaption', 'nav', 'header', '.left', '.jumplinks', '.callout.little', '.more']
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for ReadWrite:
    def ReadWrite(self, src="ReadWrite"):
        (source, url, soup) = self.handle_meta(src)
        soup = self.removeOtherGarbage(soup, *['[rel="category tag"]'])
        title = self.select_title(soup, selector='.entry-title')
        descr = self.select_descr(soup, selector='article h2')
        author = self.select_author(soup, selector='.author')
        try:
            author = author.replace("/", "").strip()
            if author.strip()[-1] == ",":
                author = author[:-2]
        except:
            pass
        date = self.select_date(soup, selector=".post-cat")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'nav', 'header', '.related_posts']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Mashable:
    def Mashable(self, src="Mashable"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.title')
        descr = None#self.select_descr(soup, selector='article h2')
        author = self.select_author(soup, selector='.byline')
        date = self.select_date(soup, selector=".article-info time")
        try:
            author = author.replace(date, "").replace("•", "").strip()
        except:
            author = None
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'nav', 'header', '.see-also']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.article-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["WATCH:", "BONUS:"])
        return (dct, article_data)

    # Method for Lee Cole's Blog: An Introduction to Soviet History:
    def LeeCole(self, src="Lee Cole's Blog: An Introduction to Soviet History"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = None#self.select_descr(soup, selector='article h2')
        author = self.select_author(soup, selector='.byline')
        date = self.select_date(soup, selector=".entry-timestamp")
        try:
            if "by" in date:
                i = date.index("by")
                date = date[:i]
        except:
            pass
        try:
            if ":" in date:
                i = date.index(":")
                date = date[:i-2]
        except:
            pass
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'nav', 'header', '.see-also']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Seventeen Moments in Soviet History:
    def SeventeenMoments(self, src="Seventeen Moments in Soviet History"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.title')
        descr = None#self.select_descr(soup, selector='article h2')
        author = self.select_author(soup, selector='.byline')
        date = self.select_date(soup, selector=".article-info time")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'nav', 'header', '#comments']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '#content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Texts Images"])
        return (dct, article_data)

    # Method for Guided History:
    def GuidedHistoryBU(self, src="Guided History"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = None#self.select_descr(soup, selector='article h2')
        author = self.select_author(soup, selector='.byline')
        date = self.select_date(soup, selector=".date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, .csl-entry'
        garbage_arr = ['aside', 'figcaption', 'figure', 'nav', 'header', '.wp-caption', '#footer', '.sidebar', '#header', '#menu']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr)
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for HI 446 Revolutionary Russia:
    def HI446(self, src="HI 446 Revolutionary Russia"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.content-panel h1')
        descr = self.select_descr(soup, selector='.content-panel p')
        author = self.select_author(soup, selector='.byline')
        date = self.select_date(soup, selector=".date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, .csl-entry'
        garbage_arr = ['aside', 'figcaption', 'figure', 'nav', 'header', '.wp-caption', '#footer', '.sidebar', '#header', '#menu']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr)
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for NYU Jordan Center for the Advanced Study of Russia:
    def JordanCenter(self, src="NYU Jordan Center for the Advanced Study of Russia"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = None#self.select_descr(soup, selector='article h2')
        author = self.select_author(soup, selector='.author.url.fn')
        date = self.select_date(soup, selector=".date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'nav', 'header', '#comments']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Texts Images"])
        return (dct, article_data)

    # Method for Russian History Blog:
    def RussianHistoryBlog(self, src="Russian History Blog"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = None#self.select_descr(soup, selector='article h2')
        author = self.select_author(soup, selector='.url.fn.n')
        date = self.select_date(soup, selector=".entry-date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'nav', 'header', '#comments']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for First Round Review:
    def FirstRoundReview(self, src="First Round Review"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='._Title')
        descr = None#self.select_descr(soup, selector='article h2')
        author = None#self.select_author(soup, selector='.url.fn.n')
        date = None#self.select_date(soup, selector=".entry-date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, blockquote'
        garbage_arr = ['aside', 'figcaption', 'figure', 'nav', 'header', '#comments']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '._Content__'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Lightspeed Venture Partners Blog (Old):
    def LSVP(self, src="Lightspeed Venture Partners Blog (Old)"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.post h2')
        descr = None#self.select_descr(soup, selector='article h2')
        author = None#self.select_author(soup, selector='.url.fn.n')
        date = None#self.select_date(soup, selector=".entry-date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'nav', 'header', '.sharedaddy']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.post'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Station F:
    def StationF(self, src="StationF"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.article-title')
        descr = self.select_descr(soup, selector='.article-subtitle')
        author = self.select_author(soup, selector='.article-press .contact-wrapper .name')
        date = self.select_date(soup, selector=".article-date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'nav', 'header', '.sharedaddy', '.article-press']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.article-contents'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        if len(dct['text']) > 6:
            n = None
            for i in range(8):
                if len(dct['text'][i].split()) > 300:
                    dct['text'].pop(i)
                if dct['text'][i+1].strip()[2:20] in dct['text'][i].strip()[1:25]:
                    n = i
                    dct['text'].append(i)
                    break
        if n is not None:
            dct['text'].pop(n)
        return (dct, article_data)

    # Method for Substack:
    def Substack(self, src="Substack"):
        try:
            if src == "Substack":
                src = self.soup.select(".headline .name")[0].text.strip()
        except:
            pass
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.post-title')
        descr = self.select_descr(soup, selector='.subtitle')
        if "sacks.substack.com" in url:
            author = "David Sacks"
        elif "wfh.substack.com" in url:
            author = "Brianne Kimmel"
        else:
            author = None
        date = self.select_date(soup, selector=".post-meta-item.post-date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'nav', 'header', '.sharedaddy', '.subscribe-widget', '.button-wrapper']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Silicon Valley Product Group:
    def SVPG(self, src="Silicon Valley Product Group"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = self.select_descr(soup, selector='.subtitle')
        author = None#self.select_author(soup, selector='.author.vcard a')
        date = self.select_date(soup, selector=".published")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'nav', 'header', '.sharedaddy', '.subscribe-widget', '.button-wrapper']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Basecamp:
    def Basecamp(self, src="Basecamp"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.intro__title')
        descr = self.select_author(soup, selector='.intro__sections li')
        author = None#self.select_author(soup, selector='.author.vcard a')
        date = self.select_date(soup, selector=".published")
        selectors = 'p, h1, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'nav', 'header']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Medium:
    def Medium(self, src="Medium"):
        try:
            if src == "Medium":
                src = self.soup.select('[aria-label="Author Homepage"]')[0].text.strip()
            else:
                src = "Medium"
        except:
            pass
        try:
            if src is None or src == "Medium":
                src = self.soup.title.text.strip().replace("| Medium", "").replace("|Medium", "").split("|")[-1].strip()
        except:
            pass
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='article h1')
        descr = self.select_descr(soup, selector='article h2')
        if "blackboxofpm.com" in url:
            author = "Brandon Chu"
        elif "gibsonbiddle.medium.com" in url:
            author = "Gibson Biddle"
        elif "/hackernoon/" in url:
            author = "HackerNoon"
        elif "merci.medium.com" in url:
            author = "Merci Victoria Grace"
        else:
            author = None
        date = self.select_date(soup, selector=".published")
        selectors = 'p, h1, h2, h3, h4, h5, h6, ul li, ol li, strong.bf'
        garbage_arr = ['aside', 'figcaption', 'figure', 'nav', 'header', '.sharedaddy', '.subscribe-widget', '.button-wrapper']#, '.pq.fm.n.ny.p'
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'body article'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Ken Norton:
    def KenNorton(self, src="Ken Norton"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.post-heading h1')
        descr = self.select_descr(soup, selector='.post-heading h3')
        author = "Ken Norton"#self.select_author(soup, selector='.author.vcard a')
        date = None#self.select_date(soup, selector=".author-byline.author-byline-box")
        selectors = 'p, h1, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'nav', 'header']
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'body article'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for innoarchitech:
    def innoarchitech(self, src="innoarchitech"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.BlogItem-title')
        descr = None#self.select_descr(soup, selector='.post-heading h3')
        author = self.select_author(soup, selector='.Blog-meta-item.Blog-meta-item--author')
        date = self.select_date(soup, selector=".date")
        selectors = 'p, h1, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'nav', 'header']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.sqs-block.html-block.sqs-block-html'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for VentureBeat:
    def VentureBeat(self, src="VentureBeat"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.article-title')
        descr = None#self.select_descr(soup, selector='.post-heading h3')
        author = self.select_author(soup, selector='.author.url.fn')
        date = self.select_date(soup, selector=".the-time")
        selectors = 'p, h1, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'nav', 'header', '.post-boilerplate', '.boilerplate-after']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.article-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for NextGov:
    def NextGov(self, src="NextGov"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.content-title')
        descr = self.select_descr(soup, selector='.content-subhed')
        author = self.select_author(soup, selector='.authors-multiple')
        date = self.select_date(soup, selector=".content-publish-date")
        selectors = 'p, h1, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'nav', 'header', '.related-articles-placeholder']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.content-body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Interesting Engineering:
    def InterestingEngineering(self, src="Interesting Engineering"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.content-title')
        descr = self.select_descr(soup, selector='.content-sub-title')
        meta = self.select_date(soup, selector=".post-tag")
        try:
            months = np.array(["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sept", "Oct", "Nov", "Dec"])
            date = None
            for month in months:
                if meta.find(month) > -1:
                    i = meta.index(month)
                    date = meta[i:]
                    meta = meta.replace(date, "")
                    break
        except:
            date = None
        try:
            author = meta
        except:
            author = None
        selectors = 'p, h1, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'nav', 'header', '.related-articles-placeholder']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.content-text'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["SEE ALSO:"])
        return (dct, article_data)

    # Method for Digital Trends:
    def DigitalTrends(self, src="Digital Trends"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='[itemprop="headline"]')
        descr = None#self.select_descr(soup, selector='.content-subhed')
        author = self.select_author(soup, selector='.b-byline__authors')
        date = self.select_date(soup, selector=".date")
        selectors = 'p, h1, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'nav', 'header', '.h-editors-recs-title', '.h-editors-recs']
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'body article'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for HackerNoon:
    def HackerNoon(self, src="HackerNoon"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='main h1')
        descr = None#self.select_descr(soup, selector='.content-subhed')
        soup = self.removeOtherGarbage(soup, *[".related-stories"])
        author = self.select_author(soup, selector='.profile small')
        date = self.select_date(soup, selector=".date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, code, blockquote'
        garbage_arr = ['aside', 'figcaption', 'figure', 'nav', 'header', '.date', '.Profile__Layout-sc-1j6ysg0-0.dWCilT', '.profile h3', '.profile a', '.profile small', '.profile p', 'footer', 'section h4', '.CallToAction__Layout-sc-1bzkg2-0']
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'main'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Inside Intercom:
    def Intercom(self, src="Inside Intercom"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='[itemprop="headline"]')
        descr = self.select_descr(soup, selector='.card__intro-text')
        author = self.select_author(soup, selector='.single-article__side-content .author.url.fn')
        date = self.select_date(soup, selector=".card__datetime")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'nav', 'blockquote', '.quote', 'header', '.date', '.Profile__Layout-sc-1j6ysg0-0.dWCilT', '.profile h3', '.profile a', '.profile small', '.profile p', 'footer', 'section h4', '.CallToAction__Layout-sc-1bzkg2-0']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.card__main-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Pmarca Guide to Startups:
    def Pmarca(self, src="The Pmarca Guide to Startups"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='h2')
        descr = None#self.select_descr(soup, selector='.card__intro-text')
        author = "Marc Andreessen"#self.select_author(soup, selector='.single-article__side-content .author.url.fn')
        date = self.select_date(soup, selector=".date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'nav', 'blockquote', '.header', '.date']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.post_content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Tomasz Tunguz:
    def TomaszTunguz(self, src="Tomasz Tunguz"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.single-blog__title')
        descr = None#self.select_descr(soup, selector='.card__intro-text')
        author = self.select_author(soup, selector='.single-blog__meta .author.url.fn')
        date = self.select_date(soup, selector=".entry-date")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'nav', 'blockquote', '.header', '.date']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for High Growth Handbook:
    def HighGrowthHandbook(self, src="High Growth Handbook"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = None#self.select_descr(soup, selector='.card__intro-text')
        author = None#self.select_author(soup, selector='.single-blog__meta .author.url.fn')
        date = None#self.select_date(soup, selector=".entry-date")
        selectors = 'p, h1, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'nav', '.subscribe-link', '.share-icons']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Elad Gil's Blog:
    def EladBlog(self, src="Elad Gil's Blog"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = None#self.select_descr(soup, selector='.card__intro-text')
        author = None#self.select_author(soup, selector='.single-blog__meta .author.url.fn')
        date = self.select_date(soup, selector=".date-header")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.post'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["MY BOOKYou can order the High Growth Handbook here."])
        return (dct, article_data)

    # Method for Felt Presence by Ryan Singer:
    def RyanSinger(self, src="Felt Presence by Ryan Singer"):
        (source, url, soup) = self.handle_meta(src)
        if "/feltpresence/" in url:
            title = self.select_title(soup, selector='.entry-title')
            descr = None  # self.select_descr(soup, selector='.card__intro-text')
            author = None  # self.select_author(soup, selector='.single-blog__meta .author.url.fn')
            date = self.select_date(soup, selector=".date-header")
            selectors = 'td'
            garbage_arr = ['aside', 'figcaption', 'figure']
            data_arr = [source, url, title, descr, author, date]
            content_selector = '#bodyTable'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
            dct['text'] = [dct['text'][0]]
            return (dct, article_data)
        else:
            raise AttributeError

    # Method for Menlo Ventures Blog:
    def MenloVCBlog(self, src="Menlo Ventures Blog"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = None#self.select_descr(soup, selector='.card__intro-text')
        author = None#self.select_author(soup, selector='.single-blog__meta .author.url.fn')
        date = None#self.select_date(soup, selector=".date-header")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.blog-item-content.e-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Growth Equity Blog:
    def TheGrowthEquityBlog(self, src="The Growth Equity Blog"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure']
        data_arr = [source, url, title, None, None, None]
        content_selector = '.entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Workhorse Growth Blog:
    def Workhorse(self, src="Workhorse Growth Blog"):
        (source, url, soup) = self.handle_meta(src)
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.sharedaddy', 'nav']
        data_arr = [source, url, soup.title.text.strip(), None, None, None]
        content_selector = '[itemprop="text"]'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Edison Partners Blog:
    def EdisonPartnersBlog(self, src="Workhorse Growth Blog"):
        (source, url, soup) = self.handle_meta(src)
        title = soup.title.text.strip()#self.select_title(soup, selector='.entry-title')
        descr = None#self.select_descr(soup, selector='.card__intro-text')
        try:
            meta = self.select_date(soup, selector=".meta")
            author, date = meta.split(".")[0].strip(), meta.split(".")[1].strip()
        except:
            author, date = None, None
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.sharedaddy', '.hs-embed-wrapper']
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'body article'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Derek Pilling's Blog:
    def DerekPilling(self, src="Derek Pilling's Blog"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = None#self.select_descr(soup, selector='.card__intro-text')
        author = "Derek Pilling"#self.select_author(soup, selector='.single-blog__meta .author.url.fn')
        date = self.select_date(soup, selector=".posted-on")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.sharedaddy']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Boston Globe:
    def TheBostonGlobe(self, src="The Boston Globe"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='h1.headline')
        descr = None#self.select_descr(soup, selector='.card__intro-text')
        author = self.select_author(soup, selector='.authors .author')
        date = self.select_date(soup, selector=".datetime")
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.sharedaddy', '.arc_ad', '.tagline']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '#article-body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Art Newspaper:
    def TheArtNewspaper(self, src="The Art Newspaper"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='[itemprop="headline"]')
        descr = self.select_descr(soup, selector='[itemprop="about"]')
        author = self.select_author(soup, selector='[itemprop="author"]')
        date = self.select_date(soup, selector='.fr-date-line')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.sharedaddy', '.arc_ad', '.tagline']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '[itemprop="articleBody"]'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Funding Universe:
    def FundingUniverse(self, src="Funding Universe"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='#main-content h1')
        descr = None#self.select_descr(soup, selector='[itemprop="about"]')
        author = None#self.select_author(soup, selector='[itemprop="author"]')
        date = None#self.select_date(soup, selector='.fr-date-line')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, dt, dd'
        garbage_arr = ['aside', 'figcaption', 'figure', '.sharedaddy', '.arc_ad', '.tagline']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '#main-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Bookforum:
    def Bookforum(self, src="Bookforum"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.blog-article__header h1')
        # if "•" in title:
        #     title = self.select_title(soup, selector='.blog-article__header h1')
        author = self.select_author(soup, selector='.blog-article__writer')
        date = self.select_date(soup, selector='.print-article__issue-title')
        if date is None:
            date = self.select_date(soup, selector='.article-list__publish-date')
        descr = self.select_descr(soup, selector='.blog-article__subtitle')
        if descr is None:
            descr = self.select_descr(soup, selector='.article-list__byline.article-list__byline--web-only-detail')
            if descr is not None:
                descr = descr.split("•")[-1].strip()
                # date = descr.split("•")[0].strip()
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.sharedaddy', '.wp-caption-text']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.blog-article__content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        if len(dct['text']) <= 1:
            content_selector = 'article'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Books & Culture:
    def BooksAndCulture(self, src="Books & Culture"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='#article_main h3')
        descr = self.select_descr(soup, selector='.italicaption')
        author = self.select_author(soup, selector='#article_main h2')
        date = None#self.select_date(soup, selector='.fr-date-line')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.sharedaddy', '.arc_ad', '.tagline']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '#body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        if "..." in dct['text'][-1]:
            dct['text'].append("Nooooo! Unfortunately, the rest of this article is only available for Books & Culture subscribers.")
        return (dct, article_data)

    # Method for Le Soir:
    def LeSoir(self, src="Le Soir"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='#gr-article h1')
        descr = self.select_descr(soup, selector='.lead.gr-article-teaser')
        author = self.select_author(soup, selector='article .gr-meta.gr-meta-author')
        date = self.select_date(soup, selector='.pubdate')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.sharedaddy', '.gr-linked-stories']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.gr-article-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        if len(dct['text']) <= 2:
            dct['text'].append("Nooooo! Unfortunately, the rest of this article is only available for Le Soir subscribers.")
        return (dct, article_data)

    # Method for New Orleans CityBusiness:
    def CityBusiness(self, src="New Orleans CityBusiness"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = self.select_descr(soup, selector='.lead.gr-article-teaser')
        author = self.select_author(soup, selector='.post-meta-author')
        date = self.select_date(soup, selector='.tie-date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for CIA:
    def CIA(self, src="CIA"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.hero-title')
        descr = self.select_descr(soup, selector='.lead.gr-article-teaser')
        author = self.select_author(soup, selector='.post-meta-author')
        date = self.select_date(soup, selector='.tie-date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.basic-image-container']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.content-area-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Palo Alto Online:
    def PaloAltoOnline(self, src="Palo Alto Online"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='h1')
        descr = self.select_descr(soup, selector='h2')
        author = self.select_author(soup, selector='.byline a')
        date = self.select_date(soup, selector='.dateline')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'header', 'nav', 'footer', '.comment', '.share-tools', '.byline', '.caption', '.dateline', '.section', '.side-block', '.tag']
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Antimafia Duemila:
    def AntimafiaDuemila(self, src="Antimafia Duemila"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.page-header h1')
        descr = None#self.select_descr(soup, selector='h2')
        author = self.select_author(soup, selector='.createdby')
        date = self.select_date(soup, selector='time')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '[itemprop="articleBody"]'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Proactive Investors:
    def ProactiveInvestors(self, src="Antimafia Duemila"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='[itemprop="headline"]')
        descr = self.select_author(soup, selector='[itemprop="description"]')
        author = self.select_author(soup, selector='[itemprop="author"]')
        date = self.select_date(soup, selector='.date-time-published')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '[itemprop="articleBody"]'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Contact the author at [email protected]", "Contact the author: [email protected]", "Follow him on Twitter @"])
        return (dct, article_data)

    # Method for The Chicago Review of Books:
    def TheChicagoReviewOfBooks(self, src="The Chicago Review of Books"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = None#self.select_descr(soup, selector='[itemprop="description"]')
        author = self.select_author(soup, selector='.entry-author')
        date = self.select_date(soup, selector='.entry-date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.sharedaddy']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '#entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for DailyFX:
    def DailyFX(self, src="DailyFX"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.dfx-articleHead__header')
        descr = None#self.select_descr(soup, selector='[itemprop="description"]')
        author = self.select_author(soup, selector='.dfx-articleHead__authorName')
        date = self.select_date(soup, selector='.dfx-articleHead__displayDate')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.sharedaddy']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.dfx-articleBody__content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Click here to read", "Open an IG demo account today."])
        return (dct, article_data)

    # Method for Protocol:
    def Protocol(self, src="Protocol"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.headline')
        descr = self.select_descr(soup, selector='.widget__subheadline')
        author = None#self.select_author(soup, selector='article .widget__body .social-author')
        try:
            author = soup.select(".widget__body .social-author")[0].text.strip()
        except:
            author = None
        date = self.select_date(soup, selector='article .widget__body .social-date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.sharedaddy', '[data-section="related-stories"]', '.around-the-web', '.shortcode-media', '.image-media.media-caption', '.image-media.media-photo-credit']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Currencies Direct:
    def CurrenciesDirect(self, src="Currencies Direct"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='[itemprop="headline"]')
        descr = None#self.select_descr(soup, selector='[itemprop="description"]')
        author = self.select_author(soup, selector='[itemprop="name"]')
        if author is not None:
            if author[0] == ",":
                author = author[1:].strip()
        date = self.select_date(soup, selector='[itemprop="datePublished"]')
        selectors = '[itemprop="description"]'#'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '#content-main'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Click here to read", "Open an IG demo account today."])
        return (dct, article_data)

    # Method for Wired UK:
    def WiredUK(self, src="Wired UK"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.a-header__title')
        descr = self.select_descr(soup, selector='.a-header__teaser')
        author = self.select_author(soup, selector='.a-header__byline')
        date = self.select_date(soup, selector='.a-header__date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.bb-callout', '.promotion-card', '.promotion-card--article']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.a-body__content'# .a-body__content
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Wired Italia:
    def WiredIT(self, src="Wired Italia"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.article-title')
        descr = self.select_descr(soup, selector='.lead')
        author = self.select_author(soup, selector='.who .link')
        date = self.select_date(soup, selector='.when')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.bb-callout', '.promotion-card', '.promotion-card--article', '.article-preview-landscape-list', 'footer']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.entry'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Wired Japan:
    def WiredJP(self, src="Wired Japan"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.tt__hed-upper')
        descr = self.select_descr(soup, selector='.article__intro')
        if descr is None:
            descr = self.select_descr(soup, selector='.tt__hed-upper')
        author = self.select_author(soup, selector='.by-line') # .article-profile__name
        if author is None or len(author) < 2:
            author = self.select_author(soup, selector='.article__credit')
        date = self.select_date(soup, selector='.publish-date')
        if date is None:
            date = self.select_date(soup, selector='.article__date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.bb-callout', '.promotion-card', '.promotion-card--article', '.article-preview-landscape-list', 'footer', '.article-related', '.article-info']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.article-body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Publisher's Weekly:
    def PublishersWeekly(self, src="Publisher's Weekly"):
        (source, url, soup) = self.handle_meta(src)
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.bb-callout', '.promotion-card', '.promotion-card--article', '.article-preview-landscape-list', 'footer']
        if "/book-reviews/" in url:
            title = self.select_title(soup, selector='.article-title')
            descr = self.select_descr(soup, selector='.heading.sub-heading')
            author = self.select_date(soup, selector='.book-description .article-author a')
            date = self.select_date(soup, selector='.book-description .pub-date-mobile')
            try:
                author = author.replace(date, "").replace("•", "").strip()
            except:
                author = None
            data_arr = [source, url, title, descr, author, date]
            content_selector = '.book-content'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        else:
            title = self.select_title(soup, selector='.heading')
            descr = self.select_descr(soup, selector='.heading.sub-heading')
            author = self.select_author(soup, selector='.title-bottom')
            date = self.select_date(soup, selector='.pub-date-mobile')
            try:
                author = author.replace(date, "").replace("•", "").strip()
            except:
                author = None
            data_arr = [source, url, title, descr, author, date]
            content_selector = '.main-content'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Inside Hook:
    def InsideHook(self, src="Inside Hook"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.title-block h1')
        descr = self.select_descr(soup, selector='.title-block h2')
        soup = self.removeOtherGarbage(soup, *[".author-twt"])
        author = self.select_author(soup, selector='.author')
        date = self.select_date(soup, selector='.date')
        try:
            date = date.replace("|", "").strip()
        except:
            pass
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.inline-related']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.main-body'# .a-body__content
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Subscribe here for our free daily newsletter."])
        return (dct, article_data)

    # Method for Romania Insider:
    def RomaniaInsider(self, src="Inside Hook"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.field--name-field-title')
        descr = self.select_descr(soup, selector='.title-block h2')
        author = self.select_author(soup, selector='.field--name-field-author')
        date = self.select_date(soup, selector='.field--name-field-date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.field--name-body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["[email protected]", "Photo source:"])
        return (dct, article_data)

    # Method for Hacker Journal:
    def HackerJournal(self, src="Hacker Journal"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = self.select_descr(soup, selector='.title-block h2')
        author = self.select_author(soup, selector='.mvp-author-info-name')
        date = self.select_date(soup, selector='.mvp-author-info-date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '#mvp-content-main'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["[email protected]", "Photo source:"])
        return (dct, article_data)

    # Method for Oxford American:
    def OxfordAmerican(self, src="Oxford American"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.itemTitle')
        descr = None#self.select_descr(soup, selector='.title-block h2')
        author = self.select_author(soup, selector='.itemAuthor')
        date = self.select_date(soup, selector='.itemDateCreated')
        try:
            date = date.replace("|", "").strip()
        except:
            pass
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'header', 'nav', 'footer']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.itemFullText'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Enjoy this story? Subscribe to the Oxford American."])
        return (dct, article_data)

    # Method for Delayed Gratification:
    def DelayedGratification(self, src="Delayed Gratification"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='#content h1')
        descr = self.select_descr(soup, selector='#content h2.byline')
        author = self.select_author(soup, selector='.article_credit')
        date = self.select_date(soup, selector='.article_date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'header', 'nav', 'footer', '.byline', '.article_credit', '.article_date', '.taken_from_wrap', '.infog_sign_up', '.share_btns_wrap', '.postmetadata', '.article_also_like_wrap', 'blockquote']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.entry'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Enjoy this story? Subscribe to the Oxford American."])
        return (dct, article_data)

    # Method for Handelsblatt:
    def Handelsblatt(self, src="Handelsblatt"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.vhb-content h2')
        descr = self.select_descr(soup, selector='.vhb-article--introduction')
        author = self.select_author(soup, selector='.article_credit')
        date = self.select_date(soup, selector='[itemprop="datePublished"]')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'header', 'nav', 'footer', 'blockquote', '.vhb-hollow-area', '.vhb-caption', '.vhb-credit', '.ob-sub-units', '.vhb-author-shortcutlist', '[data-command="relatedThemes"]', '.vhb-share-social', '.vhb-more', '.vhb-teaser--recommendation', '.vhb-teaser--tab', '.vhb-teaser', '[itemprop="relatedLink"]', '.vhb-serviceoffer-list']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '[itemprop="articleBody"]'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Mehr:", "Jetzt die besten Jobs finden und per E-Mail benachrichtigt werden."])
        return (dct, article_data)

    # Method for Karl Hughes:
    def KarlHughes(self, src="Karl Hughes"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.page-title')
        descr = None#self.select_descr(soup, selector='.vhb-article--introduction')
        author = "Karl Hughes"#self.select_author(soup, selector='.article_credit')
        date = self.select_date(soup, selector='.post-meta')
        try:
            i = date.index("—")
            date = date[:i-1]
        except:
            pass
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.signup', '.page-tags', '.post-meta']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.post-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Free Code Camp:
    def FreeCodeCamp(self, src="Free Code Camp"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.post-full-title')
        descr = None#self.select_descr(soup, selector='.vhb-article--introduction')
        author = self.select_author(soup, selector='.author-card-name')
        date = self.select_date(soup, selector='.post-full-meta-date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, code'
        garbage_arr = ['aside', 'figcaption', 'figure', '.post-full-author-header', '.social-row', '.learn-cta-row']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.post-full-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Nieman Lab:
    def NiemanLab(self, src="Nieman Lab"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.simple-headline')
        descr = self.select_descr(soup, selector='.simple-post-deck')
        author = self.select_author(soup, selector='.bylineauthorname')
        date = self.select_date(soup, selector='.simple-bylinedate')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'#, .conl, .conr
        garbage_arr = ['aside', 'figcaption', 'figure', '.embed-relatedstory', '.simple-siteheader', '.simple-hubmenu', 'header', '.photocredit', '.nieman-footer', '.simple-sidebar-citations', '.sidebar-chunk', '.simple-footer', '.simple-post-deck', '.simple-headline']
        data_arr = [source, url, title, descr, author, date]
        # content_selector = '.simple-body'
        # (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        # return (dct, article_data)
        try:
            mentries = soup.select(".mediumentry")
            if mentries is not None and len(mentries) > 0:
                mentries = True
            else:
                mentries = False
            if mentries:
                selectors = 'p, .mediumentry'
        except:
            pass
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr, dont_append_keys=["A post shared by"])
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Growth Machine:
    def GrowthMachine(self, src="Growth Machine"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.post-header')
        descr = None#self.select_descr(soup, selector='.vhb-article--introduction')
        author = self.select_author(soup, selector='.author-name')
        date = None#self.select_date(soup, selector='.post-full-meta-date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, code'
        garbage_arr = ['aside', 'figcaption', 'figure', '.post-full-author-header', '.social-row', '.learn-cta-row']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.blog-rich-text'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Indian Express:
    def TheIndianExpress(self, src="The Indian Express"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='h1')
        descr = self.select_descr(soup, selector='.synopsis')
        author = self.select_author(soup, selector='.editor a')
        date = self.select_date(soup, selector='[itemprop="dateModified"]')
        if date is None:
            date = self.select_date(soup, selector='[itemprop="datePublished"]')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, code'
        garbage_arr = ['aside', 'figcaption', 'figure', 'header', 'footer', 'nav', '.breaking-news', '.heading-part', '.breaking', '.pdsc-related-modify', '.newsletter_section', '.appstext', '.storytags', '.editor-details', '.breaking-scroll', '#section-nav', '.rightpanel', '.add-first', '.editor-pic']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr, dont_append_keys=["A post shared by"])
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Signal v. Noise:
    def SignalVNoiseM(self, src="Signal v. Noise"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = None#self.select_descr(soup, selector='.vhb-article--introduction')
        author = self.select_author(soup, selector='.byline')
        date = self.select_date(soup, selector='.posted-on')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, code'
        garbage_arr = ['aside', 'figcaption', 'figure']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Signal v. Noise:
    def SignalVNoise(self, src="Signal v. Noise"):
        (source, url, soup) = self.handle_meta(src)
        soup = self.removeOtherGarbage(soup, *[".post-header-info-discuss"])
        title = self.select_title(soup, selector='h1')
        descr = None#self.select_descr(soup, selector='.vhb-article--introduction')
        author = self.select_author(soup, selector='.post-header-info a')
        try:
            if author[0] == ",":
                author = author[1:].strip()
        except:
            pass
        date = self.select_date(soup, selector='.post-date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, code'
        garbage_arr = ['aside', 'figcaption', 'figure']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.post-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Bookseller:
    def TheBookseller(self, src="The Bookseller"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.title')
        descr = None#self.select_descr(soup, selector='.vhb-article--introduction')
        author = self.select_author(soup, selector='.date strong')
        date = self.select_date(soup, selector='.date')
        try:
            date = date.replace(author, "").strip()
        except:
            pass
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.article-content__body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Times:
    def TheTimes(self, src="The Times"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='h1[role="heading"]')
        descr = self.select_descr(soup, selector='[data-testid="standfirst"]')
        author = self.select_author(soup, selector='.responsiveweb__Meta-sc-1pihheg-5')
        date = self.select_date(soup, selector='.responsiveweb__DatePublicationContainer-sc-1pihheg-0')
        try:
            author = author.replace(date, "").strip()
            if author[-1] == ",":
                author = author[:-1].strip()
        except:
            pass
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.hidden']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '[role="article"]'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        if len(dct['text']) <= 3:
            dct['text'].append("Nooooo! If no other content is showing up, then that is because it is only available for Times subscribers.")
        return (dct, article_data)

    # Method for The Financial Times:
    def FT(self, src="The Financial Times"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.o-topper__headline')
        descr = self.select_descr(soup, selector='.o-topper__standfirst')
        author = self.select_author(soup, selector='.n-content-tag--author')
        date = self.select_date(soup, selector='.article-info__timestamp')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.article__content-body'# .n-content-body.js-article__content-body
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Toronto Star:
    def TheStar(self, src="The Toronto Star"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.c-article-headline__heading')
        descr = None#self.select_descr(soup, selector='.o-topper__standfirst')
        author = self.select_author(soup, selector='.article__author a')
        if author is None or len(author) < 2:
            author = self.select_author(soup, selector='.article__author-name')
        date = self.select_date(soup, selector='.article__published-date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'blockquote', '.pull-quote-wrapper', '.share-toolbar-container']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.c-article-body__content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Loading..."])
        return (dct, article_data)

    # Method for CTV News:
    def CTVNews(self, src="CTV News"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.articleHeadline')
        descr = None#self.select_descr(soup, selector='.o-topper__standfirst')
        author = self.select_author(soup, selector='.bioLink')
        date = self.select_date(soup, selector='.date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'blockquote', '.pull-quote-wrapper', '.share-toolbar-container']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.articleBody'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Forward:
    def Forward(self, src="Forward"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.hero-content h1')
        descr = None#self.select_descr(soup, selector='.o-topper__standfirst')
        author = self.select_author(soup, selector='.hero-content [itemprop="author"]')
        date = self.select_date(soup, selector='[itemprop="datePublished"]')
        try:
            if author[0] == ",":
                author = author[1:].strip()
        except:
            pass
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'blockquote']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '[itemprop="articleBody"]'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Big Think:
    def BigThink(self, src="Big Think"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.headline-container h1')
        descr = self.select_descr(soup, selector='.widget__subheadline')
        soup = self.removeOtherGarbage(soup, *[".post-author__bio"])
        author = self.select_author(soup, selector='.post-author-list')
        date = self.select_date(soup, selector='.post-date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li' #Below removes headlines
        garbage_arr = ['aside', 'figcaption', 'figure', '[data-role="headline"]', '.around-the-web']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Edge:
    def Edge(self, src="Edge"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.views-field-title')
        descr = None#self.select_descr(soup, selector='.widget__subheadline')
        author = self.select_author(soup, selector='.views-field-field-edge-author')
        date = self.select_date(soup, selector='.views-field-field-date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, .contribution-author strong, .contribution-author em'
        garbage_arr = ['aside', 'figcaption', 'figure']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '#main-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Sydney Morning Herald:
    def TheSydneyMorningHerald(self, src="The Sydney Morning Herald"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='[itemprop="headline"]')
        descr = self.select_descr(soup, selector='._1QUW5._1AblV')
        author = self.select_author(soup, selector='._2FyET')
        date = self.select_date(soup, selector='time._2_zR-')
        if author is None or len(author) < 2:
            author = self.select_author(soup, selector='[itemprop="author"]')
        try:
            if author[0] == ",":
                author = author[1:].strip()
        except:
            pass
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, .contribution-author strong, .contribution-author em'
        garbage_arr = ['aside', 'figcaption', 'figure', 'header', 'footer', 'nav', '#navigation', '._2ABN-.YClUs', '._22FRK', '.noPrint', '._2_2jC']
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Prototypr.io:
    def Prototypr(self, src="Prototypr.io"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='h1')
        descr = None  # self.select_descr(soup, selector='.widget__subheadline')
        author = self.select_author(soup, selector='[alt="Author avatar"] + div h1')
        date = self.select_date(soup, selector='[alt="Author avatar"] + div p')
        selectors = 'p, h1, h2, h3, h4, h5, h6, ul li, ol li, .contribution-author strong, .contribution-author em'
        garbage_arr = ['aside', 'figcaption', 'figure']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.blog-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Thanks for reading! Have a question or a project you’d like to discuss? Book a call or email me.", "Newsletter • Twitter • Website"])
        return (dct, article_data)

    # Method for The Millions:
    def TheMillions(self, src="The Millions"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = None  # self.select_descr(soup, selector='.widget__subheadline')
        soup = self.removeOtherGarbage(soup, *[".related-posts", 'article.no-embed', '.categories'])
        author = self.select_author(soup, selector='article .meta [rel="author"]')
        date = self.select_date(soup, selector='article .sing')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.related-books', '.author-description']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for WBUR:
    def WBUR(self, src="WBUR"):
        (source, url, soup) = self.handle_meta(src)
        title = soup.title.text.strip()#self.select_title(soup, selector='.article-hdr')
        descr = None  # self.select_descr(soup, selector='.widget__subheadline')
        author = self.select_author(soup, selector='article .meta [rel="author"]')
        date = self.select_date(soup, selector='.article-meta-item--date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'blockquote', '.section--breakout.section--uw']
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'article.article'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Copy the code below to embed the WBUR audio player on your site", "Support the news", "</iframe>"])
        return (dct, article_data)

    # Method for James Altucher:
    def JamesAltucher(self, src="James Altucher"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='h1.brackets')
        descr = None  # self.select_descr(soup, selector='.widget__subheadline')
        author = None#self.select_author(soup, selector='article .meta [rel="author"]')
        date = None#self.select_date(soup, selector='.article-meta-item--date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'blockquote']
        data_arr = [source, url, title, descr, author, date]
        if "/podcast/" in url:
            content_selector = '#blog-container .content'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        else:
            content_selector = '#blog-container article'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Yuval Noah Harari:
    def YuvalNoahHarari(self, src="Yuval Noah Harari"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='h1')
        descr = None  # self.select_descr(soup, selector='.widget__subheadline')
        author = None#self.select_author(soup, selector='article .meta [rel="author"]')
        date = self.select_date(soup, selector='.post_meta')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'blockquote', '.title-line', '.small_title', '.social_share']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '#page_content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for CBC:
    def CBC(self, src="CBC"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.detailHeadline')
        descr = self.select_descr(soup, selector='.detailSummary')
        author = self.select_author(soup, selector='.byline')
        date = self.select_date(soup, selector='.timeStamp')
        try:
            author = author.replace(date, "").replace("·", "").strip()
        except:
            pass
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'blockquote', '.title-line', '.small_title', '.social_share']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.story'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Nature:
    def Nature(self, src="Nature"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.article-item__title')
        if title == soup.title.text.strip():
            title = self.select_title(soup, selector='.article-heading')
        if title == soup.title.text.strip():
            title = self.select_title(soup, selector='.c-article-title')
        descr = self.select_descr(soup, selector='.article-item__teaser-text')
        if descr is None:
            descr = self.select_descr(soup, selector='.standfirst')
        soup = self.removeOtherGarbage(soup, *["#author-affiliation-news-0-content"])
        author = self.select_author(soup, selector='#author-affiliations')
        if author is None:# or len(descr) < 2:
            author = self.select_author(soup, selector='.standfirst')
        if author is None:# or len(descr) < 2:
            author = self.select_author(soup, selector='.c-author-list')
        date = self.select_date(soup, selector='.article__date')
        if date is None:
            date = self.select_date(soup, selector='.standfirst')
        if date is None:
            date = self.select_date(soup, selector='.c-article-info-details')
        try:
            date = date.replace("Cite this article", "").strip()
        except:
            pass
        try:
            citation = soup.select(".c-bibliographic-information__citation")[0].text.strip()
        except:
            citation = None
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'blockquote', '.img', '.audio-player', '.pullquote', '[aria-labelledby="article-info"]', '#article-comments-section', '.c-article-rights', '.c-article-references__links', '.c-article-references__download']
        data_arr = [source, url, title, descr, author, date]
        try:
            if "/articles/" in url:
                content_selector = '.c-article-body'
                (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
            else:
                content_selector = '.article__body'
                (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        except:
            content_selector = '.content'
            (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        if citation is not None:
            dct['text'].append(citation)
            dct['text'].append('<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.')
        return (dct, article_data)

    # Method for Data Driven Investor:
    def DataDrivenInvestor(self, src="Data Driven Investor"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = self.select_descr(soup, selector='h2 strong span em')
        author = self.select_author(soup, selector='[rel="author"]')
        date = self.select_date(soup, selector='.td-post-date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'blockquote', '.sharedaddy']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.td-post-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Rantt Media:
    def RanttMedia(self, src="Rantt Media"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='#article-title')
        descr = self.select_descr(soup, selector='#article-excerpt')
        author = self.select_author(soup, selector='.author-bio-small a')
        date = self.select_date(soup, selector='.author-bio-small')
        try:
            date = date.replace(author, "").replace('by:', "").replace('by', "").replace('on', "").strip()
        except:
            pass
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'blockquote', '.sharedaddy', '.wp-caption-text', '.su-note']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '#article-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for The Jakarta Post:
    def TheJakartaPost(self, src="The Jakarta Post"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.main-container h1')
        descr = self.select_descr(soup, selector='#article-excerpt')
        author = self.select_descr(soup, selector='.main-center p')
        date = self.select_date(soup, selector='.descrip')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'blockquote', '.sharedaddy', '.wp-caption-text', '.su-note', '.stick-trialUser', '.descTrial', '.readalso']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.show-define-text'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Valley News:
    def ValleyNews(self, src="Valley News"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='#headline1')
        descr = self.select_author(soup, selector='#article-excerpt')
        author = self.select_descr(soup, selector='#articleInfo a')
        date = self.select_date(soup, selector='#publicationDate')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'blockquote']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '#articlebody'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Activate your digital membership"])
        return (dct, article_data)

    # Method for Science Focus:
    def ScienceFocus(self, src="Science Focus"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='[itemprop="headline name"]')
        descr = self.select_author(soup, selector='[itemprop="description"]')
        author = self.select_descr(soup, selector='[itemprop="author"]')
        date = self.select_date(soup, selector='[itemprop="datePublished"]')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'blockquote', 'header', '.social-share-collection', '.author-bio', '.post-tags', '.body-copy-small', '.post-tags__heading', '.post-tags__tag-group', '.template-article__author-bio']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '[itemprop="articleBody"]'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Activate your digital membership"])
        return (dct, article_data)

    # Method for The UNESCO Courier:
    def TheUNESCOCourier(self, src="The UNESCO Courier"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.main-title')
        descr = None#self.select_author(soup, selector='[itemprop="description"]')
        author = None#self.select_descr(soup, selector='[itemprop="author"]')
        date = self.select_date(soup, selector='.subpage_issue')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'blockquote', 'header', '.field-name-field-caption']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.field-name-field-courrier-body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Subscribe to the UNESCO Courier for thought-provoking articles on contemporary subjects. The digital version is completely free.", "Follow the UNESCO Courier on"])
        return (dct, article_data)

    # Method for ADWEEK:
    def ADWEEK(self, src="ADWEEK"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='header h1')
        descr = self.select_author(soup, selector='.subheading')
        author = self.select_descr(soup, selector='.section__byline a')
        date = self.select_date(soup, selector='.section__byline.my-1.my-lg-0')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'blockquote', 'header']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for CoinDesk:
    def CoinDesk(self, src="CoinDesk"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.article-hero-headline')
        descr = self.select_author(soup, selector='.article-hero-blurb')
        author = self.select_descr(soup, selector='h5.heading')
        date = self.select_date(soup, selector='.article-hero-datetime time')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'blockquote', 'header', '.newsletter-module-wrapper', '.tags', '.end']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.article-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["See also:"])
        return (dct, article_data)

    # Method for Maxim:
    def Maxim(self, src="Maxim"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.m-detail-header--title')
        descr = self.select_author(soup, selector='.m-detail-header--dek')
        author = self.select_descr(soup, selector='.m-detail-header--meta-author')
        date = self.select_date(soup, selector='.m-detail-header--date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'blockquote', 'header', '.newsletter-module-wrapper', '.tags', '.end']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.m-detail--body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["See also:"])
        return (dct, article_data)

    # Method for Sports Illustrated:
    def SI(self, src="Sports Illustrated"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.m-detail-header--title')
        descr = self.select_author(soup, selector='.m-detail-header--dek')
        author = self.select_descr(soup, selector='.m-detail-header--meta-author')
        date = self.select_date(soup, selector='.m-detail-header--date time')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'blockquote', 'header', '.newsletter-module-wrapper', '.tags', '.end']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.m-detail--body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Kompas:
    def Kompas(self, src="Kompas"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.read__title')
        descr = None#self.select_author(soup, selector='.m-detail-header--dek')
        author = self.select_descr(soup, selector='.read__credit.clearfix')
        date = self.select_date(soup, selector='.read__time')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'blockquote', 'header', '.newsletter-module-wrapper', '.tags', '.end']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.read__content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Baca juga: "])
        return (dct, article_data)

    # Method for CoinGape:
    def CoinGape(self, src="CoinGape"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = None#self.select_author(soup, selector='.m-detail-header--dek')
        author = self.select_descr(soup, selector='.auth-name')
        date = self.select_date(soup, selector='.c-time')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.main.c-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Invezz:
    def Invezz(self, src="Invezz"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = self.select_author(soup, selector='.inv-news-summary')
        author = self.select_descr(soup, selector='.inv-news-sidebar-authorship a')
        date = self.select_date(soup, selector='aside .flex.flex-wrap.items-center')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '#content article'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Are you looking for fast-news, hot-tips and market analysis? Sign-up for the Invezz newsletter, today."])
        return (dct, article_data)

    # Method for BeInCrypto:
    def BeInCrypto(self, src="BeInCrypto"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = self.select_author(soup, selector='.post-brief')
        if descr is None or len(descr) < 2:
            descr = self.select_descr(soup, selector='.intro-text')
        author = self.select_descr(soup, selector='.post-meta-wrap')
        date = self.select_date(soup, selector='.post-meta-wrap time')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.top-share-block', '.tags-list']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.entry-content-inner'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Are you looking for fast-news, hot-tips and market analysis? Sign-up for the Invezz newsletter, today."])
        return (dct, article_data)

    # Method for The Paypers:
    def ThePaypers(self, src="The Paypers"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.article h1')
        descr = None#self.select_descr(soup, selector='.post-brief')
        author = self.select_descr(soup, selector='.article .source')
        date = None#self.select_date(soup, selector='.post-meta-wrap time')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.top-share-block', '.tags-list']
        arr = [soup.select("#pageContainer")[0].text.strip()]
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Finance Magnates:
    def FinanceMagnates(self, src="Finance Magnates"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = self.select_descr(soup, selector='.entry-excerpt')
        author = self.select_descr(soup, selector='.author-link')
        date = self.select_date(soup, selector='.entry-date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.fm-suggested-article']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.the-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Public Sector Executive:
    def PublicSectorExecutive(self, src="Public Sector Executive"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.article__title')
        descr = None#self.select_descr(soup, selector='.entry-excerpt')
        author = self.select_descr(soup, selector='.author__details p')
        date = None#self.select_date(soup, selector='.entry-date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.share', '.share__tagline', '.share__nav']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.article__body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Koinalert:
    def Koinalert(self, src="Koinalert"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = None#self.select_descr(soup, selector='.entry-excerpt')
        author = self.select_descr(soup, selector='.author-name.vcard.fn.author')
        date = self.select_date(soup, selector='.mvp-post-date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.share', '.share__tagline', '.share__nav']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '#mvp-content-main'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Disclaimer: Koinalert’s content is only for information purpose in nature and should not be considered as investment advice"])
        return (dct, article_data)

    # Method for Decrypt:
    def Decrypt(self, src="Decrypt"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='h1')
        descr = self.select_descr(soup, selector='h2')
        author = self.select_author(soup, selector='.sc-10nsls3-0.gmkWd')
        date = self.select_date(soup, selector='.posted-on')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.share', '.share__tagline', '.share__nav']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.post-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Disclaimer", "THE VIEWS AND OPINIONS EXPRESSED BY THE AUTHOR ARE FOR INFORMATIONAL PURPOSES ONLY AND DO NOT CONSTITUTE FINANCIAL, INVESTMENT, OR OTHER ADVICE."])
        return (dct, article_data)

    # Method for Inside Bitcoins:
    def InsideBitcoins(self, src="Inside Bitcoins"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = self.select_descr(soup, selector='h2')
        author = self.select_descr(soup, selector='.c-TopAuthorText p')
        date = self.select_date(soup, selector='.c-ArticleInfo--date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for CoinGeek:
    def CoinGeek(self, src="CoinGeek"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = None#self.select_descr(soup, selector='h2')
        author = self.select_descr(soup, selector='.entry-meta__author')
        date = self.select_date(soup, selector='.entry-meta__date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.container-lazyload', '.preview-lazyload', '.container-youtube']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["New to Bitcoin? Check out CoinGeek’s Bitcoin for Beginners section, the ultimate resource guide to learn more about Bitcoin—as originally envisioned by Satoshi Nakamoto—and blockchain", "See also:"])
        return (dct, article_data)

    # Method for Disrupt Magazine:
    def Disrupt(self, src="Disrupt Magazine"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = None#self.select_descr(soup, selector='.entry-excerpt')
        author = self.select_descr(soup, selector='.mvp-author-box-name a')
        date = None#self.select_date(soup, selector='.mvp-post-date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.share', '.share__tagline', '.share__nav']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '#mvp-content-main'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Disclaimer: Koinalert’s content is only for information purpose in nature and should not be considered as investment advice"])
        return (dct, article_data)

    # Method for The Bell:
    def TheBell(self, src="The Bell"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.post-content h1')
        descr = None#self.select_descr(soup, selector='.entry-excerpt')
        author = None#self.select_author(soup, selector='.mvp-author-box-name a')
        date = self.select_date(soup, selector='.post__about')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.share', '.share__tagline', '.share__nav']
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'body article'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for China Briefing:
    def ChinaBriefing(self, src="China Briefing"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = None#self.select_descr(soup, selector='.entry-excerpt')
        author = self.select_author(soup, selector='.author.vcard')
        date = self.select_date(soup, selector='.entry-date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.sharedaddy', '.article_credit']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Bitcoin News:
    def BitcoinNews(self, src="Bitcoin News"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.article__header__heading')
        descr = None#self.select_descr(soup, selector='.entry-excerpt')
        author = self.select_author(soup, selector='.article__info__author')
        date = self.select_date(soup, selector='.article__info__date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.article__body__tags-related', '.article__body__tags-related__tags', '.images_credits', '.snippet_container']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.article__body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for NDTV:
    def NDTV(self, src="NDTV"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.sp-ttl')
        descr = self.select_author(soup, selector='.sp-descp')
        author = self.select_author(soup, selector='[itemprop="author"] [itemprop="name"]')
        date = self.select_date(soup, selector='[itemprop="dateModified"]')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.ins_instory_dv', '.social_link', '.trndngWdgt', 'nav', 'header', '#jads', '.ads', '.story_footer', 'footer', '.social-tags', '.foot-news', '.watch-news', '.tv-logos', '.follow-social', '.sp-hd', '.reltd']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr)
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        print("\n\n\n\nMETHOD FOR SITE" * 8)
        print(dct.keys())
        print()
        print(article_data.keys())
        print("\n\n\n\n")
        return (dct, article_data)

    # Method for EURACTIV:
    def EURACTIV(self, src="EURACTIV"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='#main_container h1')
        descr = None#self.select_descr(soup, selector='.entry-excerpt')
        author = self.select_author(soup, selector='.ea-byline')
        date = self.select_date(soup, selector='.ea-dateformat')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'header', 'footer', 'nav', '.ea-own-embed', 'header', '.nav', '.breadcrumb', '.ea-article-meta', '.ea-article-featured-image', '.ea-image-meta', '.ea-article-footer', '#contribs_banner', '.newsletter', '#ea-copyright', '#ea-print-footer', '.ea-sidebar', '.hidden-print']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr)
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Light Reading:
    def LightReading(self, src="Light Reading"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.article-title')
        descr = None#self.select_descr(soup, selector='.entry-excerpt')
        author = self.select_author(soup, selector='.allcaps')
        date = self.select_date(soup, selector='.date')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'header', 'footer', 'nav']
        arr = self.handle_content_just_using_soup(soup, selectors, garbage_arr, breakers=["Related posts:"])
        article_data = SingleArticle(source, url, title, descr, author, date, arr)
        dct = {'source': source, 'url': url, 'title': title, 'descr': descr, 'author': author, 'date': date, 'text': arr}
        return (dct, article_data)

    # Method for Telecoms.com:
    def Telecoms(self, src="Telecoms.com"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.article-view h2')
        descr = None#self.select_descr(soup, selector='.entry-excerpt')
        author = self.select_author(soup, selector='.author-details .profile')
        date = self.select_date(soup, selector='.author-details .byline')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', 'header', 'footer', 'nav', '.sponsored-menu', '.menu', '.desktop-menu', '.navigation', '#comments', '.related-content', '.insights-snippet', '.events-snippet', '.text-articles', '.article-author', '.spex-line-title', '.page-title', '[style="display:none;"]']
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'body'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Scientific Inquirer:
    def ScientificInquirer(self, src="Scientific Inquirer"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = None#self.select_descr(soup, selector='.entry-excerpt')
        author = self.select_author(soup, selector='.byline')
        date = self.select_date(soup, selector='.posted-on')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.sharedaddy']
        data_arr = [source, url, title, descr, author, date]
        content_selector = '.entry-content'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr)
        return (dct, article_data)

    # Method for Popular Mechanics:
    def PopularMechanics(self, src="Popular Mechanics"):
        (source, url, soup) = self.handle_meta(src)
        title = self.select_title(soup, selector='.entry-title')
        descr = None#self.select_descr(soup, selector='.entry-excerpt')
        author = self.select_author(soup, selector='.byline')
        date = self.select_date(soup, selector='.posted-on')
        selectors = 'p, h2, h3, h4, h5, h6, ul li, ol li, ol li'
        garbage_arr = ['aside', 'figcaption', 'figure', '.sharedaddy', 'header', 'nav', 'footer', '.transporter', '.embed', '.seo-tags-container']
        data_arr = [source, url, title, descr, author, date]
        content_selector = 'body main'
        (dct, article_data) = self.handle_content(soup, content_selector, selectors, garbage_arr, data_arr, strs=["Tell us in the comments:", "Now watch this:"])
        return (dct, article_data)






    ################################################################################################
    ################################################################################################
    ################################################################################################
    base_arr = np.array([ # src, domain, func

        ### NEED TO GET THE OTHER USA TODAYS ex. patriotswire.usatoday.com

        ["Luxembourg Times", "luxtimes.lu", LuxembourgTimes],
        ["The Hill", "thehill.com", TheHill],
        ["The Bell", "thebell.io", TheBell],
        ["Popular Mechanics", "popularmechanics.com", PopularMechanics],
        ["Telecoms.com", "telecoms.com", Telecoms],
        ["EURACTIV", "euractiv.com", EURACTIV],
        ["Scientific Inquirer", "scientificinquirer.com", ScientificInquirer],
        ["NDTV", "ndtv.com", NDTV],
        ["Light Reading", "lightreading.com", LightReading],
        ["Bitcoin News", "news.bitcoin.com", BitcoinNews],
        ["CoinGeek", "coingeek.com", CoinGeek],
        ["China Briefing", "china-briefing.com", ChinaBriefing],
        ["CoinGape", "coingape.com", CoinGape],
        ["Disrupt Magazine", "disruptmagazine.com", Disrupt],
        ["Inside Bitcoins", "insidebitcoins.com", InsideBitcoins],
        ["Decrypt", "decrypt.co", Decrypt],
        ["Finance Magnates", "financemagnates.com", FinanceMagnates],
        ["The Paypers", "thepaypers.com", ThePaypers],
        ["BeInCrypto", "beincrypto.com", BeInCrypto],
        ["Invezz", "invezz.com", Invezz],
        ["Koinalert", "koinalert.com", Koinalert],
        ["Public Sector Executive", "publicsectorexecutive.com", PublicSectorExecutive],
        ["Kompas", "kompas.com", Kompas],
        ["Kompas Nasional", "nasional.kompas.com", Kompas],
        ["Kompas Regional", "regional.kompas.com", Kompas],
        ["Kompas News", "news.kompas.com", Kompas],
        ["Kompas Kilas Daerah", "kilasdaerah.kompas.com", Kompas],
        ["Kompas Kilas Kementerian", "kilaskementerian.kompas.com", Kompas],
        ["Kompas Kilas Badannegara", "kilasbadannegara.kompas.com", Kompas],
        ["Kompas Megapolitan", "megapolitan.kompas.com", Kompas],
        ["Kompas Inside", "inside.kompas.com", Kompas],
        ["Kompas Kilas Korporasi", "kilaskorporasi.kompas.com", Kompas],
        ["Kompas Sorot Politik", "sorotpolitik.kompas.com", Kompas],
        ["Kompas Kilas Parlemen", "kilasparlemen.kompas.com", Kompas],
        ["Kompas Medan", "medan.kompas.com", Kompas],
        ["Kompas Palembang", "palembang.kompas.com", Kompas],
        ["Kompas Surabaya", "surabaya.kompas.com", Kompas],
        ["Kompas Makassar", "makassar.kompas.com", Kompas],
        ["Kompas Balik Papan", "balikpapan.kompas.com", Kompas],
        ["Kompas Samarinda", "samarinda.kompas.com", Kompas],
        ["Kompas Health", "health.kompas.com", Kompas],
        ["Kompas Edukasi", "edukasi.kompas.com", Kompas],
        ["Kompas Kilas Pendidikan", "kilaspendidikan.kompas.com", Kompas],
        ["Kompas SBMPTN", "sbmptn.kompas.com", Kompas],
        ["Kompas Money", "money.kompas.com", Kompas],
        ["Kompas Kilas Badan", "kilasbadan.kompas.com", Kompas],
        ["Kompas Kilas Bumn", "kilasbumn.kompas.com", Kompas],
        ["Kompas Kilas Transportasi", "kilastransportasi.kompas.com", Kompas],
        ["Kompas Kilas Fintech", "kilasfintech.kompas.com", Kompas],
        ["Kompas Tekno", "tekno.kompas.com", Kompas],
        ["Kompas Inspirasli", "inspirasli.kompas.com", Kompas],
        ["Kompas Lifestyle", "lifestyle.kompas.com", Kompas],
        ["Kompas Genbest", "genbest.kompas.com", Kompas],
        ["Kompas Properti", "properti.kompas.com", Kompas],
        ["Kompas Sorot", "sorot.kompas.com", Kompas],
        ["Kompas Bola", "bola.kompas.com", Kompas],
        ["Kompas Travel", "travel.kompas.com", Kompas],
        ["Kompas Superapps", "superapps.kompas.com", Kompas],
        ["Kompas Ohayo Jepang", "ohayojepang.kompas.com", Kompas],
        ["Kompas Otomotif", "otomotif.kompas.com", Kompas],
        ["Kompas Entertainment", "entertainment.kompas.com", Kompas],
        ["Kompas Vik", "vik.kompas.com", Kompas],
        ["Kompas Kolom", "kolom.kompas.com", Kompas],
        ["Kompas Jeo", "jeo.kompas.com", Kompas],
        ["Data Driven Investor", "datadriveninvestor.com", DataDrivenInvestor],
        ["CBC", "cbc.ca", CBC],
        ["CoinDesk", "coindesk.com", CoinDesk],
        ["Maxim", "maxim.com", Maxim],
        ["Sports Illustrated", "si.com", SI],
        ["ADWEEK", "adweek.com", ADWEEK],
        ["The UNESCO Courier | EN", "en.unesco.org", TheUNESCOCourier],
        ["The UNESCO Courier | PT", "pt.unesco.org", TheUNESCOCourier],
        ["The UNESCO Courier | FR", "fr.unesco.org", TheUNESCOCourier],
        ["The UNESCO Courier | ES", "es.unesco.org", TheUNESCOCourier],
        ["The UNESCO Courier | 中文", "zh.unesco.org", TheUNESCOCourier],
        ["The UNESCO Courier | Русский", "ru.unesco.org", TheUNESCOCourier],
        ["The UNESCO Courier | AR", "العربية.unesco.org", TheUNESCOCourier],
        ["ScienceFocus", "sciencefocus.com", ScienceFocus],
        ["Valley News", "vnews.com", ValleyNews],
        ["Daily Hampshire Gazette", "gazettenet.com", ValleyNews],
        ["Greenfield Recorder", "recorder.com", ValleyNews],
        ["Monadnock Ledger-Transcript", "ledgertranscript.com", ValleyNews],
        ["Concord Monitor", "concordmonitor.com", ValleyNews],
        ["Athol Daily News", "atholdailynews.com", ValleyNews],
        ["The Jakarta Post", "thejakartapost.com", TheJakartaPost],
        ["Rantt Media", "rantt.com", RanttMedia],
        ["Nature", "nature.com", Nature],
        ["Yuval Noah Harari", "ynharari.com", YuvalNoahHarari],
        ["James Altucher", "jamesaltucher.com", JamesAltucher],
        ["The Sydney Morning Herald", "smh.com.au", TheSydneyMorningHerald],
        ["Edge", "edge.org", Edge],
        ["WBUR", "wbur.org", WBUR],
        ["The Millions", "themillions.com", TheMillions],
        ["Big Think", "bigthink.com", BigThink],
        ["Forward", "forward.com", Forward],
        ["CTV News", "ctvnews.ca", CTVNews],
        ["The Financial Times", "ft.com", FT],
        ["The Toronto Star", "thestar.com", TheStar],
        ["The Bookseller", "thebookseller.com", TheBookseller],
        ["The Times", "thetimes.co.uk", TheTimes],
        ["Signal v. Noise (m.signalvnoise.com)", "m.signalvnoise.com", SignalVNoiseM],
        ["Signal v. Noise (signalvnoise.com)", "signalvnoise.com", SignalVNoise],
        ["Nieman Lab", "niemanlab.org", NiemanLab],
        ["The Indian Express", "indianexpress.com", TheIndianExpress],
        ["Growth Machine", "growthmachine.com", GrowthMachine],
        ["Karl Hughes", "karllhughes.com", KarlHughes],
        ["Handelsblatt", "handelsblatt.com", Handelsblatt],
        ["Delayed Gratification", "slow-journalism.com", DelayedGratification],
        ["Oxford American", "oxfordamerican.org", OxfordAmerican],
        ["Hacker Journal", "hackerjournal.it", HackerJournal],
        ["RomaniaInsider", "romania-insider.com", RomaniaInsider],
        ["Publisher's Weekly", "kirkusreviews.com", PublishersWeekly],
        ["DailyFX", "dailyfx.com", DailyFX],
        ["Free Code Camp", "freecodecamp.org", FreeCodeCamp],
        ["Inside Hook", "insidehook.com", InsideHook],
        ["Protocol", "protocol.com", Protocol],
        ["Currencies Direct", "currenciesdirect.com", CurrenciesDirect],
        ["Proactive Investors", "proactiveinvestors.com", ProactiveInvestors],
        ["Palo Alto Online", "paloaltoonline.com", PaloAltoOnline],
        ["CIA", "cia.gov", CIA],
        ["The Chicago Review of Books", "chireviewofbooks.com", TheChicagoReviewOfBooks],
        ["Antimafia Duemila", "antimafiaduemila.com", AntimafiaDuemila],
        ["Antimafia Dos Mil", "antimafiadosmil.com", AntimafiaDuemila],
        ["Le Soir", "lesoir.be", LeSoir],
        ["Le Soir Plus", "plus.lesoir.be", LeSoir],
        ["Books & Culture", "booksandculture.com", BooksAndCulture],
        ["Bookforum", "bookforum.com", Bookforum],
        ["Funding Universe", "fundinguniverse.com", FundingUniverse],
        ["The Art Newspaper", "theartnewspaper.com", TheArtNewspaper],
        ["The Boston Globe", "bostonglobe.com", TheBostonGlobe],
        ["Derek Pilling's Blog", "derekpilling.com", DerekPilling],
        ["New Orleans CityBusiness", "neworleanscitybusiness.com", CityBusiness],
        ["Edison Partners Blog", "edisonpartners.com", EdisonPartnersBlog],
        ["Workhorse Growth Blog", "workhorsegrowth.com", Workhorse],
        ["The Growth Equity Blog", "thegrowthequityblog.com", TheGrowthEquityBlog],
        ["Menlo Ventures Blog", "menlovc.com", MenloVCBlog],
        ["Elad Gil's Blog", "blog.eladgil.com", EladBlog],
        ["Felt Presence by Ryan Singer", "mailchi.mp", RyanSinger],
        ["High Growth Handbook", "growth.eladgil.com", HighGrowthHandbook],
        ["Tomasz Tunguz", "tomtunguz.com", TomaszTunguz],
        ["The Pmarca Guide to Startups", "pmarchive.com", Pmarca],
        ["Inside Intercom", "intercom.com", Intercom],
        ["Interesting Engineering", "interestingengineering.com", InterestingEngineering],
        ["Digital Trends", "digitaltrends.com", DigitalTrends],
        ["VentureBeat", "venturebeat.com", VentureBeat],
        ["Medium", "medium.com", Medium],
        ["NextGov", "nextgov.com", NextGov],
        ["innoarchitech", "innoarchitech.com", innoarchitech],
        ["Station F", "stationf.co", StationF],
        ["Ken Norton", "kennorton.com", KenNorton],
        ["Basecamp", "basecamp.com", Basecamp],
        ["HackerNoon", "hackernoon.com", HackerNoon],
        ["The Black Box of Product Management", "blackboxofpm.com", Medium],
        ["Merci Victoria Grace", "merci.medium.com", Medium],
        ["Gibson Biddle", "gibsonbiddle.medium.com", Medium],
        ["Kevin LaBuz", "kjlabuz.medium.com", Medium],
        ["Monday Note", "mondaynote.com", Medium],
        ["Towards Data Science", "towardsdatascience.com", Medium],
        ["The Economist (Medium)", "medium.economist.com", Medium],
        ["The Mission", "themissionhq.medium.com", Medium],
        ["Mattan Griffel", "mattangriffel.medium.com", Medium],
        ["The Founder Coach", "medium.dave-bailey.com", Medium],
        ["GV", "library.gv.com", Medium],
        ["The Praxis Journal", "journal.praxislabs.org", Medium],
        ["thinkgrowth.org", "thinkgrowth.org", Medium],
        ["Muzli", "medium.muz.li", Medium],
        ["The Coinbase Blog", "blog.coinbase.com", Medium],
        ["UX Collective", "uxdesign.cc", Medium],
        ["UX Collective Editors", "uxdesigncc.medium.com", Medium],
        ["UX Planet", "uxplanet.org", Medium],
        ["Be Yourself", "byrslf.co", Medium],
        ["OneZero", "onezero.medium.com", Medium],
        ["Fortune Insiders", "insiders.fortune.com", Medium],
        ["3 Min Read", "blog.medium.com", Medium],
        ["Entrepreneur's Handbook", "entrepreneurshandbook.co", Medium],
        ["ART + marketing", "artplusmarketing.com", Medium],
        ["The Creative Cafe", "thecreative.cafe", Medium],
        ["Marker", "marker.medium.com", Medium],
        ["GEN", "gen.medium.com", Medium],
        ["Elemental", "elemental.medium.com", Medium],
        ["ZORA", "zora.medium.com", Medium],
        ["LEVEL", "level.medium.com", Medium],
        ["Momentum", "momentum.medium.com", Medium],
        ["Forge", "forge.medium.com", Medium],
        ["Heated", "heated.medium.com", Medium],
        ["Modus", "modus.medium.com", Medium],
        ["Extra NewsFeed", "extranewsfeed.com", Medium],
        ["Festival Peak", "festivalpeak.com", Medium],
        ["The Writing Cooperative", "writingcooperative.com", Medium],
        ["P.S. I Love You", "psiloveyou.xyz", Medium],
        ["Prototypr.io Blog", "blog.prototypr.io", Medium],
        ["Prototypr.io", "prototypr.io", Prototypr],
        ["Silicon Valley Product Group", "svpg.com", SVPG],
        ["Bottom Up by David Sacks", "sacks.substack.com", Substack],
        ["Petition", "petition.substack.com", Substack],
        ["Everything", "news.every.to", Substack],
        ["Everything | Napkin Math", "napkin-math.every.to", Substack],
        ["Everything | Means of Creation", "means-of-creation.every.to", Substack],
        ["Everything | Divinations", "divinations.every.to", Substack],
        ["Everything | Almanack", "almanack.every.to", Substack],
        # ["Everything | Superorganizers", "almanack.every.to", Substack],
        ["Everything | The Long Conversation", "the-long-conversation.every.to", Substack],
        ["Everything | Ask Jerry", "ask-jerry.every.to", Substack],
        ["Everything | Free Radicals", "free-radicals.every.to", Substack],
        ["Everything | Praxis", "praxis.every.to", Substack],
        ["Everything | Talk Therapy", "talk-therapy.every.to", Substack],
        ["Net Interest", "netinterest.substack.com", Substack],
        ["Nisha's Internet Tote Blog", "nishachittal.substack.com", Substack],
        ["Future of Belonging", "belonging.substack.com", Substack],
        ["Words With Kirstie", "kirstietaylor.substack.com", Substack],
        ["Culture Study", "annehelen.substack.com", Substack],
        ["The Audacity", "audacity.substack.com", Substack],
        ["Maybe Baby", "haleynahman.substack.com", Substack],
        ["Hung Up", "hunterharris.substack.com", Substack],
        ["Crème de la Crème", "aminatou.substack.com", Substack],
        ["And It Don't Stop", "robertchristgau.substack.com", Substack],
        ["books/snacks/softcore", "bitchesgottaeat.substack.com", Substack],
        ["Thinking Better, Together", "zatrana.substack.com", Substack],
        ["Formerly Dangerous", "drewmcweeny.substack.com", Substack],
        ["The Daily Respite", "dailyrespite.substack.com", Substack],
        ["Letters from Suzanne", "suzannemoore.substack.com", Substack],
        ["Common Sense with Bari Weiss", "bariweiss.substack.com", Substack],
        ["Melanie Phillips", "melaniephillips.substack.com", Substack],
        ["Music Journalism Insider", "musicjournalism.substack.com", Substack],
        ["The Long Version", "katz.substack.com", Substack],
        ["Here for It w/R. Eric Thomas", "rericthomas.substack.com", Substack],
        ["Please Clap", "awardsforgoodboys.substack.com", Substack],
        ["Reclaiming Hope Newsletter", "reclaiminghope.substack.com", Substack],
        ["You've Got Lipstick On Your Chin", "arabellesicardi.substack.com", Substack],
        ["Letters from an American", "heathercoxrichardson.substack.com", Substack],
        ["TK News by Matt Taibbi", "taibbi.substack.com", Substack],
        ["Glenn Greenwald", "greenwald.substack.com", Substack],
        ["The Weekly Dish", "andrewsullivan.substack.com", Substack],
        ["The Message Box", "messagebox.substack.com", Substack],
        ["Erick Erickson's Confessions of a Political Junkie", "ewerickson.substack.com", Substack],
        ["Wide World of News", "markhalperin.substack.com", Substack],
        ["Gray Mirror", "graymirror.substack.com", Substack],
        ["Roll Call", "austinchanning.substack.com", Substack],
        ["Welcome to Hell World", "luke.substack.com", Substack],
        ["Foreign Exchanges", "fx.substack.com", Substack],
        ["SHERO", "shero.substack.com", Substack],
        ["Counterpoint", "counterpoint.substack.com", Substack],
        ["The Rover with Christopher Curtis", "rover.substack.com", Substack],
        ["Krystal Kyle & Friends", "krystalkyleandfriends.substack.com", Substack],
        ["Charlotte's Web Thoughts", "charlotteclymer.substack.com", Substack],
        ["The Diff", "diff.substack.com", Substack],
        ["Insight", "zeynep.substack.com", Substack],
        ["Technically", "technically.substack.com", Substack],
        ["Razib Khan's Unsupervised Learning", "razib.substack.com", Substack],
        ["The GameDiscoverCo newsletter", "gamediscoverability.substack.com", Substack],
        ["Crypto is Easy", "cryptoiseasy.substack.com", Substack],
        ["Normcore Tech", "vicki.substack.com", Substack],
        ["Chinese Characteristics", "lillianli.substack.com", Substack],
        ["BNet", "bnet.substack.com", Substack],
        ["The Geyser - Hot Takes & Deep Thinking on the Info Economy", "thegeyser.substack.com", Substack],
        ["Simon Owens's Media Newsletter", "simonowens.substack.com", Substack],
        ["ChinAI Newsletter", "chinai.substack.com", Substack],
        ["Kneeling Bus", "kneelingbus.substack.com", Substack],
        ["Documentally", "documentally.substack.com", Substack],
        ["MSABundle.com Customers", "msabundle.substack.com", Substack],
        ["Metaviews", "metaviews.substack.com", Substack],
        ["The Tech Tribe Dispatch", "mytechtribe.substack.com", Substack],
        ["HEATED", "heated.world", Substack],
        ["Volts", "volts.wtf", Substack],
        ["This Week in MCJ (My Climate Journey)", "myclimatejourney.substack.com", Substack],
        ["Hot Take", "realhottake.substack.com", Substack],
        ["The Phoenix", "thephoenix.substack.com", Substack],
        ["Inkcap", "inkcapjournal.co.uk", Substack],
        ["Climate Risk Review", "climateriskreview.com", Substack],
        ["The End of the World Review", "endoftheworld.substack.com", Substack],
        ["Hothouse // Solutions", "hothouse.substack.com", Substack],
        ["Drilled", "drillednews.substack.com", Substack],
        ["Climate In Colour", "climateincolour.substack.com", Substack],
        ["Lights On", "lightson.substack.com", Substack],
        ["This Week in Birding", "twibchicago.com", Substack],
        ["Green Rocks", "greenrocks.substack.com", Substack],
        ["The Bitcoin Forecast by Willy Woo", "willywoo.substack.com", Substack],
        ["Lenny's Newsletter", "lennyrachitsky.substack.com", Substack],
        ["The Pomp Letter", "pomp.substack.com", Substack],
        ["The MacroTourist", "themacrotourist.substack.com", Substack],
        ["Cup of Coffee by Craig Calcaterra", "cupofcoffee.substack.com", Substack],
        ["Hoop Vision", "hoopvision.substack.com", Substack],
        ["Good Morning It's Basketball", "ziller.substack.com", Substack],
        ["The Pillar", "pillarcatholic.com", Substack],
        ["Sinocism", "sinocism.com", Substack],
        ["News Items", "newsitems.substack.com", Substack],
        ["Charlotte Ledger Business Newsletter", "charlotteledger.substack.com", Substack],
        ["TOP SECRET UMBRA", "topsecretumbra.substack.com", Substack],
        ["Numlock News", "numlock.substack.com", Substack],
        ["The Mill", "manchestermill.co.uk", Substack],
        ["Bad News", "badnews.substack.com", Substack],
        ["Murray Bridge News", "murraybridge.news", Substack],
        ["The Dissenter", "dissenter.substack.com", Substack],
        ["Portuguese news in English, for estrangeiros", "jorgebranco.substack.com", Substack],
        ["Vietnam Weekly", "vietnamweekly.substack.com", Substack],
        ["The Ledger LCJ morning update", "heavenerledger.substack.com", Substack],
        ["Chasers of the Light", "signalfire.chasersofthelight.com", Substack],
        ["EKO", "ekotoons.com", Substack],
        ["The Crypto Art Industry", "loop-news.com", Substack],
        ["The Half Marathoner", "thehalfmarathoner.com", Substack],
        ["Sick Note", "sicknote.co", Substack],
        ["The Objective", "objectivejournalism.org", Substack],
        ["HBCU Digest", "hbcudigest.com", Substack],
        ["Webworm with David Farrier", "webworm.co", Substack],
        ["The Shatner Chatner", "shatnerchatner.com", Substack],
        ["Blackbird Spyplane", "blackbirdspyplane.com", Substack],
        ["Today in Tabs", "todayintabs.com", Substack],
        ["Flow State", "flowstate.fm", Substack],
        ["Humorism", "humorism.xyz", Substack],
        ["The Dispatch", "thedispatch.com", Substack],
        ["Bulwark+", "plus.thebulwark.com", Substack],
        ["Slow Boring", "slowboring.com", Substack],
        ["Popular Information", "popular.info", Substack],
        ["Persuasion", "persuasion.community", Substack],
        ["The Daily Poster", "dailyposter.com", Substack],
        ["The Ink", "the.ink", Substack],
        ["The Informant", "informant.news", Substack],
        ["PRESS RUN", "pressrun.media", Substack],
        ["Exponential View by Azeem Azhar", "exponentialview.co", Substack],
        ["Platformer", "platformer.news", Substack],
        ["Newcomer", "newcomer.co", Substack],
        ["Nexus", "nexuslabs.online", Substack],
        ["Pirate Wires", "piratewires.com", Substack],
        ["Zero Credibility", "spakhm.com", Substack],
        ["Garbage Day", "garbageday.email", Substack],
        ["be radical.", "briefing.beradicalgroup.com", Substack],
        ["The Bear Cave", "thebearcave.substack.com", Substack],
        ["Jonah's Top Growth Stocks", "jonahlupton.substack.com", Substack],
        ["Nongaap Investing", "nongaap.substack.com", Substack],
        ["Pulte's Money and Life Thoughts", "pulte.substack.com", Substack],
        ["The Profile", "theprofile.substack.com", Substack],
        ["Snowball", "snowball.xyz", Substack],
        ["DirectorMoves", "directormoves.substack.com", Substack],
        ["Mule's Musings", "mule.substack.com", Substack],
        ["The Defiant", "thedefiant.substack.com", Substack],
        ["Rekt Capital Newsletter", "rektcapital.substack.com", Substack],
        ["DeFi Pulse Farmer", "yieldfarmer.substack.com", Substack],
        ["Ironsides Macroeconomics 'It's Never Different This Time'", "ironsidesmacro.substack.com", Substack],
        ["The Lund Loop", "thelundloop.substack.com", Substack],
        ["Market Meditations", "koroushak.substack.com", Substack],
        ["Femstreet", "femstreet.substack.com", Substack],
        ["Crypto Insights by Blockroots", "blockroots.substack.com", Substack],
        ["Bankless | Metaversal", "metaversal.banklesshq.com", Substack],
        ["Bankless | Bankless Shows", "shows.banklesshq.com", Substack],
        ["The Ankler", "theankler.com", Substack],
        ["TrueHoop", "truehoop.com", Substack],
        ["Power Plays", "powerplays.news", Substack],
        ["Go Long with Tyler Dunne", "golongtd.com", Substack],
        ["The Pick and Roll", "pickandroll.com.au", Substack],
        ["Let's Go Warriors", "letsgowarriors.com", Substack],
        ["Extra Points with Matt Brown", "extrapointsmb.com", Substack],
        ["The Draft Scout", "thedraftscout.com", Substack],
        ["Gibson Biddle's 'Ask Gib' Newsletter", "askgib.substack.com", Substack],
        ["Notes on the Crises", "nathantankus.substack.com", Substack],
        ["Brianne Kimmel's Newsletter", "wfh.substack.com", Substack],
        ["The Beautiful Mess by John Cutler", "cutlefish.substack.com", Substack],
        ["Lightspeed Venture Partners Blog (Old)", "lsvp.wordpress.com", LSVP],
        ["First Round Review", "firstround.com", FirstRoundReview],
        ["Russian History Blog", "russianhistoryblog.org", RussianHistoryBlog],
        ["NYU Jordan Center for the Advanced Study of Russia", "jordanrussiacenter.org", JordanCenter],
        ["Guided History", "blogs.bu.edu", GuidedHistoryBU],
        ["HI 446 Revolutionary Russia", "sites.bu.edu", HI446],
        ["Seventeen Moments in Soviet History", "soviethistory.msu.edu", SeventeenMoments],
        ["Lee Cole's Blog: An Introduction to Soviet History", "blogs.lt.vt.edu", LeeCole],
        ["Mashable", "mashable.com", Mashable],
        ["ReadWrite", "readwrite.com", ReadWrite],
        ["Bessemer Venture Partners | Atlas", "bvp.com", Bessemer],
        ["The Accel Blog", "theaccelblog.squarespace.com", TheAccelBlog],
        ["Sifted", "sifted.eu", Sifted],
        ["Haystack", "semilshah.com", Haystack],
        ["Index Ventures | Perspectives", "indexventures.com", IndexVentures],
        ["History.com", "history.com", History],
        ["Kleiner Perkins | Perspectives", "kleinerperkins.com", KleinerPerkins],
        ["National Geographic", "nationalgeographic.com", NationalGeographic],
        ["Nautilus", "nautil.us", Nautilus],
        ["Next Draft", "nextdraft.com", NextDraft],
        ["Fact Check", "factcheck.org", FactCheck],
        ["The Telegraph", "telegraph.co.uk", TheTelegraph],
        ["Sequoia Capital Blog", "sequoiacap.com", SequoiaCap],
        ["This Is Money", "thisismoney.co.uk", ThisIsMoney],
        ["The Evening Standard", "standard.co.uk", TheEveningStandard],
        ["The Daily Mirror", "mirror.co.uk", TheDailyMirror],
        ["The Daily Mail", "dailymail.co.uk", TheDailyMail],
        ["The Daily Star", "dailystar.co.uk", TheDailyStar],
        ["The Daily Express", "express.co.uk", TheDailyExpress],
        ["James Clear", "jamesclear.com", JamesClear],
        ["Growth.me", "growth.me", GrowthME],
        ["Graham Mann", "grahammann.net", GrahamMann],
        ["Movement Capital", "movement.capital", MovementCapital],
        ["Greylock Blog", "greylock.com", GreylockBlog],
        ["Greylock News", "news.greylock.com", GreylockNews],
        ["Collaborative Fund", "collaborativefund.com", CollaborativeFund],
        ["Nat Eliason", "nateliason.com", NatEliason],
        ["Taylor Pearson", "taylorpearson.me", TaylorPearson],
        ["Reading.Guru", "reading.guru", ReadingGuru],
        ["TechDirt", "techdirt.com", TechDirt],
        ["Pacific Standard", "psmag.com", PacificStandard],
        ["The Daily Journal", "dailyjournal.com", DailyJournal],
        ["Los Angeles Daily News", "dailynews.com", LosAngelesDailyNews],
        ["The Atlanta Journal-Constitution", "ajc.com", TheAtlantaJournalConstitution],
        ["The Atlanta Journal-Constitution - Doctors & Sex Abuse Investigation", "doctors.ajc.com", DoctorsSexAbuseInvestigation],
        ["The New York Sun", "nysun.com", TheNewYorkSun],
        ["Christian Science Monitor", "csmonitor.com", ChristianScienceMonitor],
        ["The Baltimore Sun", "baltimoresun.com", TheBaltimoreSun],
        ["The Tampa Bay Times", "tampabay.com", TheTampaBayTimes],
        ["GeekWire", "geekwire.com", GeekWire],
        ["Salon", "salon.com", Salon],
        ["Buzzfeed", "buzzfeednews.com", Buzzfeed],
        ["Inamerrata", "erisian.com.au", Inamerrata],
        ["Jim and Nancy Forest", "jimandnancyforest.com", JimAndNancyForest],
        ["SBS", "sbs.com.au", SBS],
        ["VoxEU", "voxeu.org", VoxEU],
        ["New Food Magazine", "newfoodmagazine.com", NewFoodMagazine],
        ["The Omaha World-Herald", "omaha.com", TheOmahaWorldHerald],
        ["Newsday", "newsday.com", Newsday],
        ["The Star Tribune", "startribune.com", TheStarTribune],
        ["The Globe And Mail", "theglobeandmail.com", TheGlobeAndMail],
        ["The Philadelphia Inquirer", "inquirer.com", Inquirer],
        ["The San Francisco Chronicle", "sfchronicle.com", SFChronicle],
        ["The San Francisco Chronicle - Projects", "projects.sfchronicle.com", SFChronicle],
        ["The San Francisco Chronicle - Datebook", "datebook.sfchronicle.com", Datebook],
        ["Candy Industry", "candyindustry.com", CandyIndustry],
        ["Confectionery News", "confectionerynews.com", ConfectioneryNews],
        ["Business Today", "businesstoday.in", BusinessTodayIN],
        ["The History Blog", "thehistoryblog.com", TheHistoryBlog],
        ["The Earth Institute", "earth.columbia.edu", TheEarthInstitute],
        ["The Earth Institute Blogs", "blogs.ei.columbia.edu", TheEarthInstitute],
        ["Russia Matters", "russiamatters.org", RussiaMatters],
        ["Russia Matters | Belfer Center", "belfercenter.org", RussiaMatters],
        ["Schneier on Security", "schneier.com", SchneieronSecurity],
        ["Brookings", "brookings.edu", Brookings],
        ["Lawfare", "lawfareblog.com", Lawfare],
        ["South China Morning Post", "scmp.com", SCMP],
        ["Marchmont Innovation News", "marchmontnews.com", MarchmontInnovationNews],
        ["Caixin Global", "caixinglobal.com", CaixinGlobal],
        ["ChinaTechNews", "chinatechnews.com", ChinaTechNews],
        ["Russia Beyond", "rbth.com", RussiaBeyond],
        ["TechNode", "technode.com", TechNode],
        ["China Daily", "chinadaily.com.cn", ChinaDaily],
        ["China Daily Global (CN)", "global.chinadaily.com.cn", ChinaDaily],
        ["China Daily Global", "chinadailyglobal.com", ChinaDaily],
        ["China Daily Asia", "chinadailyasia.com", ChinaDailyAsia],
        ["China Daily Hong Kong", "chinadailyhk.com", ChinaDailyAsia],
        ["China Daily Asia (CN)", "language.chinadaily.com.cn", ChinaDaily],
        ["China Daily Hong Kong (CN)", "china.chinadaily.com.cn", ChinaDaily],
        ["AFP Fact Check", "factcheck.afp.com", AFP],
        ["Australian Associated Press", "aap.com.au", AAP],
        ["United Press International", "upi.com", UPI],
        ["TASS Russian News Agency", "tass.com", TASS],
        ["TASS Russian News Agency (RU)", "tass.ru", TASS],
        ["AFP Correspondent", "correspondent.afp.com", AFP],
        ["AFP Making-of", "making-of.afp.com", AFP],
        ["AFP Focus", "focus.afp.com", AFP],
        ["NBC Sports - NBA", "nba.nbcsports.com", NBCSports],
        ["NBC Sports - Pro Football Talk", "profootballtalk.nbcsports.com", NBCSports],
        ["NBC Sports - Inside the Irish", "irish.nbcsports.com", NBCSports],
        ["NBC Sports - College Football", "collegefootball.nbcsports.com", NBCSports],
        ["NBC Sports - MLB", "mlb.nbcsports.com", NBCSports],
        ["NBC Sports - NASCAR", "nascar.nbcsports.com", NBCSports],
        ["NBC Sports - Soccer", "soccer.nbcsports.com", NBCSports],
        ["NBC Sports - NHL", "nhl.nbcsports.com", NBCSports],
        ["NBC Sports - Olympics", "olympics.nbcsports.com", NBCSports],
        ["NBC Sports - Motorsports", "motorsports.nbcsports.com", NBCSports],
        ["NBC Sports", "sports.nbcsports.com", NBCSports],
        ["NBC Sports - All American Bowl", "aab.nbcsports.com", NBCSports],
        ["NBC Sports - College Basketball", "collegebasketball.nbcsports.com", NBCSports],
        ["NBC Sports - On Her Turf", "onherturf.nbcsports.com", NBCSports],
        ["Golf Channel", "golfchannel.com", GolfChannel],
        ["MMA Fighting", "mmafighting.com", MMAFighting],
        ["TimesLIVE", "timeslive.co.za", TimesLIVE],
        ["SowetanLIVE", "sowetanlive.co.za", TimesLIVE],
        ["BusinessLive", "businesslive.co.za", BusinessLive],
        ["Moneyweb", "moneyweb.co.za", Moneyweb],
        ["CBS Sports", "cbssports.com", CBSSports],
        ["News24", "news24.com", News24],
        ["DailyMaverick", "dailymaverick.co.za", DailyMaverick],
        ["BusinessTech", "businesstech.co.za", BusinessTech],
        ["Playtech.ro", "playtech.ro", PlaytechRO],
        ["Scientific American", "scientificamerican.com", ScientificAmerican],
        ["Management Today", "managementtoday.co.uk", ManagementToday],
        ["thejournal.ie", "thejournal.ie", TheJournalIE],
        ["Independent.ie", "independent.ie", IndependentIE],
        ["Al Arabiya", "alarabiya.net", AlArabiya],
        ["Al Arabiya - Farsi", "farsi.alarabiya.net", AlArabiya],
        ["Al Arabiya - English", "english.alarabiya.net", AlArabiyaEN],
        ["Al Arabiya - Urdu", "urdu.alarabiya.net", AlArabiyaUrdu],
        ["Makers India", "in.makers.yahoo.com", MakersIndia],
        ["Spaceflight Now", "spaceflightnow.com", SpaceflightNow],
        ["Mint", "livemint.com", Mint],
        ["Adnkronos", "adnkronos.com", Adnkronos],
        ["Agenzia Giornalistica Italia (AGI)", "agi.it", AGI],
        ["Global Market Insights", "gminsights.com", GMInsights],
        ["The News International", "thenews.com.pk", TheNewsInternational],
        ["The Peninsula (Qatar)", "thepeninsulaqatar.com", ThePeninsulaQatar],
        ["Newswire", "newswire.com", Newswire],
        ["EIN Pressswire", "einpresswire.com", EINPressswire],
        ["PR Newsire", "prnewswire.com", PRNewswire],
        ["Business Wire", "businesswire.com", BusinessWire],
        ["Geneva Business News", "gbnews.ch", GBNews],
        ["Il Centro", "ilcentro.it", IlCentro],
        ["Globes", "en.globes.co.il", Globes],
        ["HelloMonaco", "hellomonaco.com", HelloMonaco],
        ["Paris Capitale", "pariscapitale.com", ParisCapitale],
        ["Modern War Institute", "mwi.usma.edu", ModernWarInstitute],
        ["Infosecurity Magazine", "infosecurity-magazine.com", InfosecurityMagazine],
        ["KrebsOnSecurity", "krebsonsecurity.com", KrebsOnSecurity],
        ["ZDNET", "zdnet.com", ZDNet],
        ["TechRepublic", "techrepublic.com", TechRepublic],
        ["WikiLeaks", "wikileaks.org", WikiLeaks],
        ["Cyware", "cyware.com", Cyware],
        ["The Hacker News", "thehackernews.com", TheHackerNews],
        ["The Daily Swig", "portswigger.net", TheDailySwig],
        ["Corriere Adriatico", "corriereadriatico.it", CorriereAdriatico],
        ["TGCOM24", "tgcom24.mediaset.it", TGCOM24],
        ["Le Courrier de Russie", "lecourrierderussie.com", LeCourrierDeRussie],
        ["Quanta Magazine", "quantamagazine.org", QuantaMagazine],
        ["BusinessWorld", "businessworld.in", BusinessWorld],
        ["CBS Boston", "boston.cbslocal.com", CBSLocal],
        ["CBS Denver", "denver.cbslocal.com", CBSLocal],
        ["CBS Dallas - Fort Worth", "dfw.cbslocal.com", CBSLocal],
        ["CBS Los Angeles", "losangeles.cbslocal.com", CBSLocal],
        ["CBS New York", "newyork.cbslocal.com", CBSLocal],
        ["CBS Pittsburgh", "pittsburgh.cbslocal.com", CBSLocal],
        ["CBS Minnesota", "minnesota.cbslocal.com", CBSLocal],
        ["CBS Philadelphia", "philadelphia.cbslocal.com", CBSLocal],
        ["CBS San Francisco", "sanfrancisco.cbslocal.com", CBSLocal],
        ["CBS Chicago", "chicago.cbslocal.com", CBSLocal],
        ["Tatler", "tatler.com", Tatler],
        ["S&P Global", "spglobal.com", SP],
        ["Anteprima24", "anteprima24.it", Anteprima24],
        ["L'Occhio", "occhionotizie.it", OcchioNotizie],
        ["L'Occhio di Salerno", "salerno.occhionotizie.it", OcchioNotizie],
        ["L'Occhio di Napoli", "napoli.occhionotizie.it", OcchioNotizie],
        ["L'Occhio di Avellino", "avellino.occhionotizie.it", OcchioNotizie],
        ["L'Occhio di Caserta", "caserta.occhionotizie.it", OcchioNotizie],
        ["L'Occhio di Benevento", "benevento.occhionotizie.it", OcchioNotizie],
        ["Cronache Salerno", "cronachesalerno.it", CronacheSalerno],
        ["Prima Tivvù", "primativvu.it", PrimaTivvu],
        ["Affaritaliani.it", "affaritaliani.it", Affaritaliani],
        ["Virgilio Notizie", "notizie.virgilio.it", VirgilioNotizie],
        ["areanapoli.it", "areanapoli.it", areanapoli],
        ["Nuova Irpinia", "nuovairpinia.it", NuovaIrpinia],
        ["Calcio Napoli 1926", "calcionapoli1926.it", CalcioNapoli1926],
        ["Calcio Napoli 24", "calcionapoli24.it", CalcioNapoli24],
        ["Calcio Napoli 24 (Mobile)", "m.calcionapoli24.it", CalcioNapoli24M],
        ["La Città di Salerno", "lacittadisalerno.it", LaCittadiSalerno],
        ["Il Quotidiano di Salerno", "ilquotidianodisalerno.it", IlQuotidianodiSalerno],
        ["CNET", "cnet.com", CNET],
        ["The Growth Manifesto", "growthmanifesto.com", TheGrowthManifesto],
        ["Harper's Bazaar", "harpersbazaar.com", HarpersBazaar],
        ["CFO", "cfo.com", CFO],
        ["CIO", "cio.com", CIO],
        ["Town & Country", "townandcountrymag.com", TownAndCountry],
        ["finews.com", "finews.com", finews],
        ["finews.ch", "finews.ch", finews],
        ["finews.asia", "finews.asia", finews],
        ["Le Figaro", "lefigaro.fr", LeFigaro],
        ["Sport24 - Le Figaro", "sport24.lefigaro.fr", Sport24],
        ["Madame Figaro", "madame.lefigaro.fr", MadameFigaro],
        ["Le Monde", "lemonde.fr", LeMonde],
        ["Inc. Magazine", "inc.com", Inc],
        ["Money", "money.com", Money],
        ["Money Magazine", "moneymag.com.au", MoneyMagazine],
        ["People Magazine", "people.com", People],
        ["Business Today Journal", "journal.businesstoday.org", BusinessToday],
        ["Georgetown Business Magazine", "msb.georgetown.edu", GeorgetownBusinessMagazine],
        ["Georgetown Magazine", "today.advancement.georgetown.edu", GeorgetownMagazine],
        ["Stanford Business Magazine", "gsb.stanford.edu", StanfordBusinessMagazine],
        ["The Spectator", "spectator.co.uk", TheSpectator],
        ["Voce di Napoli", "vocedinapoli.it", VocediNapoli],
        ["Science Alert", "sciencealert.com", ScienceAlert],
        ["New Scientist", "newscientist.com", NewScientist],
        ["InterNapoli", "internapoli.it", InterNapoli],
        ["allAfrica", "allafrica.com", allAfrica],
        ["African Business", "african.business", AfricanBusiness],
        ["Africanews - EN", "africanews.com", Africanews],
        ["Africanews - FR", "fr.africanews.com", Africanews],
        ["Ars Technica", "arstechnica.com", ArsTechnica],
        ["Corriere della Sera", "corriere.it", CorrieredellaSera],
        ["Corriere della Sera - Brescia", "brescia.corriere.it", CorrieredellaSera],
        ["Corriere della Sera - Bergamo", "bergamo.corriere.it", CorrieredellaSera],
        ["Corriere della Sera - Bologna", "bologna.corriere.it", CorrieredellaSera],
        ["Corriere della Sera - Firenze", "corrierefiorentino.corriere.it", CorrieredellaSera],
        ["Corriere della Sera - Roma", "roma.corriere.it", CorrieredellaSera],
        ["Corriere della Sera - Torino", "torino.corriere.it", CorrieredellaSera],
        ["Corriere della Sera - Veneto", "corrieredelveneto.corriere.it", CorrieredellaSera],
        ["Corriere della Sera - Mezzogiorno", "corrieredelmezzogiorno.corriere.it", CorrieredellaSera],
        ["Corriere della Sera - ViviMilano", "vivimilano.corriere.it", CorrieredellaSeraViviMilano],
        ["Corriere della Sera - Milano", "milano.corriere.it", CorrieredellaSera],
        ["Global Finance Magazine", "gfmag.com", GFMag],
        ["The South African", "thesouthafrican.com", TheSouthAfrican],
        ["Entrepreneur", "entrepreneur.com", Entrepreneur],
        ["Security Middle East", "securitymiddleeastmag.com", SecurityMiddleEast],
        ["Fanpage.IT", "fanpage.it", FanpageIT],
        ["Harvard Business Review", "hbr.org", HBR],
        ["The Nine Network News", "9news.com.au", TheNine],
        ["World Wide of Sports", "wwos.nine.com.au", WWOS],
        ["Nine Entertainment", "nine.com.au", NineEnt],
        ["9Honey", "honey.nine.com.au", Honey],
        ["Nine Finance", "finance.nine.com.au", NineFinance],
        ["Valor Econômico", "valor.globo.com", ValorEconomico],
        ["Valor Investe", "valorinveste.globo.com", ValorInveste],
        ["Cronache della Campania", "cronachedellacampania.it", CronachedellaCampania],
        ["Vogue - Business", "voguebusiness.com", VogueBusiness],
        ["Vogue - U.S.", "vogue.com", VogueUS],
        ["Vogue - Italia", "vogue.it", VogueItalia],
        ["Vogue - España", "vogue.es", VogueES],
        ["Vogue - Business - España", "business.vogue.es", VogueBusinessES],
        ["Vogue - Brasil", "vogue.globo.com", VogueBR],
        ["Vogue - Britain", "vogue.co.uk", VogueUK],
        ["Vogue - China", "vogue.com.cn", VogueCN],
        ["Vogue - Czechoslovakia", "vogue.cz", VogueCZ],
        ["Vogue - Germany", "vogue.de", VogueDE],
        ["Vogue - Greece", "vogue.gr", VogueGR],
        ["Vogue - Hong Kong", "voguehk.com", VogueHK],
        ["Vogue - India", "vogue.in", VogueIN],
        ["Vogue - Japan", "vogue.co.jp", VogueJP],
        ["Vogue - Korea", "vogue.co.kr", VogueKR],
        ["Vogue - México", "vogue.mx", VogueMX],
        ["Vogue - Nederland", "vogue.nl", VogueNL],
        ["Vogue - Paris", "vogue.fr", VogueFR],
        ["Vogue - Polska", "vogue.pl", VoguePL],
        ["Vogue - Portugal", "vogue.pt", VoguePT],
        ["Vogue - Russia", "vogue.ru", VogueRU],
        ["Vogue - Singapore", "vogue.sg", VogueSG],
        ["Vogue - Taiwan", "vogue.com.tw", VogueTW],
        ["Vogue - Thailand", "vogue.co.th", VogueTH],
        ["Vogue - Türkiye", "vogue.com.tr", VogueTR],
        ["Economic Times", "economictimes.indiatimes.com", EconomicTimes],
        ["The India Times", "indiatimes.com", TheIndiaTimes],
        ["Schweizerische Bankiervereinigung (The Swiss Bankers Association)", "swissbanking.org", SwissBanking],
        ['GQ Britain', 'gq-magazine.co.uk', GQBritain],
        ['GQ', 'gq.com', GQ],
        ["GQ Italia", "gqitalia.it", GQItalia],
        ["GQ Germany", "gq-magazin.de", GQDE],
        ['GQ Brasil', 'gq.globo.com', GQBR],
        ["GQ China", "gq.com.cn", GQCN],
        ['GQ España', 'revistagq.com', GQES],
        ['GQ France', 'gqmagazine.fr', GQFR],
        ['GQ India', 'gqindia.com', GQIN],
        ['GQ Japan', 'gqjapan.jp', GQJP],
        ["GQ Korea", "gqkorea.co.kr", GQKR],
        ['GQ México', 'gq.com.mx', GQMX],
        ['GQ Portugal', 'gqportugal.pt', GQPT],
        ['GQ South Africa', 'gq.co.za', GQSA],
        ['GQ Taiwan', 'gq.com.tw', GQTW],
        ['GQ Россия', 'gq.ru', GQRU],
        ['GQ Thailand', 'gqthailand.com', GQThailand],
        ['GQ Türkiye', 'gq.com.tr', GQTR],
        ['Swissquote - English', 'en.swissquote.com', Swissquote],
        ['Swissquote - Français', 'fr.swissquote.com', Swissquote],
        ['Swissquote - Deutsche', 'de.swissquote.com', Swissquote],
        ['Swissquote - Italiano', 'it.swissquote.com', Swissquote],
        ['Swissquote - Español', 'es.swissquote.com', Swissquote],
        ['Swissquote - Čeština', 'cs.swissquote.com', Swissquote],
        ['Swissquote - Русский', 'ru.swissquote.com', Swissquote],
        ['Swissquote - العربية', 'ar.swissquote.com', Swissquote],
        ['Swissquote - 简体中文', 'cn.swissquote.com', Swissquote],
        ['Swissquote - 繁體中文', 'tw.swissquote.com', Swissquote],
        ["Deadline", "deadline.com", Deadline],
        ["Mother Jones", "motherjones.com", MotherJones],
        ["Haaretz", "haaretz.com", Haaretz],
        ["HighSnobiety", "highsnobiety.com", HighSnobiety],
        ["Middle East Eye", "middleeasteye.net", MiddleEastEye],
        ["Farnam Street", "fs.blog", FarnamStreet],
        ["The Mercury News", "mercurynews.com", TheMercuryNews],
        ["Rand", "rand.org", Rand],
        ["Complex", "complex.com", Complex],
        ["Cosmopolitan", "cosmopolitan.com", Cosmopolitan],
        ["American Banker", "americanbanker.com", AmericanBanker],
        ["Nikkei Asia", "asia.nikkei.com", NikkeiAsia],
        ["The Tower", "thetower.org", TheTower],
        ["Trends Magazine MENA", "trendzmena.com", TrendzMENA],
        ["CTech", "calcalistech.com", CTech],
        ["The Tontine Coffee-House", "thetchblog.com", TheTontineCoffeeHouse],
        ["Reveal News", "revealnews.org", Reveal],
        ["Jewish Business News", "jewishbusinessnews.com", JewishBusinessNews],
        ["Quartz", "qz.com", Quartz],
        ["USA Today", "usatoday.com", USAToday],
        ["The National", "thenational.scot", TheNational],
        ["RT", "rt.com", RT],
        ["NPR News", "npr.org", NPRNews],
        ["PBS", "pbs.org", PBS],
        ["NBC News", "nbcnews.com", NBC],
        ["MSNBC", "msnbc.com", MSNBC],
        ["ABC News", "abcnews.go.com", ABC],
        ["CBS News", "cbsnews.com", CBSNews],
        ["CEO Magazine", "ceo-mag.com", CEOMagazine],
        ["The CEO Magazine", "theceomagazine.com", TheCEOMagazine],
        ["Alchetron", "alchetron.com", Alchetron],
        ["The Moscow Project", "themoscowproject.org", TheMoscowProject],
        ["Center for American Progress Action Fund", "americanprogressaction.org", APA],
        ["Fast Company", "fastcompany.com", FastCompany],
        ["The Real Deal", "therealdeal.com", TheRealDeal],
        ["Investopedia", "investopedia.com", Investopedia],
        ["Yahoo", "yahoo.com", YahooNews],
        ["Yahoo Finance", "finance.yahoo.com", YahooFinance],
        ["Yahoo Sports", "sports.yahoo.com", YahooSports],
        ["Yahoo News", "news.yahoo.com", YahooNews],
        ["Yahoo Style", "style.yahoo.com", YahooNews],
        ["Yahoo Italia (italiano) - Notizia", "it.notizie.yahoo.com", YahooNews],
        ["Yahoo Italia (italiano) - Style", "it.style.yahoo.com", YahooNews],
        ["Yahoo Italia (italiano) - Finanza", "it.finance.yahoo.com", YahooFinance],
        ["Yahoo Italia (italiano) - Sports", "it.sports.yahoo.com", YahooSports],
        ["Yahoo Español", "espanol.yahoo.com", YahooNews],
        ["Yahoo Australia (English)", "au.yahoo.com", YahooNews],
        ["Yahoo Australia (English) - News", "au.news.yahoo.com", YahooNews],
        ["Yahoo Australia (English) - Finance", "au.finance.yahoo.com", YahooNews],
        ["Yahoo Australia (English) - Sports", "au.sports.yahoo.com", YahooNews],
        ["Yahoo Australia (English) - Lifestyle", "au.lifestyle.yahoo.com", YahooNews],
        ["Yahoo Brasil (português)", "br.yahoo.com", YahooNews],
        ["Yahoo Brasil (português) - Notícias", "br.noticias.yahoo.com", YahooNews],
        ["Yahoo Brasil (português) - Esportes", "br.esportes.yahoo.com", YahooNews],
        ["Yahoo Brasil (português) - Finanças", "br.financas.yahoo.com", YahooNews],
        ["Yahoo Brasil (português) - Vida e Estilo", "br.vida-estilo.yahoo.com", YahooNews],
        ["Yahoo France (français)", "fr.yahoo.com", YahooNews],
        ["Yahoo France (français) - News", "fr.news.yahoo.com", YahooNews],
        ["Yahoo France (français) - Finance", "fr.finance.yahoo.com", YahooNews],
        ["Yahoo France (français) - Style", "fr.style.yahoo.com", YahooNews],
        ["Yahoo France (français) - Sports", "fr.sports.yahoo.com", YahooNews],
        ["Yahoo España (español)", "es.yahoo.com", YahooNews],
        ["Yahoo España (español) - Deportes", "es.sports.yahoo.com", YahooNews],
        ["Yahoo España (español) - Finanzas", "es.finance.yahoo.com", YahooNews],
        ["Yahoo España (español) - Vida y Estilo", "es.vida-estilo.yahoo.com", YahooNews],
        ["Yahoo España (español) - Noticias", "es.noticias.yahoo.com", YahooNews],
        ["Yahoo Estados Unidos (español) - Noticias", "es-us.noticias.yahoo.com", YahooNews],
        ["Yahoo Estados Unidos (español) - Deportes", "es-us.deportes.yahoo.com", YahooNews],
        ["Yahoo Estados Unidos (español) - Finanzas", "es-us.finanzas.yahoo.com", YahooNews],
        ["Yahoo Estados Unidos (español) - Vida y Estilo", "es-us.vida-estilo.yahoo.com", YahooNews],
        ["Yahoo Canada", "ca.yahoo.com", YahooNews],
        ["Yahoo Canada - News", "ca.news.yahoo.com", YahooNews],
        ["Yahoo Canada - Sports", "ca.sports.yahoo.com", YahooNews],
        ["Yahoo Canada - Finance", "ca.finance.yahoo.com", YahooNews],
        ["Yahoo Canada - Style", "ca.style.yahoo.com", YahooNews],
        ["Yahoo Canada - Celebrity", "ca.celebrity.yahoo.com", YahooNews],
        ["Yahoo India (English)", "in.yahoo.com", YahooNews],
        ["Yahoo India (English) - News", "in.news.yahoo.com", YahooNews],
        ["Yahoo India (English) - Finance", "in.finance.yahoo.com", YahooNews],
        ["Yahoo India (English) - Style", "in.style.yahoo.com", YahooNews],
        ["Yahoo Indonesia (Bahasa Indonesia)", "id.yahoo.com", YahooNews],
        ["Yahoo Indonesia (Bahasa Indonesia) - Berita", "id.berita.yahoo.com", YahooNews],
        ["Yahoo Deutschland (Deutsch)", "de.yahoo.com", YahooNews],
        ["Yahoo Deutschland (Deutsch) - Nachrichten", "de.nachrichten.yahoo.com", YahooNews],
        ["Yahoo Deutschland (Deutsch) - Sport", "de.sports.yahoo.com", YahooNews],
        ["Yahoo Deutschland (Deutsch) - Finanzen", "de.finance.yahoo.com", YahooNews],
        ["Yahoo Deutschland (Deutsch) - Style", "de.style.yahoo.com", YahooNews],
        ["Yahoo Malaysia (English)", "malaysia.yahoo.com", YahooNews],
        ["Yahoo Malaysia (English) - News", "malaysia.news.yahoo.com", YahooNews],
        ["Yahoo New Zealand (English)", "nz.yahoo.com", YahooNews],
        ["Yahoo New Zealand (English) - News", "nz.news.yahoo.com", YahooNews],
        ["Yahoo New Zealand (English) - Finance", "nz.finance.yahoo.com", YahooNews],
        ["Yahoo Philippines (English)", "ph.yahoo.com", YahooNews],
        ["Yahoo Philippines (English) - News", "ph.news.yahoo.com", YahooNews],
        ["Yahoo Québec (français)", "qc.yahoo.com", YahooFinance],
        ["Yahoo Singapore (English)", "sg.yahoo.com", YahooFinance],
        ["Yahoo Singapore (English) - News", "sg.news.yahoo.com", YahooFinance],
        ["Yahoo Singapore (English) - Style", "sg.style.yahoo.com", YahooFinance],
        ["Yahoo Singapore (English) - Finance", "sg.finance.yahoo.com", YahooFinance],
        ["Yahoo United Kingdom (English) - Finance", "uk.finance.yahoo.com", YahooFinance],
        ["Yahoo United Kingdom (English)", "uk.yahoo.com", YahooNews],
        ["Yahoo United Kingdom (English) - News", "uk.news.yahoo.com", YahooNews],
        ["Yahoo United Kingdom (English) - Style", "uk.style.yahoo.com", YahooNews],
        ["Yahoo United Kingdom (English) - Sports", "uk.sports.yahoo.com", YahooSports],
        ["Yahoo 香港 (繁體中文)", "hk.yahoo.com", YahooNews],
        ["Yahoo 香港 (繁體中文) - 財經", "hk.finance.yahoo.com", YahooNews],
        ["Yahoo 香港 (繁體中文) - 新聞", "hk.news.yahoo.com", YahooNews],
        ["Yahoo 香港 (繁體中文) - 體育", "hk.sports.yahoo.com", YahooNews],
        ["Yahoo 香港 (繁體中文) - 娛樂圈", "hk.celebrity.yahoo.com", YahooNews],
        ["Yahoo 香港 (繁體中文) - Style", "hk.style.yahoo.com", YahooNews],
        ["Yahoo 臺灣 (繁體中文)", "tw.yahoo.com", YahooFinance],
        ["Yahoo 臺灣 (繁體中文) - 股市", "tw.stock.yahoo.com", YahooFinance],
        ["Yahoo 臺灣 (繁體中文) - 新聞", "tw.news.yahoo.com", YahooFinance],
        ["Gulf News", "gulfnews.com", GulfNews],
        ["WNYC Studios", "wnycstudios.org", WNYCStudios],
        ["Axios", "axios.com", Axios],
        ["The Onion", "theonion.com", TheOnion],
        ["The Onion - Politics", "politics.theonion.com", TheOnion],
        ["The Onion - Sports", "sports.theonion.com", TheOnion],
        ["The Onion - Local", "local.theonion.com", TheOnion],
        ["The Onion - Entertainment", "entertainment.theonion.com", TheOnion],
        ["The Onion - Gamers", "ogn.theonion.com", TheOnion],
        ["Gizmodo", "gizmodo.com", TheOnion],
        ["Deadspin", "deadspin.com", TheOnion],
        ["The A.V. Club", "avclub.com", TheOnion],
        ["Jalopnik", "jalopnik.com", TheOnion],
        ["jezebel", "jezebel.com", TheOnion],
        ["Kotaku", "kotaku.com", TheOnion],
        ["Lifehacker", "lifehacker.com", TheOnion],
        ["The Root", "theroot.com", TheOnion],
        ["The Takeout", "thetakeout.com", TheOnion],
        ["The Inventory", "theinventory.com", TheOnion],
        ["Radio Free Europe/Radio Liberty", "rferl.org", RFERL],
        ["Radio Free Europe/Radio Liberty - Gandhara", "gandhara.rferl.org", RFERL],
        ["Radio Free Europe/Radio Liberty - Россия", "svoboda.org", RFERL],
        ["Radio Free Europe/Radio Liberty - Север.Реалии", "severreal.org", RFERL],
        ["Radio Free Europe/Radio Liberty - Сибирь.Реалии", "sibreal.org", RFERL],
        ["Radio Free Europe/Radio Liberty - Фактограф", "factograph.info", RFERL],
        ["Radio Free Europe/Radio Liberty - Татарстан", "azatliq.org", RFERL],
        ["Radio Free Europe/Radio Liberty - Къилбаседан Кавказ", "radiomarsho.com", RFERL],
        ["Radio Free Europe/Radio Liberty - Средняя Волга", "idelreal.org", RFERL],
        ["Radio Free Europe/Radio Liberty - Северный Кавказ", "kavkazr.com", RFERL],
        ["Radio Free Europe/Radio Liberty - ایران‎", "radiofarda.com", RFERL],
        ["Radio Free Europe/Radio Liberty - Iran", "en.radiofarda.com", RFERL],
        ["Radio Free Europe/Radio Liberty - Հայաստան", "azatutyun.am", RFERL],
        ["Radio Free Europe/Radio Liberty - Армения", "rus.azatutyun.am", RFERL],
        ["Radio Free Europe/Radio Liberty - Azərbaycan", "azadliq.org", RFERL],
        ["Radio Free Europe/Radio Liberty - საქართველო", "radiotavisupleba.ge", RFERL],
        ["Radio Free Europe/Radio Liberty - Грузия", "ekhokavkaza.com", RFERL],
        ["Radio Free Europe/Radio Liberty - Қазақстан", "azattyq.org", RFERL],
        ["Radio Free Europe/Radio Liberty - Казахстан", "rus.azattyq.org", RFERL],
        ["Radio Free Europe/Radio Liberty - Кыргызстан", "azattyk.org", RFERL],
        ["Radio Free Europe/Radio Liberty - Киргизия", "rus.azattyk.org", RFERL],
        ["Radio Free Europe/Radio Liberty - Тоҷикистон", "ozodi.org", RFERL],
        ["Radio Free Europe/Radio Liberty - Таджикистан", "rus.ozodi.org", RFERL],
        ["Radio Free Europe/Radio Liberty - Türkmenistan", "azathabar.com", RFERL],
        ["Radio Free Europe/Radio Liberty - Туркменистан", "rus.azathabar.com", RFERL],
        ["Radio Free Europe/Radio Liberty - Oʻzbekiston", "ozodlik.org", RFERL],
        ["Radio Free Europe/Radio Liberty - Узбекистан", "rus.ozodlik.org", RFERL],
        ["Radio Free Europe/Radio Liberty - افغانستان - PA", "pa.azadiradio.com", RFERL],
        ["Radio Free Europe/Radio Liberty - افغانستان - DA", "da.azadiradio.com", RFERL],
        ["Radio Free Europe/Radio Liberty - پاكستان‎", "mashaalradio.com", RFERL],
        ["Radio Free Europe/Radio Liberty - Magyarország", "szabadeuropa.hu", RFERL],
        ["Radio Free Europe/Radio Liberty - Moldova", "moldova.europalibera.org", RFERL],
        ["Radio Free Europe/Radio Liberty - România", "romania.europalibera.org", RFERL],
        ["Radio Free Europe/Radio Liberty - България", "svobodnaevropa.bg", RFERL],
        ["Radio Free Europe/Radio Liberty - Bosna i Hercegovina / Srbija / Crna Gora", "slobodnaevropa.org", RFERL],
        ["Radio Free Europe/Radio Liberty - Северна Македонија", "slobodnaevropa.mk", RFERL],
        ["Radio Free Europe/Radio Liberty - Kosova", "evropaelire.org", RFERL],
        ["Radio Free Europe/Radio Liberty - Беларусь", "svaboda.org", RFERL],
        ["Radio Free Europe/Radio Liberty - Україна", "radiosvoboda.org", RFERL],
        ["Radio Free Europe/Radio Liberty - Qırım", "ktat.krymr.com", RFERL],
        ["Radio Free Europe/Radio Liberty - Крим", "ua.krymr.com", RFERL],
        ["Radio Free Europe/Radio Liberty - Крым", "ru.krymr.com", RFERL],
        ["Radio Free Europe/Radio Liberty - Polygraph", "polygraph.info", RFERL],
        ["Radio Free Europe/Radio Liberty - Pressroom", "pressroom.rferl.org", RFERL],
        ["Radio Free Europe/Radio Liberty - Настоящее Время", "currenttime.tv", RFERL],
        ["Radio Free Europe/Radio Liberty - Current Time English", "en.currenttime.tv", RFERL],
        ["MarketWatch", "marketwatch.com", MarketWatch],
        ["The Street", "thestreet.com", TheStreet],
        ["The Diplomat", "thediplomat.com", TheDiplomat],
        ["Euronews", "euronews.com", Euronews],
        ["EUbusiness", "eubusiness.com", EUbusiness],
        ["Reuters", "reuters.com", Reuters],
        ["The Boston Herald", "bostonherald.com", BostonHerald],
        ["International Business Times", "ibtimes.com", IBTimes],
        ["Observer", "observer.com", Observer],
        ["Kiplinger", "kiplinger.com", Kiplinger],
        ["ESPN", "espn.com", ESPN],
        ["Bleacher Report", "bleacherreport.com", BleacherReport],
        ["Chicago Sun-Times", "chicago.suntimes.com", ChicagoSunTimes],
        ["The Chicago Tribune", "chicagotribune.com", ChicagoTribune],
        ["The Denver Post", "denverpost.com", TheDenverPost],
        ["LatinAmerican Post", "latinamericanpost.com", LAP],
        ["The Lexington Institute", "lexingtoninstitute.org", TheLexingtonInstitute],
        ["Total Politics", "totalpolitics.com", TotalPolitics],
        ["BBC", "bbc.com", BBC],
        ["The New York Daily News", "nydailynews.com", NYDailyNews],
        ["The New York Post", "nypost.com", NYPost],
        ["Institutional Investor", "institutionalinvestor.com", InstitutionalInvestor],
        ["Forbes Italia", "forbes.it", ForbesIT],
        ["Forbes España", "forbes.es", ForbesES],
        ["Forbes France", "forbes.fr", ForbesFrance],
        ["Forbes Hungary", "forbes.hu", ForbesHungary],
        ["Forbes Baltics", "forbesbaltics.com", ForbesBaltics],
        ["Forbes Argentina", "forbesargentina.com", ForbesArgentina],
        ["Forbes Russia", "forbes.ru", ForbesRussia],
        ["Forbes Brasil", "forbes.com.br", ForbesBrasil],
        ["Value Walk", "valuewalk.com", ValueWalk],
        ["Marketplace", "marketplace.org", Marketplace],
        ["Prospect Magazine", "prospectmagazine.co.uk", ProspectMagazine],
        ["The Washington Times", "washingtontimes.com", TheWashingtonTimes],
        ["Boston.com", "boston.com", Boston],
        ["Bloomberg Quint", "bloombergquint.com", BloombergQuint],
        ["Foreign Policy In Focus", "fpif.org", ForeignPolicyInFocus],
        ["CNN", "cnn.com", CNN],
        ["CNN Edition", "edition.cnn.com", CNN],
        ["CNBC", "cnbc.com", CNBC],
        ["Fox News", "foxnews.com", FoxNews],
        ["Fox Business", "foxbusiness.com", FoxBusiness],
        ["Gothamist", "gothamist.com", Gothamist],
        ["Quotidiano", "quotidiano.net", Quotidiano],
        ["Il Telegrafo Livorno", "iltelegrafolivorno.it", IlTelegrafoLivorno],
        ["AvellinoToday", "avellinotoday.it", Today],
        ["MilanoToday", "milanotoday.it", Today],
        ['ReggioToday', 'reggiotoday.it', Today],
        ['MessinaToday', 'messinatoday.it', Today],
        ['LivornoToday', 'livornotoday.it', Today],
        ['TerniToday', 'ternitoday.it', Today],
        ['FrosinoneToday', 'frosinonetoday.it', Today],
        ['RiminiToday', 'riminitoday.it', Today],
        ['MonzaToday', 'monzatoday.it', Today],
        ['ParmaToday', 'parmatoday.it', Today],
        ['PisaToday', 'pisatoday.it', Today],
        ['RavennaToday', 'ravennatoday.it', Today],
        ['SalernoToday', 'salernotoday.it', Today],
        ['VicenzaToday', 'vicenzatoday.it', Today],
        ['UdineToday', 'udinetoday.it', Today],
        ['ModenaToday', 'modenatoday.it', Today],
        ['ChietiToday', 'chietitoday.it', Today],
        ['LatinaToday', 'latinatoday.it', Today],
        ['AnconaToday', 'anconatoday.it', Today],
        ['TrentoToday', 'trentotoday.it', Today],
        ['NovaraToday', 'novaratoday.it', Today],
        ['LeccoToday', 'leccotoday.it', Today],
        ['CesenaToday', 'cesenatoday.it', Today],
        ['SondrioToday', 'sondriotoday.it', Today],
        ['VeneziaToday', 'veneziatoday.it', Today],
        ['PerugiaToday', 'perugiatoday.it', Today],
        ['TrevisoToday', 'trevisotoday.it', Today],
        ['BresciaToday', 'bresciatoday.it', Today],
        ['CataniaToday', 'cataniatoday.it', Today],
        ['FoggiaToday', 'foggiatoday.it', Today],
        ['FirenzeToday', 'firenzetoday.it', Today],
        ['TorinoToday', 'torinotoday.it', Today],
        ['NapoliToday', 'napolitoday.it', Today],
        ['PalermoToday', 'palermotoday.it', Today],
        ['ForlìToday', 'forlitoday.it', Today],
        ['BariToday', 'baritoday.it', Today],
        ['GenovaToday', 'genovatoday.it', Today],
        ['BolognaToday', 'bolognatoday.it', Today],
        ['RomaToday', 'romatoday.it', Today],
        ['QuiComo', 'quicomo.it', Today],
        ['IlPiacenza', 'ilpiacenza.it', Today],
        ['IlPescara', 'ilpescara.it', Today],
        ['VeronaSera', 'veronasera.it', Today],
        ['BrindisiReport', 'brindisireport.it', Today],
        ['TriestePrima', 'triesteprima.it', Today],
        ['LeccePrima', 'lecceprima.it', Today],
        ['PadovaOggi', 'padovaoggi.it', Today],
        ['AgrigentoNotizie', 'agrigentonotizie.it', Today],
        ['ArezzoNotizie', 'arezzonotizie.it', Today],
        ['CasertaNews', 'casertanews.it', Today],
        ['EuropaToday', 'europa.today.it', Today],
        ['Today', 'today.it', Today],
        ['Italia Oggi', 'italiaoggi.it', ItaliaOggi],
        ['InsideOver (IT)', 'it.insideover.com', InsideOver],
        ['InsideOver', 'insideover.com', InsideOver],
        ['La Gazzetta del Mezziogiorno', 'lagazzettadelmezzogiorno.it', LaGazzettadelMezziogiorno],
        ['La Sicilia', 'lasicilia.it', LaSicilia],
        ['Gazzetta del Sud', 'gazzettadelsud.it', GazzettadelSud],
        ['Gazzetta del Sud Calabria', 'calabria.gazzettadelsud.it', GazzettadelSud],
        ['Fortune', 'fortune.com', Fortune],
        ['Balkan Insight', 'balkaninsight.com', BalkanInsight],
        ['The New Yorker', 'newyorker.com', TheNewYorker],
        ['The Daily Beast', 'thedailybeast.com', TheDailyBeast],
        ['The Atlantic', 'theatlantic.com', TheAtlantic],
        ['Vanity Fair', 'vanityfair.com', VanityFair],
        ['Vanity Fair Archive', 'archive.vanityfair.com', VanityFairArchive],
        ['Vanity Fair Italia', 'vanityfair.it', VanityFairIT],
        ['Vanity Fair España', 'revistavanityfair.es', VanityFairES],
        ['Vanity Fair France', 'vanityfair.fr', VanityFairFR],
        ['Britannica', 'britannica.com', Britannica],
        ['Tech Crunch', 'techcrunch.com', TechCrunch],
        ['Politico', 'politico.com', Politico],
        ['Bellingcat', 'bellingcat.com', Bellingcat],
        ['The Times of Malta', 'timesofmalta.com', TheTimesofMalta],
        ['The Baltic Times', 'baltictimes.com', TheBalticTimes],
        ['Time', 'time.com', Time],
        ['The Verge', 'theverge.com', TheVerge],
        ['The Conversation', 'theconversation.com', TheConversation],
        ['Wired', 'wired.com', Wired],
        ['Wired UK', 'wired.co.uk', WiredUK],
        ['Wired Italia', 'wired.it', WiredIT],
        ['Wired Japan', 'wired.jp', WiredJP],
        ['La Stampa', 'lastampa.it', LaStampa],
        ['Il Secolo XIX', 'ilsecoloxix.it', IlSecoloXIX],
        ['La Nuova Sardegna', 'lanuovasardegna.it', LaNuovaSardegna],
        ['Il Piccolo', 'ilpiccolo.gelocal.it', Gelocal],
        ['Gazzetta di Mantova', 'gazzettadimantova.gelocal.it', Gelocal],
        ['Gazzetta di Modena', 'gazzettadimodena.gelocal.it', Gelocal],
        ['Gazzetta di Reggio', 'gazzettadireggio.gelocal.it', Gelocal],
        ['La Nuova Venezia', 'nuovavenezia.gelocal.it', Gelocal],
        ['La Nuova Ferrara', 'nuovaferrara.gelocal.it', Gelocal],
        ['La Provincia Pavese', 'laprovinciapavese.gelocal.it', Gelocal],
        ['La Sentinella del Canavese', 'lasentinella.gelocal.it', Gelocal],
        ['La Tribuna di Treviso', 'tribunatreviso.gelocal.it', Gelocal],
        ['Messaggero Veneto', 'messaggeroveneto.gelocal.it', Gelocal],
        ['Il Mattino di Padova', 'mattinopadova.gelocal.it', Gelocal],
        ['Il Corriere delle Alpi', 'corrierealpi.gelocal.it', Gelocal],
        ['Vox', 'vox.com', Vox],
        ['Foreign Affairs', 'foreignaffairs.com', ForeignAffairs],
        ['Il Giornale', 'ilgiornale.it', IlGiornale],
        ['Il Giornale Blog', 'blog.ilgiornale.it', IlGiornaleBlog],
        ['Giornale di Sicilia', 'gds.it', GiornalediSicilia],
        ['Palermo | Giornale di Sicilia', 'palermo.gds.it', GiornalediSicilia],
        ['Agrigento | Giornale di Sicilia', 'agrigento.gds.it', GiornalediSicilia],
        ['Messina | Giornale di Sicilia', 'messina.gds.it', GiornalediSicilia],
        ['Trapani | Giornale di Sicilia', 'trapani.gds.it', GiornalediSicilia],
        ['Caltanissetta | Giornale di Sicilia', 'caltanissetta.gds.it', GiornalediSicilia],
        ['Catania | Giornale di Sicilia', 'catania.gds.it', GiornalediSicilia],
        ['Ragusa | Giornale di Sicilia', 'ragusa.gds.it', GiornalediSicilia],
        ['Enna | Giornale di Sicilia', 'enna.gds.it', GiornalediSicilia],
        ['Siracusa | Giornale di Sicilia', 'siracusa.gds.it', GiornalediSicilia],
        ['Libertà', 'liberta.it', Liberta],
        ['Zenith Magazine', 'magazine.zenith.me', Zenith],
        ['Zenith', 'zenith.me', Zenith],
        ['Lebanon Chronicles by Zenith', 'lebanon.zenith.me', Zenith],
        ['Libya Chronicles by Zenith', 'libya.zenith.me', Zenith],
        ['The Irish Times', 'irishtimes.com', TheIrishTimes],
        ['Contrarian Edge', 'contrarianedge.com', ContrarianEdge],
        ['Federation of American Scientists', 'fas.org', FederationofAmericanScientists],
        ['Asia Times', 'asiatimes.com', AsiaTimes],
        ['Asia Times Financial', 'asiatimesfinancial.com', AsiaTimesFinancial],
        ['New York Magazine', 'nymag.com', NewYorkMagazine],
        ['Dealbreaker', 'dealbreaker.com', Dealbreaker],
        ['openDemocracy', 'opendemocracy.net', openDemocracy],
        ['The Moscow Times', 'themoscowtimes.com', TheMoscowTimes],
        ['Il Giorno', 'ilgiorno.it', IlGiorno],
        ['Il Sole 24 Ore', 'ilsole24ore.com', IlSole24Ore],
        ['Gazzetta di Parma', 'gazzettadiparma.it', GazzettadiParma],
        ['Corriere del Ticino', 'cdt.ch', CorrieredelTicino],
        ['Giornale di Brescia', 'giornaledibrescia.it', GiornalediBrescia],
        ['Il Giornale di Vicenza', 'ilgiornaledivicenza.it', IlGiornalediVicenza],
        ['Ticinonews', 'ticinonews.ch', Ticinonews],
        ['Il Tirreno', 'iltirreno.gelocal.it', IlTirreno],
        ['La Nazione', 'lanazione.it', LaNazione],
        ['Il Resto del Carlino', 'ilrestodelcarlino.it', IlRestodelCarlino],
        ['The Smithsonian Magazine', 'smithsonianmag.com', TheSmithsonianMagazine],
        ['ProPublica', 'propublica.org', ProPublica],
        ['Features by ProPublica', 'features.propublica.org', ProPublica],
        ['Slate', 'slate.com', Slate],
        ['The Jerusalem Post', 'jpost.com', TheJerusalemPost],
        ['Russian International Affairs Council', 'russiancouncil.ru' , RussianInternationalAffairsCouncil],
        ['Foreign Policy', 'foreignpolicy.com' , ForeignPolicy],
        ['Washington Post', 'washingtonpost.com', WashingtonPost],
        ["Spisok Putina (Putin's List)", 'spisok-putina.org', SpisokPutina],
        ["DW", "dw.com", DW],
        ["The Intercept", "theintercept.com", TheIntercept],
        ["AmericanMafia.com", "americanmafia.com", AmericanMafia],
        ["LIFE", "life.com", LIFE],
        ["L'Osservatore Romano", "osservatoreromano.va", LOsservatoreRomano],
        ["Le Monde diplomatique", "mondediplo.com", LeMondediplomatique],
        ["Süddeutsche Zeitung International", "projekte.sueddeutsche.de", SuddeutscheZeitung],
        ["Süddeutsche Zeitung", "sueddeutsche.de", SuddeutscheZeitung],
        ["Il Messaggero", "ilmessaggero.it", IlMessaggero],
        ["Independent Balkan News Agency", "balkaneu.com", IndependentBalkanNewsAgency],
        ["The Mainichi", "mainichi.jp", TheMainichi],
        ["The New Republic", "newrepublic.com", TheNewRepublic],
        ["Monaco Tribune", "monaco-tribune.com", MonacoTribune],
        ["Crux", "cruxnow.com", Crux],
        ["L'Espresso", "espresso.repubblica.it", LEspresso],
        ["The Gentleman's Journal", "thegentlemansjournal.com", TheGentlemansJournal],
        ["In Moscow's Shadows", "inmoscowsshadows.wordpress.com", InMoscowsShadows],
        ["Vatican News", "vaticannews.va", VaticanNews],
        ["Mafia Today", "mafiatoday.com", MafiaToday],
        ["applet-magic.com", "applet-magic.com", appletmagic],
        ["applet-magic (SJSU)", 'sjsu.edu', appletmagic],
        ["SWI swissinfo.ch", "swissinfo.ch", SWI],
        ["Rolling Stone", "rollingstone.com", RollingStone],
        ["The Week", "theweek.com", TheWeek],
        ["The Week UK", "theweek.co.uk", TheWeekUK],
        ["The Standard", "thestandard.com.hk", TheStandard],
        ["Il Tempo", "iltempo.it", IlTempo],
        ["Libero Quotidiano", "liberoquotidiano.it", LiberoQuotidiano],
        ["Corriere dell'Umbria", "corrieredellumbria.corr.it", CorrieredellUmbria],
        ["Irpinia News", "irpinianews.it", IrpiniaNews],
        ["L'Unione Sarda", "unionesarda.it", LUnioneSarda],
        ["The Asahi Shimbun", "asahi.com", TheAsahiShimbun],
        ["The Asahi Shimbun - 繁體字", "asahichinese-f.com", TheAsahiShimbun],
        ["The Asahi Shimbun - 简体字", "asahichinese-j.com", TheAsahiShimbun],
        ["New Statesman", "newstatesman.com", NewStatesman],
        ["Il Gazzettino", "ilgazzettino.it", IlGazzettino],
        ["Il Mattino", "ilmattino.it", IlMattino],
        ["El País English", "english.elpais.com", ElPais],
        ["El País", "elpais.com", ElPais],
        ["El País Brasil", "brasil.elpais.com", ElPais],
        ["El País.cat", "cat.elpais.com", ElPaiscat],
        ["OCCRP", "occrp.org", OCCRP],
        ["Al Jazeera", "aljazeera.com", AlJazeera],
        ["Vice", "vice.com", Vice],
        ["Avvenire", "avvenire.it", Avvenire],
        ["Il Fatto Quotidiano", "ilfattoquotidiano.it", IlFattoQuotidiano],
        ["Wall Street Italia", "wallstreetitalia.com", WallStreetItalia],
        ["Il Giornale d'Italia", "ilgiornaleditalia.it", IlGiornaledItalia],
        ["Esquire", "esquire.com", Esquire],
        ["Longreads", "longreads.com", Longreads],
        ["CEE Bankwatch Network", "bankwatch.org", CEEBankwatchNetwork],
        ["Ozy", "ozy.com", Ozy],
        ["Ticinonline", "tio.ch", Ticinonline],
        ["La Regione", "laregione.ch", LaRegione],
        ["Institute of Modern Russia", "imrussia.org", InstituteofModernRussia],
        ["Carnegie Endowment for International Peace", "carnegieendowment.org", CarnegieEndowment],
        ["Carnegie Moscow Center", "carnegie.ru", CarnegieMoscowCenter],
        ["Carnegie India", "carnegieindia.org", CarnegieIndia],
        ["Carnegie-Tsinghua Center for Global Policy", "carnegietsinghua.org", CarnegieTsinghua],
        ["Malcolm H. Kerr Carnegie Middle East Center", "carnegie-mec.org", CarnegieMiddleEast],
        ["Carnegie Europe", "carnegieeurope.eu", CarnegieEurope],
        ["Carnegie Council for Ethics in International Affairs", "carnegiecouncil.org", CarnegieCouncil],
        ["Business Insider", "businessinsider.com", Insider],
        ["Markets Insider", "markets.businessinsider.com", Insider],
        ["Insider", "insider.com", Insider],
        ["ANSA", "ansa.it", ANSA],
        ["ANSA Latina", "ansalatina.com", ANSALatina],
        ["ANSA Brasil", "ansabrasil.com.br", ANSALatina],
        ["ANSAmed", "ansamed.info", ANSA],
        ["La Repubblica", "repubblica.it", LaRepubblica],
        ["La Repubblica - Rep", "rep.repubblica.it", LaRepubblica],
        ["La Repubblica - Bologna", "bologna.repubblica.it", LaRepubblica],
        ["La Repubblica - Napoli", "napoli.repubblica.it", LaRepubblica],
        ["La Repubblica - Roma", "roma.repubblica.it", LaRepubblica],
        ["La Repubblica - Bari", "bari.repubblica.it", LaRepubblica],
        ["La Repubblica - Firenze", "firenze.repubblica.it", LaRepubblica],
        ["La Repubblica - Parma", "parma.repubblica.it", LaRepubblica],
        ["La Repubblica - Milano", "milano.repubblica.it", LaRepubblica],
        ["La Repubblica - Torino", "torino.repubblica.it", LaRepubblica],
        ["La Repubblica - Genova", "genova.repubblica.it", LaRepubblica],
        ["La Repubblica - Palermo", "palermo.repubblica.it", LaRepubblica],
        ["The Atlantic Council", "atlanticcouncil.org", TheAtlanticCouncil],
        ["The Wilson Center", "wilsoncenter.org", TheWilsonCenter],
        ["The The Wilson Center | Africa Up Close", "africaupclose.wilsoncenter.org", AfricaUpClose],
        ["The Wilson Quarterly", "wilsonquarterly.com", TheWilsonQuarterly],
        ["Lausan", "lausan.hk", Lausan],
        ["MIT Technology Review", "technologyreview.com", MITTechnologyReview],
        ["The National Interest", "nationalinterest.org", TheNationalInterest],
        ["Global Asia", "globalasia.org", GlobalAsia],
        ["The Acquirer's Multiple", "acquirersmultiple.com", TheAcquirersMultiple],
        ["The Nation", "thenation.com", TheNation],
        ["The New York Times", "nytimes.com", NYT],
        ["The Economist", "economist.com", TheEconomist],
        ["The Guardian", "theguardian.com", TheGuardian],
        ["Forbes", "forbes.com", Forbes],
        ["Morningstar", "morningstar.com", Morningstar],
        ["MoneyWeek", "moneyweek.com", MoneyWeek],
        ["NFX", "nfx.com", NFX],
        ["FiveThirtyEight", "fivethirtyeight.com", FiveThirtyEight],
        ["Forbes Africa", "forbesafrica.com", ForbesAfrica],
        ["AP News", "apnews.com", AP],
    ])

    # source_arr = [[i[0], i[1]] for i in base_arr]
    # print(source_arr)
    # def printAll(self, base_arr):
    #     source_arr = [[i[0], i[1]] for i in base_arr]
    #     print(source_arr)


    # For each language, append the domain to base_arr.
    # ex. append 'en.wikipedia.org' and 'it.wikipedia.org' and so on....
    langs = np.array(["en", "it", "ar", "ast", "az", "zh-yue", "ko", "zh", "bg", "nan", "be", "ca", "cs", "cy", "da", "de", "et", "el", "es", "eo", "eu", "fa", "fr", "id", "gl", "hy", "hi", "hr", "he", "ka", "la", "lv", "lt", "hu", "mk", "arz", "ms", "min", "nl", "ja", "no", "nn", "ce", "uz", "pl", "pt", "kk", "ro", "ru", "simple", "ceb", "sk", "sl", "sr", "sh", "fi", "sv", "ta", "tt", "th", "tg", "azb", "tr", "uk", "ur", "vi", "vo", "war"])
    for i in range(len(langs)):
        wiki_arr = np.array([['Wikipedia', f'{langs[i-1]}.wikipedia.org', Wikipedia]])
        base_arr = np.concatenate((base_arr, wiki_arr))

    url_dict = {ind_arr[1]: ind_arr[0] for ind_arr in base_arr}
    src_dict = {ind_arr[0]: ind_arr[1] for ind_arr in base_arr}
    src_to_func_dict = {ind_arr[0]: ind_arr[2] for ind_arr in base_arr}
    url_to_func_dict = {ind_arr[1]: ind_arr[2] for ind_arr in base_arr}

    def run_method(self, src):
        """
        Depending on the source (specified in the parameter 'src'), this method decides which scraping method to call. So for example,
        if the source is "Luxembourg Times", then this method will call the method 'scrape_luxembourgtimes(src)', which will return
        a dictionary 'dct' and an object, 'article_data', of class 'SingleArticle'. This method will then itself return 'dct' and 'article_data'.
        """
        dct = None
        article_data = None
        (dct, article_data) = self.src_to_func_dict[src](self, src)
        return (dct, article_data)

