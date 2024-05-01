
const goView = (src) => {
    $.ajax({
        method: "GET",
        url: src,
        dataType: "html",
        success: function(response) {
            $("#page-main").html(response);
        },
        error: function(err) {
            console.error(err);
        }
    });
}