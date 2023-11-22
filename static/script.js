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