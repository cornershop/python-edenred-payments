=======================
python-edenred-payments
=======================

python sdk for edenred payment method

Usage
=====

from scratch

::

	from edenred.client import Edenred
	edenred = Edenred.create_for_client(client_id, client_secret, public_key_path)

	card = edenred.register_card(card_number, cvv, expiration_month, expiration_year, username, user_id)
	# card = edenred.retrieve_card(card_token)

	authorization = card.authorize(amount, description)

	charge = authorization.capture(amount, description)


previously authorized

::

	card = edenred.retrieve_card(card_token)

	authorization = card.retrieve_authorization(charge_id)

	charge = authorization.capture(amount, description)


just capture

::

	charge = card.capture(amount, description)


Installation
============

::

	pip install -e git+https://github.com/cornershop/python-edenred-payments.git#egg=python-edenred-payments
