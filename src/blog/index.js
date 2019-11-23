let $showPic = $('.show-pic')
let $lightbox = $('#lightbox')

$showPic.click((e)=> {
    e.preventDefault();
    let self = $(e.currentTarget);
    $lightbox.find('img').attr("src", self.data('href'));
    $lightbox.css('display', 'inline');
});
