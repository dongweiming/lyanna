import UIkit from './base';

let $error = $('meta[name=error]').attr('content');

if ($error) {
  UIkit.notification({
    message: $error,
    status: 'danger',
    timeout: 1000
  });
}

$('.uk-tab a').on('click', (event)  => {
  let $this = $(event.currentTarget)[0];
  window.location.replace($this.href);
});
