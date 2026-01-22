app_name = "warranties"
app_title = "Warranties"
app_publisher = "Kraken"
app_description = "HVAC Equipment Warranty Registration Management"
app_email = "dev@kraken.local"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Add Warranties app to the apps screen
# This ensures get_default_path() returns /desk (multiple apps)
# which lets the client-side router use default_workspace
add_to_apps_screen = [
    {
        "name": "warranties",
        "logo": "/assets/kraken_theme/images/kraken-icon.png",
        "title": "Warranties",
        "route": "/app/warranties"
    }
]

# Fixtures
# --------
fixtures = [
    {"dt": "HVAC Manufacturer", "filters": []},
    {"dt": "Workspace Sidebar", "filters": [["app", "=", "warranties"]]},
    {"dt": "Workspace", "filters": [["module", "=", "Warranties"]]},
    {"dt": "Number Card", "filters": [["module", "=", "Warranties"]]},
    {"dt": "Dashboard Chart", "filters": [["module", "=", "Warranties"]]}
]

# Use Kraken logo for this app
app_logo_url = "/assets/kraken_theme/images/kraken-icon.png"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/warranties/css/warranties.css"
# app_include_js = "/assets/warranties/js/warranties.js"

# include js, css files in header of web template
# web_include_css = "/assets/warranties/css/warranties.css"
# web_include_js = "/assets/warranties/js/warranties.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "warranties/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "warranties/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "warranties.utils.jinja_methods",
# 	"filters": "warranties.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "warranties.install.before_install"
# after_install = "warranties.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "warranties.uninstall.before_uninstall"
# after_uninstall = "warranties.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "warranties.utils.before_app_install"
# after_app_install = "warranties.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "warranties.utils.before_app_uninstall"
# after_app_uninstall = "warranties.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "warranties.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"warranties.tasks.all"
# 	],
# 	"daily": [
# 		"warranties.tasks.daily"
# 	],
# 	"hourly": [
# 		"warranties.tasks.hourly"
# 	],
# 	"weekly": [
# 		"warranties.tasks.weekly"
# 	],
# 	"monthly": [
# 		"warranties.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "warranties.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "warranties.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "warranties.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "warranties.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["warranties.utils.before_request"]
# after_request = ["warranties.utils.after_request"]

# Job Events
# ----------
# before_job = ["warranties.utils.before_job"]
# after_job = ["warranties.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"warranties.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []


# Custom CLI Commands
# -----------------
commands = [
    "warranties.commands.import_extraction_logs"
]
