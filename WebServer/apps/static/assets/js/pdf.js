


function downloadpdf() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var rows = JSON.parse(this.responseText).rows;
            var table = document.getElementById("download_report");
            // Clear Rows except header row
            while (table.rows.length > 1) {
                table.deleteRow(1);
            }
            // Update Rows
            for(var i= 0; i < rows.length; i++){
                //Update Rows

                var row = table.insertRow();
                var scope = row.insertCell(0);
                var Host_Name = row.insertCell(1);
                var Device_Type = row.insertCell(2);
                var IP_Address = row.insertCell(3);
                var Last_Tested = row.insertCell(4);
                var download_report = row.insertCell(5);
                scope.innerHTML = i+1;
                Host_Name.innerHTML = rows[i][0];
                Device_Type.innerHTML = rows[i][1];
                IP_Address.innerHTML = rows[i][2];
                Last_Tested.innerHTML = `6/11/2023`;
                download_report.innerHTML = `<button type="button" class="btn btn-outline-primary" title="Download" onclick="pdfgen('${rows[i][0]}', '${rows[i][0]}_${rows[i][4]}_${rows[i][2]}.pdf')">Download</button>`;
            }
        }
    };
    xhttp.open("GET", "/report_rows", true);
    xhttp.send();
}

downloadpdf()

function pdfgen(id, filename) {
    fetch(`/generate_pdf/${id}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        } else {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
    })
    .then(blob => {
        var link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = `report_${filename}.pdf`;
        link.click();
    })
    .catch(error => {
        console.error("Error fetching PDF:", error);
    });
}