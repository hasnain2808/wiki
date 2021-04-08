# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from ghdiff import diff
from frappe.website.router import resolve_route


class WebPageUpdateRequest(Document):

	def validate(self):
		jenv = frappe.get_jenv()
		route = resolve_route(self.route[1:])
		if route.page_or_generator == "Generator":
			code = route.doc.content
		elif route.page_or_generator == "Page":
			source = jenv.loader.get_source(jenv, route.template)[0]
			code = source
		print("code")
		print(code)
		print("self.code")
		# print(self.code)
		self.old_code = code
		self.diff = diff(code, self.new_code)
		print(self.diff)

		route = resolve_route(self.route[1:])
		route.docs_base_url = '/docs'
		# if route.template.endswith('.md'):
		old_html= frappe.utils.md_to_html(self.old_code)
		new_html= frappe.utils.md_to_html(self.new_code)
		self.orignal_preview_store = jenv.from_string(old_html, route)
		self.orignal_preview_store = self.orignal_preview_store.render()
		self.new_preview_store = jenv.from_string(new_html, route)
		self.new_preview_store = self.new_preview_store.render()
		
		print(self.orignal_preview_store)
		print("self.orignal_preview_store")
		print(self.orignal_preview_store)
		print("self.orignal_preview_store")
		print(self.new_preview_store)
		print("self.new_preview_store")
		print(self.new_preview_store)
		print("self.new_preview_store")
		# frappe.db.commit()
			# print("source")
			# source =source.render()
		# else:
		# 	self.orignal_preview = jenv.from_string(self.old_code, route)
		# 	self.orignal_preview = self.orignal_preview.render()
		# 	self.new_preview = jenv.from_string(self.new_code, route)
		# 	self.new_preview = self.new_preview.render()

		# jenv = frappe.get_jenv()
		# print(route)
		# frappe.local.path = path
		# context = get_context(route)
			# jenv = frappe.get_jenv()
			# source = jenv.loader.get_source(jenv, route.template)[0]
			# context.code = source 
		
		# source = jenv.from_string(content, route)
		# print("source")
		# source =source.render()
		# return source.render()
