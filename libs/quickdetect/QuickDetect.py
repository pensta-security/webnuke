import curses
from libs.quickdetect.AngularUtil import AngularUtilV2
from libs.quickdetect.WordPressUtil import WordPressUtil
from libs.quickdetect.DrupalUtil import DrupalUtil
from libs.quickdetect.SitecoreUtil import SitecoreUtil
from libs.quickdetect.JQueryUtil import JQueryUtil
from libs.quickdetect.AWSS3Util import AWSS3Util
from libs.quickdetect.CloudIPUtil import CloudIPUtil
from libs.quickdetect.O365Util import O365Util
from libs.quickdetect.MXEmailUtil import MXEmailUtil
from libs.quickdetect.WindowNameUtil import WindowNameUtil
from libs.quickdetect.OnMessageUtil import OnMessageUtil
from libs.quickdetect.ServiceWorkerUtil import ServiceWorkerUtil
from libs.quickdetect.DojoUtil import DojoUtil
from libs.quickdetect.ReactUtil import ReactUtil
from libs.quickdetect.VueUtil import VueUtil
from libs.quickdetect.SvelteUtil import SvelteUtil
from libs.quickdetect.EmberUtil import EmberUtil
from libs.quickdetect.NextJSUtil import NextJSUtil
from libs.quickdetect.GraphQLUtil import GraphQLUtil
from libs.quickdetect.CSPUtil import CSPUtil
from libs.quickdetect.ManifestUtil import ManifestUtil
from libs.quickdetect.WebSocketUtil import WebSocketUtil
from libs.quickdetect.SecurityHeadersUtil import SecurityHeadersUtil

