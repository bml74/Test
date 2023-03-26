"""

# OPENAI 

import os
import openai

openai.api_key = "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"

prompt = "Father Patrick Desbois is a Catholic priest and President of Yahad – In Unum. He also serves as director of the French Episcopal Committee for Relations with Judaism and is an advisor to the Vatican. As the grandson of a WWII French soldier held captive in a German camp in Rawa Ruska (Ukraine), his unexpected encounter with eyewitnesses of the local 1943 massacre of Jews turned a visit to Western Ukraine in 2003 into the starting point for finding witnesses and documenting mass shootings of Jews and Roma all over the country, and subsequently also beyond Ukraine. Father Desbois’ work has been widely received and recognized; his book “Holocaust by Bullets” (2008) received the National Jewish Book Award in the United States."

response = openai.Completion.create(
    model="text-davinci-002",
    prompt="Summarize this for a second-grade student:\n\n"+prompt,
    temperature=0.7,
    max_tokens=64,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0
)
print(response['choices'][0]['text'])"""