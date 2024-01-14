
//############################################################ start of terminal output 

function terminal() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var terminaltext = JSON.parse(this.responseText).terminaltext;
            var container = document.getElementById("terminaltext");
            
            //print the strings in terminal.txt of recorded commands
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


// clear the chart.txt and different txt files for terminal
function clear_txt() {
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/clear_txt", true)
    xhttp.send()
}



clear_txt()

var intervalId = setInterval(terminal, 1000);

//#################################################################end of terminal output update


// chart.js data for initialization
const data = {
    labels: [0],
    datasets: [{
        label: 'No. of commands ran in elapsed time',
        data: [
            {x:0,y:0},


        ],
        backgroundColor: 'rgba(255,255,255,1.0)',
        borderColor: 'rgba(255,255,255,0.1)'
    }]
};

//chart.js config for initialization
const config = {
    type: 'line',
    data,
    options: {
        scales:{
            x:{
                title:{
                    display:true,
                    text: 'Time Elapsed',
                    color: 'white'
                }
            },
            y:{
                title:{
                    display:true,
                    text: 'Number of Ran Commands',
                    color: 'white'
                }
            }
        }
    }
}


// initial creation of chart
var newchart = new Chart(
    document.getElementById('graph'),
    config
);









function updateChartlst() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var updatedLst = JSON.parse(this.responseText).updatedLst;

            var datalst = []
            var dataLabel = []


            if (updatedLst != ""){ //if no value in chart.txt (no functions running)
                updatedLst = updatedLst.split(",");


                datalst.push({x: updatedLst[0], y: updatedLst[1].split("\n")[0]}); 
                dataLabel.push(updatedLst[0]);



                addData(newchart,datalst,dataLabel);
            }
            
            
            



        }
    };
    xhttp.open("GET", "/update_lst", true);
    xhttp.send();
}



// chart.js update function
function addData(chart, datalst, dataLabel) {
    var data1 = chart.data.labels.push(dataLabel[0]) //update lables
    var data2 = chart.data.datasets[0].data.push(datalst[0]); //update data
    chart.update();

}


// calls the updategraph function every 1 second to update chart.js dynamically
var updategraph = setInterval(updateChartlst, 1000)












    