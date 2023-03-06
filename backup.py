import os
from datetime import datetime
from VkClient import VkClient
from YaDiskClient import YaDiskClient
from tqdm import tqdm
import json
import requests
import logging

logging.basicConfig(level=logging.INFO, filename='backup.log', filemode='a', format="%(asctime)s %(levelname)s %(message)s")

def _get_token(client:str):
    """
    Функция возвращает токен ВК, ЯндексаДиска или GoogleDrive.
    Параметр client может принимать значения vk, ya, google.
    """
    current = os.getcwd()
    file_vk_token = 'vk_token.txt'
    file_ya_token = 'ya_token.txt'
    file_google_token = 'google_token.txt'
    full_path_vk_token = os.path.join(current, file_vk_token)
    full_path_ya_token = os.path.join(current, file_ya_token)
    full_path_google_token = os.path.join(current, file_google_token)

    if client == 'vk':
        with open(full_path_vk_token, 'r') as vk_token_file:
            return vk_token_file.read().strip()
    
    elif client == 'ya':
        with open(full_path_ya_token, 'r') as ya_token_file:
            return ya_token_file.read().strip()
    
    elif client == 'google':
        with open(full_path_google_token, 'r') as google_token_file:
            return google_token_file.read().strip()
    else:
        logging.critical(msg='Token not received.')
        return

def ya_disk_client(vk_owner_id: int, photos: list):
    """
    Функция выполняет резервное копирование фотографий пользователя ВКонтакте в хранилище ЯндексДиск.
    Параметр vk_owner_id принимает идентификатор (owner_id) пользователя ВКонтакте.
    """

    ya = YaDiskClient(ya_token=_get_token('ya'))
    logging.info(msg='Yandex token received.')

    # На ЯДиске создаем папку с названием netology_backup.
    # Если папка с таким названием уже существует, то используем её как корневую для бэкапа.
    root_folder = 'netology_backup'
    root_folder_status = ya.get_status_resources(disk_resources_path=root_folder)

    if root_folder_status == 404:
        ya.create_folder(disk_folder_path=root_folder)
        logging.info(msg=f'The folder {root_folder} created.')
    
    logging.info(msg=f'The folder {root_folder} exists.')

    # На ЯДиске создаем папку с названием vk_owner_id.
    # Если папка с таким названием уже существует, то всё содержимое перенести в папку netology/archive/vk_owner_id.
    disk_resources_path = f'{root_folder}/{vk_owner_id}'
    path_status = ya.get_status_resources(disk_resources_path=disk_resources_path)

    if path_status == 404:
        ya.create_folder(disk_folder_path=disk_resources_path)
        logging.info(msg=f'The folder {disk_resources_path} created.')

    elif path_status == 200:
        logging.info(msg=f'The folder {disk_resources_path} is out of date.')
        archive_path = f'{root_folder}/archive/{vk_owner_id}'

        ya.move_to_archive(from_path=disk_resources_path, to_path=archive_path)
        logging.info(msg=f'The folder {disk_resources_path} has been archived.')

        ya.create_folder(disk_folder_path=disk_resources_path)
        logging.info(msg=f'The current folder {disk_resources_path} has been created.')
    
    # создаем переменную json_file.
    json_file = {
        'id': vk_owner_id,
        'photos': []
    }

    # присваиваем имя файлу json.
    json_file_path = disk_resources_path + f'/{vk_owner_id}.json.txt'
    logging.debug(msg='Named json file.')

    # в переменную photos_list сохраняем url фотографий пользователя
    if not len(photos):
        ya.upload_file(disk_file_path=json_file_path, file=json.dumps(obj=json_file, ensure_ascii=False, indent=2))
        logging.info(msg='Photos are missing. JSON file loaded to YandexDisk.')
        return print(f'У пользователя {vk_owner_id} отсутствуют фотографии профиля.\n')

    # перебираем фотографии
    for photo_info in tqdm(photos, ncols=80, desc=f'In progress user {vk_owner_id}: '):
        photo_name = f"{photo_info['likes']['count']}.jpg"
        logging.debug(msg='Named photo.')

        # если фото с названием photo_name уже есть в папке disk_resources_path, то присваиваем новое название likes+date
        photo_status = ya.get_status_resources(disk_resources_path=disk_resources_path + photo_name)
        if photo_status == 200:
            logging.info(msg=f'Photo titled {photo_name} already exists.')
            date = datetime.fromtimestamp(photo_info['date']).strftime('%Y-%m-%d %H:%M:%S')
            photo_name = f"{photo_info['likes']['count']}_{date}.jpg"
            logging.info(msg=f'The photo has been given a new name {photo_name}.')
        
        # выбираем фотографию с максимальным размером и присваиваем путь до неё.
        photo_url = photo_info['sizes'][-1]['url']
        logging.debug(msg=f'{photo_name} photo URL received.')
        
        # в json file добавляем словарик с данными о фотографии.
        json_file['photos'].append({
            'file_name': photo_name,
            'size': photo_info['sizes'][-1]['type']
        })
        logging.info(msg=f'Added information about photo {photo_name} to JSON file.')

        # сохраняем фото в переменную photo_bytes для последующей загрузки на ЯДиск.
        photo_bytes = requests.get(url=photo_url).content
        logging.debug(msg='Photo saved to variable photo_bytes.')

        # загружаем фото в папку на ЯДиске.
        upload_photo_path = disk_resources_path + f'/{photo_name}'
        ya.upload_file(disk_file_path=upload_photo_path, file=photo_bytes)
        logging.info(msg=f'Photo {photo_name} uploaded to YandexDisk.')
    
    
    # загружаем json_file в папку на ЯДиске.
    ya.upload_file(disk_file_path=json_file_path, file=json.dumps(obj=json_file, ensure_ascii=False, indent=2))
    logging.info(msg=f'JSON file {json_file_path} loaded to YandexDisk.')
    logging.info(msg='Backup is performed in YandexDisk.')
    
    return print(f'Резервное копирование выполнено.\nФотографии пользователя {vk_owner_id} загружены на ЯндексДиск.\nПуть: {disk_resources_path}\n')

