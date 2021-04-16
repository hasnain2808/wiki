# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.website.website_generator import WebsiteGenerator
from frappe.website.router import resolve_route
import os
import shutil
from frappe.commands import popen
import re
import json
from github import Github

class PullRequest(WebsiteGenerator):

	def validate(self):
		self.set_route()

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
		# popen(git_init)

		attachments = json.loads(self.attachment_path_mapping)


		for edit in edits:
			print(edit.new)
			for attachment in attachments:
				edit.new_code = edit.new_code.replace(attachment.get("file_url"), attachment.get("save_path"))

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
					f = open(repository_base_path  + '/' + path , "w")
					f.write(edit.new_code)
					f.close()
				elif resolved_route.page_or_generator == "Page":
					# source = jenv.loader.get_source(jenv, route.template)[0]
					# code = source
					f = open(repository_base_path + '/' + app + '/' + resolved_route.template , "w")
					f.write(edit.new_code)
					f.close()

		for attachment in attachments:
			shutil.copy( os.getcwd() + '/' + frappe.local.site + '/public' +  attachment.get("file_url"), repository_base_path + '/' + app + '/www' + attachment.get("save_path").replace('{{docs_base_url}}', '/docs'))

		branch = repository
		repository = frappe.get_doc('Repository', app)

		popen(f'git -C {repository_base_path} remote rm upstream ')
		popen(f'git -C {repository_base_path} remote rm origin ')
		popen(f'git -C {repository_base_path} remote add origin {repository.origin}')
		popen(f'git -C {repository_base_path} remote add upstream {repository.upstream}')
		popen(f'git -C {repository_base_path} branch {branch}')
		popen(f'git -C {repository_base_path} checkout {branch}')
		popen(f'git -C {repository_base_path} add .')
		popen(f'git -C {repository_base_path} commit -m "docs:{self.pr_title}" ')
		popen(f'git -C {repository_base_path} push origin {branch}')

		# popen(f'gh -C {repository_base_path} auth login --with-token {repository.token}')

		# popen(f'gh -C {repository_base_path} pr create --title {self.pr_title} --body {self.pr_body} --head {branch} --base master')

		print(repository.token)
		print(repository.token)
		g = Github(repository.get_password('token'))

		upstream_repo = g.get_repo('/'.join(repository.upstream.split('/')[3:5] ))


		# upstream_user = g.get_user('hasnain2808')
		# upstream_repo = upstream_user.get_repo('tox')

		upstream_pullrequest = upstream_repo.create_pull(self.pr_title, self.pr_body, 'master',
				'{}:{}'.format(repository.origin.split('/')[3],branch ), True)
		print(upstream_pullrequest.number)
		upstream = repository.upstream.replace('.git', '/')
		self.pr_link = f'{upstream}/pull/{upstream_pullrequest.number}'
		print(self.pr_link)
		self.save()

		try:
			shutil.rmtree(repository_base_path)
		except:
			frappe.msgprint('Error while deleting directory')
