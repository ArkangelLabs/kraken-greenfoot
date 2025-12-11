app_name = "kraken_theme"
app_title = "Kraken Theme"
app_publisher = "Kraken"
app_description = "Kraken branding and dark mode theme for ERPNext"
app_email = "dev@kraken.local"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "kraken_theme",
# 		"logo": "/assets/kraken_theme/logo.png",
# 		"title": "Kraken Theme",
# 		"route": "/kraken_theme",
# 		"has_permission": "kraken_theme.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# Include dark mode CSS in Desk (backend UI)
app_include_css = "/assets/kraken_theme/css/kraken_theme.bundle.css"

# Include dark mode CSS in website/portal pages
web_include_css = "/assets/kraken_theme/css/kraken_theme.bundle.css"

# Override ERPNext branding - this overrides website_context from erpnext/hooks.py
website_context = {
    "favicon": "/assets/kraken_theme/images/kraken-icon.png",
    "splash_image": "/assets/kraken_theme/images/kraken-icon.png",
}

# Override app logo URL (used in loading transitions)
app_logo_url = "/assets/kraken_theme/images/kraken-icon.png"

# Extend boot info to rebrand ERPNext to Kraken
extend_bootinfo = "kraken_theme.boot.extend_bootinfo"

# Installation
# ------------

after_install = "kraken_theme.install.after_install"
after_migrate = "kraken_theme.install.after_migrate"

# Fixtures to export/import
fixtures = [
    {"dt": "Navbar Settings"},
    {"dt": "Website Settings"},
]

# Force dark theme for new users
doc_events = {
    "User": {
        "before_insert": "kraken_theme.install.set_dark_theme_for_new_user"
    }
}

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "kraken_theme/public/scss/website"

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
# app_include_icons = "kraken_theme/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# Redirect users to specific workspace based on role
# Website Users with Kraken End User role go to portal dashboard
role_home_page = {
    "Kraken End User": "/portal/dashboard"
}

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
# 	"methods": "kraken_theme.utils.jinja_methods",
# 	"filters": "kraken_theme.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "kraken_theme.install.before_install"
# after_install = "kraken_theme.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "kraken_theme.uninstall.before_uninstall"
# after_uninstall = "kraken_theme.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "kraken_theme.utils.before_app_install"
# after_app_install = "kraken_theme.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "kraken_theme.utils.before_app_uninstall"
# after_app_uninstall = "kraken_theme.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "kraken_theme.notifications.get_notification_config"

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
# 		"kraken_theme.tasks.all"
# 	],
# 	"daily": [
# 		"kraken_theme.tasks.daily"
# 	],
# 	"hourly": [
# 		"kraken_theme.tasks.hourly"
# 	],
# 	"weekly": [
# 		"kraken_theme.tasks.weekly"
# 	],
# 	"monthly": [
# 		"kraken_theme.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "kraken_theme.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "kraken_theme.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "kraken_theme.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "kraken_theme.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["kraken_theme.utils.before_request"]
# after_request = ["kraken_theme.utils.after_request"]

# Job Events
# ----------
# before_job = ["kraken_theme.utils.before_job"]
# after_job = ["kraken_theme.utils.after_job"]

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
# 	"kraken_theme.auth.validate"
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

