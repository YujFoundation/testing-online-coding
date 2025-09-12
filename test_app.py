from app import app


def test_addition():
    client = app.test_client()
    response = client.post('/', data={'num1': '2', 'num2': '3'})
    assert b'Result: 5.0' in response.data


if __name__ == '__main__':
    test_addition()
    print('Test passed')
