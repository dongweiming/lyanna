import './admin';
import './select';

import SimpleMDE from '../vendor/simplemde';
import '../css/font-awesome.min.css';
import '../css/simplemde.min.css';
import '../scss/coremirror.scss';

let $switchInput = $('.switch-input');
let $switcher = $('.uk-switch input');

$switcher.on('click', (event)  => {
  let $this = $(event.currentTarget)[0];
  let checked = $this.checked;
  if (checked) {
    $this.setAttribute('value', 'on');
    $switchInput.attr('value', 'on');
  } else {
    $this.setAttribute('value', 'off');
    $switchInput.attr('value', 'off');
  }
});

let simplemde = new SimpleMDE({ element: $("#content")[0] });

let $content = $('meta[name=raw_content]').attr('content');
if ($content) {
  simplemde.value($content);
}
