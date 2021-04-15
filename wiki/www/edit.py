# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.website.router import resolve_route
from ghdiff import diff
import json
import re

def get_context(context):
	context.route = frappe.form_dict.edit
	return

@frappe.whitelist()
def get_code(route):
	route = resolve_route(route[1:])
	jenv = frappe.get_jenv()

	if not route:
		return ''
	if route.page_or_generator == "Generator":
		# code = route.doc.content
		path = route.controller.split('.')
		path[-1] = 'templates'
		path.append(path[-2] + '.html')
		path = '/'.join(path)
		code=jenv.loader.get_source(jenv, path)[0]
	elif route.page_or_generator == "Page":
		source = jenv.loader.get_source(jenv, route.template)[0]
		code = source
	return code

@frappe.whitelist()
def preview(content, path):
	from frappe.website.context import get_context
	# context = get_context(path[7:])
	route = resolve_route(path[1:])
	if not route:
		return {
		"diff": diff('', content),
		"html": frappe.utils.md_to_html(content)
	}
	from frappe.website.context import  build_context
	route.route = path[1:]
	route.path = path[1:]
	route = build_context(route)
	# if route.template.endswith('.md'):
	jenv = frappe.get_jenv()

	if route.page_or_generator == "Generator":
		# code = route.doc.content
		path = route.controller.split('.')
		path[-1] = 'templates'
		path.append(path[-2] + '.html')
		path = '/'.join(path)
		old_code=jenv.loader.get_source(jenv, path)[0]
	elif route.page_or_generator == "Page":
		old_code = jenv.loader.get_source(jenv, route.template)[0]

		if route.template.endswith('.md'):
			content= frappe.utils.md_to_html(content)
			old_code = frappe.utils.md_to_html(old_code)


		route.docs_base_url = '/docs'
		content = jenv.from_string(content, route)
		pattern = r'<[ ]*script.*?\/[ ]*script[ ]*> || <[ ]*link.*?>'  # mach any char zero or more times
		content = re.sub(pattern, '', content.render(), flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL) | re.VERBOSE)

	
	# (REMOVE HTML <STYLE> to </style> and variations)

	response = {
		"diff": diff(old_code, content),
		"html": content
	}
	return response


@frappe.whitelist()
def update( content, edit_message_short, edit_message_long, attachments='{}'):
	pull_req = frappe.new_doc("Pull Request")
	pull_req.status = 'Unapproved'
	pull_req.raised_by = frappe.session.user
	pull_req.pr_title = edit_message_short
	pull_req.pr_body = edit_message_long

	pull_req.attachment_path_mapping = attachments

	pull_req.save()

	for attachment in json.loads(attachments):
		file = frappe.get_doc('File', attachment.get("name"))
		file.attached_to_doctype = 'Pull Request'
		file.attached_to_name = pull_req.name
		file.save()


	
	content = json.loads(content)
	pull_req_route = {}
	for route, change in content.items():
		pull_req_route[route] = frappe.new_doc("Pull Request Route")
		pull_req_route[route].new_code = change
		pull_req_route[route].web_route = route
		pull_req_route[route].pull_request = pull_req.name
		pull_req_route[route].save()

	pull_req.raise_pr()

	# wiki_page = frappe.get_doc("Wiki Page", wiki_page)
	# wiki_page.update_page(title, content, edit_message)

	frappe.response.location = "/webpage-update/"
	frappe.response.type = "redirect"
	
