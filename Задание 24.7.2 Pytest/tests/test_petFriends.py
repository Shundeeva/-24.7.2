import requests
from requests_toolbelt import MultipartEncoder

from api import PetFriends
from settings import valid_email, valid_password, invalid_email, invalid_password
import os

pf = PetFriends()

def test_get_api_key_for_invalid_user(email=invalid_email, password=invalid_password):
    """ Проверяем что запрос api ключа с неверными данными возвращает статус 403"""

    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'key' not in result

def test_get_all_pets_with_invalid_key():
    """ Проверяем что запрос всех питомцев с неверным ключом возвращает статус 403"""

    auth_key = {'key': 'invalid_key'}
    status, result = pf.get_list_of_pets(auth_key, filter='')
    assert status == 403

def test_add_new_pet_with_invalid_key(name='Барбоскин', animal_type='двортерьер',
                                      age='4', pet_photo='images/cat1.jpg'):
    """ Проверяем что нельзя добавить питомца с неверным ключом"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    auth_key = {'key': 'invalid_key'}
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 403

def test_delete_pet_with_invalid_key():
    """ Проверяем что нельзя удалить питомца с неверным ключом"""

    auth_key = {'key': 'invalid_key'}
    pet_id = 'invalid_pet_id'
    status, result = pf.delete_pet(auth_key, pet_id)
    assert status == 403

def test_update_pet_info_with_invalid_key(name='Мурзик', animal_type='Котэ', age=5):
    """ Проверяем что нельзя обновить информацию о питомце с неверным ключом"""

    auth_key = {'key': 'invalid_key'}
    pet_id = 'invalid_pet_id'
    status, result = pf.update_pet_info(auth_key, pet_id, name, animal_type, age)
    assert status == 403

def test_add_new_pet_with_invalid_data(name='', animal_type='', age='', pet_photo='images/cat1.jpg'):
    """Проверяем что нельзя добавить питомца с некорректными данными"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Проверяем, что статус ответа не равен 200
    assert status != 200

    # Дополнительно проверяем, что результат содержит сообщение об ошибке
    assert 'error' in result or status in [400, 422]

def test_successful_update_self_pet_info_with_invalid_data(name='', animal_type='', age=''):
    """ Проверяем что нельзя обновить информацию о питомце с некорректными данными"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)
        assert status == 400
    else:
        raise Exception("There is no my pets")

def test_create_pet_simple(auth_key, name='Мурзик', animal_type='кот', age='2'):
    """Проверяем возможность создания питомца без фото"""

    data = {
        'name': name,
        'animal_type': animal_type,
        'age': age
    }
    headers = {'auth_key': auth_key['key']}
    res = requests.post(pf.base_url + 'api/create_pet_simple', headers=headers, data=data)
    status = res.status_code
    result = res.json() if res.status_code == 200 else res.text
    return status, result

def test_create_pet_simple_with_valid_data():
    """ Проверяем возможность создания питомца без фото с корректными данными"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = test_create_pet_simple(auth_key)
    assert status == 200
    assert result['name'] == 'Мурзик'

def test_add_pet_photo(auth_key, pet_id, pet_photo):
    """Проверяем возможность добавления фото к существующему питомцу"""

    data = MultipartEncoder(
        fields={
            'pet_photo': (pet_photo, open(pet_photo, 'rb'), 'image/jpeg')
        }
    )
    headers = {'auth_key': auth_key['key'], 'Content-Type': data.content_type}
    res = requests.post(pf.base_url + f'api/pets/set_photo/{pet_id}', headers=headers, data=data)
    status = res.status_code
    result = res.json() if res.status_code == 200 else res.text
    return status, result

def test_add_pet_photo_with_valid_data():
    """ Проверяем возможность добавления фото к существующему питомцу с корректными данными"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    if len(my_pets['pets']) > 0:
        pet_id = my_pets['pets'][0]['id']
        pet_photo = 'images/cat1.jpg'
        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
        status, result = test_add_pet_photo(auth_key, pet_id, pet_photo)
        assert status == 200
    else:
        raise Exception("There is no my pets")
