function make_req() {
    var http = new XMLHttpRequest();
    http.onreadystatechange = function() {

        // Timeout
        if (this.readyState == 4 && this.status == 200) {
            var url = http.responseText;

            // Timeout
            if(url === '') {
                return this.ontimeout()
            } else {
                window.location.href = url;
            }
        }

    };
    http.timeout = 40000;
    http.ontimeout = function () {
        if(window.location.pathname !== '/screen/'){
            window.location.href = '/screen';
            return;
        }
        http.abort();
        make_req();
    };
    http.open("GET", "/screen/poll/", true);
    http.send();
}

make_req();
