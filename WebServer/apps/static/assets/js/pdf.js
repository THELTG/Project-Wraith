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
                var Identifier = row.insertCell(0);
                var Host_Name = row.insertCell(1);
                var OS_Version = row.insertCell(2);
                var IP_Address = row.insertCell(3);
                var Last_Tested = row.insertCell(4);
                var download_report = row.insertCell(5);
                Identifier.innerHTML = rows[i][0];
                Host_Name.innerHTML = rows[i][1];
                OS_Version.innerHTML = rows[i][2];
                IP_Address.innerHTML = rows[i][3];
                Last_Tested.innerHTML = rows[i][4];
                download_report.innerHTML = `<button type="button" class="btn btn-outline-primary" title="Download" onclick="pdfgen('${rows[i][0]}', '${rows[i][0]}_${rows[i][1]}')">Download</button>`;
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
        const currentDate = new Date();
        const formattedDate = `${currentDate.getUTCFullYear()}-${(currentDate.getUTCMonth() + 1).toString().padStart(2, '0')}-${currentDate.getUTCDate().toString().padStart(2, '0')}`;
        link.download = `report_${filename}_${formattedDate}.pdf`;
        link.click();
    })
    .catch(error => {
        console.error("Error fetching PDF:", error);
    });
}