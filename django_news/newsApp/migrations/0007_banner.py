# Generated by Django 4.0.3 on 2023-09-20 07:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('newsApp', '0006_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('banner', models.ImageField(upload_to='banner_home')),
                ('post', models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, to='newsApp.post')),
            ],
        ),
    ]