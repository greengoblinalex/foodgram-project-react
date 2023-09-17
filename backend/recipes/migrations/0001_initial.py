# Generated by Django 4.2.3 on 2023-09-17 22:50

import colorfield.fields
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True,
                 max_length=256, verbose_name='Название')),
                ('measurement_unit', models.CharField(
                    choices=[('ст. л.', 'Столовая ложка'),
                             ('ч. л.', 'Чайная ложка'),
                             ('г', 'Грамм'),
                             ('кг', 'Килограмм'),
                             ('мл', 'Милиграмм'),
                             ('л', 'Литр'),
                             ('стакан', 'Стакан'),
                             ('по вкусу', 'По вкусу'),
                             ('шт.', 'Штук'),
                             ('капля', 'Капля'),
                             ('звездочка', 'Звездочка'),
                             ('щепотка', 'Щепотка'),
                             ('горсть', 'Горсть'),
                             ('кусок', 'Кусок'),
                             ('пакет', 'Пакет'),
                             ('пучок', 'Пучок'),
                             ('долька', 'Долька'),
                             ('стручок', 'Стручок'),
                             ('стебель', 'Стебель'),
                             ('бутылка', 'Бутылка'),
                             ('зубчик', 'Зубчик'),
                             ('веточка', 'Веточка'),
                             ('банка', 'Банка'),
                             ('тушка', 'Тушка'),
                             ('батон', 'Батон'),
                             ('пачка', 'Пачка'),
                             ('лист', 'Лист'),
                             ('пласт', 'Пласт'),
                             ('упаковка', 'Упаковка')],
                    default='ст. л.',
                    max_length=9,
                    verbose_name='Ед. Измерения')),
            ],
            options={
                'unique_together': {('name', 'measurement_unit')},
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('is_in_shopping_cart', models.BooleanField(
                    default=False, verbose_name='В корзине')),
                ('name', models.CharField(
                    max_length=256, verbose_name='Название')),
                ('image', models.ImageField(null=True,
                 upload_to='media/recipes/images/', verbose_name='Картинка')),
                ('text', models.TextField(blank=True, default='',
                 null=True, verbose_name='Описание')),
                ('cooking_time', models.PositiveSmallIntegerField(
                    verbose_name='Время приготовления')),
                ('author', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                 related_name='recipes',
                 to=settings.AUTH_USER_MODEL,
                 verbose_name='Автор')),
                ('favorited_by', models.ManyToManyField(
                    blank=True, related_name='favorite_recipes',
                 to=settings.AUTH_USER_MODEL,
                 verbose_name='Избрано пользователями')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256,
                 unique=True, verbose_name='Название')),
                ('color', colorfield.fields.ColorField(default='#FF0000',
                 image_field=None, max_length=25,
                 samples=None, verbose_name='HEX цвет')),
                ('slug', models.SlugField(unique=True, verbose_name='Слаг')),
            ],
        ),
        migrations.CreateModel(
            name='RecipeIngredientAmount',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(verbose_name='Количество')),
                ('ingredient', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                 related_name='recipe_ingredient_amounts',
                 to='recipes.ingredient',
                 verbose_name='Ингредиент')),
                ('recipe', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                 related_name='recipe_ingredient_amounts',
                 to='recipes.recipe',
                 verbose_name='Рецепт')),
            ],
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(
                through='recipes.RecipeIngredientAmount',
                to='recipes.ingredient',
                verbose_name='Ингредиенты'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='shopping_cart',
            field=models.ManyToManyField(
                blank=True,
                related_name='shopping_cart_recipes',
                to=settings.AUTH_USER_MODEL,
                verbose_name='В корзине у пользователей'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(
                related_name='recipes', to='recipes.tag', verbose_name='Тэги'),
        ),
        migrations.AddConstraint(
            model_name='recipe',
            constraint=models.UniqueConstraint(
                fields=('id', 'favorited_by'), name='unique_favorite_recipe'),
        ),
        migrations.AddConstraint(
            model_name='recipe',
            constraint=models.UniqueConstraint(
                fields=('id', 'shopping_cart'),
                name='unique_shopping_cart_recipe'),
        ),
    ]
