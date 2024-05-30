from django.http import HttpResponse


# TODO: I have no clue how to serve this from a JS file
# TODO: PLS FIND A WAY TO MOVE THIS OUT OF HERE :(
def service_worker(request):
    data = (
        'importScripts("https://www.gstatic.com/firebasejs/9.18.0/firebase-app-compat.js");'
        'importScripts("https://www.gstatic.com/firebasejs/9.18.0/firebase-messaging-compat.js"); '
        "var firebaseConfig = {"
        '        apiKey: "AIzaSyBWBYDF68ic-f8vT18_JWKoIJOXHolp_n4",'
        '        authDomain: "oceanview-9bd7c.firebaseapp.com",'
        '        projectId: "oceanview-9bd7c",'
        '        storageBucket: "oceanview-9bd7c.appspot.com",'
        '        messagingSenderId: "771961665424",'
        '        appId: "1:771961665424:web:cd47c0b171cdc7e0a82515",'
        '        measurementId: "G-7LMV2TM26W"'
        " };"
        "firebase.initializeApp(firebaseConfig);"
        "const messaging=firebase.messaging();"
        "messaging.onBackgroundMessage((payload) => {"
        "   console.log(payload);"
        "   self.clients.matchAll({includeUncontrolled: true})"
        "   .then(function (clients) {"
        "       console.log(clients); "
        "       for (const client of clients) {"
        "           const url = new URL(client.url);"
        "           console.log(url.pathname);"
        "           if (url.pathname === '/admin/') {"
        "               client.postMessage(payload);"
        "           };"
        "       };"
        "   });"
        "}, e => console.log(e));"
    )

    return HttpResponse(data, content_type="text/javascript")
