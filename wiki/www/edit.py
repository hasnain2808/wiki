# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.website.router import resolve_route
from ghdiff import diff
import json
import re
from frappe.website.context import build_context


def get_context(context):
	context.route = frappe.form_dict.edit
	return


@frappe.whitelist()
def get_code(route):
	resolved_route = resolve_route(route[1:])
	jenv = frappe.get_jenv()

	if not resolved_route:
		return ""

	return get_source(resolved_route, jenv)


@frappe.whitelist()
def preview(content, path, attachments="{}"):

	raw_edited_content = content

	attachments = json.loads(attachments)

	for attachment in attachments:
		if attachment.get("save_path"):
			content = content.replace(attachment.get("save_path"), attachment.get("file_url"))

	resolved_route = resolve_route(path[1:])

	if not resolved_route:
		return {"diff": diff("", content), "html": frappe.utils.md_to_html(content)}

	resolved_route.route = path[1:]
	resolved_route.path = path[1:]

	resolved_route = build_context(resolved_route)

	jenv = frappe.get_jenv()

	old_code_md = get_source(resolved_route, jenv)

	if resolved_route.page_or_generator == "Page":
		if resolved_route.template.endswith(".md"):
			content = frappe.utils.md_to_html(content)
			old_code = frappe.utils.md_to_html(old_code_md)
		content = clean_js_css(resolved_route, content, jenv)

	return {"diff": diff(old_code_md, raw_edited_content), "html": content}


def clean_js_css(route, content, jenv):
	route.docs_base_url = "/docs"
	content = jenv.from_string(content, route)
	pattern = r"<[ ]*script.*?\/[ ]*script[ ]*> || <[ ]*link.*?>"
	flags = re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE
	return re.sub(pattern, "", content.render(), flags=flags)


@frappe.whitelist()
def update(
	content, attachments="{}"
):
	repository = 'erpnext_documentation'
	pull_req = frappe.new_doc("Pull Request")



	pull_req_dict = {
		"status": "Unapproved",
		"raised_by": frappe.session.user,
		"pr_title": "docs: automated pull request",
		"pr_body": f"author: {frappe.session.user}",
		"repository": repository,
		"attachment_path_mapping": attachments,
	}

	pull_req.update(pull_req_dict)

	pull_req.save()

	update_file_links(attachments, pull_req.name)

	create_edited_files(content, pull_req.name, attachments)

	pull_req.raise_pr()

	frappe.response.location = "/pull-request/"
	frappe.response.type = "redirect"


def update_file_links(attachments, name):

	for attachment in json.loads(attachments):
		file = frappe.get_doc("File", attachment.get("name"))
		file.attached_to_doctype = "Pull Request"
		file.attached_to_name = name
		file.save()


def create_edited_files(content, name, attachments):
	pull_req_route = {}
	content = json.loads(content)
	for route, change in content.items():
		pull_req_route[route] = frappe.new_doc("Pull Request Route")
		pull_req_route[route].new_code = change
		pull_req_route[route].web_route = route
		pull_req_route[route].pull_request = name
		pull_req_route[route].attachments = attachments
		pull_req_route[route].save()


def get_source_generator(resolved_route, jenv):
	path = resolved_route.controller.split(".")
	path[-1] = "templates"
	path.append(path[-2] + ".html")
	path = "/".join(path)
	return jenv.loader.get_source(jenv, path)[0]


def get_source(resolved_route, jenv):
	if resolved_route.page_or_generator == "Generator":
		return get_source_generator(resolved_route, jenv)

	elif resolved_route.page_or_generator == "Page":
		return jenv.loader.get_source(jenv, resolved_route.template)[0]
