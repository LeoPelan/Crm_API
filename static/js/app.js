'use strict';   // See note about 'use strict'; below

var app = angular.module('app', [
 'ngRoute',
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
    $scope.client_list = [];
    $scope.success = '';
    $scope.error = '';

    // list
    $http.get('http://localhost:5000/api/client/list').then(function(res) {
        console.log(res);
        $scope.client_list = res.data.client_list;
    }, function (err) {
        console.log(err);
    });

    // delete
    $scope.delete = function(client) {
        $scope.success = $scope.error = '';
        $http.get('http://localhost:5000/api/client/delete/'+client._id.$oid).then(function(res) {
            console.log(res);
            if (res.data.success) {
                $scope.client_list.splice($scope.client_list.indexOf(client), 1);
                $scope.success = 'Le client ' + client.lastname + ' ' + client.firstname + 'a été supprimé';
            } else {
                $scope.error = 'Erreur lors de la suppression du client ' + client.lastname + ' ' + client.firstname;
            }
        }, function (err) {
            $scope.error = 'Erreur lors de la suppression du client ' + client.lastname + ' ' + client.firstname;
            console.log(err);
        });
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
            console.log("Show errors");
        }
    };

}]);

app.controller('EditController', ['$scope', '$routeParams', '$http', function($scope, $routeParams, $http) {
    $scope.form = {};
    $scope.client = {};

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
                }
            }, function (err) {
                console.log(err);
                $scope.error = "Erreur lors de la mise à jour du client";
            });
        } else {
            console.log("Show errors");
        }
    };
}]);
