from utils import generate_key


class BaseConfig:

    SECRET_KEY = "Z_xrv8YayfE3Mtn40m0sOhz0if6RGR_M0j6_NguXj8k"
    # jwt过期时间
    JWT_EXPIRE_TIME = 24
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql123@localhost/hkwx'


config_dict = {
    'base': BaseConfig
}