def google_drive_client():
    """
    В РАБОТЕ.
    """


    logging.info(msg='Google token received.')




    logging.info(msg='Backup is performed in GoogleDrive.')
    pass

def vk_backup(vk_user, backup_client):
    """
    Функция выполняет резервное копирование фотографий пользователя ВКонтакте в хранилище ЯндексДиск или GoogleDrive.
    Параметр vk_user может принимать как идентификатор (owner_id) пользователя, так и короткое имя (screen_name) пользователя.
    Параметр backup_client принимает 'ya' или 'google'.
    """
    
    vk = VkClient(vk_token=_get_token('vk'), version='5.131')
    logging.info(msg='VK token received.')

    # Получаем ID пользователя вк на случай, если в параметр vk_user передано короткое имя (screen_name) пользователя.
    vk_owner_id = vk.get_users(vk_user)[0]['id']
    logging.info(msg='Parameter owner_id received.')

    # в переменную photos_list сохраняем url фотографий пользователя
    photos_list = vk.get_profile_photos(user_id=vk_owner_id, rev='1')
    logging.info(msg='Photo list compiled.')


    if backup_client == 'ya':
        return ya_disk_client(vk_owner_id=vk_owner_id, photos=photos_list)
    # elif backup_client == 'google:
        # google_drive_client()
    else:
        logging.critical(msg='ValueError backup client.')
        return ValueError('Параметр backup_client принимает только ya или google.')


if __name__ == '__main__':
    vk_backup(vk_user='', backup_client='ya')  # 2 фотки
    vk_backup(vk_user='', backup_client='ya')  # 5 и более фоток
    vk_backup(vk_user='', backup_client='ya')  # Нет фоток
    vk_backup(vk_user='', backup_client='ya')  # 5 и более фоток