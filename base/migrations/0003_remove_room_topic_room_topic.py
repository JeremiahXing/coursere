# Generated by Django 4.0.4 on 2022-05-27 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_topic_header_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='topic',
        ),
        migrations.AddField(
            model_name='room',
            name='topic',
            field=models.ManyToManyField(related_name='topic2room', to='base.topic'),
        ),
    ]
