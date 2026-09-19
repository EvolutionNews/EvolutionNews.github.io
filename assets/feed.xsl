<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:atom="http://www.w3.org/2005/Atom" exclude-result-prefixes="atom">
  <xsl:output method="html" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/rss">
    <html lang="en">
      <head>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1"/>
        <title><xsl:value-of select="channel/title"/> — RSS feed</title>
        <style>
          :root { color-scheme: light dark; }
          * { box-sizing: border-box; }
          body { margin: 0; background: #f4f5f1; color: #172c30; font: 1rem/1.65 system-ui, sans-serif; }
          main, header, footer { max-width: 54rem; margin: auto; padding: 1.5rem; }
          header { padding-bottom: 0; }
          h1 { font-size: clamp(1.7rem, 5vw, 2.5rem); line-height: 1.2; }
          h2 { font-size: 1.35rem; line-height: 1.35; }
          a { color: #075c70; text-underline-offset: .18em; overflow-wrap: anywhere; }
          a:focus-visible { outline: 3px solid #bd6410; outline-offset: 4px; }
          .eyebrow { text-transform: uppercase; letter-spacing: .08em; font-size: .8rem; }
          .subscribe, article { padding: 1.25rem; background: #fff; border: 1px solid #c6d1cd; border-radius: .6rem; margin-bottom: 1.25rem; }
          label { display: block; font-weight: 600; }
          input { width: 100%; padding: .75rem; font: inherit; color: inherit; background: transparent; border: 1px solid #718781; border-radius: .25rem; }
          .categories { display: flex; flex-wrap: wrap; gap: .5rem; }
          .category { border: 1px solid #718781; border-radius: 1rem; padding: .1rem .65rem; font-size: .85rem; }
          footer { border-top: 1px solid #c6d1cd; }
          .skip { position: absolute; left: -10000px; }
          .skip:focus { left: 1rem; top: 1rem; background: #fff; padding: .5rem; }
          @media (prefers-color-scheme: dark) {
            body { background: #152124; color: #ecf1ee; }
            .subscribe, article, .skip:focus { background: #1e3034; }
            a { color: #90d7e6; }
          }
          @media (max-width: 420px) { main, header, footer { padding: 1rem; } }
        </style>
      </head>
      <body>
        <a class="skip" href="#main">Skip to feed entries</a>
        <header>
          <a href="/">EvolutionNews.net home</a>
          <p class="eyebrow">RSS subscription feed</p>
          <h1><xsl:value-of select="channel/title"/></h1>
          <p><xsl:value-of select="channel/description"/></p>
        </header>
        <main id="main">
          <section class="subscribe" aria-labelledby="subscribe-title">
            <h2 id="subscribe-title">Get updates in your feed reader</h2>
            <p>Copy this address into your RSS reader's subscription or “Add feed” field. Your reader can then check for new entries without you revisiting an old report.</p>
            <label for="feed-url">Feed address</label>
            <input id="feed-url" type="text" readonly="readonly" spellcheck="false" value="{channel/atom:link[@rel='self']/@href}"/>
            <p>Substantive follow-ups and corrections receive their own entries. Cosmetic edits do not. Delivery timing depends on your reader.</p>
          </section>
          <h2>Latest entries</h2>
          <xsl:for-each select="channel/item">
            <article>
              <div class="categories"><xsl:for-each select="category"><span class="category"><xsl:value-of select="."/></span></xsl:for-each></div>
              <h2><a href="{link}"><xsl:value-of select="title"/></a></h2>
              <xsl:if test="pubDate"><p><xsl:value-of select="pubDate"/></p></xsl:if>
              <p><xsl:value-of select="description"/></p>
            </article>
          </xsl:for-each>
        </main>
        <footer><p>This is a readable view of an RSS feed, not a mailing-list signup. No account is required. <a href="/">Browse the website</a>.</p></footer>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
