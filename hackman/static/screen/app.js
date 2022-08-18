(function() {
  const timeoutSeconds = 50;
  const controller = new AbortController();
  const timeoutId = setTimeout(function() {
    controller.abort();
  }, timeoutSeconds * 1000);

  fetch("/screen/poll/")
    .then(function(resp) {
      if(!resp.ok) {
        window.location.href = '/screen/';
        return Promise.reject("Response not OK: " + resp.status);
      }
      return resp.text();
    })
    .then(function(url) {
      window.location.href = url;
    })
    .catch(function(err) {
      window.location.href = '/screen/';
    })
    .then(function() {
      clearTimeout(timeoutId);
    })
  ;
})();
