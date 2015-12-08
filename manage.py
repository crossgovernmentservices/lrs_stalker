#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from flask.ext.script import Shell, Server, Manager

if os.environ.get('LRS_URL') is None or os.environ.get('LRS_USER') is None or os.environ.get('LRS_PASS') is None:
	raise Exception("Set up LRS env variables: LRS_URL, LRS_USER and LRS_PASS")

from application import app

app.debug = True
port = os.environ.get('PORT', 8000)

manager = Manager(app)
manager.add_command('server', Server(host="0.0.0.0", port=port))

if __name__ == '__main__':
    manager.run()
