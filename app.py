
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta
      name="viewport"
      content="width=device-width,initial-scale=1,shrink-to-fit=no,user-scalable=no"
    />
    <meta name="theme-color" content="#FFFFFF" />
    <!-- Additional meta tags -->

    <!--
      We're putting icons here because ReactHelmet doesn't work for favicons.
      See https://github.com/nfl/react-helmet/issues/430
    -->

    <!--
    Following a mix of:
    @st.cache_data(ttl=3600) # 
def load_data(tickers):
    # Download massal lebih aman dari blokir IP 
    return yf.download(tickers, period="1y", interval="1d", group_by='ticker')

# Cara mengambil nilai indikator yang benar (Menghindari TypeError) 
l_band = float(latest_bb.iloc) # Mengambil nilai pertama, bukan objek indexer
u_band = float(latest_bb.iloc[2])    - https://css-tricks.com/svg-favicons-and-all-the-fun-things-we-can-do-with-them/
    -->
    <link id="favicon" rel="icon" href="/-/build/favicon.svg" />
    <!--
    Including all these other <link> statements here just so they're all in the same place.
    Not because we expect someone to Helmet-override them.
    -->
    <link id="alternate-favicon" rel="alternate icon" href="/-/build/favicon.ico" />
    <link rel="mask-icon" href="/favicon_safari_mask.png" color="#FF2B2B" />
    <link rel="apple-touch-icon" href="/-/build/favicon_256.png" />
    <link rel="manifest" href="/-/build/manifest.json" />
    <!-- Google Tag Manager -->
    <script>
      ;(function (w, d, s, l, i) {
        w[l] = w[l] || []
        w[l].push({
          'gtm.start': new Date().getTime(),
          event: 'gtm.js',
        })
        var f = d.getElementsByTagName(s)[0],
          j = d.createElement(s),
          dl = l != 'dataLayer' ? '&l=' + l : ''
        j.async = true
        j.src = 'https://www.googletagmanager.com/gtm.js?id=' + i + dl
        f.parentNode.insertBefore(j, f)
      })(window, document, 'script', 'dataLayer', 'GTM-52GRQSL')
    </script>
    <!-- End Google Tag Manager -->
    <!-- Segment -->
    <script>
      !(function () {
        var analytics = (window.analytics = window.analytics || [])
        if (!analytics.initialize)
          if (analytics.invoked)
            window.console &&
              console.error &&
              console.error('Segment snippet included twice.')
          else {
            analytics.invoked = !0
            analytics.methods = [
              'trackSubmit',
              'trackClick',
              'trackLink',
              'trackForm',
              'pageview',
              'identify',
              'reset',
              'group',
              'track',
              'ready',
              'alias',
              'debug',
              'page',
              'once',
              'off',
              'on',
              'addSourceMiddleware',
              'addIntegrationMiddleware',
              'setAnonymousId',
              'addDestinationMiddleware',
            ]
            analytics.factory = function (e) {
              return function () {
                var t = Array.prototype.slice.call(arguments)
                t.unshift(e)
                analytics.push(t)
                return analytics
              }
            }
            for (var e = 0; e < analytics.methods.length; e++) {
              var key = analytics.methods[e]
              analytics[key] = analytics.factory(key)
            }
            analytics.load = function (key, e) {
              var t = document.createElement('script')
              t.type = 'text/javascript'
              t.async = !0
              t.src =
                'https://cdn.segment.com/analytics.js/v1/' +
                key +
                '/analytics.min.js'
              var n = document.getElementsByTagName('script')[0]
              n.parentNode.insertBefore(t, n)
              analytics._loadOptions = e
            }
            analytics.SNIPPET_VERSION = '4.13.1'
            analytics.load('GI7vYWHNmWwHbyFjBrvL0jOBA1TpZOXC')
            // analytics.page()
          }
      })()
    </script>
    <!-- End Segment -->
    <script type="module" crossorigin src="/-/build/assets/index-DYBM4Ov8.js"></script>
    <link rel="modulepreload" crossorigin href="/-/build/assets/rolldown-runtime-BYbx6iT9.js">
    <link rel="modulepreload" crossorigin href="/-/build/assets/bufferedData-CKlkiO8t.js">
    <link rel="modulepreload" crossorigin href="/-/build/assets/routes-B0aSYRS-.js">
    <link rel="modulepreload" crossorigin href="/-/build/assets/page-9cfZfd7y.js">
    <link rel="modulepreload" crossorigin href="/-/build/assets/index.module-z0vTqeTA.js">
    <link rel="modulepreload" crossorigin href="/-/build/assets/toFinite-7Yp-8BSX.js">
    <link rel="modulepreload" crossorigin href="/-/build/assets/icon_star_outline-BxhkP8_9.js">
    <link rel="modulepreload" crossorigin href="/-/build/assets/emoji_u1f626-hZrEhAAQ.js">
    <link rel="modulepreload" crossorigin href="/-/build/assets/icon_edit-BU_DOgQY.js">
    <link rel="modulepreload" crossorigin href="/-/build/assets/icon_github-DR7UzAhA.js">
    <link rel="modulepreload" crossorigin href="/-/build/assets/ProfilePagePreview-BAMhqc1U.js">
    <link rel="modulepreload" crossorigin href="/-/build/assets/errorDetails-Dc7j6m6V.js">
    <link rel="modulepreload" crossorigin href="/-/build/assets/iframe-C28S6DqR.js">
    <link rel="modulepreload" crossorigin href="/-/build/assets/states-C_wySNIB.js">
    <link rel="modulepreload" crossorigin href="/-/build/assets/trim-B4olBp9N.js">
    <link rel="modulepreload" crossorigin href="/-/build/assets/isEqual-Brh2vIE3.js">
    <link rel="modulepreload" crossorigin href="/-/build/assets/confirmationModal-D71PiKoW.js">
    <link rel="modulepreload" crossorigin href="/-/build/assets/usePythonVersions-C7vwt1b1.js">
    <link rel="modulepreload" crossorigin href="/-/build/assets/appSettings-BSjvRq8P.js">
    <link rel="modulepreload" crossorigin href="/-/build/assets/popoverMenu-WzMrVZRw.js">
    <link rel="modulepreload" crossorigin href="/-/build/assets/useAppState-hQLZp-HV.js">
    <link rel="modulepreload" crossorigin href="/-/build/assets/errorPage-BBka7It_.js">
    <link rel="modulepreload" crossorigin href="/-/build/assets/notFound-CNiFLk-w.js">
    <link rel="modulepreload" crossorigin href="/-/build/assets/queryGithubRepository-BvsuDgoZ.js">
    <link rel="modulepreload" crossorigin href="/-/build/assets/error-Bs7kb_VV.js">
    <link rel="stylesheet" crossorigin href="/-/build/assets/page-CPsH8USs.css">
    <link rel="stylesheet" crossorigin href="/-/build/assets/icon_star_outline-DH69RDEi.css">
    <link rel="stylesheet" crossorigin href="/-/build/assets/ProfilePagePreview-BWWUYPxS.css">
    <link rel="stylesheet" crossorigin href="/-/build/assets/errorDetails-BDQowOym.css">
    <link rel="stylesheet" crossorigin href="/-/build/assets/states-Do7gXefQ.css">
    <link rel="stylesheet" crossorigin href="/-/build/assets/confirmationModal-BwNoJBuP.css">
    <link rel="stylesheet" crossorigin href="/-/build/assets/usePythonVersions-CBwCrTS9.css">
    <link rel="stylesheet" crossorigin href="/-/build/assets/appSettings-jOmLW4LG.css">
    <link rel="stylesheet" crossorigin href="/-/build/assets/popoverMenu-D49xGQkE.css">
    <link rel="stylesheet" crossorigin href="/-/build/assets/useAppState-SCryp0xD.css">
    <link rel="stylesheet" crossorigin href="/-/build/assets/errorPage-CK-Jpwy3.css">
    <link rel="stylesheet" crossorigin href="/-/build/assets/notFound-BzJWtTwJ.css">
    <link rel="stylesheet" crossorigin href="/-/build/assets/index-Dng3n069.css">
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>

    <!-- Status page embed -->
    <script src="https://www.streamlitstatus.com/embed/script.js"></script>
  </body>
</html>
