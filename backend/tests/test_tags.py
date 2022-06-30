import pytest


class TestTagsApi:
    url_tags = '/api/tags/'

    @pytest.mark.django_db(transaction=True)
    def test_tags_list(self, client, tag):
        url = self.url_tags
        response = client.get(url)
        code_expected = 200
        assert response.status_code == code_expected, (
            f'Убедитесь, что при запросе от неавторизированного пользователя '
            f'`{url}` без параметров, возвращается код {code_expected}'
        )

        response_data = response.json()
        assert type(response_data) == list, (
            f'Проверьте, что при GET запросе на `{url}`, '
            'возвращается список без пагинации'
        )
        expected_fields = ('id', 'name', 'color', 'slug')
        for field in expected_fields:
            assert field in response_data[0], (
                f'Проверьте, что при GET запросе на `{url}`, '
                f'объект списка содержит {field}'
            )

    @pytest.mark.django_db(transaction=True)
    def test_tag(self, client, tag):
        url = f'{self.url_tags}{tag.id}/'
        response = client.get(url)
        code_expected = 200
        assert response.status_code == code_expected, (
            f'Убедитесь, что при запросе от неавторизированного пользователя '
            f'`{url}` без параметров, возвращается код {code_expected}'
        )

        response_data = response.json()
        expected_fields = ('id', 'name', 'color', 'slug')
        for field in expected_fields:
            assert field in response_data, (
                f'Проверьте, что при GET запросе на `{url}`, '
                f'объект списка содержит {field}'
            )
