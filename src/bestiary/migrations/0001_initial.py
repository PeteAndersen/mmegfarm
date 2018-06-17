# Generated by Django 2.0.6 on 2018-06-17 04:24

import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Creature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_id', models.CharField(db_index=True, max_length=20)),
                ('name', models.CharField(max_length=30)),
                ('playable', models.BooleanField()),
                ('summonable', models.BooleanField()),
                ('inMenagerie', models.BooleanField()),
                ('rank', models.IntegerField()),
                ('archetype', models.CharField(choices=[('attacker', 'Attacker'), ('defender', 'Defender'), ('saboteur', 'Saboteur'), ('support', 'Support')], max_length=15)),
                ('element', models.CharField(choices=[('fire', 'Fire'), ('water', 'Water'), ('air', 'Air'), ('earth', 'Earth'), ('light', 'Light'), ('dark', 'Dark')], max_length=10)),
                ('group', models.CharField(choices=[('bad', 'Bad'), ('avg', 'Average'), ('good', 'Good'), ('veryGood', 'Very Good'), ('outstanding', 'Outstanding')], max_length=15)),
                ('subgroup', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20), blank=True, size=None)),
                ('lore', models.TextField(blank=True, default='')),
                ('creatureType', models.CharField(max_length=50)),
                ('trackingName', models.CharField(max_length=50)),
                ('hp', models.IntegerField()),
                ('attack', models.IntegerField()),
                ('defense', models.IntegerField()),
                ('criticalChance', models.IntegerField()),
                ('criticalDamage', models.IntegerField()),
                ('accuracy', models.FloatField()),
                ('resistance', models.FloatField()),
                ('initialSpeed', models.IntegerField()),
                ('speed', models.FloatField()),
            ],
            options={
                'ordering': ['rank', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Spell',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField()),
                ('game_id', models.CharField(max_length=35)),
                ('title', models.CharField(max_length=80)),
                ('description', models.TextField()),
                ('image', models.CharField(max_length=50)),
                ('type_image', models.CharField(default='', max_length=50)),
                ('turns', models.IntegerField(blank=True, null=True)),
                ('passive', models.BooleanField(default=False)),
                ('passiveTrigger', models.CharField(blank=True, default='', max_length=30)),
                ('creature', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bestiary.Creature')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='SpellEffect',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField()),
                ('effect', models.CharField(max_length=30)),
                ('target', models.CharField(choices=[('one', 'One'), ('all', 'All'), ('self', 'Self'), ('one_minus_self', 'One (excluding self)'), ('all_minus_self', 'All (excluding self)'), ('all_minus_one', 'All (minus one)'), ('random_dead', 'Random Dead')], max_length=20)),
                ('params', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={})),
                ('condition', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('attackCriticalLaunched', 'Critical Hit'), ('targetHasDebuff', 'Target Has Debuff'), ('selfHpAbove', 'Own HP Above Threshold'), ('targetHpEquals', 'Target HP Equals Threshold'), ('targetHpAbove', 'Target HP Above Threshold'), ('targetHpBelow', 'Target HP Below Threshold'), ('link', 'Link')], default='', max_length=30), blank=True, size=None)),
                ('permanent', models.NullBooleanField()),
                ('spell', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bestiary.Spell')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='SpellUpgrade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField()),
                ('game_id', models.CharField(max_length=50)),
                ('amount', models.FloatField()),
                ('is_percentage', models.BooleanField()),
                ('attribute', models.CharField(max_length=10)),
                ('description', models.CharField(max_length=150)),
                ('spell', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bestiary.Spell')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='spellupgrade',
            unique_together={('spell', 'order')},
        ),
        migrations.AlterUniqueTogether(
            name='spelleffect',
            unique_together={('spell', 'order')},
        ),
        migrations.AlterUniqueTogether(
            name='spell',
            unique_together={('creature', 'order')},
        ),
    ]
