function showLoading()
{
    if(!document.querySelector(".overlay").hasAttribute("hidden"))
        return;

    window.scrollTo(0, 0);
    
    document.querySelector(".overlay").removeAttribute("hidden");
    document.body.style.overflow = "hidden";
}

function hideLoading()
{
    if(document.querySelector(".overlay").hasAttribute("hidden"))
        return;

    document.querySelector(".overlay").setAttribute("hidden", "");
    document.body.style.overflow = "auto";
}

function showNetwork()
{
    if(!document.getElementById("networkContainer").hidden)
        return

    document.getElementsByClassName("switch-container")[0].getElementsByTagName("input")[0].checked = true;
    document.getElementById("networkContainer").hidden = false;
    document.getElementsByClassName("switch-container")[0].getElementsByTagName("h3")[0].innerText = "Network ON";

    document.getElementById("scenario").hidden = false;
}

function hideNetwork()
{
    if(document.getElementById("networkContainer").hidden)
        return

    document.getElementsByClassName("switch-container")[0].getElementsByTagName("input")[0].checked = false;
    document.getElementById("networkContainer").hidden = true;
    document.getElementsByClassName("switch-container")[0].getElementsByTagName("h3")[0].innerText = "Network OFF";

    document.getElementById("scenario").hidden = true;
}

function updateSwitchText() 
{
    var switchbtn = document.getElementsByClassName("switch-container")[0].getElementsByTagName("input")[0];

    if (switchbtn.checked) 
    {
        showLoading();
        networkON();
    } 
    else 
    {
        showLoading();
        networkOFF();
    }
}

function init()
{
    showLoading();
    hideNetwork();

    var buttons = document.querySelectorAll(".rounded-button");
    const popup = document.getElementById("popup");

    for (var i = 0; i < buttons.length; i++) 
    {
        let scenarioId = i;

        buttons[i].addEventListener("click", function() {
            
            if(this.classList.contains("active"))
                return;
                
            for (var j = 0; j < buttons.length; j++) 
            {
                buttons[j].classList.remove("active");
                buttons[j].classList.add("inactive");
            }

            this.classList.remove("inactive");
            this.classList.add("active");

            // load scenario via loading(f)
            showLoading();
            changeScenario(scenarioId);
        });

        let text = "";

        if (i == 0)
            text = "Only hosts h1, h2, h3, h4 are connected.";
        else if (i == 1)
            text = "Only hosts h1, h2, h3, h4, h5, h6 are connected.";
        else if (i == 2)
            text = "Only hosts h1, h2, h3, h4, h7, h8 are connected.";
        else if (i == 3)
            text = "All the hosts are connected.";
        else if (i == 4) 
            text = "Switch s3 is broken";
        
        buttons[i].addEventListener("mousemove", function(event) 
        {
            const x = event.clientX;
            const y = event.clientY;

            popup.style.display = "block";
            popup.style.left = x + 20 + "px";
            popup.style.top = y + 10 + "px";

            popup.innerText = text;
            popup.style.display = "block";
        });

        buttons[i].addEventListener("mouseout", function() 
        {
            document.getElementById("popup").style.display = "none";
        });

        buttons[i].classList.add("inactive");
    }

    ping();
    mapNetworkScenarios(true);
}