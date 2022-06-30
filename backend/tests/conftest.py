import pytest

USER_REG_DATA = {
    'username': 'TestUser',
    'password': '1234567',
    'email': 'test@test.ru',
    'first_name': 'Test',
    'last_name': 'Test'
}

USER_2_REG_DATA = {
    'username': 'TestUser2',
    'password': '1234567',
    'email': 'test2@test.ru',
    'first_name': 'Test2',
    'last_name': 'Test2'
}


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(**USER_REG_DATA)


@pytest.fixture
def user_data_me(user):
    data = USER_REG_DATA.copy()
    data.pop('password')
    data['id'] = user.id
    return data


@pytest.fixture
def user_2(django_user_model):
    return django_user_model.objects.create_user(**USER_2_REG_DATA)


@pytest.fixture
def user_2_data(user_2):
    data = USER_2_REG_DATA.copy()
    data.pop('password')
    data['id'] = user_2.id
    data['is_subscribed'] = False
    return data


@pytest.fixture
def token(user):
    from rest_framework.authtoken.models import Token
    token, created = Token.objects.get_or_create(user=user)

    return {'auth_token': token.key}


@pytest.fixture
def user_client(token):
    from rest_framework.test import APIClient

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token["auth_token"]}')
    return client


@pytest.fixture
def tag():
    from recipes.models import Tag
    return Tag.objects.create(name='Пироги', color='#123456')


@pytest.fixture
def measurement_unit():
    from recipes.models import MeasurementUnit
    return MeasurementUnit.objects.create(name='кг.')


@pytest.fixture
def ingredient(measurement_unit):
    from recipes.models import Ingredient
    return Ingredient.objects.create(
        name='Картошка',
        measurement_unit=measurement_unit
    )


@pytest.fixture
def recipe(user_2, tag, measurement_unit):
    from django.core.files.uploadedfile import SimpleUploadedFile
    from recipes.models import Recipe
    small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
    uploaded = SimpleUploadedFile(
        name='small.gif',
        content=small_gif,
        content_type='image/gif'
    )
    recipe = Recipe.objects.create(
        author=user_2,
        name='Пирог с картошкой',
        image=uploaded,
        text='text',
        cooking_time=1
    )
    field = getattr(recipe, 'tags')
    field.set((tag,))
    return recipe
