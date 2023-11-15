// Logo slide in animation

/*
const title = document.querySelector(".titleContainer")

title.addEventListener("animationend", () => {
    title.setAttribute("style", "display: none");
})
*/

// Mobile menu interactivity
function toggleMenu()
{
    const navbar = document.querySelector(".navbarContainer");
    const links = document.querySelector(".navbarItemsContainer");
    if (links.style.visibility === "visible")
    {
        navbar.setAttribute("style", "height: 5rem");
        links.setAttribute("style", "visibility: none");
    }
    else
    {
        navbar.setAttribute("style", "height: 20rem");
        links.setAttribute("style", "visibility: visible");
    }
}

// Google Chart

google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawChart);

function drawChart() 
{
  var data = google.visualization.arrayToDataTable
    (
        [
            ['Month', 'Total'],
            ['Jan',  1000],
            ['Feb',  1170],
            ['Mar',  1339],
            ['Apr',  1784]
        ]
    );

  var options = 
  {
    theme: 'material',
    curveType: 'function',
    legend: 'none',
    chartArea:{left:60,right:10, width:"100%", height:"80%"}
  };

  var chart = new google.visualization.LineChart(document.getElementById('chart_div'));

  chart.draw(data, options);
}