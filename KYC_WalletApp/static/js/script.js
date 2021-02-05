$(document).ready(function() {

  console.log('READY');

  $('.btn').on('click', function() {
    var $this = $(this);
    var loadingText = '<i class="fa fa-circle-o-notch fa-spin"></i> loading...';
    if ($(this).html() !== loadingText) {
      $this.data('original-text', $(this).html());
      $this.html(loadingText);
    }
    setTimeout(function() {
      $this.html($this.data('original-text'));
    }, 6000);
  });

  $(function () {
    $('[data-toggle="popover"]').popover()
  });


  const target = document.querySelector("main");

  const config = {attributes: true, childList: true, subtree: true};

  const callback = function (mutationsList, observer) {
    for (const mutation of mutationsList) {
        if ($('.alert')) {
            setTimeout(function () {
                $('.alert').alert('close');
            }, 4000);
            console.log('ALERT FOUND');
        }
    }
  };

  const observer = new MutationObserver(callback);
  observer.observe(target, config);
});




