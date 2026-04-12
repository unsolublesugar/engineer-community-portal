/**
 * EasyEasy Community Portal - メインスクリプト
 */

document.addEventListener('DOMContentLoaded', () => {
  initLocalFileDetection();
  initYouTubePlayer();
  initYearFilter();
  initSpeakerSearch();
  initSpeakerSort();
  initSpeakerPagination();
});

/**
 * file:// プロトコルの検出
 * ローカルファイルではiframe埋め込み（Speaker Deck, Docswell等）が
 * 動作しないため、CSSクラスを付与してリンク表示にフォールバックする
 */
function initLocalFileDetection() {
  if (window.location.protocol === 'file:') {
    document.body.classList.add('is-local-file');
  }
}

/**
 * YouTube埋め込みプレーヤー
 * 公開ページ（http/https）ではクリックでiframe埋め込み再生に切り替え、
 * ローカル（file://）やJS無効時は<a>タグのデフォルト動作でYouTubeページへ遷移
 */
function initYouTubePlayer() {
  const players = document.querySelectorAll('.youtube-player-wrapper');
  if (!players.length) return;

  const isLocal = window.location.protocol === 'file:';
  if (isLocal) return; // ローカルでは<a>タグのデフォルト動作に任せる

  players.forEach(wrapper => {
    const videoId = wrapper.dataset.videoId;
    if (!videoId) return;

    wrapper.addEventListener('click', (e) => {
      e.preventDefault();

      // 公開ページではiframe埋め込みに差し替え
      const iframe = document.createElement('iframe');
      iframe.src = 'https://www.youtube-nocookie.com/embed/' + videoId + '?autoplay=1&rel=0';
      iframe.setAttribute('allow', 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture');
      iframe.setAttribute('allowfullscreen', '');
      iframe.className = 'youtube-iframe';
      iframe.title = 'YouTube video player';

      wrapper.innerHTML = '';
      wrapper.appendChild(iframe);
      wrapper.style.cursor = 'default';
    });
  });
}

/**
 * 年度フィルター（トップページ）
 * デフォルトは現在年のみ表示。「すべて」選択時はページネーション付き。
 */
function initYearFilter() {
  const filterContainer = document.getElementById('yearFilter');
  const grid = document.getElementById('eventsGrid');
  if (!filterContainer || !grid) return;

  const PAGE_SIZE = 12;
  const buttons = filterContainer.querySelectorAll('.filter-btn');
  const allCards = Array.from(grid.querySelectorAll('.event-card'));
  const loadMoreWrapper = document.getElementById('loadMoreWrapper');
  const loadMoreBtn = document.getElementById('loadMoreBtn');
  const yearNav = document.getElementById('yearNav');

  // 年ボタンのリストを取得（「すべて」除く、降順）
  const yearButtons = Array.from(buttons).filter(b => b.dataset.year !== 'all');
  const years = yearButtons.map(b => b.dataset.year);

  let currentFilter = 'year';
  let visibleCount = 0;
  let filteredCards = [];

  function applyFilter(year) {
    if (year === 'all') {
      currentFilter = 'all';
      filteredCards = allCards;
    } else {
      currentFilter = 'year';
      filteredCards = allCards.filter(card => card.dataset.year === year);
    }

    // 全カードを非表示
    allCards.forEach(card => card.style.display = 'none');

    if (currentFilter === 'all') {
      // ページネーション: 最初のページ分だけ表示
      visibleCount = Math.min(PAGE_SIZE, filteredCards.length);
    } else {
      // 年フィルター: 全件表示
      visibleCount = filteredCards.length;
    }

    for (let i = 0; i < visibleCount; i++) {
      filteredCards[i].style.display = '';
    }

    updateLoadMore();
    updateYearNav(year);
  }

  function showMore() {
    const nextCount = Math.min(visibleCount + PAGE_SIZE, filteredCards.length);
    for (let i = visibleCount; i < nextCount; i++) {
      filteredCards[i].style.display = '';
    }
    visibleCount = nextCount;
    updateLoadMore();
  }

  function updateLoadMore() {
    if (loadMoreWrapper) {
      loadMoreWrapper.style.display =
        (currentFilter === 'all' && visibleCount < filteredCards.length) ? '' : 'none';
    }
  }

  function updateYearNav(year) {
    if (!yearNav) return;
    yearNav.innerHTML = '';

    if (year === 'all') {
      yearNav.style.display = 'none';
      return;
    }

    yearNav.style.display = '';
    const idx = years.indexOf(year);

    // 翌年（配列では前の要素 = より新しい年）
    if (idx > 0) {
      const nextYear = years[idx - 1];
      const nextBtn = document.createElement('button');
      nextBtn.className = 'btn btn-outline year-nav-btn';
      nextBtn.textContent = '← ' + nextYear + '年';
      nextBtn.addEventListener('click', () => switchYear(nextYear));
      yearNav.appendChild(nextBtn);
    }

    // 前年（配列では後の要素 = より古い年）
    if (idx < years.length - 1) {
      const prevYear = years[idx + 1];
      const prevBtn = document.createElement('button');
      prevBtn.className = 'btn btn-outline year-nav-btn';
      prevBtn.style.marginLeft = 'auto';
      prevBtn.textContent = prevYear + '年 →';
      prevBtn.addEventListener('click', () => switchYear(prevYear));
      yearNav.appendChild(prevBtn);
    }
  }

  function switchYear(year) {
    buttons.forEach(b => {
      b.classList.toggle('active', b.dataset.year === year);
    });
    applyFilter(year);
    window.scrollTo({ top: grid.offsetTop - 80, behavior: 'smooth' });
  }

  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      applyFilter(btn.dataset.year);
    });
  });

  if (loadMoreBtn) {
    loadMoreBtn.addEventListener('click', showMore);
  }

  // 初期表示: activeボタンの年でフィルター
  const activeBtn = filterContainer.querySelector('.filter-btn.active');
  if (activeBtn) {
    applyFilter(activeBtn.dataset.year);
  }
}

