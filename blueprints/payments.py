<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aloha Wellness - Lose Weight the Kingdom Way</title>
    <meta name="google-site-verification" content="ba5d8e311152a3a0" />
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-V2NY3MEWKB"></script>
    <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-V2NY3MEWKB');</script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: Georgia, serif; background: #0a2a35; color: white; }
        a { text-decoration: none; }

        /* NAV */
        .aw-nav { position: fixed; top: 0; left: 0; right: 0; z-index: 9999; padding: 1rem 2rem; display: flex; align-items: center; justify-content: space-between; background: rgba(10,42,53,0.95); }
        .aw-nav img { height: 50px; width: auto; }
        .aw-nav-link { color: #c8a84b; font-weight: 600; font-size: 1rem; }
        .aw-nav-link:hover { color: white; }

        /* HERO */
        .aw-hero { min-height: 100vh; background: linear-gradient(160deg, #0a2a35 0%, #1a5c6b 40%, #2d8a70 100%); display: flex; align-items: center; justify-content: center; padding: 8rem 2rem 4rem; }
        .aw-inner { max-width: 1100px; width: 100%; display: grid; grid-template-columns: 1fr 1fr; gap: 4rem; align-items: center; }
        .aw-eyebrow { letter-spacing: 0.3em; text-transform: uppercase; color: #c8a84b; font-size: 0.85rem; margin-bottom: 1.5rem; }
        .aw-inner h1 { font-size: clamp(2rem, 5vw, 3.5rem); font-weight: 900; line-height: 1.1; margin-bottom: 1.5rem; color: white; }
        .aw-inner h1 span { color: #c8a84b; display: block; }
        .aw-subhead { font-size: 1.1rem; line-height: 1.7; color: rgba(255,255,255,0.85); margin-bottom: 2rem; border-left: 3px solid #c8a84b; padding-left: 1.25rem; }
        .aw-counter { background: rgba(200,168,75,0.15); border: 2px solid #c8a84b; border-radius: 12px; padding: 1.25rem; margin-bottom: 2rem; text-align: center; }
        .aw-counter-label { font-size: 0.8rem; letter-spacing: 0.2em; text-transform: uppercase; color: #c8a84b; margin-bottom: 0.5rem; }
        .aw-spots { font-size: 3rem; font-weight: 900; color: white; line-height: 1; }
        .aw-spots-sub { font-size: 0.9rem; color: rgba(255,255,255,0.7); margin-top: 0.25rem; }
        .aw-price-row { display: flex; align-items: center; gap: 1.5rem; margin-bottom: 1.5rem; }
        .aw-sale { font-size: 3rem; font-weight: 900; color: #c8a84b; }
        .aw-regular { font-size: 1.5rem; color: rgba(255,255,255,0.4); text-decoration: line-through; }
        .aw-save { background: #d4622a; color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.85rem; font-weight: 700; }
        .aw-btn { display: block; width: 100%; padding: 1.25rem 2rem; background: linear-gradient(135deg, #d4622a, #b8511f); color: white; font-size: 1.2rem; font-weight: 700; border-radius: 8px; text-align: center; box-shadow: 0 8px 30px rgba(212,98,42,0.4); transition: transform 0.2s; }
        .aw-btn:hover { transform: translateY(-2px); color: white; }
        .aw-small { text-align: center; margin-top: 1rem; font-size: 0.85rem; color: rgba(255,255,255,0.5); }
        .aw-photo { position: relative; }
        .aw-photo img { width: 100%; border-radius: 16px; box-shadow: 0 30px 80px rgba(0,0,0,0.5); display: block; }
        .aw-badge { position: absolute; top: -15px; right: -15px; width: 90px; height: 90px; background: #c8a84b; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; }
        .aw-badge-num { font-size: 1.5rem; font-weight: 900; color: #1a1a1a; line-height: 1; }
        .aw-badge-text { font-size: 0.55rem; font-weight: 700; color: #1a1a1a; text-transform: uppercase; text-align: center; }

        /* STORY */
        .aw-story { background: #f5e6c8; color: #1a1a1a; padding: 5rem 2rem; }
        .aw-story-inner { max-width: 800px; margin: 0 auto; }
        .aw-story h2 { font-size: clamp(1.8rem, 4vw, 2.8rem); color: #1a5c6b; margin-bottom: 2rem; }
        .aw-story p { font-size: 1.15rem; line-height: 1.9; margin-bottom: 1.5rem; color: #333; }
        .aw-quote { background: #1a5c6b; color: white; padding: 2rem; border-radius: 12px; margin: 2rem 0; font-size: 1.4rem; font-style: italic; line-height: 1.5; }

        /* BENEFITS */
        .aw-benefits { background: #0d1f25; padding: 5rem 2rem; }
        .aw-benefits h2 { font-size: clamp(1.8rem, 4vw, 2.5rem); text-align: center; color: #c8a84b; margin-bottom: 3rem; }
        .aw-grid { max-width: 900px; margin: 0 auto; display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1.5rem; }
        .aw-card { background: rgba(255,255,255,0.05); border: 1px solid rgba(200,168,75,0.2); border-radius: 12px; padding: 1.75rem; }
        .aw-card .icon { font-size: 2rem; margin-bottom: 1rem; }
        .aw-card h3 { font-size: 1.1rem; color: #c8a84b; margin-bottom: 0.75rem; }
        .aw-card p { font-size: 0.95rem; color: rgba(255,255,255,0.7); line-height: 1.7; }

        /* CTA */
        .aw-cta { background: linear-gradient(135deg, #1a5c6b, #0a2a35); padding: 5rem 2rem; text-align: center; }
        .aw-cta h2 { font-size: clamp(1.8rem, 4vw, 2.8rem); color: white; margin-bottom: 1rem; }
        .aw-cta p { font-size: 1.1rem; color: rgba(255,255,255,0.7); margin-bottom: 2rem; }
        .aw-cta .aw-counter { max-width: 400px; margin: 0 auto 2rem; }
        .aw-cta .aw-price-row { justify-content: center; margin-bottom: 1.5rem; }
        .aw-cta .aw-btn { max-width: 400px; margin: 0 auto; }

        /* FOOTER */
        .aw-footer { text-align: center; padding: 2rem; color: rgba(255,255,255,0.5); background: #0a2a35; font-size: 0.9rem; }

        @media (max-width: 768px) {
            .aw-inner { grid-template-columns: 1fr; gap: 2rem; }
            .aw-photo { order: -1; }
        }
    </style>
</head>
<body>

<nav class="aw-nav">
    <a href="/"><img src="/static/images/output-onlinepngtools.png" alt="Ke Aupuni O Ke Akua"></a>
    <a href="/" class="aw-nav-link">← Back to Site</a>
</nav>

<section class="aw-hero">
    <div class="aw-inner">
        <div>
            <p class="aw-eyebrow">🌺 Molokaʻi, Hawaiʻi</p>
            <h1>54 Pounds Gone.<span>No Diet. No Starving.</span></h1>
            <p class="aw-subhead">I went from a 42 to a 34 waist. I didn't change <em>what</em> I ate. I changed <em>when</em> — and everything changed.</p>
            <div class="aw-counter">
                <div class="aw-counter-label">🔥 Founding Member Offer — First 100 Only</div>
                <div class="aw-spots" id="spotsLeft">87</div>
                <div class="aw-spots-sub">spots remaining at half price</div>
            </div>
            <div class="aw-price-row">
                <span class="aw-sale">$23.50</span>
                <span class="aw-regular">$47</span>
                <span class="aw-save">SAVE 50%</span>
            </div>
            <a href="/checkout/prod_aloha_wellness" class="aw-btn">🌺 Yes — I Want Aloha Wellness Now</a>
            <p class="aw-small">📱 Instant digital download • Read on any device</p>
        </div>
        <div class="aw-photo">
            <img src="/static/images/Paniolo_Phil_MR.jpg" alt="Kahu Phil Stephens - Paniolo on Molokaʻi">
            <div class="aw-badge">
                <span class="aw-badge-num">54</span>
                <span class="aw-badge-text">lbs lost</span>
            </div>
        </div>
    </div>
</section>

<section class="aw-story">
    <div class="aw-story-inner">
        <h2>The Story Nobody Expected</h2>
        <p>I'm a 67-year-old Hawaiian pastor and Paniolo. I spent 30 years as a Paniolo on Molokaʻi. I know hard work. I know the land. And I know my body.</p>
        <p>Within two weeks of one simple change, my weight started dropping. After three months, everybody on Molokaʻi noticed. I went from a size 42 waist to a 34. Not from dieting. Not from starving. From understanding one thing God designed into your body from the very beginning.</p>
        <div class="aw-quote">
            "I only ate when I was hungry. That's it. And the weight left."
            <div style="font-size:0.9rem;margin-top:0.75rem;color:#c8a84b;">— Kahu Phil Stephens</div>
        </div>
        <p>This isn't another diet book. It's a Kingdom book. God designed your body with wisdom. Aloha Wellness helps you return to that design — and the results will surprise you.</p>
    </div>
</section>

<section class="aw-benefits">
    <h2>What You'll Discover Inside</h2>
    <div class="aw-grid">
        <div class="aw-card"><div class="icon">🍽️</div><h3>Eat When Hungry — Not By the Clock</h3><p>The one principle that changed everything. Your body knows when it needs fuel. Learn to listen.</p></div>
        <div class="aw-card"><div class="icon">🌿</div><h3>Hawaiian Mana'o (Wisdom)</h3><p>Ancient Hawaiian understanding of nourishment — Aloha 'Āina, Lōkahi, Mālama — applied to how you eat.</p></div>
        <div class="aw-card"><div class="icon">👑</div><h3>Kingdom Design for Your Body</h3><p>God didn't create your body to be overweight. Discover the design He built in from the beginning.</p></div>
        <div class="aw-card"><div class="icon">📉</div><h3>The Belly Secret</h3><p>What Kahu discovered after the initial weight loss that took him from a 42 to a 34 waist.</p></div>
        <div class="aw-card"><div class="icon">🏇</div><h3>A Paniolo's Perspective</h3><p>30 years as a Paniolo on Molokaʻi taught Kahu Phil how animals eat. And how we should too.</p></div>
        <div class="aw-card"><div class="icon">🙏</div><h3>Spirit, Soul & Body</h3><p>True wellness isn't just physical. Learn how your spiritual life and your physical health are connected.</p></div>
    </div>
</section>

<section class="aw-cta">
    <h2>This Is Your Moment</h2>
    <p>First 100 founding members get Aloha Wellness at half price. Forever.</p>
    <div class="aw-counter">
        <div class="aw-counter-label">🔥 Spots Remaining at $23.50</div>
        <div class="aw-spots" id="spotsLeft2">87</div>
        <div class="aw-spots-sub">of 100 founding member spots</div>
    </div>
    <div class="aw-price-row">
        <span class="aw-sale">$23.50</span>
        <span class="aw-regular">$47</span>
        <span class="aw-save">SAVE 50%</span>
    </div>
    <a href="/checkout/prod_aloha_wellness" class="aw-btn">🌺 Get Aloha Wellness — $23.50</a>
    <p class="aw-small" style="margin-top:1rem;">📱 Instant digital download • Read on any device<br>Questions? <a href="/cdn-cgi/l/email-protection" class="__cf_email__" data-cfemail="6308020b16130b0a0f230806021613160d0a4d05020a170b">[email&#160;protected]</a></p>
</section>

<footer class="aw-footer">
    <p>© 2025 Ke Aupuni O Ke Akua. All rights reserved. Made with aloha in Hawaiʻi. 🌺</p>
</footer>

<script data-cfasync="false" src="/cdn-cgi/scripts/5c5dd728/cloudflare-static/email-decode.min.js"></script><script>
let spots = 87;
function updateCounter() {
    document.getElementById('spotsLeft').textContent = spots;
    document.getElementById('spotsLeft2'
