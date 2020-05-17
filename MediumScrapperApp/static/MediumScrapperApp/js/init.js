$(document).on("click", "#search-btn", function(e) {

    user_query = document.getElementById("tags-input").value;
    if (user_query.trim() == "") {
        return;
    }
    $("#search-loader").show()
    $('.suggested-tags').html("")

    search_history_array = get_cookie('search_history_array')
    if (search_history_array==""){
        var search_history_array = [user_query];
        var json_str = JSON.stringify(search_history_array);
        set_cookie('search_history_array', json_str);        
    }
    else{
        search_history_array = JSON.parse(search_history_array)
        search_history_array.unshift(user_query);
        var json_str = JSON.stringify(search_history_array);
        set_cookie('search_history_array', json_str);   
    }
    $('.search-history-chips').prepend('<div class="chip tag-chip">'+user_query+'</div>')

    $.ajax({
        url: '/get-articles-based-on-query/',
        type: "POST",
        data: {
            user_query: user_query,
        },
        success: function(response) {
            if (response["status"] == 200) {
                $('.suggested-tags').html("")
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

function set_cookie(cookiename,cookievalue) {
  document.cookie = cookiename + "=" + cookievalue;
}


function get_cookie(cookiename) {
  var cookie_name = cookiename + "=";
  var decodedCookie = decodeURIComponent(document.cookie);
  var cookie_array = decodedCookie.split(';');
  for(var i = 0; i < cookie_array.length; i++) {
    var c = cookie_array[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(cookie_name) == 0) {
      return c.substring(cookie_name.length, c.length);
    }
  }
  return "";
}


function append_suggested_tags(suggested_tags){
    html="Results not found <br> <br>"
    if (suggested_tags.length>0){
        html+="Suggested Tags: <br>"
    }
    else{
        html+="No suggested ags<br>"   
    }
    for (var i = 0; i < suggested_tags.length; i++) {
        html += '<div class="chip tag-chip">'+suggested_tags[i]+'</div>'
    }
    $('.suggested-tags').html(html)
}

$(document).on("click", ".tag-chip", function(e) {
    tag= $(this).html()
    document.getElementById("tags-input").value = tag
    $("#search-btn").click()
});

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
                    <a target="_blank" href="/article-page/?medium-url='+articles_data[i]["link"]+'"><h5 class="card-title">'+articles_data[i]["title"]+'</h5></a>\
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
            $('.suggested-tags').html("")
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
