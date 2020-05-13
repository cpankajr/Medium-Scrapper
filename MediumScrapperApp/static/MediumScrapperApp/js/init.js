$(document).on("click", "#search-btn", function(e) {

    user_query = document.getElementById("tags-input").value;
    if (user_query.trim() == "") {
        return;
    }
    $.ajax({
        url: '/get-articles-based-on-query/',
        type: "POST",
        data: {
            user_query: user_query,
        },
        success: function(response) {

            if (response["status"] == 200) {
                append_search_results(response["articles_data"])
            } else if (response["status"] == 301) {
                append_suggested_tags(response["suggested_tags"])
            }
        }
    });
});

function append_suggested_tags(suggested_tags){
}


function append_search_results(articles_data){
    html = ""
    for (var i = 0; i < articles_data.length; i++) {
        html += '<div class="card bg-light mb-3 w-100">\
                  <div class="card-header">\
                        <div class="row">\
                            <span class="h5 col-sm-12"><b>'+articles_data[i]["author"]+'</b></span>\
                        </div>\
                        <div class="row">\
                            <span class="small col-sm-2">'+articles_data[i]["date"]+'</span>\
                            <span class="small col-sm-4">'+Math.round(articles_data[i]["reading_time"])+' min read</span> \
                        </div>\
                  </div>\
                  <div class="card-body">\
                    <h5 class="card-title">'+articles_data[i]["title"]+'</h5>\
                  </div>\
                  <div class="card-footer" style="border: none;background-color: initial;">\
                    <button type="button" class="btn btn-light btn-outline-danger">\
                            <i class="material-icons" style="vertical-align: sub;">\
                                favorite\
                            </i>\
                            <span class="badge badge-light">'+articles_data[i]["claps"]+'</span>\
                    </button>\
                    <span class="float-right">\
                    </span>\
                  </div>\
                </div>'
    }
    $(".search-results").html(html)
}
