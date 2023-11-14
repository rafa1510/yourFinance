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

// Logo slide in animation

const title = document.querySelector(".titleContainer")

title.addEventListener("animationend", () => {
    title.setAttribute("style", "display: none");
})