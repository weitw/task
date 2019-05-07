# Generated by Django 2.1.5 on 2019-04-24 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Groups',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('name', models.CharField(max_length=50)),
                ('amount', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'group',
            },
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'permission',
            },
        ),
        migrations.CreateModel(
            name='Students',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=30)),
                ('password', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=50)),
                ('age', models.CharField(default='18', max_length=10)),
                ('gender', models.CharField(default='男', max_length=10)),
                ('group_id', models.IntegerField()),
                ('details', models.TextField()),
                ('permission', models.CharField(default='0', max_length=10)),
            ],
            options={
                'db_table': 'student',
            },
        ),
        migrations.CreateModel(
            name='StuTest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test_id', models.IntegerField()),
                ('stu_id', models.IntegerField()),
                ('number', models.IntegerField(null=True)),
                ('path', models.CharField(max_length=150, null=True)),
                ('filename', models.CharField(max_length=150, null=True)),
                ('count', models.IntegerField(default=1)),
                ('time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'stu_test',
            },
        ),
        migrations.CreateModel(
            name='Tests',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=100)),
                ('release_time', models.DateTimeField(auto_now_add=True)),
                ('is_download', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'Test',
            },
        ),
    ]