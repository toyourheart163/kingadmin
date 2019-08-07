# Generated by Django 2.2.4 on 2019-08-07 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0006_auto_20190803_2333'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='customer',
        ),
        migrations.AddField(
            model_name='student',
            name='customer',
            field=models.ManyToManyField(to='crm.CustomerInfo', verbose_name='客户'),
        ),
    ]