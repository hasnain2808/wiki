# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.website.router import resolve_route
import os
import shutil
from frappe.commands import popen
import re
import json
class PullRequest(Document):

	def raise_pr(self):
		jenv = frappe.get_jenv()

		edits = frappe.get_all(
			'Pull Request Route', 
			filters=[['pull_request','=', self.name]],
			fields=['name', 'new_code', 'web_route', 'new']	
		)
		# print(edits)
		# app = None
		# for edit in edits:
		# 	print(edit.new)
		# 	if not edit.new:
		# 		resolved_route = resolve_route(edit.web_route[1:])
		# 		print(resolved_route)
		# 		print(hasattr(resolved_route,"controller"))
		# 		print(hasattr(resolved_route,"controller_path"))
		# 		if resolved_route.get("controller"):
		# 			app = resolved_route.controller.split('.')[0]
		# 			break
					
		# 		elif resolved_route.get("controller_path"):
		# 			splits = resolved_route.controller_path.split('/')
		# 			app = splits[splits.index('apps') + 1]
		# 			break
		# if not app:
		# 	# frappe.throw("app not found")
		# 	app = 'erpnext_documentation'

		app = self.repository


		print(app)
		print(frappe.get_app_path(app))
		print(frappe.local.site)
		print(os.getcwd())
		repository = frappe.generate_hash()
		repository_base_path=os.getcwd() + '/' + frappe.local.site + '/private/' + repository
		# os.makedirs(repository_base_path)
		shutil.copytree('/'.join(frappe.get_app_path(app).split('/')[:-1]), repository_base_path + '/')
		# print(frappe.get_pymodule_path(frappe.local.site))
		# subprocess.run(['git', 'init', '-c', repository_base_path], shell=True)
		git_init = 'git  -C ' + repository_base_path + ' init'
		popen(git_init)


		for edit in edits:
			print(edit.new)
			for attachemt in attachments:
				edit.new_code = edit.new_code.replace(f.file_url, attachment.save_path)

			if edit.new:
				f = open(repository_base_path + '/' + app + '/www' + edit.web_route + '.md' , "w")
				f.write(edit.new_code)
				f.close()
			else:
				print(edit.web_route[1:])
				print("edit.web_route[1:]")
				resolved_route = resolve_route(edit.web_route[1:])
				print(resolved_route.page_or_generator)
				print("resolved_route.page_or_generator")
				if resolved_route.page_or_generator == "Generator":
					# code = route.doc.content
					path = resolved_route.controller.split('.')
					path[-1] = 'templates'
					path.append(path[-2] + '.html')
					path = '/'.join(path)
					code=jenv.loader.get_source(jenv, path)[0]
					print("app")
					print(app)
					print("repository_base_path")
					print(repository_base_path)
					print("path")
					print(path)
					f = open(repository_base_path  + '/' + path , "w")
					f.write(edit.new_code)
					f.close()
				elif resolved_route.page_or_generator == "Page":
					# source = jenv.loader.get_source(jenv, route.template)[0]
					# code = source
					f = open(repository_base_path + '/' + app + '/' + resolved_route.template , "w")
					f.write(edit.new_code)
					f.close()

		attachments = json.laods(self.attachment_path_mapping)
		for attachment in attachments:
			print(os.getcwd() + '/' + frappe.local.site + '/' +  f.file_url)
			print(repository_base_path + attachment.save_path.replace('{docs_base_url}', '/docs'))
			shutil.copy( os.getcwd() + '/' + frappe.local.site + '/' +  f.file_url, repository_base_path + attachment.save_path.replace('{docs_base_url}', '/docs'))