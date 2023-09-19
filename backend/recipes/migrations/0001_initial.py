import colorfield.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
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
                    default='ст. л.', max_length=9,
                    verbose_name='Ед. Измерения')),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(
                    max_length=256, verbose_name='Название')),
                ('image', models.ImageField(null=True,
                 upload_to='media/recipes/images/', verbose_name='Картинка')),
                ('text', models.TextField(blank=True, default='',
                 null=True, verbose_name='Описание')),
                ('cooking_time', models.PositiveSmallIntegerField(
                    verbose_name='Время приготовления')),
            ],
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
                 to='recipes.ingredient', verbose_name='Ингредиент')),
                ('recipe', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                 related_name='recipe_ingredient_amounts',
                 to='recipes.recipe', verbose_name='Рецепт')),
            ],
        ),
    ]
