import './admin';
import UIkit from './base';

let $switcher = $('.uk-switch input');
let $delBtn = $('.delete');

$switcher.on('click', (event)  => {
    let $this = $(event.currentTarget)[0];
    let $url = $($this).data('url');
    let checked = $this.checked;
    $.ajax({
        url: $url,
        type: checked ? 'POST' : 'DELETE',
        data: {},
        success: function(rs) {
            if (rs.r) {
                UIkit.notification({
                    message: rs.msg || 'Ops!',
                    status: 'danger',
                    timeout: 1000
                });
            }
        }
    });
});

$delBtn.on('click', (event)  => {
  let $this = $(event.currentTarget)[0];
  let $url = $($this).data('url');
  let id = $($this).data('id');

  UIkit.modal.confirm(`Post(${id}) Will delete, Plz confirm!`).then(() => {
  $.ajax({
      url: $url,
      type: 'DELETE',
      data: {},
      success: function(rs) {
        if (rs.r) {
          UIkit.notification({
            message: rs.msg || 'Ops!',
            status: 'danger',
            timeout: 1000
          });
        } else {
          $this.closest('tr').remove();
        }
      }
    });
    console.log('Deleted.');
  }, ()=> {
    console.log('Rejected.')
  });
});
