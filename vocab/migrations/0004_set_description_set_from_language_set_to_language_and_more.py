# Generated by Django 4.0.6 on 2022-08-09 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vocab', '0003_alter_definition_language_pair'),
    ]

    operations = [
        migrations.AddField(
            model_name='set',
            name='description',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name='set',
            name='from_language',
            field=models.CharField(blank=True, choices=[('af', 'Afrikaans'), ('sq', 'Albanian'), ('am', 'Amharic'), ('ar', 'Arabic'), ('hy', 'Armenian'), ('az', 'Azerbaijani'), ('eu', 'Basque'), ('be', 'Belarusian'), ('bn', 'Bengali'), ('bs', 'Bosnian'), ('bg', 'Bulgarian'), ('ca', 'Catalan'), ('ceb', 'Cebuano'), ('ny', 'Chichewa'), ('zh-cn', 'Chinese Simplified'), ('zh-tw', 'Chinese Traditional'), ('co', 'Corsican'), ('hr', 'Croatian'), ('cs', 'Czech'), ('da', 'Danish'), ('nl', 'Dutch'), ('en', 'English'), ('eo', 'Esperanto'), ('et', 'Estonian'), ('tl', 'Filipino'), ('fi', 'Finnish'), ('fr', 'French'), ('fy', 'Frisian'), ('gl', 'Galician'), ('ka', 'Georgian'), ('de', 'German'), ('el', 'Greek'), ('gu', 'Gujarati'), ('ht', 'Haitian Creole'), ('ha', 'Hausa'), ('haw', 'Hawaiian'), ('he', 'Hebrew'), ('hi', 'Hindi'), ('hmn', 'Hmong'), ('hu', 'Hungarian'), ('is', 'Icelandic'), ('ig', 'Igbo'), ('id', 'Indonesian'), ('ga', 'Irish'), ('it', 'Italian'), ('ja', 'Japanese'), ('jw', 'Javanese'), ('kn', 'Kannada'), ('kk', 'Kazakh'), ('km', 'Khmer'), ('ko', 'Korean'), ('ku', 'Kurdish Kurmanji'), ('ky', 'Kyrgyz'), ('lo', 'Lao'), ('la', 'Latin'), ('lv', 'Latvian'), ('lt', 'Lithuanian'), ('lb', 'Luxembourgish'), ('mk', 'Macedonian'), ('mg', 'Malagasy'), ('ms', 'Malay'), ('ml', 'Malayalam'), ('mt', 'Maltese'), ('mi', 'Maori'), ('mr', 'Marathi'), ('mn', 'Mongolian'), ('my', 'Myanmar Burmese'), ('ne', 'Nepali'), ('no', 'Norwegian'), ('or', 'Odia'), ('ps', 'Pashto'), ('fa', 'Persian'), ('pl', 'Polish'), ('pt', 'Portuguese'), ('pa', 'Punjabi'), ('ro', 'Romanian'), ('ru', 'Russian'), ('sm', 'Samoan'), ('gd', 'Scots Gaelic'), ('sr', 'Serbian'), ('st', 'Sesotho'), ('sn', 'Shona'), ('sd', 'Sindhi'), ('si', 'Sinhala'), ('sk', 'Slovak'), ('sl', 'Slovenian'), ('so', 'Somali'), ('es', 'Spanish'), ('su', 'Sundanese'), ('sw', 'Swahili'), ('sv', 'Swedish'), ('tg', 'Tajik'), ('ta', 'Tamil'), ('te', 'Telugu'), ('th', 'Thai'), ('tr', 'Turkish'), ('uk', 'Ukrainian'), ('ur', 'Urdu'), ('ug', 'Uyghur'), ('uz', 'Uzbek'), ('vi', 'Vietnamese'), ('cy', 'Welsh'), ('xh', 'Xhosa'), ('yi', 'Yiddish'), ('yo', 'Yoruba'), ('zu', 'Zulu'), ('ee', 'Et')], default='en', max_length=64),
        ),
        migrations.AddField(
            model_name='set',
            name='to_language',
            field=models.CharField(blank=True, choices=[('af', 'Afrikaans'), ('sq', 'Albanian'), ('am', 'Amharic'), ('ar', 'Arabic'), ('hy', 'Armenian'), ('az', 'Azerbaijani'), ('eu', 'Basque'), ('be', 'Belarusian'), ('bn', 'Bengali'), ('bs', 'Bosnian'), ('bg', 'Bulgarian'), ('ca', 'Catalan'), ('ceb', 'Cebuano'), ('ny', 'Chichewa'), ('zh-cn', 'Chinese Simplified'), ('zh-tw', 'Chinese Traditional'), ('co', 'Corsican'), ('hr', 'Croatian'), ('cs', 'Czech'), ('da', 'Danish'), ('nl', 'Dutch'), ('en', 'English'), ('eo', 'Esperanto'), ('et', 'Estonian'), ('tl', 'Filipino'), ('fi', 'Finnish'), ('fr', 'French'), ('fy', 'Frisian'), ('gl', 'Galician'), ('ka', 'Georgian'), ('de', 'German'), ('el', 'Greek'), ('gu', 'Gujarati'), ('ht', 'Haitian Creole'), ('ha', 'Hausa'), ('haw', 'Hawaiian'), ('he', 'Hebrew'), ('hi', 'Hindi'), ('hmn', 'Hmong'), ('hu', 'Hungarian'), ('is', 'Icelandic'), ('ig', 'Igbo'), ('id', 'Indonesian'), ('ga', 'Irish'), ('it', 'Italian'), ('ja', 'Japanese'), ('jw', 'Javanese'), ('kn', 'Kannada'), ('kk', 'Kazakh'), ('km', 'Khmer'), ('ko', 'Korean'), ('ku', 'Kurdish Kurmanji'), ('ky', 'Kyrgyz'), ('lo', 'Lao'), ('la', 'Latin'), ('lv', 'Latvian'), ('lt', 'Lithuanian'), ('lb', 'Luxembourgish'), ('mk', 'Macedonian'), ('mg', 'Malagasy'), ('ms', 'Malay'), ('ml', 'Malayalam'), ('mt', 'Maltese'), ('mi', 'Maori'), ('mr', 'Marathi'), ('mn', 'Mongolian'), ('my', 'Myanmar Burmese'), ('ne', 'Nepali'), ('no', 'Norwegian'), ('or', 'Odia'), ('ps', 'Pashto'), ('fa', 'Persian'), ('pl', 'Polish'), ('pt', 'Portuguese'), ('pa', 'Punjabi'), ('ro', 'Romanian'), ('ru', 'Russian'), ('sm', 'Samoan'), ('gd', 'Scots Gaelic'), ('sr', 'Serbian'), ('st', 'Sesotho'), ('sn', 'Shona'), ('sd', 'Sindhi'), ('si', 'Sinhala'), ('sk', 'Slovak'), ('sl', 'Slovenian'), ('so', 'Somali'), ('es', 'Spanish'), ('su', 'Sundanese'), ('sw', 'Swahili'), ('sv', 'Swedish'), ('tg', 'Tajik'), ('ta', 'Tamil'), ('te', 'Telugu'), ('th', 'Thai'), ('tr', 'Turkish'), ('uk', 'Ukrainian'), ('ur', 'Urdu'), ('ug', 'Uyghur'), ('uz', 'Uzbek'), ('vi', 'Vietnamese'), ('cy', 'Welsh'), ('xh', 'Xhosa'), ('yi', 'Yiddish'), ('yo', 'Yoruba'), ('zu', 'Zulu'), ('ee', 'Et')], default='en', max_length=64),
        ),
        migrations.AlterField(
            model_name='set',
            name='title',
            field=models.CharField(max_length=64),
        ),
    ]
