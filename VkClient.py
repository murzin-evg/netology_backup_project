import requests


class VkClient:

    vk_url = 'https://api.vk.com/method/'
    
    def __init__(self, vk_token, version) -> None:

        self.params = {
            'access_token': vk_token,
            'v': version
            }
    
    def get_users(self, user_ids: str, fields=''):
        """
        Метод возвращает информацию о пользователях.
        Параметр user_ids принимает строку с ID (screen_name) пользователей, написанные через запятую.
        Параметр fields принимает строку с дополнительными полями, написанные через запятую.
        """
        
        get_users_url = self.vk_url + 'users.get'
        get_users_params = {
            'user_ids': user_ids,
            'fields': fields
            }

        response = requests.get(url=get_users_url, params={**self.params, **get_users_params})

        return response.json()['response']
    
    def get_profile_photos(self, user_id, rev='0', count=5):
        """
        Метод возвращает список фотографий профиля.
        Параметр user_id принимает ID владельца альбома.
        Параметр rev принимает порядок сортировки: 0 - хронологический, 1 - антихронологический.
        Параметр count принимает максимальное количество фотографий профиля. По умолчанию - 5.
        """

        get_profile_photos_url = self.vk_url + 'photos.get'
        get_profile_photos_params = {
            'owner_id': user_id,
            'album_id': 'profile',
            'rev': rev,
            'photo_sizes': '0',
            'extended': '1',
            'count': count
            }

        response = requests.get(url=get_profile_photos_url, params={**self.params, **get_profile_photos_params})

        return response.json()['response']['items']