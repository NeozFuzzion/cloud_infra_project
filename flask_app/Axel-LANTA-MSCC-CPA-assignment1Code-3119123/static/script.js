'use strict';

window.addEventListener('load', function () {
    console.log(document.cookie)
    // get the signout button and add an onclick listener to it
    document.getElementById('sign-out').onclick = function() {
        // ask firebase to sign out the user
        firebase.auth().signOut();
        document.cookie = "token=;path=/";
        window.location.replace("/")
    };
    var uiConfig = {
        
        signInSuccessUrl: window.location.href,  // where in the application we will redirect to on a successful user login
        signInOptions: [
            // permit email authentication
            firebase.auth.EmailAuthProvider.PROVIDER_ID
        ]
    };

    document.getElementById('login').onclick=function(){
        // there is no user signed in so initialise a firebase UI widget and set it on the approriate part of the template
        document.getElementById('login_ui').hidden = false;
        try{
            var ui = new firebaseui.auth.AuthUI(firebase.auth());

            ui.start('#firebase-auth-container', uiConfig);
        } catch{}
    }


    // variable that will be used to determine how firebase will show its UI

    // javascript that will react to whenever the firebase authentication state changes
    firebase.auth().onAuthStateChanged(function(user) {
        // determine if a user is signed in or not
        if(user) {
            // user is signed in so display the sign out button, and login info
            document.getElementById('sign-out').hidden = false;

            // log the user login to console for debug purposes with the name and email address
            console.log('Signed in as '+user.displayName+' ' +user.email);

            // get the id token for the user and set it as a cookie so we can maintain a session
            user.getIdToken().then(function(token) {
                document.cookie = "token=" + token + ";path=/";
            });
        } else {
            
            // hide the signout and login-info fields and clear the token
            document.getElementById('sign-out').hidden = true;
            document.getElementById('login').hidden = false;
            document.cookie = "token=;path=/";
        }
    }, function(error) {
        // if something goes wrong then log the error to console and state the user could not be logged in
        console.log(error);
        alert('Unable to log in: ' + error);
    });

   
    
    
});
window.addEventListener('click', function(e){   
    if (!(document.getElementById('firebase-auth-container').contains(e.target)) && !(document.getElementById('login').contains(e.target))){
        document.getElementById('login_ui').hidden = true;
    }
    });