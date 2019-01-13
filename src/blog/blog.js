import SocialSharer from './social-sharer';

let $commentContainer = $('.gitment-comments-list')
let $editorTab = $('.gitment-editor-tab');
let $editorPreview = $('.gitment-editor-preview')
let $editorWriteField = $('.gitment-editor-write-field')
let $writeTextarea = $editorWriteField.find('textarea')
let $editorPreviewField = $('.gitment-editor-preview-field')
let $loginBtn = $('.gitment-editor-login-link')
let $submitBtn = $('.gitment-editor-submit')
let $pageItemBtn = $('.gitment-comments-page-item')
let $reactionBtn = $('.reaction-item-button')
let $reactionContainer = $('#reactions-container')

const target_id = $('meta[name=post_id]').attr('content');

$editorTab.click((e)=> {
    let self = $(e.currentTarget);
    $editorTab.removeClass('gitment-selected');
    self.addClass('gitment-selected');
    if (self.hasClass('preview')) {
        $editorWriteField.addClass('gitment-hidden')
        $editorPreviewField.removeClass('gitment-hidden')
        let text = $writeTextarea.val();
        if (!$writeTextarea.disabled) {
            if (!text) {
                $editorPreview.html('空空如也')
                return
            }
            $editorPreview.html('渲染中...')
            $.ajax({
                url: '/j/markdown',
                type: 'post',
                data: {'text': text},
                dataType: 'json',
                success: function (rs) {
                    $editorPreview.html(rs.text);
                }
            });
        }
    } else {
        $editorWriteField.removeClass('gitment-hidden')
        $editorPreviewField.addClass('gitment-hidden')
    }
});

$loginBtn.click((e)=> {
    document.location.href = `/login?next=${document.location.href}`
});

$pageItemBtn.click((e)=> {
    let self = $(e.currentTarget), page;
    if (self.hasClass('gitment-selected')) {
        return
    }
    let current_page = parseInt($('.gitment-comments-pagination .gitment-selected').html())
    if (self.hasClass('next')) {
        page = current_page + 1
    } else if (self.hasClass('prev')) {
        page = current_page - 1
    } else {
        page = parseInt(self.html())
    }
    if (page != 1) {
        $pageItemBtn.eq(0).removeClass('gitment-hidden')
    } else {
        $pageItemBtn.eq(0).addClass('gitment-hidden')
    }
    if ($pageItemBtn.length - 2 <= page) {
        $pageItemBtn.eq(-1).addClass('gitment-hidden')
    } else {
        $pageItemBtn.eq(-1).removeClass('gitment-hidden')
    }
    $pageItemBtn.removeClass('gitment-selected');
    $pageItemBtn.eq(page).addClass('gitment-selected')
    const loading = document.createElement('div')
    loading.innerText = '加载评论...'
    loading.className = 'gitment-comments-loading'
    $commentContainer.empty().append(loading)
    $.ajax({
        url: `/j/post/${target_id}/comments?page=${page}&per_page=10`,
        type: 'get',
        dataType: 'json',
        success: function (rs) {
            $commentContainer.empty().append(rs.html)
        }
    })
});

$commentContainer.on('click', '.gitment-comment-like-btn', (e)=> {
    let self = $(e.currentTarget);
    let rqType = self.hasClass('liked') ? 'delete' : 'post'
    $.ajax({
        url: `/j/comment/${self.data('id')}/like`,
        type: rqType,
        dataType: 'json',
        success: function (rs) {
            if (!rs.r) {
                self.toggleClass('liked')
                self.find('span').html(rs.n_likes)
            }
        }
    })
})

$submitBtn.click((e)=> {
    let content = $writeTextarea.val();
    if (!content) {
        return
    }
    let self = $(e.currentTarget);
    self.html('提交...')
    self.attr('disabled', true)
    $.ajax({
        url: `/j/post/${target_id}/comment`,
        type: 'post',
        data: {'content': content},
        dataType: 'json',
        success: function (rs) {
            if (!rs.r) {
                $writeTextarea.val('')
                self.removeAttr('disabled')
                self.html('评论')
                $commentContainer.prepend(rs.html)
                console.log('评论成功')
            } else {
                console.log('评论失败')
            }
        }
    });
});

$reactionBtn.on('click', (e)=> {
  let self = $(e.currentTarget);
  let $reactionEnabled = $('.reaction-item__enabled').length > 0;

  if (!$reactionEnabled) {
    return  // 目前只支持表态，不能取消
  }

  $.ajax({
    url: `/j/post/${target_id}/react`,
    type: $reactionEnabled ? 'post' : 'delete',
    data: {'reaction_type': self.data('kind')},
    dataType: 'json',
    success: function (rs) {
      if (!rs.r) {
        $reactionContainer.empty().append(rs.html)
        $reactionEnabled = !$reactionEnabled
        console.log('表态成功')
      } else {
        console.log('表态失败')
        if (rs.r == 403) {  // 未登录
          window.location.href = `/oauth/post/${target_id}`;
        }
      }
    }
  });
})

$(document).ready(function() {
  $('figure pre').each(function(i, block) {
    var figure = $(this).parents('figure');
    var lang = figure.attr('class').split(' ')[1] || 'code';
    figure.attr('data-lang', lang.toUpperCase());
    hljs.highlightBlock(block);
  });
});

let socialSharer = new SocialSharer('.social-sharer');
