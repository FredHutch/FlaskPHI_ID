import os
from setuptools import setup

PROJECT_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_env_variable(var_name, default=False):
    """
    Get the environment variable or return exception
    :param var_name: Environment Variable to lookup
    """
    try:
        return os.environ[var_name]
    except KeyError:
        from io import StringIO
        import configparser
        env_file = os.environ.get('PROJECT_ENV_FILE', PROJECT_ROOT_DIR + "/.env")
        try:
            config = StringIO()
            config.write("[DATA]\n")
            config.write(open(env_file).read())
            config.seek(0, os.SEEK_SET)
            cp = configparser.ConfigParser()
            cp.read_file(config)
            value = dict(cp.items('DATA'))[var_name.lower()]
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            os.environ.setdefault(var_name, value)
            return value
        except (KeyError, IOError):
            if default is not False:
                return default

            error_msg = "Either set the env variable '{var}' or place it in your " \
                        "{env_file} file as '{var} = VALUE'"
            raise EnvironmentError(error_msg.format(var=var_name, env_file=env_file))

setup(
    name='FlaskPHI_ID',
    version='0.1',
    packages=['flaskphiid',],
    test_packages=['test', 'test.flaskphiid',],
    url='https://github.com/FredHutch/FlaskPHI_ID',
    install_requires=['compmed',
                      'HutchNERPredict',
                      'flask',
                      'boto3',
                      'compmed_utils',
                      ],
    tests_require=['nose'],
    test_suite='nose.collector',
    dependency_links = ["https://{}@github.com/FredHutch/ComprehendMedicalInterface/tarball/master#egg=compmed"
                            .format(get_env_variable('HDCGITAUTHTOKEN')),
                        "https://{}@github.com/FredHutch/HutchNERPredict/tarball/master#egg=HutchNERPredict"
                            .format(get_env_variable('HDCGITAUTHTOKEN')),
                        ],
    license='',
    author='HDC Data Science',
    author_email='whiteau@fhcrc.org',
    description='Flask Service for Identifying PHI',
    zip_safe=False
)
