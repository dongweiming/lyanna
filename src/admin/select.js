import 'select2/dist/js/select2';
import 'select2/dist/css/select2.css';
import "../scss/select.scss";

$(document).ready(() => {
  $("select").select2({
    tags: true
  });
});
