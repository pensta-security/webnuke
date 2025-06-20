import curses
from libs.quickdetect.AngularUtil import *
from libs.quickdetect.WordPressUtil import *
from libs.quickdetect.DrupalUtil import *
from libs.quickdetect.SitecoreUtil import SitecoreUtil
from libs.quickdetect.JQueryUtil import *
from libs.quickdetect.AWSS3Util import *
from libs.quickdetect.CloudIPUtil import CloudIPUtil
from libs.quickdetect.O365Util import O365Util
from libs.quickdetect.MXEmailUtil import MXEmailUtil
from libs.quickdetect.WindowNameUtil import WindowNameUtil
from libs.quickdetect.OnMessageUtil import OnMessageUtil
from libs.quickdetect.ServiceWorkerUtil import ServiceWorkerUtil
from libs.quickdetect.DojoUtil import DojoUtil
from libs.quickdetect.ReactUtil import ReactUtil
from libs.quickdetect.VueUtil import VueUtil
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
        
    def run(self):
        angular_util = AngularUtilV2(self.driver, self.current_url)
        isAngular = angular_util.isAngularApp()
        angular_version = 0
        if isAngular:
            angular_version = angular_util.getVersionString()

        react_util = ReactUtil(self.driver)
        is_react = react_util.is_react()
        react_version = None
        if is_react:
            react_version = react_util.get_version_string()

        vue_util = VueUtil(self.driver)
        is_vue = vue_util.is_vue()
        vue_version = None
        if is_vue:
            vue_version = vue_util.get_version_string()

        graphql_util = GraphQLUtil(self.driver, self.logger)
        has_graphql = graphql_util.has_graphql()
        
        wordpress_util = WordPressUtil(self.driver)
        isWordpress = wordpress_util.isWordPress()
        wordpress_version = 0
        if isWordpress:
            wordpress_version = wordpress_util.getVersionString()
            
        
        drupal_util = DrupalUtil(self.driver)
        isDrupal = drupal_util.isDrupal()
        drupal_version = 0
        if isDrupal:
            drupal_version = drupal_util.getVersionString()

        sitecore_util = SitecoreUtil(self.driver)
        is_sitecore = sitecore_util.is_sitecore()
        sitecore_version = 0
        if is_sitecore:
            sitecore_version = sitecore_util.get_version_string()
        
        jquery_util = JQueryUtil(self.driver)
        isJQuery = jquery_util.isJQuery()
        jquery_version =0
        if isJQuery:
            jquery_version = jquery_util.getVersionString()

        cloud_util = CloudIPUtil(self.current_url)
        cloud_provider = cloud_util.get_provider()
            
        dojo_util = DojoUtil(self.driver)
        is_dojo = dojo_util.is_dojo()
        dojo_version = 0
        if is_dojo:
            dojo_version = dojo_util.getVersionString()
        
        s3util = AWSS3Util(self.driver, self.current_url, self.logger)
        isS3 = s3util.hasS3Buckets()
        bucket_urls = []
        if isS3:
            bucket_urls = s3util.get_bucket_urls()

        email_util = MXEmailUtil(self.current_url, self.logger)
        email_provider = email_util.get_provider()

        o365_util = O365Util(self.driver, self.current_url, self.logger)
        has_bookings = o365_util.has_ms_bookings()
        is_o365 = (
            o365_util.is_office365() or
            o365_util.domain_uses_office365() or
            (email_provider == 'Office 365')
        )

        has_cloud = cloud_provider is not None

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
            
            
        showscreen = True
        
        while showscreen:
            self.curses_util.show_header()
            self.screen.addstr(2, 2, "Technologies:")
            
            
            current_line = 4
            
            if isAngular:
                message = "AngularJS Application Discovered"
                if angular_version is not None:
                    message += " ("+angular_version+")"
                self.screen.addstr(current_line, 4, message, curses.color_pair(2))
                current_line += 1

            if is_react:
                message = "React Detected"
                if react_version is not None:
                    message += " ("+react_version+")"
                self.screen.addstr(current_line, 4, message, curses.color_pair(2))
                current_line += 1

            if is_vue:
                message = "Vue.js Detected"
                if vue_version is not None:
                    message += " ("+vue_version+")"
                self.screen.addstr(current_line, 4, message, curses.color_pair(2))
                current_line += 1

            if has_graphql:
                message = "GraphQL Detected"
                self.screen.addstr(current_line, 4, message, curses.color_pair(2))
                current_line += 1
                
            if isWordpress:
                message = "WordPress CMS Discovered"
                if wordpress_version is not None:
                    message += " ("+wordpress_version+")"
                self.screen.addstr(current_line, 4, message, curses.color_pair(2))
                current_line += 1
                
            if isDrupal:
                message = "Drupal CMS Discovered"
                if drupal_version is not None:
                    message += " ("+drupal_version+")"

                self.screen.addstr(current_line, 4, message, curses.color_pair(2))
                current_line += 1

            if is_sitecore:
                message = "Sitecore CMS Discovered"
                if sitecore_version is not None:
                    message += " ("+sitecore_version+")"
                self.screen.addstr(current_line, 4, message, curses.color_pair(2))
                current_line += 1
                
            if isJQuery:
                message = "JQuery Discovered"
                if jquery_version is not None:
                    message += " ("+jquery_version+")"
                self.screen.addstr(current_line, 4, message, curses.color_pair(2))
                current_line += 1
            
            if is_dojo:
                message = "Dojo Discovered"
                if dojo_version is not None:
                    message += " ("+dojo_version+")"
                self.screen.addstr(current_line, 4, message, curses.color_pair(2))
                current_line += 1

            if has_cloud:
                message = "Cloud Provider Detected"
                if cloud_provider:
                    message += " (" + cloud_provider + ")"
                self.screen.addstr(current_line, 4, message, curses.color_pair(2))
                current_line += 1
            
            if isS3:
                message = "AWS S3 Bucket Detected"
                if bucket_urls:
                    message += " (" + ", ".join(bucket_urls) + ")"
                self.screen.addstr(current_line, 4, message, curses.color_pair(2))
                current_line += 1

            if email_provider:
                message = "Email Provider Detected"
                message += " (" + email_provider + ")"
                self.screen.addstr(current_line, 4, message, curses.color_pair(2))
                current_line += 1

            if has_bookings:
                message = "Microsoft Bookings Detected"
                self.screen.addstr(current_line, 4, message, curses.color_pair(2))
                current_line += 1

            if is_o365:
                message = "Office 365 Detected"
                self.screen.addstr(current_line, 4, message, curses.color_pair(2))
                current_line += 1

            if sw_supported:
                message = "Service Worker"
                if sw_registered:
                    message += " registered"
                    if sw_running:
                        message += " (running)"
                    else:
                        message += " (not running)"
                else:
                    message += " supported"
                self.screen.addstr(current_line, 4, message, curses.color_pair(2))
                current_line += 1

            if window_name_set:
                message = "window.name is set"
                if window_name_value:
                    truncated = str(window_name_value)[:30]
                    message += f" (\"{truncated}\")"
                self.screen.addstr(current_line, 4, message, curses.color_pair(2))
                current_line += 1

            if on_message_set:
                message = "onmessage handler set"
                if on_message_checks_origin:
                    message += " (origin checked)"
                else:
                    message += " (origin not checked)"
                self.screen.addstr(current_line, 4, message, curses.color_pair(2))
                current_line += 1

            if has_csp:
                message = "Content Security Policy Detected"
                self.screen.addstr(current_line, 4, message, curses.color_pair(2))
                current_line += 1

            if has_hsts:
                message = "HSTS Enabled"
                self.screen.addstr(current_line, 4, message, curses.color_pair(2))
                current_line += 1

            if has_xfo:
                message = "X-Frame-Options Set"
                self.screen.addstr(current_line, 4, message, curses.color_pair(2))
                current_line += 1

            if has_xcto:
                message = "X-Content-Type-Options Set"
                self.screen.addstr(current_line, 4, message, curses.color_pair(2))
                current_line += 1

            if has_manifest:
                message = "Web App Manifest Detected"
                if manifest_url:
                    message += f" ({manifest_url})"
                self.screen.addstr(current_line, 4, message, curses.color_pair(2))
                current_line += 1

            if has_websocket:
                message = "WebSocket Detected"
                self.screen.addstr(current_line, 4, message, curses.color_pair(2))
                current_line += 1
                
            self.screen.addstr(22, 28, "PRESS M FOR MAIN MENU")
            self.screen.refresh()
            
            c = self.screen.getch()
            if c == ord('M') or c == ord('m'):
                showscreen=False



