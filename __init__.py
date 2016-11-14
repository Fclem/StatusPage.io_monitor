#!/usr/bin/python
from infra_monitor import *
import json

__author__ = 'clement.fiere@helsinki.fi'
__date__ = '14/11/2016'


#########
# ENUMs #
#########
class CheckStates(SpecialEnum):
	OPERATIONAL = 'operational'
	DEGRADED = 'degraded_performance'
	PARTIAL_OUT = 'partial_outage'
	MAJOR_OUT = 'major_outage'


##################
# ACTUAL OBJECTS #
##################

# clem 10/10/2016
class Component(object):
	"""
	ypkdj35tpnkz {u'status': u'operational', u'description': None, u'created_at': u'2016-10-28T09:34:54.006Z',
	u'updated_at': u'2016-11-10T13:56:54.417Z', u'position': 3, u'group_id': u'fmdlrkh6h12q', u'page_id':
	u'', u'id': u'', u'name': u'CAS'}
	"""
	_raw_data = dict()
	_status = ''
	_id = ''
	_name = ''
	
	def __init__(self, a_dict=None):
		if a_dict:
			self._raw_data = a_dict
			self._status = a_dict.get('status', '')
			self._id = a_dict.get('id', '')
			self._name = a_dict.get('name', '')
	
	@property
	def status(self):
		return self._status
	
	@status.setter
	def status(self, value):
		assert value in CheckStates()
		self._status = value
	
	@property
	def name(self):
		return self._name
	
	@property
	def id(self):
		return self._id
	
	@property
	def raw(self):
		return self._raw_data
	
	def __str__(self):
		return str(self.raw)


# noinspection PyTypeChecker
class StatusPageIoInterface(ServiceInterfaceAbstract):
	""" Interface between configured checks and StatusPage.io components """
	COMPONENT_BASE_URL = 'components/%s.json'
	COMPONENTS_URL = 'components.json'
	
	_components_cache = None
	
	def __init__(self, inst_conf=get_config()):
		super(StatusPageIoInterface, self).__init__(inst_conf)
		_ = self.components_dict
		
	def _send(self, endpoint, data=None, method=HTTPMethods.GET):
		""" send a query to the StatusPage.io api using conf.api_bas_url
		
		:type endpoint: str
		:type data: dict
		:type method: str
		"""
		return self._sender(self._host_url, self._gen_url(endpoint), method, data, True)
	
	# clem 10/11/2016
	@property
	def _base_end_point_url(self): return self._conf.api_url_path_base
	
	# clem 10/11/2016
	@property
	def _host_url(self): return self._conf.api_host_name
	
	# clem 10/11/2016
	def _gen_url(self, url): return self._base_end_point_url + url
	
	###############################
	# REMOTE COMPONENTS SPECIFICS #
	###############################
	
	@property
	def _component_base_url(self): return self.COMPONENT_BASE_URL
	
	def _component_url(self, component_id): return self._component_base_url % component_id
	
	def component_update(self, component_id, data):
		return self._send(self._component_url(component_id), data, HTTPMethods.PATCH)
	
	# FIXME obsolete
	def get_component_status(self, component_id):
		return json.load(self._send(self._component_url(component_id), method=HTTPMethods.GET))['status']
	
	@property
	def _legacy_components_list(self):
		obj = list()
		try:
			obj = json.load(self._send(self.COMPONENTS_URL))
		except ValueError:
			pass
		return obj
	
	# clem 10/11/2016
	def _update_components(self):
		a_dict = dict()
		a_list = self._legacy_components_list
		for each in a_list:
			a_dict.update({each['id']: Component(each)})
		return a_dict
	
	# clem 10/11/2016
	@property
	def components_dict(self):
		if not self._components_cache:
			self._components_cache = self._update_components()
		return self._components_cache
	
	def show_components(self):
		a_list = self._legacy_components_list
		for each in a_list:
			print each['id'], each
	
	def _gen_config_generator(self, callbacks):
		""" fetch all the components from StatusPage.io and write then in the config file
		
		:param callbacks:
		:type callbacks: tuple[callable[str], callable[str, k, v], callable]
		"""
		assert isinstance(callbacks, tuple) and len(callbacks) == 3 and callable(callbacks[0]) and \
			callable(callbacks[1]) and callable(callbacks[2])
		
		header_callback = callbacks[0]
		inner_callback = callbacks[1]
		footer_callback = callbacks[2]
		
		a_list = self._legacy_components_list
		for each in a_list:
			sec_title = '%s%s' % (self._conf.section_items_prefix, each['id'])
			if sec_title not in self._conf.sections:
				header_callback(sec_title)
				for k, v in self.check_def.iteritems():
					inner_callback(sec_title, k, str(each.get(k, v)))
				footer_callback()
		self._conf.save()
	
	def show_config(self):
		""" fetch all the components from StatusPage.io and display then as ini structured data """
		def header(sec_title):
			print '[%s]' % sec_title
			
		def inner(_, k, val):
			print k, '=', val
			
		def footer():
			print ''
		
		self._gen_config_generator((header, inner, footer))
	
	def write_config(self):
		""" fetch all the components from StatusPage.io and write then in the config file """
		
		def header(sec_title):
			self._conf.config.add_section(sec_title)
		
		def inner(sec_title, k, val):
			self._conf.config.set(sec_title, k, str(val))
		
		def footer():
			pass
		
		self._gen_config_generator((header, inner, footer))
		self._conf.save()
	
	###################
	# IMPLEMENTATIONS #
	###################
	
	def no_status_change(self, check_instance, old_status, new_status):
		pass

	def update_check(self, check_instance, status, force=False):
		""" Update the status of one check, state has to be a value of CheckStates
		
		:type check_instance: CheckObject
		:type status: str
		:type force: bool
		:rtype:
		"""
		assert isinstance(check_instance, CheckObject)
		a_component = self.components_dict.get(check_instance.id, Component())
		if force or a_component.status != status:
			response = self.component_update(check_instance.id, {'component[status]': status})
			if response.status == 200:
				a_component.status = status
			return response
		return False
	
	# clem 10/11/2016
	def set_check(self, check_instance, value=False):
		""" Set the check component value to On or Off
		
		:type check_instance: CheckObject
		:type value: bool
		"""
		assert isinstance(check_instance, CheckObject)
		return self.update_check(check_instance, CheckStates.OPERATIONAL if value else CheckStates.MAJOR_OUT)
	
	###############
	# SUP METHODS #
	###############
	
	# clem 10/11/2016
	def init_all_check_down(self):
		def sub(_, check_instance):
			assert isinstance(check_instance, CheckObject)
			# check_instance._last_status = False
			self.update_check(check_instance, CheckStates.PARTIAL_OUT)
		self.__check_apply(sub)


def main():
	# runs the watcher loop
	return Watcher.loop(StatusPageIoInterface(get_config()))

if __name__ == '__main__':
	exit(0 if main() else 1)
else:
	conf = get_config()
