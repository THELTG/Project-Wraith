function terminal() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var terminaltext = JSON.parse(this.responseText).terminaltext;
            var container = document.getElementById("terminaltext");
            

            terminaltext = terminaltext.split("\n");
            terminaltext.pop();


            // Clear existing content
            container.innerHTML = '';

            // Update Rows
            for(var i= 0; i < terminaltext.length; i++){
                var paraline = document.createElement('p');
                paraline.textContent = terminaltext[i];
                // Set the class attribute
                paraline.classList.add('mt-3', 'ml-3');

                // Set the style attribute
                paraline.style.color = '#39FF14';
                container.appendChild(paraline);
            }
        }
    };
    xhttp.open("GET", "/update_terminal", true);
    xhttp.send();
}



function clear_txt() {
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/clear_txt", true)
    xhttp.send()
}

clear_txt()

var intervalId = setInterval(terminal, 1000);