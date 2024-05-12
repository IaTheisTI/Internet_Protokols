from urllib.request import urlopen
import json
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

access_token = '9eba420b9eba420b9eba420b149ec2554999eba9eba420bfe0df3b73cb2a579ed4420dc'
v = '5.74'

def request(method, fields):
    url = 'https://api.vk.com/method/{}?{}&v={}&access_token={}'.format(method,
                                                                        fields,
                                                                        '5.131',
                                                                        access_token)

    with urlopen(url) as url:
        j = json.loads(url.read())
    return j

def user(id_or_name):
    data = request('users.get', 'user_ids={}'.format(id_or_name))
    if data is not None and 'response' in data and 'error' not in data:
        return data

def userinfo(data, field):
    if data is not None and 'response' in data:
        return data['response'][0][field]

def userid(data):
    return userinfo(data, 'id')

def deactivated(user_id):
    data = user(user_id)
    if data is not None:
        return 'deactivated' in data['response'][0].keys()

def friends(user_id, count=None):
    count_param = ''
    if count is not None:
        count_param = '&count={}'.format(count)
    return request('friends.get', 'user_id={}'.format(user_id) + count_param)

def friendlist(friends_data):
    if 'error' in friends_data.keys():
        if friends_data['error']['error_code'] == 15:
            return 'private'
    return friends_data['response']['items']

def userinfostr(data):
    first_name = userinfo(data, 'first_name')
    last_name = userinfo(data, 'last_name')
    if first_name is None or last_name is None:
        return
    return last_name + ' ' + first_name

def albums(user_id):
    global access_token
    data = request("photos.getAlbums", 'user_id={}'.format(user_id))
    if 'error' in data:
        print('Этот профиль является приватным для данного токена')
        return
    print('\nКоличество альбомов: ' + str(data['response']['count']))
    for index, album in enumerate(data['response']['items']):
        print('\nНазвание: ' + str(
            album['title']) + '\n' + 'Количество фото: ' + str(
            album['size']))

if __name__ == '__main__':
    user_name_or_id = input("Введите id пользователя: ")
    user_data = user(user_name_or_id)
    user_id = userid(user_data)
    if user_data is None:
        print("Пользователя не существует")
    else:
        req = input("Что вы хотите получить?\nВведите 'Друзья', "
                    "чтобы вывести список друзей пользователя,"
                    "\nВведите 'Альбомы',"
                    " чтобы вывести список альбомов пользователя: ")
        if req == 'Друзья':
            friends_count = input("Скольких друзей вы хотите увидеть? ")
            friends_data = friends(user_id, friends_count)
            friend_list = friendlist(friends_data)
            if friend_list == 'private':
                print('Этот профиль является приватным для данного токена')
            else:
                print("\nДрузья " + user_name_or_id)
                for friend_id in friend_list:
                    if not deactivated(friend_id):
                        friend_data = user(friend_id)
                        friend_info = userinfostr(friend_data)
                        if friend_data is not None and 'error' not in friend_data and 'deactivated' not in friend_data:
                            friend_friends = friends(friend_id)
                            if 'error' in friend_friends:
                                friends_count = 'этот пользователь скрыл своих'
                            else:
                                friends_count = str(friend_friends['response']['count'])
                            print("\nИмя/Фамилия пользователя: " + friend_info +
                                  '\n\nУ него/неё : ' + friends_count + " друзей" +
                                  '\n\n id=' + str(friend_id))
                        else:
                            print("Профиль друга закрыт для данного токена или удалён")
        elif req == 'Альбомы':
            print("\nАльбомы " + user_name_or_id)
            albums(user_id)
        else:
            print('Некорректный запрос')
