# import requests
# import time
# from urllib.parse import urlparse
# from bs4 import BeautifulSoup as bs
# from pprint import pprint

# from ecoles.models import Assignment, Submodule

# url = "http://deathcamps.org/contents/index.html"
# doc = requests.get(url)
# soup = bs(doc.content, 'html.parser')

# # GET LINKS
# categories = ["belzec", "sobibor", "treblinka", "aktion_reinhard", "gas_chambers", "lublin", "occupation", "euthanasia", "risiera_di_san_sabba"]
# links = soup.select('a')[17:]
# for link in links:
# 	if "../" not in link['href']:
# 		links.remove(link)
# belzec = links[:72]
# sobibor = links[72:105]
# treblinka = links[105:160]
# aktion_reinhard = links[160:295]
# gas_chambers = links[295:345]
# lublin = links[345:370]
# occupation = links[370:553]
# euthanasia = links[553:606]
# risiera_di_san_sabba = links[606:609]



# for link in belzec:
#     a_href = link['href']
#     if a_href[0:3] == "../":
#         new_link = a_href[3:]
#         new_href = f"http://deathcamps.org/{new_link}"
#         link['href'] = new_href

# # If has spaces, replace with "%20":
# for link in belzec:
#     a_href = link['href']
#     if " " in a_href:
#         href = a_href.replace(" ", "%20")
#         link['href'] = href



# for link in sobibor:
#     a_href = link['href']
#     if a_href[0:3] == "../":
#         new_link = a_href[3:]
#         new_href = f"http://deathcamps.org/{new_link}"
#         link['href'] = new_href
#         # print(new_href)

# # If has spaces, replace with "%20":
# for link in sobibor:
#     a_href = link['href']
#     if " " in a_href:
#         href = a_href.replace(" ", "%20")
#         link['href'] = href



# for link in treblinka:
#     a_href = link['href']
#     if a_href[0:3] == "../":
#         new_link = a_href[3:]
#         new_href = f"http://deathcamps.org/{new_link}"
#         link['href'] = new_href
#         # print(new_href)

# # If has spaces, replace with "%20":
# for link in treblinka:
#     a_href = link['href']
#     if " " in a_href:
#         href = a_href.replace(" ", "%20")
#         link['href'] = href



# for link in aktion_reinhard:
#     a_href = link['href']
#     if a_href[0:3] == "../":
#         new_link = a_href[3:]
#         new_href = f"http://deathcamps.org/{new_link}"
#         link['href'] = new_href
#         # print(new_href)

# # If has spaces, replace with "%20":
# for link in aktion_reinhard:
#     a_href = link['href']
#     if " " in a_href:
#         href = a_href.replace(" ", "%20")
#         link['href'] = href



# for link in gas_chambers:
#     a_href = link['href']
#     if a_href[0:3] == "../":
#         new_link = a_href[3:]
#         new_href = f"http://deathcamps.org/{new_link}"
#         link['href'] = new_href
#         # print(new_href)

# # If has spaces, replace with "%20":
# for link in gas_chambers:
#     a_href = link['href']
#     if " " in a_href:
#         href = a_href.replace(" ", "%20")
#         link['href'] = href



# for link in lublin:
#     a_href = link['href']
#     if a_href[0:3] == "../":
#         new_link = a_href[3:]
#         new_href = f"http://deathcamps.org/{new_link}"
#         link['href'] = new_href
#         # print(new_href)

# # If has spaces, replace with "%20":
# for link in lublin:
#     a_href = link['href']
#     if " " in a_href:
#         href = a_href.replace(" ", "%20")
#         link['href'] = href



# for link in occupation:
#     a_href = link['href']
#     if a_href[0:3] == "../":
#         new_link = a_href[3:]
#         new_href = f"http://deathcamps.org/{new_link}"
#         link['href'] = new_href
#         # print(new_href)

# # If has spaces, replace with "%20":
# for link in occupation:
#     a_href = link['href']
#     if " " in a_href:
#         href = a_href.replace(" ", "%20")
#         link['href'] = href



