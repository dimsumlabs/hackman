(() => {
  const timeoutSeconds = 50;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutSeconds * 1000);

  fetch("/screen/poll/")
    .then(resp => {
      if(!resp.ok) {
        window.location.href = '/screen/';
        return Promise.reject("Response not OK: " + resp.status);
      }
      return resp.text();
    })
    .then((url) => {
      window.location.href = url;
    })
    .catch(err => {
        window.location.href = '/screen/';
    })
    .then(() => {
      clearTimeout(timeoutId);
    })
  ;
})();
