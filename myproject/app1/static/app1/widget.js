fetch("/static/app1/config/config.json")
.then(response => response.json())
.then(config => {

    document.title = config.companyName;

    document.querySelector("h4").innerHTML = config.widgetTitle;

    document.querySelector(".btn-primary").innerHTML = config.buttonText;

});