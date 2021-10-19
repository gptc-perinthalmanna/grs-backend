import datetime
from pydantic import ValidationError

from models.posts import Post, PostResponse
from models.user import User, UserCreate


def ok(message):
    success = '\x1b[6;30;42m' + ' SUCCESS ' + '\x1b[0m'
    print(f'{success} {message}')
    return True


def err(message):
    fail = '\x1b[0;30;41m' + '  FAIL   ' + '\x1b[0m'
    print(f'{fail} {message}')
    return False


user = {
    'key': 'a4f42a1a-d01a-4af7-b9e3-dfecf69224ad',
    'username': 'myUsername',
    'email': 'me@gmail.com',
    'first_name': 'Amjed',
    'last_name': 'Ali',
    'contact_number': 9609666636,
    'type': 'staff',
    'designation': 'tradesman',
    'address': "My Local Address",
    'state': 'Kerala',
    'pin': 646461,
    'gender': 'male',
    'avatar': 'https://google.com/image.jpg',
    'createdAt': datetime.datetime.now(),
    'updatedAt': datetime.datetime.now()
}

test_admin_user = {
    "key": "64ff8d1a-7e49-4e81-a988-937c468c6512",
    "username": "testadmin",
    "email": "test_admin@test.com",
    "disabled": False,
    "first_name": "Test",
    "last_name": "Admin",
    "contact_number": 9797979797,
    "type": "staff",
    "address": "Test Admin Address",
    "state": "Kerala",
    "pin": 656565,
    "gender": "male",
    "designation": "tradesman",
    "password": "Sup3RUse3R!",
    "repeat_password": "Sup3RUse3R!"
}

post = {
    'key': '529e35c3-1fc1-456b-9254-e37d27a7dfbf',
    'subject': 'Test Subject',
    'content': 'Sample Content',
    'priority': 'high',
    'status': 'open',
    'author': '64ff8d1a-7e49-4e81-a988-937c468c6512',
    'authorName': 'Amjed Ali',
    'published': datetime.datetime.now(),
    'modified': datetime.datetime.now(),
}

new_response = {
    "post_key": post['key'],
    "content": 'This is a test post reply',
    "status": 'open'
}

responses = [
    {
        'id': '1',
        'content': 'Sample Content',
        'statusChange': {
            'prev': 'draft',
            'to': 'solved'
        },
        'author': '705d0866-40fd-40e6-bfc7-804ab7fad43e',
        'published': datetime.datetime.now(),
        'modified': datetime.datetime.now(),
        'visible': True,
        'deleted': False,
    }
]


def pd_validation(name: str, model, element, errors, invert: bool = False, ):
    try:
        model(**element)
        if invert:
            errors.append(err(f'{name} Error'))
        else:
            errors.append(ok(f'{name} Ok'))
    except ValidationError as e:
        if invert:
            errors.append(ok(f'{name} Ok'))
        else:
            errors.append(err(f'{name} Error - {e}'))
    except Exception as e:
        errors.append(err(f'Unknown Error in {name} - {e}'))
    return errors


def user_validation():
    errors = []
    errors = pd_validation('User Model', User, user, errors)
    # Password Validation
    user['password'] = 'mypassword'
    user['repeat_password'] = 'mypassword2'
    errors = pd_validation('Password Validation', UserCreate, user, errors, True)
    user['repeat_password'] = 'mypassword'
    errors = pd_validation('Password Verification', UserCreate, user, errors)

    return False if False in errors else True


def post_validation():
    errors = []
    errors = pd_validation('Posts Model', Post, post, errors)
    post['responses'] = responses
    errors = pd_validation('Responses Model', PostResponse, responses[0], errors)
    errors = pd_validation('Posts ReValidation', Post, post, errors)

    return False if False in errors else True


def run_tests():
    print('Waiting... ')
    errors = []
    errors.append(user_validation())
    errors.append(post_validation())
    if False in errors:
        raise RuntimeError('Errors Found!')


if __name__ == '__main__':
    run_tests()
