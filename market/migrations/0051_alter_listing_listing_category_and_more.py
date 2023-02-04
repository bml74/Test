# Generated by Django 4.0.6 on 2023-02-04 02:08

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0050_alter_listing_listing_category_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='listing_category',
            field=models.CharField(choices=[('Consulting', 'Consulting'), ('Tutoring - College', 'Tutoring - College'), ('Tutoring - MSB', 'Tutoring - MSB'), ('Tutoring - Computer Science', 'Tutoring - Computer Science'), ('Tutoring - SFS', 'Tutoring - SFS'), ('Tutoring - NHS', 'Tutoring - NHS'), ('Translation services', 'Translation services'), ('Programming services', 'Programming services'), ('Research', 'Research'), ('Used textbook', 'Used textbook'), ('Book', 'Book'), ('Textbook', 'Textbook'), ('Furniture', 'Furniture'), ('Electronics', 'Electronics'), ('Household appliances', 'Household appliances'), ('Sports tickets', 'Sports tickets'), ('Concert tickets', 'Concert tickets'), ('Other tickets', 'Other tickets'), ('Sports gear', 'Sports gear'), ("Men's basketball sneakers", "Men's basketball sneakers"), ("Women's basketball sneakers", "Women's basketball sneakers"), ("Men's running sneakers", "Men's running sneakers"), ("Women's running sneakers", "Women's running sneakers"), ("Other men's sneakers", "Other men's sneakers"), ("Other women's sneakers", "Other women's sneakers"), ("Men's jackets", "Men's jackets"), ("Women's jackets", "Women's jackets"), ("Men's clothing", "Men's clothing"), ("Women's clothing", "Women's clothing"), ('Video games', 'Video games'), ('Food', 'Food'), ('Gift cards', 'Gift cards'), ('Miscellaneous', 'Miscellaneous'), ('Other', 'Other')], default='Other', max_length=100),
        ),
        migrations.AlterField(
            model_name='suggesteddelivery',
            name='suggested_date_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 2, 4, 2, 8, 56, 77864, tzinfo=utc)),
        ),
    ]