class QuickDetect:
    def __init__(self, screen, webdriver, curses_util, logger):
        self.version = 2.0
        self.screen = screen
        self.driver = webdriver
        self.current_url = self.driver.current_url
        self.curses_util = curses_util
        self.logger = logger

    # ------------------------------------------------------------------
    def _capture_screenshot(self, screenshot_path):
        """Capture a screenshot and log the outcome."""
        try:
            if self.driver.save_screenshot(screenshot_path):
                self.logger.log(f"Screenshot saved to {screenshot_path}")
            else:
                self.logger.error(f"Failed to save screenshot to {screenshot_path}")
        except Exception as exc:
            self.logger.error(f"Error capturing screenshot: {exc}")

    def _gather_detections(self):
        """Run detection utilities and return a list of (condition, message, info)."""
        angular_util = AngularUtilV2(self.driver, self.current_url)
        is_angular = angular_util.isAngularApp()
        angular_version = angular_util.getVersionString() if is_angular else None

        react_util = ReactUtil(self.driver)
        is_react = react_util.is_react()
        react_version = react_util.get_version_string() if is_react else None

        vue_util = VueUtil(self.driver)
        is_vue = vue_util.is_vue()
        vue_version = vue_util.get_version_string() if is_vue else None

        svelte_util = SvelteUtil(self.driver)
        is_svelte = svelte_util.is_svelte()
        svelte_version = svelte_util.get_version_string() if is_svelte else None

        ember_util = EmberUtil(self.driver)
        is_ember = ember_util.is_ember()
        ember_version = ember_util.get_version_string() if is_ember else None

        nextjs_util = NextJSUtil(self.driver)
        is_nextjs = nextjs_util.is_nextjs()
        nextjs_version = nextjs_util.get_version_string() if is_nextjs else None

        graphql_util = GraphQLUtil(self.driver, self.logger)
        has_graphql = graphql_util.has_graphql()

        wordpress_util = WordPressUtil(self.driver)
        is_wordpress = wordpress_util.isWordPress()
        wordpress_version = wordpress_util.getVersionString() if is_wordpress else None

        drupal_util = DrupalUtil(self.driver)
        is_drupal = drupal_util.isDrupal()
        drupal_version = drupal_util.getVersionString() if is_drupal else None

        sitecore_util = SitecoreUtil(self.driver)
        is_sitecore = sitecore_util.is_sitecore()
        sitecore_version = sitecore_util.get_version_string() if is_sitecore else None

        jquery_util = JQueryUtil(self.driver)
        is_jquery = jquery_util.isJQuery()
        jquery_version = jquery_util.getVersionString() if is_jquery else None

        cloud_util = CloudIPUtil(self.current_url)
        cloud_provider = cloud_util.get_provider()
        has_cloud = cloud_provider is not None

        dojo_util = DojoUtil(self.driver)
        is_dojo = dojo_util.is_dojo()
        dojo_version = dojo_util.getVersionString() if is_dojo else None

        s3util = AWSS3Util(self.driver, self.current_url, self.logger)
        has_s3 = s3util.hasS3Buckets()
        bucket_urls = s3util.get_bucket_urls() if has_s3 else []

        email_util = MXEmailUtil(self.current_url, self.logger)
        email_provider = email_util.get_provider()

        o365_util = O365Util(self.driver, self.current_url, self.logger)
        has_bookings = o365_util.has_ms_bookings()
        is_o365 = (
            o365_util.is_office365()
            or o365_util.domain_uses_office365()
            or email_provider == "Office 365"
        )

        window_name_util = WindowNameUtil(self.driver)
        window_name_set = window_name_util.is_set()
        window_name_value = window_name_util.get_value() if window_name_set else None

        on_message_util = OnMessageUtil(self.driver)
        on_message_set = on_message_util.is_set()
        on_message_checks_origin = on_message_util.checks_origin() if on_message_set else False

        sw_util = ServiceWorkerUtil(self.driver)
        sw_supported = sw_util.is_supported()
        sw_registered = sw_util.has_service_worker()
        sw_running = sw_util.is_running() if sw_registered else False

        csp_util = CSPUtil(self.driver, self.logger)
        has_csp = csp_util.has_csp()

        manifest_util = ManifestUtil(self.driver, self.logger)
        has_manifest = manifest_util.has_manifest()
        manifest_url = manifest_util.get_manifest_url() if has_manifest else None

        websocket_util = WebSocketUtil(self.driver, self.logger)
        has_websocket = websocket_util.has_websocket()

        security_util = SecurityHeadersUtil(self.driver, self.logger)
        has_hsts = security_util.has_hsts()
        has_xfo = security_util.has_x_frame_options()
        has_xcto = security_util.has_x_content_type_options()

        service_worker_info = None
        if sw_supported:
            if sw_registered:
                service_worker_info = "registered"
                if sw_running:
                    service_worker_info += " (running)"
                else:
                    service_worker_info += " (not running)"
            else:
                service_worker_info = "supported"

        window_name_info = None
        if window_name_set and window_name_value:
            window_name_info = f'"{str(window_name_value)[:30]}"'

        on_message_info = None
        if on_message_set:
            on_message_info = "origin checked" if on_message_checks_origin else "origin not checked"

        s3_info = ", ".join(bucket_urls) if bucket_urls else None

        detections = [
            (is_angular, "AngularJS Application Discovered", angular_version),
            (is_react, "React Detected", react_version),
            (is_vue, "Vue.js Detected", vue_version),
            (is_svelte, "Svelte Detected", svelte_version),
            (is_ember, "Ember.js Detected", ember_version),
            (is_nextjs, "Next.js Detected", nextjs_version),
            (has_graphql, "GraphQL Detected", None),
            (is_wordpress, "WordPress CMS Discovered", wordpress_version),
            (is_drupal, "Drupal CMS Discovered", drupal_version),
            (is_sitecore, "Sitecore CMS Discovered", sitecore_version),
            (is_jquery, "JQuery Discovered", jquery_version),
            (is_dojo, "Dojo Discovered", dojo_version),
            (has_cloud, "Cloud Provider Detected", cloud_provider),
            (has_s3, "AWS S3 Bucket Detected", s3_info),
            (bool(email_provider), "Email Provider Detected", email_provider),
            (has_bookings, "Microsoft Bookings Detected", None),
            (is_o365, "Office 365 Detected", None),
            (sw_supported, "Service Worker", service_worker_info),
            (window_name_set, "window.name is set", window_name_info),
            (on_message_set, "onmessage handler set", on_message_info),
            (has_csp, "Content Security Policy Detected", None),
            (has_hsts, "HSTS Enabled", None),
            (has_xfo, "X-Frame-Options Set", None),
            (has_xcto, "X-Content-Type-Options Set", None),
            (has_manifest, "Web App Manifest Detected", manifest_url),
            (has_websocket, "WebSocket Detected", None),
        ]

        return detections

    # ------------------------------------------------------------------
    def run(self, screenshot_path=None):
        if screenshot_path:
            self._capture_screenshot(screenshot_path)

        detections = self._gather_detections()

        showscreen = True

        while showscreen:
            self.curses_util.show_header()
            self.screen.addstr(2, 2, "Technologies:")

            current_line = 4
            for condition, message, info in detections:
                if condition:
                    if info:
                        message = f"{message} ({info})"
                    self.screen.addstr(current_line, 4, message, curses.color_pair(2))
                    current_line += 1

            self.screen.addstr(22, 28, "PRESS M FOR MAIN MENU")
            self.screen.refresh()

            c = self.screen.getch()
            if c in (ord('M'), ord('m')):
                showscreen = False