# for link in euthanasia:
#     a_href = link['href']
#     if a_href[0:3] == "../":
#         new_link = a_href[3:]
#         new_href = f"http://deathcamps.org/{new_link}"
#         link['href'] = new_href
#         # print(new_href)

# # If has spaces, replace with "%20":
# for link in euthanasia:
#     a_href = link['href']
#     if " " in a_href:
#         href = a_href.replace(" ", "%20")
#         link['href'] = href



# for link in risiera_di_san_sabba:
#     a_href = link['href']
#     if a_href[0:3] == "../":
#         new_link = a_href[3:]
#         new_href = f"http://deathcamps.org/{new_link}"
#         link['href'] = new_href
#         # print(new_href)

# # If has spaces, replace with "%20":
# for link in risiera_di_san_sabba:
#     a_href = link['href']
#     if " " in a_href:
#         href = a_href.replace(" ", "%20")
#         link['href'] = href





# def get_html_body(url, topic):
#     doc = requests.get(url); soup = bs(doc.content, 'lxml'); title = soup.title.get_text(); body = soup.find('body'); [body.b.unwrap() for b in body.select("b")]; [body.font.unwrap() for font in body.select("font")]
        
#     for image in body.select("img"):
#         img_url = image['src']
#         if "http:" not in img_url:
#             img_url=f"http://deathcamps.org/{topic}/{img_url}"; image['src'] = img_url
#     for link in body.select("a"):
#         a_href = link['href']
#         if a_href[0:3] == "../":
#             new_link = a_href[2:]; new_href = f"http://deathcamps.org/{new_link}"; link['href'] = new_href
#         if a_href[0:4] == "pic/":
#             new_href = f"http://deathcamps.org/{topic}/{a_href}"; link['href'] = new_href
#         if " " in a_href:
#             a_href.replace(" ", "%20"); link['href'] = new_href
#         if "http://" not in a_href:
#             new_href = f"http://deathcamps.org/{topic}/{a_href}"; link['href'] = new_href
#     results = soup.findAll("table", {"summary" : "blind"})
#     for result in results[0:7]:
#         txt = result.get_text().strip()
#         if txt == '' or 'ARC Main Page' in txt:
#             result.decompose()
#     return (title, body)

# # get_html_body("http://deathcamps.org/occupation/bialystok%20ghetto.html", "occupation")




# dict_of_topics = {"belzec": belzec, "sobibor": sobibor, "treblinka": treblinka, "reinhard": aktion_reinhard, "gas_chambers": gas_chambers, "lublin": lublin, "occupation": occupation, "euthanasia": euthanasia, "sabba": risiera_di_san_sabba}
# for topic, arr in dict_of_topics.items():
# 	for el in arr:
# 		link = el['href']; language = "English"; lang_keys = {"_de": "German", "_it": "Italian", "_nl": "Dutch", "_fr": "French", "_es": "Spanish", "_dk": "Danish", "_pl": "Polish"}
# 		for k, v in lang_keys.items():
# 			if f"{k}.html" in link:
# 				language = v
# 				break

# 		try:
# 			(t, txt) = get_html_body(link, topic); assignment_type = "Text"; topics_dict = {"belzec": "Belzec", "sobibor": "Sobibor", "treblinka": "Treblinka", "reinhard": "Aktion Reinhard", "gas_chambers": "Gas Chambers", "lublin": "Lublin", "occupation": "Occupation", "euthanasia": "Euthanasia", "sabba": "Risiera di San Sabba"}
# 			for k, v in topics_dict.items():
# 				if topic == k:
# 					sm = Submodule.objects.filter(title=v)[0]
# 					break
# 			a = Assignment(title=t, assignment_type=assignment_type, text=str(txt), submodule=sm, language=language); a.save()
# 		except:
# 			pass

# a = Assignment(title='t', submodule=Submodule.objects.first(), language='English', assignment_type="Text", text='t')