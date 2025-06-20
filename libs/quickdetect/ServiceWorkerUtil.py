from selenium.webdriver.remote.webdriver import WebDriver

class ServiceWorkerUtil:
    def __init__(self, webdriver: WebDriver):
        self.webdriver = webdriver

    def is_supported(self) -> bool:
        try:
            return bool(self.webdriver.execute_script("return 'serviceWorker' in navigator"))
        except Exception:
            return False

    def has_service_worker(self) -> bool:
        try:
            script = """
var cb = arguments[0];
if(navigator.serviceWorker && navigator.serviceWorker.getRegistrations){
    navigator.serviceWorker.getRegistrations().then(function(r){cb(r.length>0);}).catch(function(){cb(false);});
}else cb(false);
"""
            return bool(self.webdriver.execute_async_script(script))
        except Exception:
            return False

    def is_running(self) -> bool:
        try:
            script = """
var cb = arguments[0];
if(navigator.serviceWorker && navigator.serviceWorker.getRegistrations){
    navigator.serviceWorker.getRegistrations().then(function(r){
        for(var i=0;i<r.length;i++){
            if(r[i].active){ cb(true); return; }
        }
        cb(false);
    }).catch(function(){cb(false);});
}else cb(false);
"""
            return bool(self.webdriver.execute_async_script(script))
        except Exception:
            return False

