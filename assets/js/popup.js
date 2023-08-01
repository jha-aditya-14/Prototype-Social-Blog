function openUpdateModal(id, userId, csrfToken) {
    var modal = document.getElementById("updateModal" + id);
    var form = document.getElementById("updateprojectsform" + id);
    form.setAttribute("method", "POST");
    form.action = "/" + userId + "/update-blog/" + id + "/";
    modal.style.display = "block";
}

function closeUpdateModal(id) {
    document.getElementById("updateModal" + id).style.display = "none";
}

