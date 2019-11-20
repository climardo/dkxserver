// Update file-browser text onchange
const file_browser = document.getElementById("file-browser")
file_browser.addEventListener("change", update_filename)

function update_filename() {
    var file_label = document.getElementById("file-label")
    var filename = file_browser.value.substring(file_browser.value.lastIndexOf('\\') + 1)
    file_label.innerHTML = filename
    console.log(filename)
}