function updateConnections() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var clients = JSON.parse(this.responseText).clients;
            var table = document.getElementById("update_connections");
            // Clear Rows except header row
            while (table.rows.length > 1) {
                table.deleteRow(1);
            }
            // Update Rows
            for(var i= 0; i < clients.length; i++){
                //Update Rows
                    var row = table.insertRow();
                    var Identifier = row.insertCell(0);
                    var Host = row.insertCell(1);
                    var Username = row.insertCell(2);
                    var IP_Address= row.insertCell(3);
                    var OS_Version = row.insertCell(4);
                    var Status = row.insertCell(5);
                    var Last_Seen = row.insertCell(6);
                    var Terminate = row.insertCell(7);
                    Identifier.innerHTML = clients[i][1];
                    Host.innerHTML = clients[i][3];
                    Username.innerHTML = clients[i][4];
                    IP_Address.innerHTML = clients[i][2];
                    OS_Version.innerHTML = clients[i][8];
                    Terminate.innerHTML = `<button type="submit" class="btn btn-outline-primary" onclick="terminateConnection(${clients[i][0]})">Terminate</button>`;
                    if (Number.isInteger(clients[i][6])){
                        Last_Seen.innerHTML = clients[i][6].toString() + " seconds ago"
                    } else {
                        Last_Seen.innerHTML = clients[i][6]
                    }
                    if(clients[i][5] == 'Alive'){
                        Status.innerHTML = '<i class="fas fa-circle text-c-green f-10"></i> ' + clients[i][5];
                    } else {
                        Status.innerHTML = '<i class="fas fa-circle text-c-red f-10"></i> ' + clients[i][5];
                    }
            }
        }
    };
    xhttp.open("GET", "/update_connections", true);
    xhttp.send();
}

setInterval(updateConnections, 5000);

function terminateConnection(id){
    var xhttp = new XMLHttpRequest();
    var url = `/terminate_connections/${id}`
    xhttp.open("POST", url, true);
    xhttp.send();
}