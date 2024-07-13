from utils import generate_key


class BaseConfig:
    key = generate_key.generate_key()
    SECRET_KEY = key
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql123@localhost/hmwx'


config_dict = {
    'base': BaseConfig
}