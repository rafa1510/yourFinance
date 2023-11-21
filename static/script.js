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
    const loginNavbar = document.querySelector(".loginNavbarContainer");
    const navbar = document.querySelector(".navbarContainer");
    const links = document.querySelector(".navbarItemsContainer");
    if (links.style.visibility === "visible")
    {
        navbar.setAttribute("style", "height: 5rem");
        links.setAttribute("style", "visibility: none");
    }
    else
    {
        navbar.setAttribute("style", "height: 17rem");
        links.setAttribute("style", "visibility: visible");
    }
}

function toggleLoginMenu()
{
    const loginNavbar = document.querySelector(".loginNavbarContainer");
    const links = document.querySelector(".navbarItemsContainer");
    if (links.style.visibility === "visible")
    {
        loginNavbar.setAttribute("style", "height: 5rem");
        links.setAttribute("style", "visibility: none");
    }
    else
    {
        loginNavbar.setAttribute("style", "height: 11rem");
        links.setAttribute("style", "visibility: visible");
    }
}

// Line and Bar Chart Buttons

const lineButton = document.querySelector(".lineButton");
const barButton = document.querySelector(".barButton");

// Chart Header Title

const chartTitle = document.querySelector(".chartTitle")

// Chart container to add/remove margin
const chartContainer = document.querySelector(".canvasContainer")

// Main functions to create the charts

function createBarChart() 
{
  // Bar Chart
  const data = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
    datasets: [{
      label: 'Expenses',
      data: [1800, 1650, 1940, 2068, 2345, 2934, 3068],
      backgroundColor: [
        'rgba(255, 26, 104, 0.4)'
      ],
      borderWidth: 3,
      borderColor: 'rgba(255, 26, 104, 0.4)',
      pointStyle: false
    },
    {
      label: 'Income',
      data: [3600, 2459, 1264, 4871, 8924, 2615, 1784],
      backgroundColor: [
        'rgba(75, 192, 192, 0.4)'
      ],
      borderWidth: 3,
      borderColor: 'rgba(75, 192, 192, 0.4)',
      pointStyle: false
    }]
  };

  // config 
  const config = {
    type: 'bar',
    data,
    options: {
      
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      }
    }
  };

  // render init block
  const barChart = new Chart(
    document.getElementById('myChart'),
    config
  );

  // Set up Line Chart Button
  lineButton.addEventListener("click", () => {
    chartTitle.textContent = 'Net Worth';
    barChart.destroy();
    createLineChart();
  })  
}

function createLineChart()
{
  // Line Chart
  const data = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
    datasets: [{
      label: 'Net Worth',
      data: [1800, 1650, 1940, 2068, 2345, 2934, 3068],
      backgroundColor: [
        'rgba(255, 26, 104, 0.2)',
        'rgba(54, 162, 235, 0.2)',
        'rgba(255, 206, 86, 0.2)',
        'rgba(75, 192, 192, 0.2)',
        'rgba(153, 102, 255, 0.2)',
        'rgba(255, 159, 64, 0.2)',
        'rgba(0, 0, 0, 0.2)'
      ],
      borderColor: [
        'rgba(255, 26, 104, 1)',
        'rgba(54, 162, 235, 1)',
        'rgba(255, 206, 86, 1)',
        'rgba(75, 192, 192, 1)',
        'rgba(153, 102, 255, 1)',
        'rgba(255, 159, 64, 1)',
        'rgba(0, 0, 0, 1)'
      ],
      borderWidth: 3,
      borderColor: '#6cc3d5',
      pointStyle: false,
      pointradius: 15,
      radius: 15
    }]
  };

  // config 
  const config = {
    type: 'line',
    data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      }
    }
  };

  // render init block
  const lineChart = new Chart(
    document.getElementById('myChart'),
    config
  );

  // Set up Bar Chart Button
  barButton.addEventListener("click", () => {
    chartTitle.textContent = 'Expenses vs Income';
    lineChart.destroy();
    createBarChart();
  })
}

// Call lineChart on initial page load
createLineChart();