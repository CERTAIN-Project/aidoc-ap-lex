// Back-to-top link: shown once the page header (#top) is about one screen above the viewport.
// Without JavaScript or IntersectionObserver the link stays visible and still works (href="#top").
(function(){
  var link = document.querySelector('.back-to-top');
  var header = document.getElementById('top');
  if (!link || !header || !('IntersectionObserver' in window)) return;
  document.documentElement.classList.add('js');
  new IntersectionObserver(function(entries){
    link.classList.toggle('is-visible', !entries[0].isIntersecting);
  }, { rootMargin: '100% 0px 0px 0px' }).observe(header);
})();
