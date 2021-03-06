# Generated by Django 3.1.3 on 2020-11-19 00:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('django_chatterbot', '0018_text_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Statement',
            fields=[
                ('statement_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='django_chatterbot.statement')),
            ],
            options={
                'abstract': False,
            },
            bases=('django_chatterbot.statement',),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('tag_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='django_chatterbot.tag')),
            ],
            options={
                'abstract': False,
            },
            bases=('django_chatterbot.tag',),
        ),
    ]
