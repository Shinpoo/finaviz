# Generated by Django 3.2 on 2021-04-17 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0031_alter_company_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='isin',
            field=models.CharField(default='', max_length=30),
        ),
    ]