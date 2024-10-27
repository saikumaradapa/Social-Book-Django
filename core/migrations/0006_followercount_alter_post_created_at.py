# Generated by Django 5.1.2 on 2024-10-23 11:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_likepost_alter_post_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='FollowerCount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('follower', models.CharField(max_length=100)),
                ('user', models.CharField(max_length=100)),
            ],
        ),
        migrations.AlterField(
            model_name='post',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 23, 16, 43, 29, 73005)),
        ),
    ]
