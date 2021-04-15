# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document
import frappe
from ghdiff import diff
from frappe.website.router import resolve_route
import re
from frappe.website.context import  build_context

class PullRequestRoute(Document):
	def validate(self):
		jenv = frappe.get_jenv()
		route = resolve_route(self.web_route[1:])
		if not route:
			self.orignal_code = ''
			self.diff = diff(self.orignal_code, self.new_code)
			old_html= frappe.utils.md_to_html(self.orignal_code)
			new_html= frappe.utils.md_to_html(self.new_code)
			self.new=1
			self.orignal_preview_store = ''
			self.new_preview_store = new_html
			return
		route.route = self.web_route[1:]
		route.path = self.web_route[1:]
		route = build_context(route)

		if route.page_or_generator == "Generator":
			# code = route.doc.content
			path = route.controller.split('.')
			path[-1] = 'templates'
			path.append(path[-2] + '.html')
			path = '/'.join(path)
			self.orignal_code =jenv.loader.get_source(jenv, path)[0]
			self.orignal_preview_store = self.orignal_code
			self.new_preview_store = self.new_code

		elif route.page_or_generator == "Page":
			self.orignal_code = jenv.loader.get_source(jenv, route.template)[0]
			old_html = self.orignal_code
			new_html = self.new_code
			if route.template.endswith('.md'):
				old_html= frappe.utils.md_to_html(self.orignal_code)
				new_html= frappe.utils.md_to_html(self.new_code)
	
			route.docs_base_url = '/docs'

			pattern = r'<[ ]*script.*?\/[ ]*script[ ]*> || <[ ]*link.*?>'  # mach any char zero or more times
		

			self.orignal_preview_store = jenv.from_string(old_html, route)
			self.orignal_preview_store = re.sub(pattern, '', self.orignal_preview_store.render(), flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE))
			self.new_preview_store = jenv.from_string(new_html, route)
			self.new_preview_store = re.sub(pattern, '', self.new_preview_store.render(), flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE))

			self.diff = diff(self.orignal_code , self.new_code)

