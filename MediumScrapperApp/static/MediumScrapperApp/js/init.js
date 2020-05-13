$(document).on("click", "#search-btn", function(e) {

    user_query = document.getElementById("tags-input").value;
    if (user_query.trim() == "") {
        return;
    }
    $("#search-loader").show()
    $.ajax({
        url: '/get-articles-based-on-query/',
        type: "POST",
        data: {
            user_query: user_query,
        },
        success: function(response) {
            if (response["status"] == 200) {
                append_search_results(response["articles_data"])
                append_pagination_data(response["no_of_results"],1,user_query)
            } else if (response["status"] == 301) {
                $(".pagination-div").html("")
                $(".search-results").html("")
                append_suggested_tags(response["suggested_tags"])
            }
            $("#search-loader").hide()
        }
    });
});

function append_suggested_tags(suggested_tags){
}

function get_result_for_selected_tag(tag) {
    document.getElementById("tags-input").value = tag
    $("#search-btn").click()
}

function append_pagination_data(total_results,current_page,user_query) {
    no_of_pages = Math.ceil(total_results/10)
    html = '<nav aria-label="Page navigation example">\
      <ul class="pagination">'
    for (var i = 1; i <(no_of_pages+1) ; i++) {
        console.log(i)
        if (i == current_page){
            html += '<li class="page-item disabled"><a class="page-link" href="javascript:void(0)">'+i+'</a></li>'
        }
        else{
            html += '<li class="page-item" ><a class="page-link" href="javascript:void(0)" onclick=get_articles_by_page('+i+",'"+user_query+"') >"+i+'</a></li>'
        }
    }
    html += '</ul>\
    </nav>'
    $(".pagination-div").html(html)
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
                            <span class="small col-sm-4">'+Math.ceil(articles_data[i]["reading_time"])+' min read</span> \
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
function get_articles_by_page(page_no,user_query){
    $("#search-loader").show()
    $(".search-results").hide()
    $.ajax({
        url: '/get-next-n-articles/',
        type: "POST",
        data: {
            user_query: user_query,
            start: page_no*10,
            limit: 10,
        },
        success: function(response) {
            $(".search-results").html("")
            $(".search-results").show()

            if (response["status"] == 200) {
                append_search_results(response["articles_data"])
                append_pagination_data(response["no_of_results"],page_no,user_query)
            } 
            $("#search-loader").hide()
        }
    });
}
