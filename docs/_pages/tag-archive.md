---
title: 主題文章
permalink: /tags/
layout: tags
---

{% assign entries_layout = page.entries_layout | default: 'list' %}
<div id="hash-nav" class="entries-{{ entries_layout }}">
  <div v-for="nav in nav_list" class="{{ include.type | default: 'list' }}__item">
    <article class="archive__item">
      <h2 class="archive__item-title no_toc">
        {% raw %}<a href="/posts/123" rel="permalink">{{ nav.title }}</a>{% endraw %}
      </h2>
    </article>
  </div>
</div>
