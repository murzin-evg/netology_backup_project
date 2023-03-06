import requests


class YaDiskClient:

    ya_disk_url = 'https://cloud-api.yandex.net'

    def __init__(self, ya_token) -> None:
        self.headers = {
            'Authorization': f'OAuth {ya_token}',
            'Content-Type': 'application/json'
        }

    def get_metainformations_resources(self, disk_resources_path):
        """Метод возвращает метаинформацию о ресурсе (файл, папка)"""

        full_path = self.ya_disk_url + '/v1/disk/resources'
        params = {'path': disk_resources_path}
        response = requests.get(url=full_path, params=params, headers=self.headers)

        response.raise_for_status()

        return response.json()['_embedded']['items']
    
    def get_status_resources(self, disk_resources_path):
        """Метод возвращает статус код о ресурсе (файл, папка)"""

        full_path = self.ya_disk_url + '/v1/disk/resources'
        params = {'path': disk_resources_path}
        response = requests.get(url=full_path, params=params, headers=self.headers)

        return response.status_code
    
    def create_folder(self, disk_folder_path):
        """Метод создает папку"""

        full_path = self.ya_disk_url + '/v1/disk/resources'
        params = {'path': disk_folder_path}

        response = requests.put(url=full_path, params=params, headers=self.headers)

        response.raise_for_status()

        if response.status_code == 201:
            return print(f'Папка {disk_folder_path} создана.')
        
    def move_to_archive(self, from_path, to_path):
        """
        Метод перемещает папку/файл из from_path по указанному пути to_path.
        Параметр from_path принимает путь к перемещаемому ресурсу.
        Параметр to_path принимает путь к создаваемому ресурсу.
        """
        
        if self.get_status_resources(disk_resources_path='netology/archive') == 404:
            self.create_folder(disk_folder_path='netology/archive')


        full_path = self.ya_disk_url + '/v1/disk/resources/move'
        params = {
            'from': from_path,
            'path': to_path,
            'overwrite': True
        }

        response = requests.post(url=full_path, params=params, headers=self.headers)

        response.raise_for_status()

        if response.status_code == 201:
            return print(f'Папка {from_path} перемещена в {to_path}')
        
    def delete_resource(self, disk_resources_path, permanently=False):
        """
        Метод удаляет ресурс (файл, папку).
        Параметр permanently=True позволяет удалить ресурс не помещая в корзину
        """

        full_path = self.ya_disk_url + '/v1/disk/resources'
        params = {'path': disk_resources_path, 'permanently': permanently}

        response = requests.get(url=full_path, params=params, headers=self.headers)
        
        response.raise_for_status()

        if response.status_code == 204:
            return print(f'{disk_resources_path} удален.')

    def _get_upload_url(self, disk_file_path):
        """Метод возвращает путь для загрузки файла"""

        full_path = self.ya_disk_url + '/v1/disk/resources/upload'
        params = {'path': disk_file_path, 'overwrite': True}

        response = requests.get(url=full_path, params=params, headers=self.headers)

        return response.json()

    def upload_file(self, disk_file_path, file):
        """Метод загружает файл на Яндекс.Диск"""
        href = self._get_upload_url(disk_file_path=disk_file_path).get('href', '')

        response = requests.put(url=href, data=file)
        
        response.raise_for_status()

        if response.status_code == 202:
            return print(f'Файл {disk_file_path} загружен.')