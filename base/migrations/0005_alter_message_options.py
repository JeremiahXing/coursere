# Generated by Django 4.0.4 on 2022-06-01 02:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_alter_topic_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ['-updated', '-created']},
        ),
    ]
