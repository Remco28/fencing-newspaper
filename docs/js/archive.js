(function () {
  'use strict';
  var list = document.getElementById('issues');
  EGG.loadIssues().then(function (issues) {
    list.textContent = '';
    issues.forEach(function (iss) {
      var li = EGG.el('li', { 'class': 'issue' });
      var no = EGG.el('div', { 'class': 'no' }, [EGG.el('small', { text: 'No.' }), document.createTextNode(iss.number)]);
      var time = EGG.el('time', { datetime: iss.date, text: EGG.fmtDate(iss.date, true) + (iss.edition ? ' · ' + iss.edition : '') });
      var h = EGG.el('h2', { text: iss.headline });
      var read = EGG.el('a', { href: 'index.html?read=' + iss.number, 'aria-label': 'Read No. ' + iss.number + ': ' + iss.headline, text: 'Read' });
      var pdf = EGG.el('a', { href: iss.pdf, download: '', 'aria-label': 'Download PDF of No. ' + iss.number, text: 'PDF' });
      read.addEventListener('click', function (e) {
        if (e.metaKey || e.ctrlKey || e.shiftKey) return;
        e.preventDefault();
        EGG.openReader(iss, 0, read);
      });
      li.appendChild(no);
      li.appendChild(EGG.el('div', {}, [time, h]));
      li.appendChild(EGG.el('div', { 'class': 'links' }, [read, pdf]));
      list.appendChild(li);
    });
    EGG.openFromQuery(issues);
  }).catch(function () {
    list.innerHTML = '<li>Could not load the issue list. Please try again.</li>';
  });
})();
