window.wn_testHTTPClasses = function(){
        console.log('webnuke: AngularJS Testing Classes using $http');
        console.log('-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=');

        // Temporarily replace alert with console logging to prevent popups
        var originalAlert = window.alert;
        window.alert = function(msg){ console.log(msg); };

        try {
                var angular_classes = wn_getAngularAllClasses();
                var drf = [];

                var component_names = [];
                for (var class_record in angular_classes){
                        //console.log("--[ "+angular_classes[class_record]['namespace']+" ]--");
                        var components = angular_classes[class_record]['classes'];

                        angular.forEach(components, function(m){
                                //creane new instance
                                try{
                                        if(component_names.indexOf(m.name) >= 0)
                                        {
                                                // do nothing
                                        }
                                        else
                                        {
                                                component_names.push(m.name);
                                                var api = angular.element(document.body).injector().get(m.name)
                                                var service_name = m.name
                                                if(service_name.startsWith('$') == false)
                                                {
                                                        console.log("Testing "+service_name);
                                                       try{
                                                                if(typeof api.query === 'function'){
                                                                        api.query();
                                                                        drf.push(service_name+".query()");
                                                                }
                                                       }
                                                       catch(err){}

                                                       angular.forEach(api, function(func, fname){
                                                                var fnameLower = fname.toLowerCase();
                                                                if(typeof func === 'function' && (fnameLower.startsWith('get') || (fnameLower.startsWith('query') && fnameLower !== 'query'))){
                                                                        try{
                                                                                func.call(api);
                                                                                drf.push(service_name+"."+fname+"()");
                                                                        }
                                                                        catch(err){}
                                                                }
                                                       });
                                                }
                                        }
                                }
                                catch(err){//console.log("err");
                                        }

                        });
                }

                console.log("Found the following items...");
                for (var x in drf){
                        console.log(drf[x]);
                }
        } finally {
                // Restore original alert function
                window.alert = originalAlert;
        }

};


window.wn_isPromise = function(x){
        try{
                if (typeof x.then === "function"){return true;}
        }
        catch(err){
                console.log("EEEEE");
                console.log(err);
                return false;
                }
};
