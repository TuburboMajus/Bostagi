from flask import current_app, render_template, request, redirect, url_for, abort, session,g
from flask_login import LoginManager, login_required, current_user

from temod_flask.utils.content_readers import body_content
from temod_flask.blueprint import MultiLanguageBlueprint
from temod_flask.blueprint.utils import Paginator

from temod.base.condition import Not, In, Equals
from temod.base.attribute import *

from front.renderers.normal_user import NormalUserTemplate

from tools.doveadm import Doveadm, Mailbox

from datetime import datetime, date
from pathlib import Path

import traceback
import json
	

email_manager_blueprint = MultiLanguageBlueprint('email_manager',__name__, load_in_g=True, default_config={
	"templates_folder":"{language}/email_manager",
	"emails_per_page":50,
}, dictionnary_selector=lambda lg:lg['code'])


@email_manager_blueprint.route('/emails')
@login_required
@email_manager_blueprint.with_dictionnary
def listEmails():
	data = [email.to_dict() for email in Doveadm(current_app.config['domain_name']).list_dovecot_users()]
	if request.args.get('fmt','html') == 'html':
		return NormalUserTemplate(
			Path(email_manager_blueprint.configuration["templates_folder"].format(language=g.language['code'])).joinpath("list.html"),
			email=data
		).handles_success_and_error().with_dictionnary().with_sidebar("emails").with_navbar().render()
	return {"status":"ok","data":data}


@email_manager_blueprint.route('/email',methods=["POST"])
@login_required
@body_content('form')
def createEmail(form):
	assert(all([val in form for val in ['firstName','password','confirmPassword']]))
	assert(form['password'] == form['confirmPassword'])

	if form.get('lastName') is None:
		new_box = Mailbox(name=form['firstName'])
	else:
		new_box = Mailbox.generate(firstname=form['firstName'], lastname=form['lastName'])

	Doveadm(current_app.config['domain_name']).generate_new_mailbox(new_box, password)

	return redirect(url_for("emails.listEmails"))


@email_manager_blueprint.route('/reset_password',methods=["POST"])
@login_required
@body_content('form')
def resetEmailPassword(form):
	assert(all([val in form for val in ['username','password','confirmPassword']]))
	assert(form['password'] == form['confirmPassword'])

	try:
		mailbox = [email.to_dict() for email in Doveadm(current_app.config['domain_name']).list_dovecot_users() if email['name'] == form['username']][0]
		Doveadm(current_app.config['domain_name']).generate_new_mailbox(mailbox, password)
	except:
		pass

	return redirect(url_for("emails.listEmails"))

