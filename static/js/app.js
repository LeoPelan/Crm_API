'use strict';   // See note about 'use strict'; below

var app = angular.module('app', [
 'ngRoute'
]);

app.config(['$routeProvider',
     function($routeProvider) {
         $routeProvider.
             when('/', {
                 templateUrl: '/static/partials/index.html'
             }).
             when('/client/add', {
                 templateUrl: '/static/partials/add.html'
             }).
             when('/client/edit/:clientId', {
                 templateUrl: '/static/partials/edit.html'
             }).
             otherwise({
                 redirectTo: '/'
             });
    }]);

app.controller('HeaderController', ['$scope', function($scope) {
    $scope.title = "PyCrm";
}]);

app.controller('IndexController', ['$scope', '$http', function($scope, $http) {
    $scope.client_list = list();
    $scope.search = {};
    $scope.success = '';
    $scope.error = '';

    $scope.load = false;
    $scope.loadMessage = '';

    // list
    function list() {
        $http.get('http://localhost:5000/api/client/list').then(function(res) {
            $scope.client_list = res.data.client_list;
        }, function (err) {
            console.log(err);
        });
    }

    // delete
    $scope.delete = function(client) {
        $scope.success = $scope.error = '';
        $http.get('http://localhost:5000/api/client/delete/'+client._id.$oid).then(function(res) {
            console.log(res);
            if (res.data.success) {
                $scope.client_list.splice($scope.client_list.indexOf(client), 1);
                $scope.success = 'Le client ' + client.lastname + ' ' + client.firstname + ' a été supprimé';
            } else {
                $scope.error = 'Erreur lors de la suppression du client ' + client.lastname + ' ' + client.firstname;
            }
        }, function (err) {
            $scope.error = 'Erreur lors de la suppression du client ' + client.lastname + ' ' + client.firstname;
            console.log(err);
        });
    };

    // search
    $scope.doSearch = function(isValid) {
        $scope.success = $scope.error = '';
        if (isValid) {
            setLoading('Recherche en cours');
            var query = prepareGetParams($scope.search);

            $http.get('http://localhost:5000/api/client/search'+query).then(function(res) {
                console.log(res);
                if (res.data.success) {
                    // GERER LE CAS OU AUCUN CRITERE NEST PASSE
                    $scope.client_list = res.data.client_list;
                    $scope.success = res.data.client_list.length + ' résultat(s)';
                } else {
                    $scope.success = 'Aucun client ne correspond à cette recherche';
                    $scope.client_list = list();
                }
                resetLoading();
            }, function (err) {
                $scope.error = 'Erreur lors de la recherche';
                console.log(err);
                resetLoading();
            });
        } else {
            $scope.error = "Le formulaire n'est pas valide";
        }
    };

    // export
    $scope.export = function() {
        $scope.success = $scope.error = '';
        setLoading('Export en cours');
        $http.get('http://localhost:5000/api/client/export').then(function(res) {
            console.log(res);
            if (res.data.success) {
                $scope.success = 'Les clients ont bien été exportés';
            } else {
                $scope.error = 'Erreur lors de l\'export';
            }
            resetLoading();
        }, function (err) {
            $scope.error = 'Erreur lors de l\'export';
            console.log(err);
            resetLoading();
        });
    };

    // import
    $scope.import = function() {
        $scope.success = $scope.error = '';
        setLoading('Import en cours');
        $http.get('http://localhost:5000/api/client/import').then(function(res) {
            if (res.data.success) {
                if (res.data.users_added > 1) {
                    $scope.success = res.data.users_added + ' clients ont été importés';
                } else {
                    $scope.success = res.data.users_added + ' client à été importé';
                }
                $scope.client_list = list();
            } else {
                $scope.error = 'Une erreur est survenue lors de l\'import';
            }
            resetLoading();
        }, function (err) {
            $scope.error = 'Erreur lors de l\'import';
            console.log(err);
            resetLoading();
        });
    };

    function prepareGetParams(search) {
        var res = '?';
        angular.forEach(search, function(value, key) {
            res += key + '=' + value + '&';
        });
        return res.slice(0, -1);
    }

    function setLoading(message) {
        $scope.load = true;
        $scope.loadMessage = message;
    }

    function resetLoading() {
        $scope.load = false;
        $scope.loadMessage = '';
    }
}]);

app.controller('AddController', ['$scope', '$http', function($scope, $http) {
    $scope.form = {};
    $scope.success = '';
    $scope.error = '';

    // add
    $scope.submit = function(isValid) {
        $scope.success = $scope.error = '';
        if (isValid) {
            $http.post('http://localhost:5000/api/client/add', {newClient: $scope.form}).then(function(res) {
                console.log(res);
                if (res.data.success) {
                    $scope.success = "Le client à bien été ajouté";
                }
            }, function (err) {
                console.log(err);
                $scope.error = "Erreur lors de l'ajout du client";
            });
        } else {
            $scope.error = "Le formulaire n'est pas valide";
        }
    };

}]);

app.controller('EditController', ['$scope', '$routeParams', '$http', function($scope, $routeParams, $http) {
    $scope.form = {};
    $scope.client = {};

    // get client id from route params
    var clientId = $routeParams.clientId;

    // get client
    $http.get('http://localhost:5000/api/client/'+clientId).then(function(res) {
        console.log("cb get client");
        console.log(res);
        if (res.data.success) {
            $scope.client = res.data.client;
        } else {
            $scope.error = 'Impossible de récupérer ce client';
        }
    }, function (err) {
        $scope.error = 'Impossible de récupérer ce client';
        console.log(err);
    });

    // update
    $scope.submit = function(isValid) {
        $scope.success = $scope.error = '';
        delete $scope.client._id; // erreur si on laisse l'id - je comprends pas
        if (isValid) {
            $http.post('http://localhost:5000/api/client/edit/'+clientId, {client: $scope.client}).then(function(res) {
                console.log(res);
                if (res.data.success) {
                    $scope.success = "Le client à bien été mis à jour";
                } else {
                    $scope.error = "Erreur lors de la mise à jour du client";
                }
            }, function (err) {
                console.log(err);
                $scope.error = "Erreur lors de la mise à jour du client";
            });
        } else {
            $scope.error = "Le formulaire n'est pas valide";
        }
    };
}]);
