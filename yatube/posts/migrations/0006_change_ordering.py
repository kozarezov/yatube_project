# Generated by Django 2.2.16 on 2022-06-22 14:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_change_list_on_turple'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-pub_date'], 'verbose_name': 'Пост', 'verbose_name_plural': 'Посты'},
        ),
    ]
