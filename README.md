# Webnuke README

Webnuke is a console based python application useful when pentesting web based applications.

## Prerequisites

- Python 3
- Google Chrome and a matching Chromedriver available in your `PATH`

## Installation

Install Webnuke using pip:

```bash
pip install .
```


To run:
```
python console.py
```
The console also supports running Chrome in headless mode with the `--headless` flag:
```
python console.py --headless https://example.com
```
Network traffic is logged automatically when the console exits. HAR files are
saved into the `har_logs` directory by default; use `--har <dir>` to change the
output location.

### QuickDetect CLI

Run QuickDetect directly from the command line without the curses interface. Use the optional `--log`/`-l` flag to write results to a file. A screenshot of the target page can also be saved with `--screenshot`/`-s`. Use `--headless` to run Chrome without a GUI. Pass `--json` to emit the findings in JSON format (optionally to a file):

```bash
python quickdetect_cli.py https://example.com
python quickdetect_cli.py https://example.com --log scan.log
python quickdetect_cli.py https://example.com -s page.png
python quickdetect_cli.py https://example.com --headless
python quickdetect_cli.py https://example.com --json results.json
```
Detect technologies in use not by parsing files or applying regex to file names but from Javascript variables and HTML elements on the page.

## New Features

- Detect cloud service providers based on IP lookup
- Identify email providers via MX records
- Office 365 and Microsoft Bookings detection
- Terminal state reset on exit
- Basic unit tests to help ensure reliability
- Main menu items can also be selected by entering their number
- Detect window.name usage and generate exploit file
- Builtin browser functions are highlighted in the Javascript shell
- DNS history shows IP owner
- DNS history saved to dns_history/<domain>_<timestamp>.txt
- Nmap SSL certificate scan for historical IPs with results saved to dns_history


## JSCONSOLE

The jsconsole option allows you to execute javascript or run internal webnuke javascript.

Enter the Javascript to run and start a new line with @@@ to execute in the browser

### Demo:
```javascript
var msg="hello world";
alert(msg);
@@@
```

### To escape back to menu
```javascript
quit()
@@@
```


### Internal Webnuke Javascript Functions
```
wn_help() - Shows WebNuke Help
wn_findMethodsOfThis() - print javascript methods
wn_getMethodsPlusCode() - print javascript methods and code
wn_getFunctions() - returns array of javascript functions
wn_listFunctions() - print javascript function names
wn_findStringsWithUrls() - Try and locate urls within Javascript strings
wn_showHiddenFormElements() - Show hidden form elements in the browser
wn_showPasswordFieldsAsText() - Show password fields as text in the browser
wn_showAllHTMLElements() - Set CSS visibility to visible on all HTML elements in the browser
wn_showAngularAppName() - Show AngularJS Main Application Name
wn_showAngularDeps() - Show AngularJS Main Dependencies
wn_showAngularMainClasses() - Show AngularJS Main Classes
wn_showAngularAllClasses() - Show AngularJS All Classes
wn_testNgResourceClasses() - Test ngResource Classes
wn_showAngularRoutes() - Show AngularJS URL Routes
```

## HTML tools menu

The HTML tools can be used to expose hidden form elements and can also control the browser by clicking every HTML elements on the page. 

The click every element option can take abit of time to complete but can be helpful flushing out urls for the site.

The type 'test' option is useful when dealing with Ajax calls.
                                        
### HTML Options                                                                        
1. Show hidden form elements
2. Turn password fields into text
3. Turn css visibility on for all HTML elements
4. Click every element on the page
5. Type 'test' into every text box
6. Removes hidden & hide from classnames
7. Show all modals (modal fade -> modal fade show)
8. Refresh current page


## Javascript

### Javascript Options
                                                                              
1. Find URLS within Javascript Global Properties
2. Show Javascript functions of Document
3. Run all js functions without args
4. Show Cookies accessable by Javascript
5. Walk Javascript Functions
6. Javascript Shell
7. Update builtin object list


## AngularJS

The main advantage of the AngularJS option is the ability to try and attempt data extraction from any service or api defined using the AngularJS ngResource class within the AngularJS web application.

### AngularJS Options

1. Show Main Application Name                                              
2. Show Routes (Urls to things!)                                                            
3. Show Dependencies                                                       
4. Show Main Classes                                                       
5. Show All Classes                                                        
6. Test classes relying on ngResource 


## Spider

Spider will crawl the current url using the awesome KitchenSinks resource by FuzzDB

### Spider Options

1. Set Url to spider                                                       
2. Run Kitchensinks in foreground


## Followme

The followme option is useful for testing authenicated access, this option will open another browser instance and visit the urls being visited by the orinigal browser instance.

1. login as an a user
2. activate followme
3. click around the web application using the browser thats currently logged in
4. Urls visited will be loaded in the unauthenicated second browser instance


## Brute

The brute option will attempt to brute force login screens, first the user has to identify the login and password fields by supplying nukeuser into the username field amd nukepass into the password field.

The username and password list is limited and left to the user to supply/code.


## AWS

The aws option will attempt to detect if any image files, css files, javascript files, meta tags and link tags reference a url that points to an AWS S3 Bucket.

## Running the Tests

Execute the unit tests with:

```bash
python -m pytest
```

