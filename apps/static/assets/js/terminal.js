function summary() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var summary = JSON.parse(this.responseText).summary;


            if (summary != ""){ //if no value in chart.txt (no functions running)
                updatedLst = summary.split(",");
                console.log(summary)


                document.getElementById("Operation").innerHTML = updatedLst[5]
                document.getElementById("Agent").innerHTML = updatedLst[0]
                document.getElementById("HostIp").innerHTML = updatedLst[1]
                if (updatedLst[2] == "True"){
                    document.getElementById("successRate").innerHTML = "Successful"
                }else{
                    document.getElementById("successRate").innerHTML = "Unsuccessful"
                }
                document.getElementById("numOfCommands").innerHTML= updatedLst[4]
                document.getElementById("timeElapsed").innerHTML = `${updatedLst[3]}(s)`

            }else{
                console.log("no value")
                document.getElementById("Operation").innerHTML = "None"
                document.getElementById("Agent").innerHTML = ""
                document.getElementById("HostIp").innerHTML = ""
                document.getElementById("successRate").innerHTML = ""
                document.getElementById("numOfCommands").innerHTML= ""
                document.getElementById("timeElapsed").innerHTML = ""
            }

        }
    };
    xhttp.open("GET", "/ops_summary", true);
    xhttp.send();
}





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
            if (terminaltext.length <= 6){
                for(var i= 0; i < terminaltext.length; i++){
                    var paraline = document.createElement('p');
                    paraline.textContent = terminaltext[i];
                    // Set the class attribute
                    paraline.classList.add('mt-3', 'ml-3');

                    // Set the style attribute
                    paraline.style.color = '#39FF14';
                    container.appendChild(paraline);
                }
            }else{

                var newlst = terminaltext.slice(-6)
                console.log(newlst)
                for(var i= 0; i < newlst.length; i++){
                    var paraline = document.createElement('p');
                    paraline.textContent = newlst[i];
                    // Set the class attribute
                    paraline.classList.add('mt-3', 'ml-3');

                    // Set the style attribute
                    paraline.style.color = '#39FF14';
                    container.appendChild(paraline);
                }
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
                    text: 'Time Elapsed (s)',
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


summary()

// calls the updategraph function every 1 second to update chart.js dynamically
var updategraph = setInterval(updateChartlst, 1000)


var themecheck = localStorage.getItem("theme"); // changing colour of graph if dashboard is started with light theme
if (themecheck == "light"){
    newchart.options.scales.x.title.color = 'black';
    newchart.options.scales.y.title.color = 'black';
    newchart.data.datasets[0].backgroundColor = 'rgba(0,0,0,1.0)';
    newchart.data.datasets[0].borderColor = 'rgba(0,0,0,0.1)'
    newchart.update();
    document.getElementById("currentOp").style.color = 'rgba(255,255,255,1.0)'
}



// used to update the graph colour in light theme or dark theme
var theme = document.getElementById("theme-switch");
theme.addEventListener('click', ()=> {
    console.log("yes")
    
    function delay(callback){ // creating timmeout function to wait for local storage to update colour theme
        setTimeout(()=> {
            const data = localStorage.getItem("theme");
        callback(data);
        },200)
    }

    delay((currentTheme)=> { 
        console.log(currentTheme)
        if (currentTheme == "dark"){ // dark theme graph
            newchart.options.scales.x.title.color = 'white';
            newchart.options.scales.y.title.color = 'white';
            newchart.data.datasets[0].backgroundColor = 'rgba(255,255,255,1.0)';
            newchart.data.datasets[0].borderColor = 'rgba(255,255,255,0.1)'
            newchart.update();
            
        }else{ // light theme graph
            newchart.options.scales.x.title.color = 'black';
            newchart.options.scales.y.title.color = 'black';
            newchart.data.datasets[0].backgroundColor = 'rgba(0,0,0,1.0)';
            newchart.data.datasets[0].borderColor = 'rgba(0,0,0,0.1)'
            newchart.update();
            document.getElementById("currentOp").style.color = 'rgba(255,255,255,1.0)'
        }
    });

})















    