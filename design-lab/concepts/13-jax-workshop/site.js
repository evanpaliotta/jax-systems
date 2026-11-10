'use strict';
const menu = document.querySelector('.menu-toggle');
const nav = document.querySelector('#site-nav');
const mobile = window.matchMedia('(max-width: 760px)');
function syncNavigation() {
  nav.hidden = mobile.matches && menu.getAttribute('aria-expanded') !== 'true';
}
menu.addEventListener('click', () => {
  menu.setAttribute('aria-expanded', String(menu.getAttribute('aria-expanded') !== 'true'));
  syncNavigation();
});
mobile.addEventListener('change', syncNavigation);
syncNavigation();
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && mobile.matches && menu.getAttribute('aria-expanded') === 'true') {
    menu.setAttribute('aria-expanded', 'false');
    syncNavigation();
    menu.focus();
  }
});

const flows = {
  calls: ['A missed call.', "You're out on a job.", 'Ready to call back.', 'Details captured. Owner assigned.', 'Your team makes the call.'],
  quotes: ['An open estimate.', 'The next job took over.', 'Follow-up queued.', 'Stops when the customer replies.', 'Your team sets the price.'],
  updates: ['“Any update?”', 'The answer is in three places.', 'One clear update.', 'Drafted for your team to review.', 'Your team approves the message.']
};
for (const button of document.querySelectorAll('[data-flow]')) {
  button.addEventListener('click', () => {
    const flow = flows[button.dataset.flow];
    document.querySelectorAll('[data-flow]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    for (const [index, selector] of ['[data-node-input]', '[data-node-input-detail]', '[data-node-output]', '[data-node-output-detail]'].entries()) {
      document.querySelector(selector).textContent = flow[index];
    }
    document.querySelector('[data-flow-caption]').textContent = 'Illustrative flow · ' + flow[4];
  });
}

const motionButton = document.querySelector('.motion-toggle');
if (motionButton) {
  const art = document.querySelector('.hero-art');
  const svg = document.querySelector('.flow-line');
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  let paused = reduced.matches;
  function syncMotion() {
    art.classList.toggle('paused', paused);
    motionButton.setAttribute('aria-pressed', String(paused));
    motionButton.setAttribute('aria-label', paused ? 'Resume motion' : 'Pause motion');
    motionButton.textContent = paused ? '▷' : 'Ⅱ';
    if (paused) svg.pauseAnimations(); else svg.unpauseAnimations();
  }
  motionButton.addEventListener('click', () => { paused = !paused; syncMotion(); });
  reduced.addEventListener('change', event => { paused = event.matches; syncMotion(); });
  // Preview iframes start static to avoid twelve concurrently animated gallery panels.
  if (window.self !== window.top) paused = true;
  syncMotion();
}

for (const button of document.querySelectorAll('[data-filter]')) {
  button.addEventListener('click', () => {
    const industry = button.dataset.filter;
    let count = 0;
    document.querySelectorAll('.example-card').forEach(card => {
      card.hidden = industry !== 'all' && card.dataset.industry !== industry;
      if (!card.hidden) count += 1;
    });
    document.querySelectorAll('[data-filter]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    document.querySelector('[data-example-count]').textContent = count + ' possibilities';
  });
}

const form = document.querySelector('#preview-form');
if (form) {
  form.addEventListener('submit', event => {
    event.preventDefault();
    const problem = document.querySelector('#problem').value;
    const result = document.querySelector('#preview-result');
    result.querySelector('[data-result-summary]').textContent = 'Starting point: ' + problem + '. The next conversation would cover the current tools, the people involved and one recent example.';
    result.hidden = false;
    result.focus();
  });
}