/**
 * 登壇者検索
 */
function initSpeakerSearch() {
  const input = document.getElementById('speakerSearch');
  const grid = document.getElementById('speakersGrid');
  if (!input || !grid) return;

  // 各タイトル要素の元テキストを保持
  const titleElements = grid.querySelectorAll('.speaker-talk-title');
  const originalTexts = new Map();
  titleElements.forEach(el => originalTexts.set(el, el.textContent));

  input.addEventListener('input', () => {
    const query = input.value.toLowerCase().trim();
    const cards = grid.querySelectorAll('.speaker-card');

    cards.forEach(card => {
      const name = (card.dataset.name || '').toLowerCase();
      const id = (card.dataset.id || '').toLowerCase();
      const twitter = (card.dataset.twitter || '').toLowerCase();
      const github = (card.dataset.github || '').toLowerCase();

      // ハイライトをリセット
      card.querySelectorAll('.speaker-talk-title').forEach(el => {
        el.textContent = originalTexts.get(el) || el.textContent;
      });

      // 折りたたみを閉じる
      const details = card.querySelector('.speaker-talks-more');
      if (details) details.removeAttribute('open');

      if (!query) {
        card.dataset.filtered = '';
        return;
      }

      // タイトルマッチを検索しハイライト
      let titleMatch = false;
      card.querySelectorAll('.speaker-talk-title').forEach(el => {
        const original = originalTexts.get(el) || el.textContent;
        if (original.toLowerCase().includes(query)) {
          titleMatch = true;
          const regex = new RegExp('(' + query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi');
          el.innerHTML = original.replace(regex, '<mark class="search-highlight">$1</mark>');
        }
      });

      const matched = name.includes(query) || id.includes(query) || twitter.includes(query) || github.includes(query) || titleMatch;
      card.dataset.filtered = matched ? '' : 'hidden';

      // タイトルマッチ時に折りたたみ内にヒットがあれば展開
      if (titleMatch && details) {
        const hasHiddenMatch = details.querySelector('.search-highlight');
        if (hasHiddenMatch) details.setAttribute('open', '');
      }
    });

    // 検索後にページネーションをリセット
    if (window.speakerPagination) window.speakerPagination.reset();
  });
}

/**
 * 登壇者ソート
 */
function initSpeakerSort() {
  const buttons = document.querySelectorAll('.sort-buttons .filter-btn');
  const grid = document.getElementById('speakersGrid');
  if (!buttons.length || !grid) return;

  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      const sortBy = btn.dataset.sort;

      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const cards = Array.from(grid.querySelectorAll('.speaker-card'));

      cards.sort((a, b) => {
        if (sortBy === 'count') {
          const diff = parseInt(b.dataset.count || 0) - parseInt(a.dataset.count || 0);
          if (diff !== 0) return diff;
          return (b.dataset.latest || '').localeCompare(a.dataset.latest || '');
        } else if (sortBy === 'latest') {
          const diff = (b.dataset.latest || '').localeCompare(a.dataset.latest || '');
          if (diff !== 0) return diff;
          return parseInt(b.dataset.count || 0) - parseInt(a.dataset.count || 0);
        } else {
          return (a.dataset.name || '').localeCompare(b.dataset.name || '', 'ja');
        }
      });

      const fragment = document.createDocumentFragment();
      cards.forEach(card => fragment.appendChild(card));
      grid.appendChild(fragment);

      // ソート後にページネーションをリセット
      if (window.speakerPagination) window.speakerPagination.reset();
    });
  });
}

/**
 * 登壇者ページネーション
 */
function initSpeakerPagination() {
  const grid = document.getElementById('speakersGrid');
  const loadMoreWrapper = document.getElementById('speakerLoadMoreWrapper');
  const loadMoreBtn = document.getElementById('speakerLoadMoreBtn');
  if (!grid || !loadMoreWrapper || !loadMoreBtn) return;

  const PAGE_SIZE = 20;
  let visibleCount = 0;

  function getVisibleCards() {
    return Array.from(grid.querySelectorAll('.speaker-card'))
      .filter(card => card.dataset.filtered !== 'hidden');
  }

  function reset() {
    const cards = getVisibleCards();
    visibleCount = Math.min(PAGE_SIZE, cards.length);

    grid.querySelectorAll('.speaker-card').forEach(card => {
      card.style.display = card.dataset.filtered === 'hidden' ? 'none' : 'none';
    });

    const visible = getVisibleCards();
    for (let i = 0; i < Math.min(visibleCount, visible.length); i++) {
      visible[i].style.display = '';
    }

    updateBtn();
  }

  function showMore() {
    const cards = getVisibleCards();
    const nextCount = Math.min(visibleCount + PAGE_SIZE, cards.length);
    for (let i = visibleCount; i < nextCount; i++) {
      cards[i].style.display = '';
    }
    visibleCount = nextCount;
    updateBtn();
  }

  function updateBtn() {
    const total = getVisibleCards().length;
    loadMoreWrapper.style.display = visibleCount < total ? '' : 'none';
  }

  loadMoreBtn.addEventListener('click', showMore);

  window.speakerPagination = { reset };
  reset();
}
