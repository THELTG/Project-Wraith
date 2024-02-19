


function welcome(){
    var image = document.getElementById("welcome-img")
    var txt = document.getElementById("welcome-txt")

    image.style.opacity = 1
    image.style.transition = "3.8s"

    txt.style.opacity = 1
    txt.style.transition = "3.8s"
    
}

welcome()


setTimeout( ()=> {window.location.href='agents.html'}, 4500);

