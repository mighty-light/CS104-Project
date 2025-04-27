document.addEventListener("DOMContentLoaded", () => {
    const plot = document.querySelector("#plot_image");
    const link = document.createElement('a');
    link.href = plot.src;
    
    plot.addEventListener("click", () => {
        document.body.appendChild(link);
        link.click();
        document.removeChild(link);
    })
})


