# Generated by Django 2.0.6 on 2018-07-15 04:17

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
            name='Boss',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_id', models.CharField(db_index=True, max_length=20)),
                ('name', models.CharField(max_length=30)),
                ('playable', models.BooleanField(default=False)),
                ('trackingName', models.CharField(blank=True, max_length=50, null=True)),
                ('rank', models.IntegerField()),
                ('archetype', models.CharField(choices=[('attacker', 'Attacker'), ('defender', 'Defender'), ('saboteur', 'Saboteur'), ('support', 'Support')], max_length=15)),
                ('element', models.CharField(choices=[('fire', 'Fire'), ('water', 'Water'), ('air', 'Air'), ('earth', 'Earth'), ('light', 'Light'), ('dark', 'Dark')], max_length=10)),
                ('hp', models.IntegerField()),
                ('attack', models.IntegerField()),
                ('defense', models.IntegerField()),
                ('criticalChance', models.IntegerField()),
                ('criticalDamage', models.IntegerField()),
                ('accuracy', models.FloatField()),
                ('resistance', models.FloatField()),
                ('initialSpeed', models.IntegerField()),
                ('speed', models.FloatField()),
                ('order', models.IntegerField()),
                ('level', models.IntegerField()),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='BossSpell',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slot', models.IntegerField(default=1)),
                ('game_id', models.CharField(max_length=35)),
                ('title', models.CharField(max_length=80)),
                ('description', models.TextField()),
                ('image', models.CharField(max_length=50)),
                ('type_image', models.CharField(default='', max_length=50)),
                ('turns', models.IntegerField(blank=True, null=True)),
                ('passive', models.BooleanField(default=False)),
                ('passiveTrigger', models.CharField(blank=True, default='', max_length=30)),
                ('creature', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bestiary.Boss')),
            ],
            options={
                'ordering': ['slot'],
            },
        ),
        migrations.CreateModel(
            name='BossSpellEffect',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField()),
                ('effect', models.CharField(max_length=30)),
                ('target', models.CharField(choices=[('one', 'One'), ('all', 'All'), ('self', 'Self'), ('one_minus_self', 'One (excluding self)'), ('all_minus_self', 'All (excluding self)'), ('all_minus_one', 'All (minus one)'), ('random_dead', 'Random Dead')], max_length=20)),
                ('params', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={})),
                ('condition', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('attackCriticalLaunched', 'Critical Hit'), ('targetHasDebuff', 'Target Has Debuff'), ('selfHpAbove', 'Own HP Above Threshold'), ('targetHpEquals', 'Target HP Equals Threshold'), ('targetHpAbove', 'Target HP Above Threshold'), ('targetHpBelow', 'Target HP Below Threshold'), ('link', 'Link')], default='', max_length=30), blank=True, default=[], size=None)),
                ('permanent', models.NullBooleanField()),
                ('probability', models.FloatField(blank=True, null=True)),
                ('spell', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bestiary.BossSpell')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Creature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_id', models.CharField(db_index=True, max_length=20)),
                ('name', models.CharField(max_length=30)),
                ('playable', models.BooleanField(default=False)),
                ('trackingName', models.CharField(blank=True, max_length=50, null=True)),
                ('rank', models.IntegerField()),
                ('archetype', models.CharField(choices=[('attacker', 'Attacker'), ('defender', 'Defender'), ('saboteur', 'Saboteur'), ('support', 'Support')], max_length=15)),
                ('element', models.CharField(choices=[('fire', 'Fire'), ('water', 'Water'), ('air', 'Air'), ('earth', 'Earth'), ('light', 'Light'), ('dark', 'Dark')], max_length=10)),
                ('hp', models.IntegerField()),
                ('attack', models.IntegerField()),
                ('defense', models.IntegerField()),
                ('criticalChance', models.IntegerField()),
                ('criticalDamage', models.IntegerField()),
                ('accuracy', models.FloatField()),
                ('resistance', models.FloatField()),
                ('initialSpeed', models.IntegerField()),
                ('speed', models.FloatField()),
                ('group', models.CharField(choices=[('bad', 'Bad'), ('avg', 'Average'), ('good', 'Good'), ('veryGood', 'Very Good'), ('outstanding', 'Outstanding')], max_length=15)),
                ('subgroup', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20), blank=True, size=None)),
                ('inMenagerie', models.BooleanField()),
                ('summonable', models.BooleanField(default=False)),
                ('lore', models.TextField(blank=True, default='')),
                ('creatureType', models.CharField(max_length=50)),
                ('evoHp', models.IntegerField(default=0)),
                ('evoAttack', models.IntegerField(default=0)),
                ('evoDefense', models.IntegerField(default=0)),
                ('evoCriticalChance', models.IntegerField(default=0)),
                ('maxLvlHp', models.IntegerField(blank=True, null=True)),
                ('maxLvlAttack', models.IntegerField(blank=True, null=True)),
                ('maxLvlDefense', models.IntegerField(blank=True, null=True)),
                ('slug', models.SlugField(blank=True, max_length=100, null=True)),
                ('evolvesFrom', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='evolvesTo', to='bestiary.Creature')),
            ],
            options={
                'ordering': ['rank', 'name'],
            },
        ),
        migrations.CreateModel(
            name='DropGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instant', models.BooleanField(default=False, help_text='Drops when running with Instant Tickets')),
                ('xp', models.IntegerField()),
                ('crystals', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Drops',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('probability', models.FloatField(help_text='Chance of reward')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bestiary.DropGroup')),
            ],
        ),
        migrations.CreateModel(
            name='Dungeon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_id', models.CharField(db_index=True, max_length=50)),
                ('name', models.CharField(max_length=100)),
                ('group', models.CharField(choices=[('GroupElements', 'Elemental Dungeon'), ('GroupGlyphs', 'Glyph Dungeon'), ('GroupTwinTowers', 'Tower of Trials'), ('GroupEventDungeon', 'Event Dungeon'), ('ScenarioDungeon', 'Shattered Islands Scenario')], max_length=25)),
                ('always_available', models.BooleanField(default=True)),
                ('days_available', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=[], size=None)),
                ('months_available', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=[], size=None)),
            ],
        ),
        migrations.CreateModel(
            name='Enemy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_id', models.CharField(db_index=True, max_length=20)),
                ('name', models.CharField(max_length=30)),
                ('playable', models.BooleanField(default=False)),
                ('trackingName', models.CharField(blank=True, max_length=50, null=True)),
                ('rank', models.IntegerField()),
                ('archetype', models.CharField(choices=[('attacker', 'Attacker'), ('defender', 'Defender'), ('saboteur', 'Saboteur'), ('support', 'Support')], max_length=15)),
                ('element', models.CharField(choices=[('fire', 'Fire'), ('water', 'Water'), ('air', 'Air'), ('earth', 'Earth'), ('light', 'Light'), ('dark', 'Dark')], max_length=10)),
                ('hp', models.IntegerField()),
                ('attack', models.IntegerField()),
                ('defense', models.IntegerField()),
                ('criticalChance', models.IntegerField()),
                ('criticalDamage', models.IntegerField()),
                ('accuracy', models.FloatField()),
                ('resistance', models.FloatField()),
                ('initialSpeed', models.IntegerField()),
                ('speed', models.FloatField()),
                ('order', models.IntegerField(default=0)),
                ('miniboss', models.BooleanField(default=False)),
                ('level', models.IntegerField()),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_id', models.CharField(db_index=True, max_length=50)),
                ('order', models.IntegerField()),
                ('difficulty', models.IntegerField(blank=True, choices=[(1, 'Normal'), (2, 'Advanced'), (3, 'Nightmare')], null=True)),
                ('slots', models.IntegerField(help_text='Creatures allowed to bring')),
                ('energy_cost', models.IntegerField()),
                ('dungeon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bestiary.Dungeon')),
            ],
            options={
                'ordering': ['difficulty', 'order'],
            },
        ),
        migrations.CreateModel(
            name='Spell',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slot', models.IntegerField(default=1)),
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
                'ordering': ['slot'],
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
                ('condition', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('attackCriticalLaunched', 'Critical Hit'), ('targetHasDebuff', 'Target Has Debuff'), ('selfHpAbove', 'Own HP Above Threshold'), ('targetHpEquals', 'Target HP Equals Threshold'), ('targetHpAbove', 'Target HP Above Threshold'), ('targetHpBelow', 'Target HP Below Threshold'), ('link', 'Link')], default='', max_length=30), blank=True, default=[], size=None)),
                ('permanent', models.NullBooleanField()),
                ('probability', models.FloatField(blank=True, null=True)),
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
        migrations.CreateModel(
            name='Wave',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_id', models.CharField(db_index=True, max_length=50)),
                ('order', models.IntegerField(default=0)),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bestiary.Level')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.AddField(
            model_name='enemy',
            name='wave',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bestiary.Wave'),
        ),
        migrations.AddField(
            model_name='dropgroup',
            name='level',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bestiary.Level'),
        ),
        migrations.AddField(
            model_name='boss',
            name='wave',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bestiary.Wave'),
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
            unique_together={('creature', 'slot')},
        ),
        migrations.AlterUniqueTogether(
            name='bossspelleffect',
            unique_together={('spell', 'order')},
        ),
        migrations.AlterUniqueTogether(
            name='bossspell',
            unique_together={('creature', 'slot')},
        ),
    ]
