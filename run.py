from flask import Flask, Response, request, render_template, redirect, session, url_for
from flask_login import login_required,login_user,logout_user,current_user

from temod_flask.security.authentification import Authenticator, TemodUserHandler
from temod_flask.utils.external_api import register_api
from temod_open_api.parser import SwaggerYmlParser
from temod.ext.holders import init_holders

from subprocess import Popen, PIPE, STDOUT

from context import *

import traceback
import mimetypes
import yaml
import toml
import json
import os


LANGUAGES = [{"code":"fr","name":"Français"},{"code":"ar","name":"العربية"},{"code":"en","name":"English"}]


# ** Section ** MimetypesDefinition
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('text/css', '.min.css')
mimetypes.add_type('text/javascript', '.js')
mimetypes.add_type('text/javascript', '.min.js')
# ** EndSection ** MimetypesDefinition


# ** Section ** LoadConfiguration
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"config.toml")) as config_file:
    config = toml.load(config_file)

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"dictionnary.yml")) as dictionnary_file:
    dictionnary = yaml.safe_load(dictionnary_file.read())
# ** EndSection ** LoadConfiguration


# ** Section ** ContextCreation
init_holders(
    entities_dir=os.path.join(config['temod']['core_directory'],r"entity"),
    joins_dir=os.path.join(config['temod']['core_directory'],r"join"),
    databases=config['temod']['bound_database'],
    db_credentials=config['storage']['credentials'],
)
init_context(config)
# ** EndSection ** ContextCreation

# ** Section ** AppCreation
def update_configuration(original_config, new_config):
    new_keys = set(new_config).difference(set(original_config))
    common_keys = set(new_config).intersection(set(original_config))
    for k in common_keys:
        if type(original_config[k]) is dict and type(new_config[k]) is not dict:
            raise Exception("Unmatched config type")
        if type(original_config[k]) is dict:
            update_configuration(original_config[k],new_config[k])
        else:
            original_config[k] = new_config[k]
    for k in new_keys:
        original_config[k] = new_config[k]

def build_app(**app_configuration):

    update_configuration(config,app_configuration)

    app = Flask(
        __name__,
        template_folder=config['app']['templates_folder'],
        static_folder=config['app']['static_folder']
    )

    secret_key = config['app'].get('secret_key','')
    app.secret_key = secret_key if len(secret_key) > 0 else generate_secret_key(32)
    app.config.update({k:v for k,v in config['app'].items() if not type(v) is dict})
    app.config['LANGUAGES'] = {language["code"]:language for language in LANGUAGES}
    app.config['DICTIONNARY'] = dictionnary

    # ** Section ** Authentification
    AUTHENTICATOR = Authenticator(TemodUserHandler(
        joins.UserAccount, "mysql", logins=['username'], **config['storage']['credentials']
    ),login_view="auth.login")
    AUTHENTICATOR.init_app(app)
    # ** EndSection ** Authentification

    import blueprints

    auth_blueprint_config = config['app'].get('blueprints',{}).get('auth',{})
    auth_blueprint_config['authenticator'] = AUTHENTICATOR

    app.register_blueprint(blueprints.email_manager_blueprint.setup(config['app'].get('blueprints',{}).get("email_manager",{})))
    app.register_blueprint(blueprints.auth_blueprint.setup(auth_blueprint_config))

    # ** Section ** AppMainRoutes
    @app.route('/', methods=['GET'])
    @login_required
    def home():
        if current_user.is_anonymous:
            return redirect(url_for("auth.login"))
        return redirect(url_for('email_manager.listEmails'))
    # ** EndSection ** AppMainRoutes

    return app

# ** EndSection ** AppCreation


if __name__ == '__main__':

    app = build_app(**config)

    server_configs = {
        "host":config['app']['host'], "port":config['app']['port'],
        "threaded":config['app']['threaded'],"debug":config['app']['debug']
    }
    if config['app'].get('ssl',False):
        server_configs['ssl_context'] = (config['app']['ssl_cert'],config['app']['ssl_key'])

    app.run(**server_configs)
