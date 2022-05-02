/* global hexo */

'use strict';

// Add comment
hexo.extend.filter.register('theme_inject', injects => {
  injects.comment.file('pixnet', 'source/_data/comments.njk');
});
