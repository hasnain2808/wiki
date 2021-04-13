# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.website.router import resolve_route
from ghdiff import diff
import json

def get_context(context):
	# res = frappe.db.get_all(
	# 	"Wiki Page",
	# 	filters={"route": ("is", "set")},
	# 	fields=["name", "route"],
	# 	order_by="creation asc",
	# 	limit=1,
	# )
	# wiki_page = res[0] if res else None
	# # find and route to the first wiki page
	# if wiki_page:
	# 	frappe.response.location = wiki_page.route
	# 	frappe.response.type = "redirect"
	# 	raise frappe.Redirect


	# if frappe.form_dict.edit:
	print("frappe.form_dict.edit")
	print(frappe.form_dict.edit)
	print(resolve_route(frappe.form_dict.edit[1:]))
	# route = resolve_route(frappe.form_dict.edit[1:])
	context.route = frappe.form_dict.edit
	# context.title = "Editing "
	# if route.page_or_generator == "Generator":
	# 	context.code = route.doc.content
	# elif route.page_or_generator == "Page":
	# 	jenv = frappe.get_jenv()
	# 	source = jenv.loader.get_source(jenv, route.template)[0]
	# 	context.code = source
	return

@frappe.whitelist()
def get_code(route):
	# res = frappe.db.get_all(
	# 	"Wiki Page",
	# 	filters={"route": ("is", "set")},
	# 	fields=["name", "route"],
	# 	order_by="creation asc",
	# 	limit=1,
	# )
	# wiki_page = res[0] if res else None
	# # find and route to the first wiki page
	# if wiki_page:
	# 	frappe.response.location = wiki_page.route
	# 	frappe.response.type = "redirect"
	# 	raise frappe.Redirect


	# if frappe.form_dict.edit:
	print("route")
	print(route)
	print(resolve_route(route[1:]))
	route = resolve_route(route[1:])
	if route.page_or_generator == "Generator":
		code = route.doc.content
	elif route.page_or_generator == "Page":
		jenv = frappe.get_jenv()
		source = jenv.loader.get_source(jenv, route.template)[0]
		code = source
	return code

@frappe.whitelist()
def preview(content, path):
	# content = r.content
	# print("path")
	# print(path)
	# print(path[7:])
	# print("resolve_route(path[7:])")
	# print(resolve_route(path[7:]))
	from frappe.website.context import get_context
	# context = get_context(path[7:])
	route = resolve_route(path[7:])
	from frappe.website.context import  build_context
	route.path = route.route  = path[7:]
	route = build_context(route)
	# if route.template.endswith('.md'):
	content= frappe.utils.md_to_html(content)
	jenv = frappe.get_jenv()

	if route.page_or_generator == "Generator":
		code = route.doc.content
	elif route.page_or_generator == "Page":
		source = jenv.loader.get_source(jenv, route.template)[0]
		code = source
	
	old_code = frappe.utils.md_to_html(code)


	route.docs_base_url = '/docs'
	# print(route)
	# frappe.local.path = path
	# context = get_context(route)
		# jenv = frappe.get_jenv()
		# source = jenv.loader.get_source(jenv, route.template)[0]
		# context.code = source 
	
	source = jenv.from_string(content, route)
	print("source")
	print(source.render())
	response = {
		"diff": diff(old_code, content),
		"html": source.render()
	}
	return response


@frappe.whitelist()
def update( route, content, edit_message_short, edit_message_long, attachments):
	print(attachments)
	upd_req = frappe.new_doc("WebPage Update Request")
	upd_req.new_code = content
	upd_req.status = 'Unapproved'
	upd_req.web_route = route
	upd_req.raised_by = frappe.session.user
	upd_req.pr_title = edit_message_short
	upd_req.pr_body = edit_message_long
	upd_req.attachment_path_mapping = attachments

	upd_req.save()

	for attachment in json.loads(attachments):
		file = frappe.get_doc('File', attachment.get("name"))
		file.attached_to_doctype = 'WebPage Update Request'
		file.attached_to_name = upd_req.name
		file.save()

	# wiki_page = frappe.get_doc("Wiki Page", wiki_page)
	# wiki_page.update_page(title, content, edit_message)

	frappe.response.location = "/webpage-update/"
	frappe.response.type = "redirect"
	
