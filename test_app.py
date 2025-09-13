import os

os.environ["AUTHORIZED_EMAIL"] = "tester@example.com"

from app import app


def test_addition():
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["user"] = "tester@example.com"
    response = client.post('/', data={'num1': '2', 'num2': '3'})
    assert b'Result: 5.0' in response.data


if __name__ == '__main__':
    test_addition()
    print('Test passed')
