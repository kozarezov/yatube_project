# Generated by Django 2.2.6 on 2022-06-06 20:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_add_helptext'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('-pub_date',), 'verbose_name': 'Пост', 'verbose_name_plural': 'Посты'},
        ),
    ]