let searchFunc = function(path, search_id, content_id) {
  $.ajax({
    url: path,
    dataType: 'json',
    success: function(posts) {
      var $input = document.getElementById(search_id);
      if (!$input) return;
      var $resultContent = document.getElementById(content_id);
      let _search = function(event, value=null) {
        var str = '<ul class=\"search-result-list\">';
        $resultContent.innerHTML = "";
        if (value != null) {
          this.value = value
        }
        var keywords = this.value.trim().toLowerCase().split(/[\s\-]+/);
        if (this.value.trim().length <= 0) {
          return;
        }
        var str = '<ul class=\"search-result-list\">';
        $resultContent.innerHTML = "";
        // perform local searching
        posts.forEach(function(data) {
          var isMatch = true;
          var content_index = [];
          if (!data.content) {
            return
          }
          if (!data.title || data.title.trim() === '') {
            data.title = "Untitled";
          }
          var data_title = data.title.trim().toLowerCase();
          var data_content = data.content.trim().replace(/<[^>]+>/g, "").toLowerCase();
          var data_url = data.url;
          var index_title = -1;
          var index_content = -1;
          var first_occur = -1;
          if (data_content !== '') {
            keywords.forEach(function(keyword, i) {
              index_title = data_title.indexOf(keyword);
              index_content = data_content.indexOf(keyword);
              if (index_title < 0 && index_content < 0) {
                isMatch = false;
              } else {
                if (index_content < 0) {
                  index_content = 0;
                }
                if (i == 0) {
                  first_occur = index_content;
                }
              }
            });
          } else {
            isMatch = false;
          }
          // show search results
          if (isMatch) {
            str += "<li><a href='" + data_url + "' class='search-result-title'>" + data_title + "</a>";
            var content = data.content.trim().replace(/<[^>]+>/g, "");
            if (first_occur >= 0) {
              // cut out 100 characters
              var start = first_occur - 20;
              var end = first_occur + 80;
              if (start < 0) {
                start = 0;
              }
              if (start == 0) {
                end = 100;
              }
              if (end > content.length) {
                end = content.length;
              }
              var match_content = content.substr(start, end);
              // highlight all keywords
              keywords.forEach(function(keyword) {
                var regS = new RegExp(keyword, "gi");
                match_content = match_content.replace(regS, "<em class=\"search-keyword\">" + keyword + "</em>");
              });
              str += "<p class=\"search-result\">" + match_content + "...</p>"
            }
            str += "</li>";
          }
        });
        str += "</ul>";
        $resultContent.innerHTML = str;
      };

      $input.addEventListener('input', _search);
      if ($input.value !== "") {
        _search(value=$input.value);
      }
    }
  });
};

searchFunc('/search.json', 'local-search-input', 'local-search-result');
