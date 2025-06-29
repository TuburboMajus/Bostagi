# ** Section ** Imports
from temod.base.entity import Entity
from temod.base.attribute import *
from copy import deepcopy
# ** EndSection ** Imports


# ** Section ** Entity_Bostagi
class Bostagi(Entity):
	ENTITY_NAME = "bostagi"
	ATTRIBUTES = [
		{"name":"version","type":StringAttribute, "max_length":20, "required":True,"is_id":True,"non_empty":True,"is_nullable":False},
	]
# ** EndSection ** Entity_Bostagi


# ** Section ** Entity_Language
class Language(Entity):
	ENTITY_NAME = "language"
	ATTRIBUTES = [
		{"name":"code","type":StringAttribute,"max_length":10, "required":True,"is_id":True,"is_nullable":False},
		{"name":"name","type":StringAttribute,"max_length":30,"is_nullable":False}
	]
# ** EndSection ** Entity_Language
