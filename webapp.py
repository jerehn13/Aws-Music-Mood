import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

from test import analyze, decide_mood, recommend

PORT = 8000

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Mood App</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      font-family: -apple-system, Segoe UI, Roboto, sans-serif;
      background: linear-gradient(135deg, #2b3149 0%, #1f2436 100%);
      color: #f5f5f5; margin: 0; min-height: 100vh;
      display: flex; align-items: center; justify-content: center; padding: 20px;
    }}
    .card {{
      background: #ffffff; color: #2b3149; border-radius: 18px;
      padding: 40px; max-width: 760px; width: 100%;
      box-shadow: 0 20px 60px rgba(0,0,0,0.35);
    }}
    h1 {{ margin: 0 0 6px; font-size: 26px; }}
    p.sub {{ margin: 0 0 24px; color: #6b7280; }}
    textarea {{
      width: 100%; min-height: 90px; padding: 14px; font-size: 16px;
      border: 2px solid #d8dbe4; border-radius: 12px; resize: none;
      font-family: inherit;
    }}
    textarea:focus {{ outline: none; border-color: #2b3149; }}
    button {{
      margin-top: 14px; width: 100%; padding: 14px; font-size: 16px;
      font-weight: 600; color: #fff; background: #2b3149; border: none;
      border-radius: 12px; cursor: pointer;
    }}
    button:hover {{ background: #3a4163; }}
    .result {{ margin-top: 26px; }}
    .mood-banner {{
      text-align: center; font-size: 22px; font-weight: 700;
      padding: 18px; border-radius: 14px; background: #f0f2f8;
    }}
    .meta {{ text-align: center; color: #6b7280; margin: 10px 0 18px; }}
    .song {{
      display: flex; align-items: center; gap: 12px; padding: 12px 16px;
      border: 1px solid #eceef4; border-radius: 12px; margin-bottom: 10px;
      cursor: pointer; transition: background 0.15s, transform 0.1s;
    }}
    .song:hover {{ background: #f7f8fc; transform: translateX(3px); }}
    .song.active {{ background: #eef0fa; border-color: #c7cdf0; }}
    .song .num {{
      background: #2b3149; color: #fff; width: 28px; height: 28px;
      border-radius: 50%; display: flex; align-items: center;
      justify-content: center; font-size: 14px; flex-shrink: 0;
    }}
    .song .title {{ font-weight: 600; }}
    .song .artist {{ color: #6b7280; font-size: 14px; }}

    .player-layout {{ display: flex; gap: 26px; align-items: flex-start; flex-wrap: wrap; }}
    .cd-side {{
      flex: 0 0 200px; display: flex; flex-direction: column; align-items: center;
      position: sticky; top: 20px;
    }}
    .song-list {{ flex: 1; min-width: 240px; }}

    /* iPod mini */
    .cd {{
      width: 170px; padding: 14px 14px 10px;
      background: linear-gradient(#dfe2e8, #c7ccd4);
      border: 4px solid #b0b5bf; border-radius: 26px;
      box-shadow: 0 6px 0 #aab0ba, 0 16px 22px rgba(0,0,0,0.25);
      position: relative; transition: transform 0.1s;
    }}
    .cd .screen {{
      width: 100%; aspect-ratio: 1 / 1; border-radius: 8px;
      background: #1f2430; border: 3px solid #9aa0ab; overflow: hidden;
      position: relative; display: flex; align-items: center; justify-content: center;
    }}
    .cd .screen img {{
      width: 100%; height: 100%; object-fit: cover; display: none;
    }}
    .cd .screen.has-art img {{ display: block; }}
    .cd .screen .ph {{
      color: #8a8f99; font-size: 11px; text-align: center; padding: 8px; line-height: 1.4;
    }}
    .cd .screen.has-art .ph {{ display: none; }}
    .cd .wheel {{
      width: 96px; height: 96px; border-radius: 50%; margin: 14px auto 2px;
      background: radial-gradient(circle at 50% 40%, #f3f5f8, #dfe2e8);
      border: 3px solid #b0b5bf; position: relative;
    }}
    .cd .wheel::after {{
      content: ""; position: absolute; top: 50%; left: 50%;
      width: 34px; height: 34px; margin: -17px 0 0 -17px; border-radius: 50%;
      background: #cfd4dc; border: 3px solid #b0b5bf;
    }}
    .cd.playing .wheel {{ animation: spin 3s linear infinite; }}
    @keyframes spin {{ from {{ transform: rotate(0); }} to {{ transform: rotate(360deg); }} }}
    @keyframes bump {{
      0% {{ transform: scale(1); }}
      45% {{ transform: scale(1.035); }}
      100% {{ transform: scale(1); }}
    }}
    .cd.bump {{ animation: bump 0.35s ease; }}
    .now-playing {{
      margin-top: 16px; font-weight: 600; font-size: 14px;
      min-height: 38px; text-align: center;
    }}
    .hint {{ color: #9aa0ad; font-size: 13px; margin-top: 4px; text-align: center; }}
    .stop-btn {{
      margin-top: 14px; width: 48px; height: 48px; border-radius: 10px;
      background: #e23b3b; border: none; cursor: pointer;
      display: flex; align-items: center; justify-content: center;
      transition: transform 0.08s, background 0.15s;
    }}
    .stop-btn::before {{
      content: ""; width: 16px; height: 16px; background: #ffffff; border-radius: 3px;
    }}
    .stop-btn:hover {{ background: #c52f2f; }}
    button:active, .stop-btn:active {{ transform: scale(0.95); }}

    @keyframes pop {{
      0% {{ transform: scale(1); }}
      40% {{ transform: scale(1.025); }}
      100% {{ transform: scale(1); }}
    }}
    .song.clicked {{ animation: pop 0.28s ease; }}

    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(4px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    .now-playing.show {{ animation: fadeIn 0.4s ease; }}

    .eq {{
      display: none; gap: 3px; height: 22px; align-items: flex-end;
      justify-content: center; margin-top: 12px;
    }}
    .eq.on {{ display: flex; }}
    .eq span {{
      width: 4px; background: #8a8f99; border-radius: 2px;
      animation: bounce 0.8s ease-in-out infinite;
    }}
    .eq span:nth-child(2) {{ animation-delay: 0.2s; }}
    .eq span:nth-child(3) {{ animation-delay: 0.4s; }}
    .eq span:nth-child(4) {{ animation-delay: 0.1s; }}
    .eq span:nth-child(5) {{ animation-delay: 0.3s; }}
    @keyframes bounce {{
      0%, 100% {{ height: 5px; }}
      50% {{ height: 22px; }}
    }}
  </style>
</head>
<body>
  <div class="card">
    <h1>Mood App</h1>
    <p class="sub">Tell me how you're feeling and I'll pick songs to match.</p>
    <form method="POST" action="/">
      <textarea name="text">{text}</textarea>
      <button type="submit">Recommend music</button>
    </form>
    {result}
  </div>
  <audio id="player" preload="none"></audio>
  <script>
    var audioCtx = null;
    var stopTimer = null;
    var activeOscs = [];
    var jsonpId = 0;
    var BEAT = 0.42;
    var SAMPLE_LENGTH = 20;
    var STEPS = {{ 'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11 }};

    // Stop every note from the previous sample so nothing overlaps.
    function stopAll() {{
      if (!audioCtx) return;
      var n = audioCtx.currentTime;
      activeOscs.forEach(function (o) {{ try {{ o.stop(n); }} catch (e) {{}} }});
      activeOscs = [];
    }}

    function noteToFreq(name) {{
      if (name[0] === 'R') return 0;
      var semis = STEPS[name[0]];
      var i = 1;
      if (name[i] === '#') {{ semis += 1; i += 1; }}
      else if (name[i] === 'b') {{ semis -= 1; i += 1; }}
      var octave = parseInt(name.slice(i), 10);
      var midi = semis + (octave + 1) * 12;
      return 440 * Math.pow(2, (midi - 69) / 12);
    }}

    // One bowed violin-style note: sawtooth tone, smooth attack, gentle vibrato.
    function violinNote(ctx, out, freq, t, dur) {{
      var end = t + dur;

      var osc = ctx.createOscillator();
      osc.type = 'sawtooth';
      osc.frequency.value = freq;

      // Vibrato: a slow oscillator wobbling the pitch slightly, like a bow.
      var lfo = ctx.createOscillator();
      lfo.type = 'sine';
      lfo.frequency.value = 5.5;
      var lfoGain = ctx.createGain();
      lfoGain.gain.value = freq * 0.011;
      lfo.connect(lfoGain);
      lfoGain.connect(osc.frequency);

      var gain = ctx.createGain();
      gain.gain.setValueAtTime(0.0001, t);
      gain.gain.linearRampToValueAtTime(0.22, t + 0.09);
      gain.gain.setValueAtTime(0.22, Math.max(t + 0.09, end - 0.09));
      gain.gain.linearRampToValueAtTime(0.0001, end);

      osc.connect(gain);
      gain.connect(out);
      osc.start(t);
      osc.stop(end + 0.04);
      lfo.start(t);
      lfo.stop(end + 0.04);
      activeOscs.push(osc);
      activeOscs.push(lfo);
    }}

    function playMelody(melody) {{
      if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      var ctx = audioCtx;
      stopAll();

      // Warm low-pass filter so it sounds mellow and acoustic, not harsh.
      var master = ctx.createGain();
      master.gain.value = 0.85;
      var filter = ctx.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.value = 2800;
      master.connect(filter);
      filter.connect(ctx.destination);

      var notes = melody.trim().split(' ');
      var loopDur = 0;
      notes.forEach(function (token) {{
        loopDur += parseFloat(token.split(':')[1]) * BEAT;
      }});

      var now = ctx.currentTime + 0.05;
      var cursor = now;
      var total = 0;
      // Repeat the melody until we reach about 20 seconds.
      while (total < SAMPLE_LENGTH) {{
        notes.forEach(function (token) {{
          var parts = token.split(':');
          var freq = noteToFreq(parts[0]);
          var dur = parseFloat(parts[1]) * BEAT;
          if (freq > 0) violinNote(ctx, master, freq, cursor, dur);
          cursor += dur;
        }});
        total += loopDur;
      }}
      return total;
    }}

    function setPlaying(on) {{
      var cd = document.getElementById('cd');
      var eq = document.getElementById('eq');
      if (cd) cd.classList.toggle('playing', on);
      if (eq) eq.classList.toggle('on', on);
    }}

    function stopEverything() {{
      stopAll();
      var player = document.getElementById('player');
      if (player) {{ player.pause(); }}
      if (stopTimer) clearTimeout(stopTimer);
      setPlaying(false);
    }}

    // Look up the song on the iTunes Search API (JSONP) for an official preview.
    function norm(s) {{ return (s || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim(); }}

    function fetchPreview(title, artist, onResult) {{
      var cb = 'itc' + (jsonpId++);
      var script = document.createElement('script');
      var done = false;
      var wantT = norm(title);
      var wantA = norm(artist);
      function cleanup() {{
        try {{ delete window[cb]; }} catch (e) {{ window[cb] = undefined; }}
        if (script.parentNode) script.parentNode.removeChild(script);
      }}
      window[cb] = function (data) {{
        done = true;
        var results = (data && data.results) ? data.results : [];
        var bad = /karaoke|tribute|made famous|originally performed|cover|instrumental|remake/i;
        var best = null, bestScore = -1;
        for (var i = 0; i < results.length; i++) {{
          var r = results[i];
          if (!r.previewUrl) continue;
          if (bad.test((r.trackName || '') + ' ' + (r.artistName || ''))) continue;
          var rt = norm(r.trackName), ra = norm(r.artistName);
          // The title must actually match, or we'd play a different song.
          var titleMatch = (rt.indexOf(wantT) >= 0 || wantT.indexOf(rt) >= 0);
          if (!titleMatch) continue;
          var artistMatch = (ra.indexOf(wantA.split(' ')[0]) >= 0
                             || wantA.indexOf(ra.split(' ')[0]) >= 0);
          var score = (artistMatch ? 3 : 0) + (results.length - i) * 0.1;
          if (score > bestScore) {{ bestScore = score; best = r; }}
        }}
        cleanup();
        onResult(best);
      }};
      script.onerror = function () {{ if (!done) {{ cleanup(); onResult(null); }} }};
      script.src = 'https://itunes.apple.com/search?term=' + encodeURIComponent(title + ' ' + artist)
        + '&entity=song&limit=8&callback=' + cb;
      document.body.appendChild(script);
      setTimeout(function () {{ if (!done) {{ cleanup(); onResult(null); }} }}, 6000);
    }}

    function showArt(url) {{
      var screen = document.getElementById('screen');
      var img = document.getElementById('albumArt');
      if (!screen || !img) return;
      if (url) {{
        img.src = url;
        screen.classList.add('has-art');
      }} else {{
        img.removeAttribute('src');
        screen.classList.remove('has-art');
      }}
    }}

    function playFallback(melody) {{
      var duration = playMelody(melody);
      setPlaying(true);
      if (stopTimer) clearTimeout(stopTimer);
      stopTimer = setTimeout(function () {{ setPlaying(false); }}, duration * 1000);
    }}

    document.querySelectorAll('.song').forEach(function (el) {{
      el.addEventListener('click', function () {{
        var title = el.getAttribute('data-title');
        var artist = el.getAttribute('data-artist');
        var melody = el.getAttribute('data-melody');

        document.querySelectorAll('.song').forEach(function (s) {{ s.classList.remove('active'); }});
        el.classList.add('active');

        // Pop animation on the clicked song.
        el.classList.remove('clicked');
        void el.offsetWidth;
        el.classList.add('clicked');

        // Little bump on the cassette.
        var cdEl = document.getElementById('cd');
        if (cdEl) {{
          cdEl.classList.remove('bump');
          void cdEl.offsetWidth;
          cdEl.classList.add('bump');
        }}

        var np = document.getElementById('nowPlaying');
        function showNow(text) {{
          if (!np) return;
          np.textContent = text;
          np.classList.remove('show');
          void np.offsetWidth;
          np.classList.add('show');
        }}

        stopEverything();
        showNow('Loading: ' + title + ' - ' + artist);

        fetchPreview(title, artist, function (r) {{
          // Ignore if the user clicked a different song meanwhile.
          if (!el.classList.contains('active')) return;
          var player = document.getElementById('player');
          var art = r && r.artworkUrl100 ? r.artworkUrl100.replace('100x100', '300x300') : null;
          showArt(art);
          if (r && r.previewUrl && player) {{
            player.src = r.previewUrl;
            var p = player.play();
            if (p && p.catch) p.catch(function () {{ playFallback(melody); }});
            setPlaying(true);
            showNow('Now Playing: ' + title + ' - ' + artist);
            player.onended = function () {{ setPlaying(false); }};
          }} else {{
            showNow('Sample (no preview found): ' + title + ' - ' + artist);
            playFallback(melody);
          }}
        }});
      }});
    }});

    var stopBtn = document.getElementById('stopBtn');
    if (stopBtn) {{
      stopBtn.addEventListener('click', function () {{
        stopEverything();
        showArt(null);
        var np = document.getElementById('nowPlaying');
        if (np) np.textContent = '';
        document.querySelectorAll('.song').forEach(function (s) {{ s.classList.remove('active'); }});
      }});
    }}
  </script>
</body>
</html>"""

RESULT = """<div class="result">
  <div class="mood-banner">You're feeling {mood}</div>
  <div class="meta">Sentiment: {sentiment} &nbsp;·&nbsp; Emotion: {emotion}</div>
  <div class="player-layout">
    <div class="cd-side">
      <div class="cd" id="cd">
        <div class="screen" id="screen">
          <div class="ph">No song playing</div>
          <img id="albumArt" alt="">
        </div>
        <div class="wheel"></div>
      </div>
      <div class="now-playing" id="nowPlaying"></div>
      <div class="eq" id="eq"><span></span><span></span><span></span><span></span><span></span></div>
      <button type="button" class="stop-btn" id="stopBtn" aria-label="Stop"></button>
      <div class="hint">Click a song to play a sample</div>
    </div>
    <div class="song-list">{songs}</div>
  </div>
</div>"""

SONG_ROW = """<div class="song" data-title="{title}" data-artist="{artist}" data-melody="{melody}">
  <div class="num">{n}</div>
  <div><div class="title">{title}</div><div class="artist">{artist} &middot; {genre}</div></div>
</div>"""


def render(text=""):
    if not text.strip():
        return PAGE.format(text="", result="")

    analysis = analyze(text)
    mood = decide_mood(analysis)
    songs_html = "".join(
        SONG_ROW.format(n=i, title=t, artist=a, genre=g, melody=m)
        for i, (t, a, g, m) in enumerate(recommend(mood), 1)
    )
    result = RESULT.format(
        mood=mood,
        sentiment=analysis["sentiment"],
        emotion=analysis["emotion"],
        songs=songs_html,
    )
    return PAGE.format(text=text.replace("<", "&lt;"), result=result)


class Handler(BaseHTTPRequestHandler):
    def _send(self, html):
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path != "/":
            self.send_error(404)
            return
        self._send(render())

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(length).decode("utf-8")
        fields = parse_qs(data)
        text = fields.get("text", [""])[0]
        self._send(render(text))

    def log_message(self, *args):
        pass


def start_server():
    for port in range(PORT, PORT + 20):
        try:
            return HTTPServer(("127.0.0.1", port), Handler), port
        except OSError:
            continue
    raise OSError("No free port found between 8000 and 8019.")


def main():
    server, port = start_server()
    url = f"http://localhost:{port}"
    print(f"\n  Mood App is running!")
    print(f"  Open this in your browser:  {url}\n")
    print("  Press Ctrl+C here to stop.\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
