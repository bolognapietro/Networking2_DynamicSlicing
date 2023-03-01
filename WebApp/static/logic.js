function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function networkON()
{
    let xhttp = new XMLHttpRequest();
    xhttp.open("GET", "networkON");

    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) 
        {
            changeScenario(0);
        }
    };

    xhttp.send();
}

function networkOFF()
{
    let xhttp = new XMLHttpRequest();
    xhttp.open("GET", "networkOFF");

    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) 
        {
            hideLoading();
            hideNetwork();
        }
    };

    xhttp.send();
}

function mapNetworkScenarios(coldstart = false)
{
    let find = function(name) {
        var table = document.getElementsByTagName("table")[0];
        var rows = table.getElementsByTagName("tr");

        var selected = null;

        for(let i=1; i<rows.length; i++)
        {
            let row = rows[i];
            let td = row.getElementsByTagName("td")[0];

            if(td.innerText != name)
                continue

            selected = row;
            break
        }

        return selected
    };

    function isJsonString(str) 
    {
        try 
        {
            str = JSON.parse(str);
            JSON.parse(str);
        } 
        catch (e) 
        {
            return false;
        }

        return true;
    }

    let xhttp = new XMLHttpRequest();
    xhttp.open("GET", "mapNetworkScenarios");

    xhttp.onreadystatechange = async function () {
        if (this.readyState == 4 && this.status == 200) 
        {
            let data = this.responseText;
            
            document.querySelectorAll(".rounded-button").forEach((node) => {
                node.classList.remove("active");
                node.classList.add("inactive");
            });

            if(!isJsonString(data))
            {
                var table = document.getElementsByTagName("table")[0];
                var rows = table.getElementsByTagName("tr");

                for(let i=1; i<13; i++)
                {
                    let row = rows[i];
                    let td = row.getElementsByTagName("td")[2];
                    td.innerText = "-"
                }
            }
            else
            {
                data = JSON.parse(data);
                data = JSON.parse(data);

                scenario = data["scenario"]
                let name = (scenario == -1) ? "-" : "";

                for(let i=0; i<data["network"].length; i++)
                {
                    let pair = data["network"][i];
                    
                    let host1 = pair["host1"];
                    let host1_row = find(host1["name"]);
                    let host1_td = host1_row.getElementsByTagName("td");
                    host1_td[2].innerText = (name.length == 0) ? host1["speed"] : name;
                    host1_td[4].getElementsByTagName("span")[0].className = (host1["speed"] == "-") ? "circle circle-red" : "circle circle-green";

                    let host2 = pair["host2"];
                    let host2_row = find(host2["name"]);
                    let host2_td = host2_row.getElementsByTagName("td");
                    host2_td[2].innerText = (name.length == 0) ? host2["speed"] : name;
                    host2_td[4].getElementsByTagName("span")[0].className = (host2["speed"] == "-") ? "circle circle-red" : "circle circle-green";
                }

                var rows = document.getElementsByTagName("tr");

                for(let i=9; i<13; i++)
                {
                    let row = rows[i];
                    let td = row.getElementsByTagName("td");
                    
                    speed = "100 Mbits/sec";
                    className = "circle circle-green";

                    if(scenario == 4 && i == 11)
                    {
                        speed = "-";
                        className = "circle circle-red";
                    }

                    td[3].innerText = speed;
                    td[4].getElementsByTagName("span")[0].className = className;
                }
                
                console.log(scenario)
                
                if(scenario == 0)
                {
                    rows[1].getElementsByTagName("td")[3].innerText = "100 Mbits/sec";
                    rows[2].getElementsByTagName("td")[3].innerText = "100 Mbits/sec";
                    rows[3].getElementsByTagName("td")[3].innerText = "100 Mbits/sec";
                    rows[4].getElementsByTagName("td")[3].innerText = "100 Mbits/sec";
                    rows[5].getElementsByTagName("td")[3].innerText = "-";
                    rows[6].getElementsByTagName("td")[3].innerText = "-";
                    rows[7].getElementsByTagName("td")[3].innerText = "-";
                    rows[8].getElementsByTagName("td")[3].innerText = "-";

                    document.getElementById("scenario").getElementsByTagName("img")[0].src = "static/default.png";
                }
                else if(scenario == 1)
                {
                    rows[1].getElementsByTagName("td")[3].innerText = "20 Mbits/sec";
                    rows[2].getElementsByTagName("td")[3].innerText = "20 Mbits/sec";
                    rows[3].getElementsByTagName("td")[3].innerText = "100 Mbits/sec";
                    rows[4].getElementsByTagName("td")[3].innerText = "100 Mbits/sec";
                    rows[5].getElementsByTagName("td")[3].innerText = "80 Mbits/sec";
                    rows[6].getElementsByTagName("td")[3].innerText = "80 Mbits/sec";
                    rows[7].getElementsByTagName("td")[3].innerText = "-";
                    rows[8].getElementsByTagName("td")[3].innerText = "-";

                    document.getElementById("scenario").getElementsByTagName("img")[0].src = "static/upper.png";
                }
                else if(scenario == 2)
                {
                    rows[1].getElementsByTagName("td")[3].innerText = "100 Mbits/sec";
                    rows[2].getElementsByTagName("td")[3].innerText = "100 Mbits/sec";
                    rows[3].getElementsByTagName("td")[3].innerText = "20 Mbits/sec";
                    rows[4].getElementsByTagName("td")[3].innerText = "20 Mbits/sec";
                    rows[5].getElementsByTagName("td")[3].innerText = "-";
                    rows[6].getElementsByTagName("td")[3].innerText = "-";
                    rows[7].getElementsByTagName("td")[3].innerText = "80 Mbits/sec";
                    rows[8].getElementsByTagName("td")[3].innerText = "80 Mbits/sec";

                    document.getElementById("scenario").getElementsByTagName("img")[0].src = "static/lower.png";
                }
                else if(scenario == 3)
                {
                    rows[1].getElementsByTagName("td")[3].innerText = "20 Mbits/sec";
                    rows[2].getElementsByTagName("td")[3].innerText = "20 Mbits/sec";
                    rows[3].getElementsByTagName("td")[3].innerText = "20 Mbits/sec";
                    rows[4].getElementsByTagName("td")[3].innerText = "20 Mbits/sec";
                    rows[5].getElementsByTagName("td")[3].innerText = "80 Mbits/sec";
                    rows[6].getElementsByTagName("td")[3].innerText = "80 Mbits/sec";
                    rows[7].getElementsByTagName("td")[3].innerText = "80 Mbits/sec";
                    rows[8].getElementsByTagName("td")[3].innerText = "80 Mbits/sec";

                    document.getElementById("scenario").getElementsByTagName("img")[0].src = "static/all.png";
                }
                else if(scenario == 4)
                {
                    rows[1].getElementsByTagName("td")[3].innerText = "10 Mbits/sec";
                    rows[2].getElementsByTagName("td")[3].innerText = "10 Mbits/sec";
                    rows[3].getElementsByTagName("td")[3].innerText = "10 Mbits/sec";
                    rows[4].getElementsByTagName("td")[3].innerText = "10 Mbits/sec";
                    rows[5].getElementsByTagName("td")[3].innerText = "40 Mbits/sec";
                    rows[6].getElementsByTagName("td")[3].innerText = "40 Mbits/sec";
                    rows[7].getElementsByTagName("td")[3].innerText = "40 Mbits/sec";
                    rows[8].getElementsByTagName("td")[3].innerText = "40 Mbits/sec";

                    document.getElementById("scenario").getElementsByTagName("img")[0].src = "static/broken.png";
                }

                if(scenario != -1)
                {
                    let button = document.querySelectorAll(".rounded-button")[scenario];
                    button.classList.remove("inactive");
                    button.classList.add("active");
                }
            }
            
            hideLoading();

            if(!coldstart)
            showNetwork();
        }
    };

    xhttp.send();
}

function ping()
{
    let xhttp = new XMLHttpRequest();
    xhttp.open("GET", "ping");

    xhttp.onreadystatechange = async function () {
        if (this.readyState == 4 && this.status == 200) 
        {
            data = this.responseText;
            
            if(data == "true")
                showNetwork();
            else
                hideNetwork();
            
            //await sleep(5000);
            //ping();
        }

        /*
        else if(this.readyState == 4)
        {
            await sleep(5000);
            ping()
        }
        */
    
    };

    xhttp.send();
}

function changeScenario(scenarioId)
{
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "changeScenario");
    xhttp.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');

    xhttp.onreadystatechange = async function () 
    {
        if (this.readyState == 4 && this.status == 200) 
        {
            mapNetworkScenarios();
        }
    };

    xhttp.send("scenarioId="+scenarioId);
}