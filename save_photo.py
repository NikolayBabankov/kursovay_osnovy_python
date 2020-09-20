import requests, json, time, os
from operator import itemgetter
from tqdm import tqdm
import shutil
from pprint import pprint

def get_photo_dict(ident,quantity):
    api = requests.get(
    'https://api.vk.com/method/photos.get',
    params={
        'access_token': '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008',
        'v': 5.122,
        'owner_id': ident,
        'album_id':'profile',
        'count':quantity,
        'photo_sizes': 1,
        'extended': 1
    })
    return api.json()

def get_foto(ident,quantity):
    data = get_photo_dict(ident,quantity)
    os.mkdir('photos')
    info_photos = []
    print("Скачиваем фото с vk.com")
    for files in tqdm(data['response']['items']):
        sizes_sort = files['sizes']
        sorted_dict = sorted(sizes_sort, key=itemgetter('width','height'))
        file_url = sorted_dict[-1]['url']
        filename = str(files['likes']['count']) + '.jpg'
        size = str(sorted_dict[-1]['height']) + 'x' + str(sorted_dict[-1]['width']) 
        info_dict = {}
        info_dict.setdefault('filename',filename)
        info_dict.setdefault('size',size)
        info_photos.append(info_dict)
        time.sleep(0.1)
        api = requests.get(file_url)

        with open('photos/%s' % filename, 'wb') as file:
            file.write(api.content)
    
    json_foto = {}
    json_foto.setdefault('photo', info_photos)
    with open('photos.json', 'w') as f:
        json.dump(json_foto, f,sort_keys=True, indent=2)

def directory(token):
    url = 'https://cloud-api.yandex.net:443/v1/disk/resources'
    params = {'path': 'photos'}
    headers = {'Authorization': token}
    resp = requests.put(url, params=params, headers=headers)
    upload(token)
    shutil.rmtree('photos')
    os.mkdir('photos')
    os.rmdir('photos')

def upload(token):
    files = os.listdir('photos/')
    print('Загружаем фото на Яндекс Диск')
    for n in tqdm(files):
        directory = 'photos/' + n
        url = 'https://cloud-api.yandex.net:443/v1/disk/resources/upload'
        params = {'path': 'photos/' + n}
        headers = {'Authorization': token}
        resp = requests.get(url, params=params, headers=headers)
        resp2 = resp.json()
        operation_id = resp2['operation_id']
        url2 = resp2['href']
        with open(directory, 'rb') as f:
            requests.put(url2, headers=headers, data=f)
        status = ''
        while status != 'success':
            url_verif = 'https://cloud-api.yandex.net:443/v1/disk/operations/' + operation_id 
            verif_operation = requests.get(url_verif, headers=headers)
            verif_dict = (verif_operation.json())
            status = verif_dict['status']


def main():
    ident = int(input('Введите номер id: '))
    quantity = int(input('Введите количество фото: '))
    token_ya = input('Введите токен Яндекс Диск: ')
    get_foto(ident, quantity)
    directory(token_ya)
    print('Загрузка завершена успешно')

if __name__ == '__main__':
    main()
