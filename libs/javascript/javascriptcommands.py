from selenium.common.exceptions import WebDriverException
import sys


class JavascriptCommands:
    def __init__(self, webdriver, jsinjector):
        self.version = 2.0
        self.driver = webdriver
        self.jsinjector = jsinjector
        
    def search_for_urls(self):
        self.jsinjector.execute_javascript(self.driver, 'wn_findStringsWithUrls();')
        print('')
        print('')
        input("Press ENTER to return to menu.")


    def walk_functions(self):
        #javascript="jsproberesults=[];for (name in this) {  try{jsproberesults.push( {'name':''+name, 'value': ''+this[name]})}catch(err){var anyerror='ignore'};};return jsproberesults"
        javascript = """
window.wn_walk_functions = function(rootnode, pathstring){
    var blacklist = ["InstallTrigger", "window", "__webDriverComplete", "__webDriverArguments", "close","stop","focus","blur","open","alert","confirm","prompt","print","postMessage","captureEvents","releaseEvents","getSelection","getComputedStyle","matchMedia","moveTo","moveBy","resizeTo","resizeBy","scroll","scrollTo","scrollBy","requestAnimationFrame","cancelAnimationFrame","getDefaultComputedStyle","scrollByLines","scrollByPages","sizeToContent","updateCommands","find","dump","setResizable","requestIdleCallback","cancelIdleCallback","btoa","atob","setTimeout","clearTimeout","setInterval","clearInterval","createImageBitmap","fetch","self","name","history","locationbar","menubar","personalbar","scrollbars","statusbar","toolbar","status","closed","frames","length","opener","parent","frameElement","navigator","external","applicationCache","screen","innerWidth","innerHeight","scrollX","pageXOffset","scrollY","pageYOffset","screenX","screenY","outerWidth","outerHeight","performance","mozInnerScreenX","mozInnerScreenY","devicePixelRatio","scrollMaxX","scrollMaxY","fullScreen","mozPaintCount","ondevicemotion","ondeviceorientation","onabsolutedeviceorientation","ondeviceproximity","onuserproximity","ondevicelight","sidebar","crypto","onabort","onblur","onfocus","onauxclick","oncanplay","oncanplaythrough","onchange","onclick","onclose","oncontextmenu","ondblclick","ondrag","ondragend","ondragenter","ondragexit","ondragleave","ondragover","ondragstart","ondrop","ondurationchange","onemptied","onended","oninput","oninvalid","onkeydown","onkeypress","onkeyup","onload","onloadeddata","onloadedmetadata","onloadend","onloadstart","onmousedown","onmouseenter","onmouseleave","onmousemove","onmouseout","onmouseover","onmouseup","onwheel","onpause","onplay","onplaying","onprogress","onratechange","onreset","onresize","onscroll","onseeked","onseeking","onselect","onshow","onstalled","onsubmit","onsuspend","ontimeupdate","onvolumechange","onwaiting","onselectstart","ontoggle","onpointercancel","onpointerdown","onpointerup","onpointermove","onpointerout","onpointerover","onpointerenter","onpointerleave","ongotpointercapture","onlostpointercapture","onmozfullscreenchange","onmozfullscreenerror","onanimationcancel","onanimationend","onanimationiteration","onanimationstart","ontransitioncancel","ontransitionend","ontransitionrun","ontransitionstart","onwebkitanimationend","onwebkitanimationiteration","onwebkitanimationstart","onwebkittransitionend","onerror","speechSynthesis","onafterprint","onbeforeprint","onbeforeunload","onhashchange","onlanguagechange","onmessage","onmessageerror","onoffline","ononline","onpagehide","onpageshow","onpopstate","onstorage","onunload","localStorage","origin","isSecureContext","indexedDB","caches","sessionStorage","document","location","top","addEventListener","removeEventListener","dispatchEvent"];
    var rtndata = [];
    for (name in rootnode) {  
        typefound = typeof rootnode[name];
        var fullname = ""+pathstring+"."+name;
        if(typefound == "object"){
            blacklistlookup = fullname.substring(5);
            if (blacklist.includes(blacklistlookup) == false ) {
                console.log("OBJECT: "+fullname);
                rtndata.push({'type': 'object', 'fullpath': fullname});
                //wn_walk_functions(rootnode[name], fullname);
            }
            
        }
        else if(typefound == "function"){
            blacklistlookup = fullname.substring(5);
            if (blacklist.includes(blacklistlookup) == false && name.startsWith("wn_") == false) {
                rtndata.push({'type': 'function', 'fullpath': fullname});
                console.log("FUNCTION: "+fullname+"()");
            }
        }
        else {
            rtndata.push({'type': 'ignored', 'fullpath': fullname});
            //console.log("Name: "+name+" ["+typefound+"]"); 
            //console.log(fullname)  
        }
    
    }
    
    return rtndata;
}
"""
        self.jsinjector.execute_javascript(self.driver, javascript)

        javascript="return wn_walk_functions(this, 'this');"        
        jsresults = self.executeJavascriptAndReturnArray(javascript)
        #print jsresults
        for record in jsresults:
            recordtype = record['type']
            fullpath = record['fullpath']
            if recordtype == 'function':
                confirmed = self.confirm("Do you want to run javascript function '"+fullpath+"'?")
                if confirmed:
                    print("running function "+fullpath+"();")
            if recordtype == 'object':
                confirmed = self.confirm("Do you want to walk '"+fullpath+"'?")
                if confirmed:
                    print("walking object "+fullpath+"")
            print("%s [%s]"%(record['fullpath'], record['type']))
        print('')
        print('')
        input("Press ENTER to return to menu.")


    def search_for_document_javascript_methods(self):
        script_to_include = """
var blacklist = ["__webDriverComplete", "__webDriverArguments", "close","stop","focus","blur","open","alert","confirm","prompt","print","postMessage","captureEvents","releaseEvents","getSelection","getComputedStyle","matchMedia","moveTo","moveBy","resizeTo","resizeBy","scroll","scrollTo","scrollBy","requestAnimationFrame","cancelAnimationFrame","getDefaultComputedStyle","scrollByLines","scrollByPages","sizeToContent","updateCommands","find","dump","setResizable","requestIdleCallback","cancelIdleCallback","btoa","atob","setTimeout","clearTimeout","setInterval","clearInterval","createImageBitmap","fetch","self","name","history","locationbar","menubar","personalbar","scrollbars","statusbar","toolbar","status","closed","frames","length","opener","parent","frameElement","navigator","external","applicationCache","screen","innerWidth","innerHeight","scrollX","pageXOffset","scrollY","pageYOffset","screenX","screenY","outerWidth","outerHeight","performance","mozInnerScreenX","mozInnerScreenY","devicePixelRatio","scrollMaxX","scrollMaxY","fullScreen","mozPaintCount","ondevicemotion","ondeviceorientation","onabsolutedeviceorientation","ondeviceproximity","onuserproximity","ondevicelight","sidebar","crypto","onabort","onblur","onfocus","onauxclick","oncanplay","oncanplaythrough","onchange","onclick","onclose","oncontextmenu","ondblclick","ondrag","ondragend","ondragenter","ondragexit","ondragleave","ondragover","ondragstart","ondrop","ondurationchange","onemptied","onended","oninput","oninvalid","onkeydown","onkeypress","onkeyup","onload","onloadeddata","onloadedmetadata","onloadend","onloadstart","onmousedown","onmouseenter","onmouseleave","onmousemove","onmouseout","onmouseover","onmouseup","onwheel","onpause","onplay","onplaying","onprogress","onratechange","onreset","onresize","onscroll","onseeked","onseeking","onselect","onshow","onstalled","onsubmit","onsuspend","ontimeupdate","onvolumechange","onwaiting","onselectstart","ontoggle","onpointercancel","onpointerdown","onpointerup","onpointermove","onpointerout","onpointerover","onpointerenter","onpointerleave","ongotpointercapture","onlostpointercapture","onmozfullscreenchange","onmozfullscreenerror","onanimationcancel","onanimationend","onanimationiteration","onanimationstart","ontransitioncancel","ontransitionend","ontransitionrun","ontransitionstart","onwebkitanimationend","onwebkitanimationiteration","onwebkitanimationstart","onwebkittransitionend","onerror","speechSynthesis","onafterprint","onbeforeprint","onbeforeunload","onhashchange","onlanguagechange","onmessage","onmessageerror","onoffline","ononline","onpagehide","onpageshow","onpopstate","onstorage","onunload","localStorage","origin","isSecureContext","indexedDB","caches","sessionStorage","document","location","top","addEventListener","removeEventListener","dispatchEvent"];

jsproberesults=[];for (name in this) {  
if ((blacklist.includes(name) == false) && (name.startsWith('wn_') == false)){jsproberesults.push('"'+name+'"')};}
var full = jsproberesults.join(','); console.log(full);     
        
        """
        self.jsinjector.execute_javascript(self.driver, script_to_include)
        print('')
        print('')
        input("Press ENTER to return to menu.")
        
    def run_lone_javascript_functions(self):
        print("getting global window object")
        globalitems=[]
        noargfunctions=[]
        properrors=0
        try:
            javascript="jsproberesults=[];for (name in this) {  try{jsproberesults.push( {'name':''+name, 'value': ''+this[name]})}catch(err){var anyerror='ignore'};};return jsproberesults"
            jsresults = self.executeJavascriptAndReturnArray(javascript)
            for logline in jsresults:
                if '[native code]' not in logline['value'] and 'jsproberesults' not in logline['name']:
                    globalitems.append(logline)
            
            print(str(len(globalitems))+' global items found')
            for record in globalitems:
                if not record['name'].startswith('wn_'):
                    if record['value'].startswith('function '+record['name']+'()') or record['value'].startswith('function ()'):
                        noargfunctions.append(record['name'])
                    #print '\t'+record['name']+': '+record['value']
            
            
            print("Found "+str(len(noargfunctions))+" lone Javascript functions")
            for record in noargfunctions:
                print("\t"+record)
            print("")
            
            if len(noargfunctions) > 0: 
                print("Calling "+str(len(noargfunctions))+" lone Javascript functions")
                for record in noargfunctions:
                    if not record.startswith("wn_"):
                        print("\tCalling %s()"%record)
                        javascript = record+"()"
                        try:
                            self.driver.execute_script(javascript)
                        except:
                            pass
            
                
        except WebDriverException as e:
            print("Selenium Exception: Message: "+str(e))
        except:
            print('probe_window FAILED')
            print("Unexpected error:", sys.exc_info()[0])
            raise

        print('')
        input("Press ENTER to return to menu.")

    def show_cookies(self):
        self.jsinjector.execute_javascript(self.driver, 'wn_showCookie()')
        print('')
        print('')
        input("Press ENTER to return to menu.")

    def dump_browser_objects(self, filepath='libs/javascript/browser_builtins.txt'):
        try:
            self.driver.get('about:blank')
            objects = self.driver.execute_script('return Object.getOwnPropertyNames(this);')
            with open(filepath, 'w') as fh:
                for name in sorted(objects):
                    fh.write(name + '\n')
            print(f'Saved {len(objects)} objects to {filepath}')
        except WebDriverException as e:
            print(f'Selenium Exception: Message: {str(e)}')
        input("Press ENTER to return to menu.")



            
    def executeJavascriptAndReturnArray(self, javascript):
        try:
            self.clearAlertBox()
            return self.driver.execute_script(javascript)
        except WebDriverException as e:
            print("Selenium Exception: Message: "+str(e))
        except:
            print('probe_window FAILED')
            print("Unexpected error:", sys.exc_info()[0])
            raise

    def clearAlertBox(self):
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
        except:
            pass
        
    
    def confirm(self, message):
        bah = input(message+" (Y/n):")
        if bah == 'Y' or bah == 'y' or bah == '':
            return True
        if bah == 'N' or bah == 'n':    
            return False
        return self.confirm(message)
